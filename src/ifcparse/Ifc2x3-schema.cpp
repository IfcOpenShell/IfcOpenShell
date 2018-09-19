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

entity* IFC2X3_Ifc2DCompositeCurve_type = 0;
entity* IFC2X3_IfcActionRequest_type = 0;
entity* IFC2X3_IfcActor_type = 0;
entity* IFC2X3_IfcActorRole_type = 0;
entity* IFC2X3_IfcActuatorType_type = 0;
entity* IFC2X3_IfcAddress_type = 0;
entity* IFC2X3_IfcAirTerminalBoxType_type = 0;
entity* IFC2X3_IfcAirTerminalType_type = 0;
entity* IFC2X3_IfcAirToAirHeatRecoveryType_type = 0;
entity* IFC2X3_IfcAlarmType_type = 0;
entity* IFC2X3_IfcAngularDimension_type = 0;
entity* IFC2X3_IfcAnnotation_type = 0;
entity* IFC2X3_IfcAnnotationCurveOccurrence_type = 0;
entity* IFC2X3_IfcAnnotationFillArea_type = 0;
entity* IFC2X3_IfcAnnotationFillAreaOccurrence_type = 0;
entity* IFC2X3_IfcAnnotationOccurrence_type = 0;
entity* IFC2X3_IfcAnnotationSurface_type = 0;
entity* IFC2X3_IfcAnnotationSurfaceOccurrence_type = 0;
entity* IFC2X3_IfcAnnotationSymbolOccurrence_type = 0;
entity* IFC2X3_IfcAnnotationTextOccurrence_type = 0;
entity* IFC2X3_IfcApplication_type = 0;
entity* IFC2X3_IfcAppliedValue_type = 0;
entity* IFC2X3_IfcAppliedValueRelationship_type = 0;
entity* IFC2X3_IfcApproval_type = 0;
entity* IFC2X3_IfcApprovalActorRelationship_type = 0;
entity* IFC2X3_IfcApprovalPropertyRelationship_type = 0;
entity* IFC2X3_IfcApprovalRelationship_type = 0;
entity* IFC2X3_IfcArbitraryClosedProfileDef_type = 0;
entity* IFC2X3_IfcArbitraryOpenProfileDef_type = 0;
entity* IFC2X3_IfcArbitraryProfileDefWithVoids_type = 0;
entity* IFC2X3_IfcAsset_type = 0;
entity* IFC2X3_IfcAsymmetricIShapeProfileDef_type = 0;
entity* IFC2X3_IfcAxis1Placement_type = 0;
entity* IFC2X3_IfcAxis2Placement2D_type = 0;
entity* IFC2X3_IfcAxis2Placement3D_type = 0;
entity* IFC2X3_IfcBSplineCurve_type = 0;
entity* IFC2X3_IfcBeam_type = 0;
entity* IFC2X3_IfcBeamType_type = 0;
entity* IFC2X3_IfcBezierCurve_type = 0;
entity* IFC2X3_IfcBlobTexture_type = 0;
entity* IFC2X3_IfcBlock_type = 0;
entity* IFC2X3_IfcBoilerType_type = 0;
entity* IFC2X3_IfcBooleanClippingResult_type = 0;
entity* IFC2X3_IfcBooleanResult_type = 0;
entity* IFC2X3_IfcBoundaryCondition_type = 0;
entity* IFC2X3_IfcBoundaryEdgeCondition_type = 0;
entity* IFC2X3_IfcBoundaryFaceCondition_type = 0;
entity* IFC2X3_IfcBoundaryNodeCondition_type = 0;
entity* IFC2X3_IfcBoundaryNodeConditionWarping_type = 0;
entity* IFC2X3_IfcBoundedCurve_type = 0;
entity* IFC2X3_IfcBoundedSurface_type = 0;
entity* IFC2X3_IfcBoundingBox_type = 0;
entity* IFC2X3_IfcBoxedHalfSpace_type = 0;
entity* IFC2X3_IfcBuilding_type = 0;
entity* IFC2X3_IfcBuildingElement_type = 0;
entity* IFC2X3_IfcBuildingElementComponent_type = 0;
entity* IFC2X3_IfcBuildingElementPart_type = 0;
entity* IFC2X3_IfcBuildingElementProxy_type = 0;
entity* IFC2X3_IfcBuildingElementProxyType_type = 0;
entity* IFC2X3_IfcBuildingElementType_type = 0;
entity* IFC2X3_IfcBuildingStorey_type = 0;
entity* IFC2X3_IfcCShapeProfileDef_type = 0;
entity* IFC2X3_IfcCableCarrierFittingType_type = 0;
entity* IFC2X3_IfcCableCarrierSegmentType_type = 0;
entity* IFC2X3_IfcCableSegmentType_type = 0;
entity* IFC2X3_IfcCalendarDate_type = 0;
entity* IFC2X3_IfcCartesianPoint_type = 0;
entity* IFC2X3_IfcCartesianTransformationOperator_type = 0;
entity* IFC2X3_IfcCartesianTransformationOperator2D_type = 0;
entity* IFC2X3_IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IFC2X3_IfcCartesianTransformationOperator3D_type = 0;
entity* IFC2X3_IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IFC2X3_IfcCenterLineProfileDef_type = 0;
entity* IFC2X3_IfcChamferEdgeFeature_type = 0;
entity* IFC2X3_IfcChillerType_type = 0;
entity* IFC2X3_IfcCircle_type = 0;
entity* IFC2X3_IfcCircleHollowProfileDef_type = 0;
entity* IFC2X3_IfcCircleProfileDef_type = 0;
entity* IFC2X3_IfcClassification_type = 0;
entity* IFC2X3_IfcClassificationItem_type = 0;
entity* IFC2X3_IfcClassificationItemRelationship_type = 0;
entity* IFC2X3_IfcClassificationNotation_type = 0;
entity* IFC2X3_IfcClassificationNotationFacet_type = 0;
entity* IFC2X3_IfcClassificationReference_type = 0;
entity* IFC2X3_IfcClosedShell_type = 0;
entity* IFC2X3_IfcCoilType_type = 0;
entity* IFC2X3_IfcColourRgb_type = 0;
entity* IFC2X3_IfcColourSpecification_type = 0;
entity* IFC2X3_IfcColumn_type = 0;
entity* IFC2X3_IfcColumnType_type = 0;
entity* IFC2X3_IfcComplexProperty_type = 0;
entity* IFC2X3_IfcCompositeCurve_type = 0;
entity* IFC2X3_IfcCompositeCurveSegment_type = 0;
entity* IFC2X3_IfcCompositeProfileDef_type = 0;
entity* IFC2X3_IfcCompressorType_type = 0;
entity* IFC2X3_IfcCondenserType_type = 0;
entity* IFC2X3_IfcCondition_type = 0;
entity* IFC2X3_IfcConditionCriterion_type = 0;
entity* IFC2X3_IfcConic_type = 0;
entity* IFC2X3_IfcConnectedFaceSet_type = 0;
entity* IFC2X3_IfcConnectionCurveGeometry_type = 0;
entity* IFC2X3_IfcConnectionGeometry_type = 0;
entity* IFC2X3_IfcConnectionPointEccentricity_type = 0;
entity* IFC2X3_IfcConnectionPointGeometry_type = 0;
entity* IFC2X3_IfcConnectionPortGeometry_type = 0;
entity* IFC2X3_IfcConnectionSurfaceGeometry_type = 0;
entity* IFC2X3_IfcConstraint_type = 0;
entity* IFC2X3_IfcConstraintAggregationRelationship_type = 0;
entity* IFC2X3_IfcConstraintClassificationRelationship_type = 0;
entity* IFC2X3_IfcConstraintRelationship_type = 0;
entity* IFC2X3_IfcConstructionEquipmentResource_type = 0;
entity* IFC2X3_IfcConstructionMaterialResource_type = 0;
entity* IFC2X3_IfcConstructionProductResource_type = 0;
entity* IFC2X3_IfcConstructionResource_type = 0;
entity* IFC2X3_IfcContextDependentUnit_type = 0;
entity* IFC2X3_IfcControl_type = 0;
entity* IFC2X3_IfcControllerType_type = 0;
entity* IFC2X3_IfcConversionBasedUnit_type = 0;
entity* IFC2X3_IfcCooledBeamType_type = 0;
entity* IFC2X3_IfcCoolingTowerType_type = 0;
entity* IFC2X3_IfcCoordinatedUniversalTimeOffset_type = 0;
entity* IFC2X3_IfcCostItem_type = 0;
entity* IFC2X3_IfcCostSchedule_type = 0;
entity* IFC2X3_IfcCostValue_type = 0;
entity* IFC2X3_IfcCovering_type = 0;
entity* IFC2X3_IfcCoveringType_type = 0;
entity* IFC2X3_IfcCraneRailAShapeProfileDef_type = 0;
entity* IFC2X3_IfcCraneRailFShapeProfileDef_type = 0;
entity* IFC2X3_IfcCrewResource_type = 0;
entity* IFC2X3_IfcCsgPrimitive3D_type = 0;
entity* IFC2X3_IfcCsgSolid_type = 0;
entity* IFC2X3_IfcCurrencyRelationship_type = 0;
entity* IFC2X3_IfcCurtainWall_type = 0;
entity* IFC2X3_IfcCurtainWallType_type = 0;
entity* IFC2X3_IfcCurve_type = 0;
entity* IFC2X3_IfcCurveBoundedPlane_type = 0;
entity* IFC2X3_IfcCurveStyle_type = 0;
entity* IFC2X3_IfcCurveStyleFont_type = 0;
entity* IFC2X3_IfcCurveStyleFontAndScaling_type = 0;
entity* IFC2X3_IfcCurveStyleFontPattern_type = 0;
entity* IFC2X3_IfcDamperType_type = 0;
entity* IFC2X3_IfcDateAndTime_type = 0;
entity* IFC2X3_IfcDefinedSymbol_type = 0;
entity* IFC2X3_IfcDerivedProfileDef_type = 0;
entity* IFC2X3_IfcDerivedUnit_type = 0;
entity* IFC2X3_IfcDerivedUnitElement_type = 0;
entity* IFC2X3_IfcDiameterDimension_type = 0;
entity* IFC2X3_IfcDimensionCalloutRelationship_type = 0;
entity* IFC2X3_IfcDimensionCurve_type = 0;
entity* IFC2X3_IfcDimensionCurveDirectedCallout_type = 0;
entity* IFC2X3_IfcDimensionCurveTerminator_type = 0;
entity* IFC2X3_IfcDimensionPair_type = 0;
entity* IFC2X3_IfcDimensionalExponents_type = 0;
entity* IFC2X3_IfcDirection_type = 0;
entity* IFC2X3_IfcDiscreteAccessory_type = 0;
entity* IFC2X3_IfcDiscreteAccessoryType_type = 0;
entity* IFC2X3_IfcDistributionChamberElement_type = 0;
entity* IFC2X3_IfcDistributionChamberElementType_type = 0;
entity* IFC2X3_IfcDistributionControlElement_type = 0;
entity* IFC2X3_IfcDistributionControlElementType_type = 0;
entity* IFC2X3_IfcDistributionElement_type = 0;
entity* IFC2X3_IfcDistributionElementType_type = 0;
entity* IFC2X3_IfcDistributionFlowElement_type = 0;
entity* IFC2X3_IfcDistributionFlowElementType_type = 0;
entity* IFC2X3_IfcDistributionPort_type = 0;
entity* IFC2X3_IfcDocumentElectronicFormat_type = 0;
entity* IFC2X3_IfcDocumentInformation_type = 0;
entity* IFC2X3_IfcDocumentInformationRelationship_type = 0;
entity* IFC2X3_IfcDocumentReference_type = 0;
entity* IFC2X3_IfcDoor_type = 0;
entity* IFC2X3_IfcDoorLiningProperties_type = 0;
entity* IFC2X3_IfcDoorPanelProperties_type = 0;
entity* IFC2X3_IfcDoorStyle_type = 0;
entity* IFC2X3_IfcDraughtingCallout_type = 0;
entity* IFC2X3_IfcDraughtingCalloutRelationship_type = 0;
entity* IFC2X3_IfcDraughtingPreDefinedColour_type = 0;
entity* IFC2X3_IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IFC2X3_IfcDraughtingPreDefinedTextFont_type = 0;
entity* IFC2X3_IfcDuctFittingType_type = 0;
entity* IFC2X3_IfcDuctSegmentType_type = 0;
entity* IFC2X3_IfcDuctSilencerType_type = 0;
entity* IFC2X3_IfcEdge_type = 0;
entity* IFC2X3_IfcEdgeCurve_type = 0;
entity* IFC2X3_IfcEdgeFeature_type = 0;
entity* IFC2X3_IfcEdgeLoop_type = 0;
entity* IFC2X3_IfcElectricApplianceType_type = 0;
entity* IFC2X3_IfcElectricDistributionPoint_type = 0;
entity* IFC2X3_IfcElectricFlowStorageDeviceType_type = 0;
entity* IFC2X3_IfcElectricGeneratorType_type = 0;
entity* IFC2X3_IfcElectricHeaterType_type = 0;
entity* IFC2X3_IfcElectricMotorType_type = 0;
entity* IFC2X3_IfcElectricTimeControlType_type = 0;
entity* IFC2X3_IfcElectricalBaseProperties_type = 0;
entity* IFC2X3_IfcElectricalCircuit_type = 0;
entity* IFC2X3_IfcElectricalElement_type = 0;
entity* IFC2X3_IfcElement_type = 0;
entity* IFC2X3_IfcElementAssembly_type = 0;
entity* IFC2X3_IfcElementComponent_type = 0;
entity* IFC2X3_IfcElementComponentType_type = 0;
entity* IFC2X3_IfcElementQuantity_type = 0;
entity* IFC2X3_IfcElementType_type = 0;
entity* IFC2X3_IfcElementarySurface_type = 0;
entity* IFC2X3_IfcEllipse_type = 0;
entity* IFC2X3_IfcEllipseProfileDef_type = 0;
entity* IFC2X3_IfcEnergyConversionDevice_type = 0;
entity* IFC2X3_IfcEnergyConversionDeviceType_type = 0;
entity* IFC2X3_IfcEnergyProperties_type = 0;
entity* IFC2X3_IfcEnvironmentalImpactValue_type = 0;
entity* IFC2X3_IfcEquipmentElement_type = 0;
entity* IFC2X3_IfcEquipmentStandard_type = 0;
entity* IFC2X3_IfcEvaporativeCoolerType_type = 0;
entity* IFC2X3_IfcEvaporatorType_type = 0;
entity* IFC2X3_IfcExtendedMaterialProperties_type = 0;
entity* IFC2X3_IfcExternalReference_type = 0;
entity* IFC2X3_IfcExternallyDefinedHatchStyle_type = 0;
entity* IFC2X3_IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IFC2X3_IfcExternallyDefinedSymbol_type = 0;
entity* IFC2X3_IfcExternallyDefinedTextFont_type = 0;
entity* IFC2X3_IfcExtrudedAreaSolid_type = 0;
entity* IFC2X3_IfcFace_type = 0;
entity* IFC2X3_IfcFaceBasedSurfaceModel_type = 0;
entity* IFC2X3_IfcFaceBound_type = 0;
entity* IFC2X3_IfcFaceOuterBound_type = 0;
entity* IFC2X3_IfcFaceSurface_type = 0;
entity* IFC2X3_IfcFacetedBrep_type = 0;
entity* IFC2X3_IfcFacetedBrepWithVoids_type = 0;
entity* IFC2X3_IfcFailureConnectionCondition_type = 0;
entity* IFC2X3_IfcFanType_type = 0;
entity* IFC2X3_IfcFastener_type = 0;
entity* IFC2X3_IfcFastenerType_type = 0;
entity* IFC2X3_IfcFeatureElement_type = 0;
entity* IFC2X3_IfcFeatureElementAddition_type = 0;
entity* IFC2X3_IfcFeatureElementSubtraction_type = 0;
entity* IFC2X3_IfcFillAreaStyle_type = 0;
entity* IFC2X3_IfcFillAreaStyleHatching_type = 0;
entity* IFC2X3_IfcFillAreaStyleTileSymbolWithStyle_type = 0;
entity* IFC2X3_IfcFillAreaStyleTiles_type = 0;
entity* IFC2X3_IfcFilterType_type = 0;
entity* IFC2X3_IfcFireSuppressionTerminalType_type = 0;
entity* IFC2X3_IfcFlowController_type = 0;
entity* IFC2X3_IfcFlowControllerType_type = 0;
entity* IFC2X3_IfcFlowFitting_type = 0;
entity* IFC2X3_IfcFlowFittingType_type = 0;
entity* IFC2X3_IfcFlowInstrumentType_type = 0;
entity* IFC2X3_IfcFlowMeterType_type = 0;
entity* IFC2X3_IfcFlowMovingDevice_type = 0;
entity* IFC2X3_IfcFlowMovingDeviceType_type = 0;
entity* IFC2X3_IfcFlowSegment_type = 0;
entity* IFC2X3_IfcFlowSegmentType_type = 0;
entity* IFC2X3_IfcFlowStorageDevice_type = 0;
entity* IFC2X3_IfcFlowStorageDeviceType_type = 0;
entity* IFC2X3_IfcFlowTerminal_type = 0;
entity* IFC2X3_IfcFlowTerminalType_type = 0;
entity* IFC2X3_IfcFlowTreatmentDevice_type = 0;
entity* IFC2X3_IfcFlowTreatmentDeviceType_type = 0;
entity* IFC2X3_IfcFluidFlowProperties_type = 0;
entity* IFC2X3_IfcFooting_type = 0;
entity* IFC2X3_IfcFuelProperties_type = 0;
entity* IFC2X3_IfcFurnishingElement_type = 0;
entity* IFC2X3_IfcFurnishingElementType_type = 0;
entity* IFC2X3_IfcFurnitureStandard_type = 0;
entity* IFC2X3_IfcFurnitureType_type = 0;
entity* IFC2X3_IfcGasTerminalType_type = 0;
entity* IFC2X3_IfcGeneralMaterialProperties_type = 0;
entity* IFC2X3_IfcGeneralProfileProperties_type = 0;
entity* IFC2X3_IfcGeometricCurveSet_type = 0;
entity* IFC2X3_IfcGeometricRepresentationContext_type = 0;
entity* IFC2X3_IfcGeometricRepresentationItem_type = 0;
entity* IFC2X3_IfcGeometricRepresentationSubContext_type = 0;
entity* IFC2X3_IfcGeometricSet_type = 0;
entity* IFC2X3_IfcGrid_type = 0;
entity* IFC2X3_IfcGridAxis_type = 0;
entity* IFC2X3_IfcGridPlacement_type = 0;
entity* IFC2X3_IfcGroup_type = 0;
entity* IFC2X3_IfcHalfSpaceSolid_type = 0;
entity* IFC2X3_IfcHeatExchangerType_type = 0;
entity* IFC2X3_IfcHumidifierType_type = 0;
entity* IFC2X3_IfcHygroscopicMaterialProperties_type = 0;
entity* IFC2X3_IfcIShapeProfileDef_type = 0;
entity* IFC2X3_IfcImageTexture_type = 0;
entity* IFC2X3_IfcInventory_type = 0;
entity* IFC2X3_IfcIrregularTimeSeries_type = 0;
entity* IFC2X3_IfcIrregularTimeSeriesValue_type = 0;
entity* IFC2X3_IfcJunctionBoxType_type = 0;
entity* IFC2X3_IfcLShapeProfileDef_type = 0;
entity* IFC2X3_IfcLaborResource_type = 0;
entity* IFC2X3_IfcLampType_type = 0;
entity* IFC2X3_IfcLibraryInformation_type = 0;
entity* IFC2X3_IfcLibraryReference_type = 0;
entity* IFC2X3_IfcLightDistributionData_type = 0;
entity* IFC2X3_IfcLightFixtureType_type = 0;
entity* IFC2X3_IfcLightIntensityDistribution_type = 0;
entity* IFC2X3_IfcLightSource_type = 0;
entity* IFC2X3_IfcLightSourceAmbient_type = 0;
entity* IFC2X3_IfcLightSourceDirectional_type = 0;
entity* IFC2X3_IfcLightSourceGoniometric_type = 0;
entity* IFC2X3_IfcLightSourcePositional_type = 0;
entity* IFC2X3_IfcLightSourceSpot_type = 0;
entity* IFC2X3_IfcLine_type = 0;
entity* IFC2X3_IfcLinearDimension_type = 0;
entity* IFC2X3_IfcLocalPlacement_type = 0;
entity* IFC2X3_IfcLocalTime_type = 0;
entity* IFC2X3_IfcLoop_type = 0;
entity* IFC2X3_IfcManifoldSolidBrep_type = 0;
entity* IFC2X3_IfcMappedItem_type = 0;
entity* IFC2X3_IfcMaterial_type = 0;
entity* IFC2X3_IfcMaterialClassificationRelationship_type = 0;
entity* IFC2X3_IfcMaterialDefinitionRepresentation_type = 0;
entity* IFC2X3_IfcMaterialLayer_type = 0;
entity* IFC2X3_IfcMaterialLayerSet_type = 0;
entity* IFC2X3_IfcMaterialLayerSetUsage_type = 0;
entity* IFC2X3_IfcMaterialList_type = 0;
entity* IFC2X3_IfcMaterialProperties_type = 0;
entity* IFC2X3_IfcMeasureWithUnit_type = 0;
entity* IFC2X3_IfcMechanicalConcreteMaterialProperties_type = 0;
entity* IFC2X3_IfcMechanicalFastener_type = 0;
entity* IFC2X3_IfcMechanicalFastenerType_type = 0;
entity* IFC2X3_IfcMechanicalMaterialProperties_type = 0;
entity* IFC2X3_IfcMechanicalSteelMaterialProperties_type = 0;
entity* IFC2X3_IfcMember_type = 0;
entity* IFC2X3_IfcMemberType_type = 0;
entity* IFC2X3_IfcMetric_type = 0;
entity* IFC2X3_IfcMonetaryUnit_type = 0;
entity* IFC2X3_IfcMotorConnectionType_type = 0;
entity* IFC2X3_IfcMove_type = 0;
entity* IFC2X3_IfcNamedUnit_type = 0;
entity* IFC2X3_IfcObject_type = 0;
entity* IFC2X3_IfcObjectDefinition_type = 0;
entity* IFC2X3_IfcObjectPlacement_type = 0;
entity* IFC2X3_IfcObjective_type = 0;
entity* IFC2X3_IfcOccupant_type = 0;
entity* IFC2X3_IfcOffsetCurve2D_type = 0;
entity* IFC2X3_IfcOffsetCurve3D_type = 0;
entity* IFC2X3_IfcOneDirectionRepeatFactor_type = 0;
entity* IFC2X3_IfcOpenShell_type = 0;
entity* IFC2X3_IfcOpeningElement_type = 0;
entity* IFC2X3_IfcOpticalMaterialProperties_type = 0;
entity* IFC2X3_IfcOrderAction_type = 0;
entity* IFC2X3_IfcOrganization_type = 0;
entity* IFC2X3_IfcOrganizationRelationship_type = 0;
entity* IFC2X3_IfcOrientedEdge_type = 0;
entity* IFC2X3_IfcOutletType_type = 0;
entity* IFC2X3_IfcOwnerHistory_type = 0;
entity* IFC2X3_IfcParameterizedProfileDef_type = 0;
entity* IFC2X3_IfcPath_type = 0;
entity* IFC2X3_IfcPerformanceHistory_type = 0;
entity* IFC2X3_IfcPermeableCoveringProperties_type = 0;
entity* IFC2X3_IfcPermit_type = 0;
entity* IFC2X3_IfcPerson_type = 0;
entity* IFC2X3_IfcPersonAndOrganization_type = 0;
entity* IFC2X3_IfcPhysicalComplexQuantity_type = 0;
entity* IFC2X3_IfcPhysicalQuantity_type = 0;
entity* IFC2X3_IfcPhysicalSimpleQuantity_type = 0;
entity* IFC2X3_IfcPile_type = 0;
entity* IFC2X3_IfcPipeFittingType_type = 0;
entity* IFC2X3_IfcPipeSegmentType_type = 0;
entity* IFC2X3_IfcPixelTexture_type = 0;
entity* IFC2X3_IfcPlacement_type = 0;
entity* IFC2X3_IfcPlanarBox_type = 0;
entity* IFC2X3_IfcPlanarExtent_type = 0;
entity* IFC2X3_IfcPlane_type = 0;
entity* IFC2X3_IfcPlate_type = 0;
entity* IFC2X3_IfcPlateType_type = 0;
entity* IFC2X3_IfcPoint_type = 0;
entity* IFC2X3_IfcPointOnCurve_type = 0;
entity* IFC2X3_IfcPointOnSurface_type = 0;
entity* IFC2X3_IfcPolyLoop_type = 0;
entity* IFC2X3_IfcPolygonalBoundedHalfSpace_type = 0;
entity* IFC2X3_IfcPolyline_type = 0;
entity* IFC2X3_IfcPort_type = 0;
entity* IFC2X3_IfcPostalAddress_type = 0;
entity* IFC2X3_IfcPreDefinedColour_type = 0;
entity* IFC2X3_IfcPreDefinedCurveFont_type = 0;
entity* IFC2X3_IfcPreDefinedDimensionSymbol_type = 0;
entity* IFC2X3_IfcPreDefinedItem_type = 0;
entity* IFC2X3_IfcPreDefinedPointMarkerSymbol_type = 0;
entity* IFC2X3_IfcPreDefinedSymbol_type = 0;
entity* IFC2X3_IfcPreDefinedTerminatorSymbol_type = 0;
entity* IFC2X3_IfcPreDefinedTextFont_type = 0;
entity* IFC2X3_IfcPresentationLayerAssignment_type = 0;
entity* IFC2X3_IfcPresentationLayerWithStyle_type = 0;
entity* IFC2X3_IfcPresentationStyle_type = 0;
entity* IFC2X3_IfcPresentationStyleAssignment_type = 0;
entity* IFC2X3_IfcProcedure_type = 0;
entity* IFC2X3_IfcProcess_type = 0;
entity* IFC2X3_IfcProduct_type = 0;
entity* IFC2X3_IfcProductDefinitionShape_type = 0;
entity* IFC2X3_IfcProductRepresentation_type = 0;
entity* IFC2X3_IfcProductsOfCombustionProperties_type = 0;
entity* IFC2X3_IfcProfileDef_type = 0;
entity* IFC2X3_IfcProfileProperties_type = 0;
entity* IFC2X3_IfcProject_type = 0;
entity* IFC2X3_IfcProjectOrder_type = 0;
entity* IFC2X3_IfcProjectOrderRecord_type = 0;
entity* IFC2X3_IfcProjectionCurve_type = 0;
entity* IFC2X3_IfcProjectionElement_type = 0;
entity* IFC2X3_IfcProperty_type = 0;
entity* IFC2X3_IfcPropertyBoundedValue_type = 0;
entity* IFC2X3_IfcPropertyConstraintRelationship_type = 0;
entity* IFC2X3_IfcPropertyDefinition_type = 0;
entity* IFC2X3_IfcPropertyDependencyRelationship_type = 0;
entity* IFC2X3_IfcPropertyEnumeratedValue_type = 0;
entity* IFC2X3_IfcPropertyEnumeration_type = 0;
entity* IFC2X3_IfcPropertyListValue_type = 0;
entity* IFC2X3_IfcPropertyReferenceValue_type = 0;
entity* IFC2X3_IfcPropertySet_type = 0;
entity* IFC2X3_IfcPropertySetDefinition_type = 0;
entity* IFC2X3_IfcPropertySingleValue_type = 0;
entity* IFC2X3_IfcPropertyTableValue_type = 0;
entity* IFC2X3_IfcProtectiveDeviceType_type = 0;
entity* IFC2X3_IfcProxy_type = 0;
entity* IFC2X3_IfcPumpType_type = 0;
entity* IFC2X3_IfcQuantityArea_type = 0;
entity* IFC2X3_IfcQuantityCount_type = 0;
entity* IFC2X3_IfcQuantityLength_type = 0;
entity* IFC2X3_IfcQuantityTime_type = 0;
entity* IFC2X3_IfcQuantityVolume_type = 0;
entity* IFC2X3_IfcQuantityWeight_type = 0;
entity* IFC2X3_IfcRadiusDimension_type = 0;
entity* IFC2X3_IfcRailing_type = 0;
entity* IFC2X3_IfcRailingType_type = 0;
entity* IFC2X3_IfcRamp_type = 0;
entity* IFC2X3_IfcRampFlight_type = 0;
entity* IFC2X3_IfcRampFlightType_type = 0;
entity* IFC2X3_IfcRationalBezierCurve_type = 0;
entity* IFC2X3_IfcRectangleHollowProfileDef_type = 0;
entity* IFC2X3_IfcRectangleProfileDef_type = 0;
entity* IFC2X3_IfcRectangularPyramid_type = 0;
entity* IFC2X3_IfcRectangularTrimmedSurface_type = 0;
entity* IFC2X3_IfcReferencesValueDocument_type = 0;
entity* IFC2X3_IfcRegularTimeSeries_type = 0;
entity* IFC2X3_IfcReinforcementBarProperties_type = 0;
entity* IFC2X3_IfcReinforcementDefinitionProperties_type = 0;
entity* IFC2X3_IfcReinforcingBar_type = 0;
entity* IFC2X3_IfcReinforcingElement_type = 0;
entity* IFC2X3_IfcReinforcingMesh_type = 0;
entity* IFC2X3_IfcRelAggregates_type = 0;
entity* IFC2X3_IfcRelAssigns_type = 0;
entity* IFC2X3_IfcRelAssignsTasks_type = 0;
entity* IFC2X3_IfcRelAssignsToActor_type = 0;
entity* IFC2X3_IfcRelAssignsToControl_type = 0;
entity* IFC2X3_IfcRelAssignsToGroup_type = 0;
entity* IFC2X3_IfcRelAssignsToProcess_type = 0;
entity* IFC2X3_IfcRelAssignsToProduct_type = 0;
entity* IFC2X3_IfcRelAssignsToProjectOrder_type = 0;
entity* IFC2X3_IfcRelAssignsToResource_type = 0;
entity* IFC2X3_IfcRelAssociates_type = 0;
entity* IFC2X3_IfcRelAssociatesAppliedValue_type = 0;
entity* IFC2X3_IfcRelAssociatesApproval_type = 0;
entity* IFC2X3_IfcRelAssociatesClassification_type = 0;
entity* IFC2X3_IfcRelAssociatesConstraint_type = 0;
entity* IFC2X3_IfcRelAssociatesDocument_type = 0;
entity* IFC2X3_IfcRelAssociatesLibrary_type = 0;
entity* IFC2X3_IfcRelAssociatesMaterial_type = 0;
entity* IFC2X3_IfcRelAssociatesProfileProperties_type = 0;
entity* IFC2X3_IfcRelConnects_type = 0;
entity* IFC2X3_IfcRelConnectsElements_type = 0;
entity* IFC2X3_IfcRelConnectsPathElements_type = 0;
entity* IFC2X3_IfcRelConnectsPortToElement_type = 0;
entity* IFC2X3_IfcRelConnectsPorts_type = 0;
entity* IFC2X3_IfcRelConnectsStructuralActivity_type = 0;
entity* IFC2X3_IfcRelConnectsStructuralElement_type = 0;
entity* IFC2X3_IfcRelConnectsStructuralMember_type = 0;
entity* IFC2X3_IfcRelConnectsWithEccentricity_type = 0;
entity* IFC2X3_IfcRelConnectsWithRealizingElements_type = 0;
entity* IFC2X3_IfcRelContainedInSpatialStructure_type = 0;
entity* IFC2X3_IfcRelCoversBldgElements_type = 0;
entity* IFC2X3_IfcRelCoversSpaces_type = 0;
entity* IFC2X3_IfcRelDecomposes_type = 0;
entity* IFC2X3_IfcRelDefines_type = 0;
entity* IFC2X3_IfcRelDefinesByProperties_type = 0;
entity* IFC2X3_IfcRelDefinesByType_type = 0;
entity* IFC2X3_IfcRelFillsElement_type = 0;
entity* IFC2X3_IfcRelFlowControlElements_type = 0;
entity* IFC2X3_IfcRelInteractionRequirements_type = 0;
entity* IFC2X3_IfcRelNests_type = 0;
entity* IFC2X3_IfcRelOccupiesSpaces_type = 0;
entity* IFC2X3_IfcRelOverridesProperties_type = 0;
entity* IFC2X3_IfcRelProjectsElement_type = 0;
entity* IFC2X3_IfcRelReferencedInSpatialStructure_type = 0;
entity* IFC2X3_IfcRelSchedulesCostItems_type = 0;
entity* IFC2X3_IfcRelSequence_type = 0;
entity* IFC2X3_IfcRelServicesBuildings_type = 0;
entity* IFC2X3_IfcRelSpaceBoundary_type = 0;
entity* IFC2X3_IfcRelVoidsElement_type = 0;
entity* IFC2X3_IfcRelationship_type = 0;
entity* IFC2X3_IfcRelaxation_type = 0;
entity* IFC2X3_IfcRepresentation_type = 0;
entity* IFC2X3_IfcRepresentationContext_type = 0;
entity* IFC2X3_IfcRepresentationItem_type = 0;
entity* IFC2X3_IfcRepresentationMap_type = 0;
entity* IFC2X3_IfcResource_type = 0;
entity* IFC2X3_IfcRevolvedAreaSolid_type = 0;
entity* IFC2X3_IfcRibPlateProfileProperties_type = 0;
entity* IFC2X3_IfcRightCircularCone_type = 0;
entity* IFC2X3_IfcRightCircularCylinder_type = 0;
entity* IFC2X3_IfcRoof_type = 0;
entity* IFC2X3_IfcRoot_type = 0;
entity* IFC2X3_IfcRoundedEdgeFeature_type = 0;
entity* IFC2X3_IfcRoundedRectangleProfileDef_type = 0;
entity* IFC2X3_IfcSIUnit_type = 0;
entity* IFC2X3_IfcSanitaryTerminalType_type = 0;
entity* IFC2X3_IfcScheduleTimeControl_type = 0;
entity* IFC2X3_IfcSectionProperties_type = 0;
entity* IFC2X3_IfcSectionReinforcementProperties_type = 0;
entity* IFC2X3_IfcSectionedSpine_type = 0;
entity* IFC2X3_IfcSensorType_type = 0;
entity* IFC2X3_IfcServiceLife_type = 0;
entity* IFC2X3_IfcServiceLifeFactor_type = 0;
entity* IFC2X3_IfcShapeAspect_type = 0;
entity* IFC2X3_IfcShapeModel_type = 0;
entity* IFC2X3_IfcShapeRepresentation_type = 0;
entity* IFC2X3_IfcShellBasedSurfaceModel_type = 0;
entity* IFC2X3_IfcSimpleProperty_type = 0;
entity* IFC2X3_IfcSite_type = 0;
entity* IFC2X3_IfcSlab_type = 0;
entity* IFC2X3_IfcSlabType_type = 0;
entity* IFC2X3_IfcSlippageConnectionCondition_type = 0;
entity* IFC2X3_IfcSolidModel_type = 0;
entity* IFC2X3_IfcSoundProperties_type = 0;
entity* IFC2X3_IfcSoundValue_type = 0;
entity* IFC2X3_IfcSpace_type = 0;
entity* IFC2X3_IfcSpaceHeaterType_type = 0;
entity* IFC2X3_IfcSpaceProgram_type = 0;
entity* IFC2X3_IfcSpaceThermalLoadProperties_type = 0;
entity* IFC2X3_IfcSpaceType_type = 0;
entity* IFC2X3_IfcSpatialStructureElement_type = 0;
entity* IFC2X3_IfcSpatialStructureElementType_type = 0;
entity* IFC2X3_IfcSphere_type = 0;
entity* IFC2X3_IfcStackTerminalType_type = 0;
entity* IFC2X3_IfcStair_type = 0;
entity* IFC2X3_IfcStairFlight_type = 0;
entity* IFC2X3_IfcStairFlightType_type = 0;
entity* IFC2X3_IfcStructuralAction_type = 0;
entity* IFC2X3_IfcStructuralActivity_type = 0;
entity* IFC2X3_IfcStructuralAnalysisModel_type = 0;
entity* IFC2X3_IfcStructuralConnection_type = 0;
entity* IFC2X3_IfcStructuralConnectionCondition_type = 0;
entity* IFC2X3_IfcStructuralCurveConnection_type = 0;
entity* IFC2X3_IfcStructuralCurveMember_type = 0;
entity* IFC2X3_IfcStructuralCurveMemberVarying_type = 0;
entity* IFC2X3_IfcStructuralItem_type = 0;
entity* IFC2X3_IfcStructuralLinearAction_type = 0;
entity* IFC2X3_IfcStructuralLinearActionVarying_type = 0;
entity* IFC2X3_IfcStructuralLoad_type = 0;
entity* IFC2X3_IfcStructuralLoadGroup_type = 0;
entity* IFC2X3_IfcStructuralLoadLinearForce_type = 0;
entity* IFC2X3_IfcStructuralLoadPlanarForce_type = 0;
entity* IFC2X3_IfcStructuralLoadSingleDisplacement_type = 0;
entity* IFC2X3_IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IFC2X3_IfcStructuralLoadSingleForce_type = 0;
entity* IFC2X3_IfcStructuralLoadSingleForceWarping_type = 0;
entity* IFC2X3_IfcStructuralLoadStatic_type = 0;
entity* IFC2X3_IfcStructuralLoadTemperature_type = 0;
entity* IFC2X3_IfcStructuralMember_type = 0;
entity* IFC2X3_IfcStructuralPlanarAction_type = 0;
entity* IFC2X3_IfcStructuralPlanarActionVarying_type = 0;
entity* IFC2X3_IfcStructuralPointAction_type = 0;
entity* IFC2X3_IfcStructuralPointConnection_type = 0;
entity* IFC2X3_IfcStructuralPointReaction_type = 0;
entity* IFC2X3_IfcStructuralProfileProperties_type = 0;
entity* IFC2X3_IfcStructuralReaction_type = 0;
entity* IFC2X3_IfcStructuralResultGroup_type = 0;
entity* IFC2X3_IfcStructuralSteelProfileProperties_type = 0;
entity* IFC2X3_IfcStructuralSurfaceConnection_type = 0;
entity* IFC2X3_IfcStructuralSurfaceMember_type = 0;
entity* IFC2X3_IfcStructuralSurfaceMemberVarying_type = 0;
entity* IFC2X3_IfcStructuredDimensionCallout_type = 0;
entity* IFC2X3_IfcStyleModel_type = 0;
entity* IFC2X3_IfcStyledItem_type = 0;
entity* IFC2X3_IfcStyledRepresentation_type = 0;
entity* IFC2X3_IfcSubContractResource_type = 0;
entity* IFC2X3_IfcSubedge_type = 0;
entity* IFC2X3_IfcSurface_type = 0;
entity* IFC2X3_IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IFC2X3_IfcSurfaceOfLinearExtrusion_type = 0;
entity* IFC2X3_IfcSurfaceOfRevolution_type = 0;
entity* IFC2X3_IfcSurfaceStyle_type = 0;
entity* IFC2X3_IfcSurfaceStyleLighting_type = 0;
entity* IFC2X3_IfcSurfaceStyleRefraction_type = 0;
entity* IFC2X3_IfcSurfaceStyleRendering_type = 0;
entity* IFC2X3_IfcSurfaceStyleShading_type = 0;
entity* IFC2X3_IfcSurfaceStyleWithTextures_type = 0;
entity* IFC2X3_IfcSurfaceTexture_type = 0;
entity* IFC2X3_IfcSweptAreaSolid_type = 0;
entity* IFC2X3_IfcSweptDiskSolid_type = 0;
entity* IFC2X3_IfcSweptSurface_type = 0;
entity* IFC2X3_IfcSwitchingDeviceType_type = 0;
entity* IFC2X3_IfcSymbolStyle_type = 0;
entity* IFC2X3_IfcSystem_type = 0;
entity* IFC2X3_IfcSystemFurnitureElementType_type = 0;
entity* IFC2X3_IfcTShapeProfileDef_type = 0;
entity* IFC2X3_IfcTable_type = 0;
entity* IFC2X3_IfcTableRow_type = 0;
entity* IFC2X3_IfcTankType_type = 0;
entity* IFC2X3_IfcTask_type = 0;
entity* IFC2X3_IfcTelecomAddress_type = 0;
entity* IFC2X3_IfcTendon_type = 0;
entity* IFC2X3_IfcTendonAnchor_type = 0;
entity* IFC2X3_IfcTerminatorSymbol_type = 0;
entity* IFC2X3_IfcTextLiteral_type = 0;
entity* IFC2X3_IfcTextLiteralWithExtent_type = 0;
entity* IFC2X3_IfcTextStyle_type = 0;
entity* IFC2X3_IfcTextStyleFontModel_type = 0;
entity* IFC2X3_IfcTextStyleForDefinedFont_type = 0;
entity* IFC2X3_IfcTextStyleTextModel_type = 0;
entity* IFC2X3_IfcTextStyleWithBoxCharacteristics_type = 0;
entity* IFC2X3_IfcTextureCoordinate_type = 0;
entity* IFC2X3_IfcTextureCoordinateGenerator_type = 0;
entity* IFC2X3_IfcTextureMap_type = 0;
entity* IFC2X3_IfcTextureVertex_type = 0;
entity* IFC2X3_IfcThermalMaterialProperties_type = 0;
entity* IFC2X3_IfcTimeSeries_type = 0;
entity* IFC2X3_IfcTimeSeriesReferenceRelationship_type = 0;
entity* IFC2X3_IfcTimeSeriesSchedule_type = 0;
entity* IFC2X3_IfcTimeSeriesValue_type = 0;
entity* IFC2X3_IfcTopologicalRepresentationItem_type = 0;
entity* IFC2X3_IfcTopologyRepresentation_type = 0;
entity* IFC2X3_IfcTransformerType_type = 0;
entity* IFC2X3_IfcTransportElement_type = 0;
entity* IFC2X3_IfcTransportElementType_type = 0;
entity* IFC2X3_IfcTrapeziumProfileDef_type = 0;
entity* IFC2X3_IfcTrimmedCurve_type = 0;
entity* IFC2X3_IfcTubeBundleType_type = 0;
entity* IFC2X3_IfcTwoDirectionRepeatFactor_type = 0;
entity* IFC2X3_IfcTypeObject_type = 0;
entity* IFC2X3_IfcTypeProduct_type = 0;
entity* IFC2X3_IfcUShapeProfileDef_type = 0;
entity* IFC2X3_IfcUnitAssignment_type = 0;
entity* IFC2X3_IfcUnitaryEquipmentType_type = 0;
entity* IFC2X3_IfcValveType_type = 0;
entity* IFC2X3_IfcVector_type = 0;
entity* IFC2X3_IfcVertex_type = 0;
entity* IFC2X3_IfcVertexBasedTextureMap_type = 0;
entity* IFC2X3_IfcVertexLoop_type = 0;
entity* IFC2X3_IfcVertexPoint_type = 0;
entity* IFC2X3_IfcVibrationIsolatorType_type = 0;
entity* IFC2X3_IfcVirtualElement_type = 0;
entity* IFC2X3_IfcVirtualGridIntersection_type = 0;
entity* IFC2X3_IfcWall_type = 0;
entity* IFC2X3_IfcWallStandardCase_type = 0;
entity* IFC2X3_IfcWallType_type = 0;
entity* IFC2X3_IfcWasteTerminalType_type = 0;
entity* IFC2X3_IfcWaterProperties_type = 0;
entity* IFC2X3_IfcWindow_type = 0;
entity* IFC2X3_IfcWindowLiningProperties_type = 0;
entity* IFC2X3_IfcWindowPanelProperties_type = 0;
entity* IFC2X3_IfcWindowStyle_type = 0;
entity* IFC2X3_IfcWorkControl_type = 0;
entity* IFC2X3_IfcWorkPlan_type = 0;
entity* IFC2X3_IfcWorkSchedule_type = 0;
entity* IFC2X3_IfcZShapeProfileDef_type = 0;
entity* IFC2X3_IfcZone_type = 0;
type_declaration* IFC2X3_IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IFC2X3_IfcAccelerationMeasure_type = 0;
type_declaration* IFC2X3_IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IFC2X3_IfcAngularVelocityMeasure_type = 0;
type_declaration* IFC2X3_IfcAreaMeasure_type = 0;
type_declaration* IFC2X3_IfcBoolean_type = 0;
type_declaration* IFC2X3_IfcBoxAlignment_type = 0;
type_declaration* IFC2X3_IfcComplexNumber_type = 0;
type_declaration* IFC2X3_IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IFC2X3_IfcContextDependentMeasure_type = 0;
type_declaration* IFC2X3_IfcCountMeasure_type = 0;
type_declaration* IFC2X3_IfcCurvatureMeasure_type = 0;
type_declaration* IFC2X3_IfcDayInMonthNumber_type = 0;
type_declaration* IFC2X3_IfcDaylightSavingHour_type = 0;
type_declaration* IFC2X3_IfcDescriptiveMeasure_type = 0;
type_declaration* IFC2X3_IfcDimensionCount_type = 0;
type_declaration* IFC2X3_IfcDoseEquivalentMeasure_type = 0;
type_declaration* IFC2X3_IfcDynamicViscosityMeasure_type = 0;
type_declaration* IFC2X3_IfcElectricCapacitanceMeasure_type = 0;
type_declaration* IFC2X3_IfcElectricChargeMeasure_type = 0;
type_declaration* IFC2X3_IfcElectricConductanceMeasure_type = 0;
type_declaration* IFC2X3_IfcElectricCurrentMeasure_type = 0;
type_declaration* IFC2X3_IfcElectricResistanceMeasure_type = 0;
type_declaration* IFC2X3_IfcElectricVoltageMeasure_type = 0;
type_declaration* IFC2X3_IfcEnergyMeasure_type = 0;
type_declaration* IFC2X3_IfcFontStyle_type = 0;
type_declaration* IFC2X3_IfcFontVariant_type = 0;
type_declaration* IFC2X3_IfcFontWeight_type = 0;
type_declaration* IFC2X3_IfcForceMeasure_type = 0;
type_declaration* IFC2X3_IfcFrequencyMeasure_type = 0;
type_declaration* IFC2X3_IfcGloballyUniqueId_type = 0;
type_declaration* IFC2X3_IfcHeatFluxDensityMeasure_type = 0;
type_declaration* IFC2X3_IfcHeatingValueMeasure_type = 0;
type_declaration* IFC2X3_IfcHourInDay_type = 0;
type_declaration* IFC2X3_IfcIdentifier_type = 0;
type_declaration* IFC2X3_IfcIlluminanceMeasure_type = 0;
type_declaration* IFC2X3_IfcInductanceMeasure_type = 0;
type_declaration* IFC2X3_IfcInteger_type = 0;
type_declaration* IFC2X3_IfcIntegerCountRateMeasure_type = 0;
type_declaration* IFC2X3_IfcIonConcentrationMeasure_type = 0;
type_declaration* IFC2X3_IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IFC2X3_IfcKinematicViscosityMeasure_type = 0;
type_declaration* IFC2X3_IfcLabel_type = 0;
type_declaration* IFC2X3_IfcLengthMeasure_type = 0;
type_declaration* IFC2X3_IfcLinearForceMeasure_type = 0;
type_declaration* IFC2X3_IfcLinearMomentMeasure_type = 0;
type_declaration* IFC2X3_IfcLinearStiffnessMeasure_type = 0;
type_declaration* IFC2X3_IfcLinearVelocityMeasure_type = 0;
type_declaration* IFC2X3_IfcLogical_type = 0;
type_declaration* IFC2X3_IfcLuminousFluxMeasure_type = 0;
type_declaration* IFC2X3_IfcLuminousIntensityDistributionMeasure_type = 0;
type_declaration* IFC2X3_IfcLuminousIntensityMeasure_type = 0;
type_declaration* IFC2X3_IfcMagneticFluxDensityMeasure_type = 0;
type_declaration* IFC2X3_IfcMagneticFluxMeasure_type = 0;
type_declaration* IFC2X3_IfcMassDensityMeasure_type = 0;
type_declaration* IFC2X3_IfcMassFlowRateMeasure_type = 0;
type_declaration* IFC2X3_IfcMassMeasure_type = 0;
type_declaration* IFC2X3_IfcMassPerLengthMeasure_type = 0;
type_declaration* IFC2X3_IfcMinuteInHour_type = 0;
type_declaration* IFC2X3_IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IFC2X3_IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IFC2X3_IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IFC2X3_IfcMolecularWeightMeasure_type = 0;
type_declaration* IFC2X3_IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IFC2X3_IfcMonetaryMeasure_type = 0;
type_declaration* IFC2X3_IfcMonthInYearNumber_type = 0;
type_declaration* IFC2X3_IfcNormalisedRatioMeasure_type = 0;
type_declaration* IFC2X3_IfcNumericMeasure_type = 0;
type_declaration* IFC2X3_IfcPHMeasure_type = 0;
type_declaration* IFC2X3_IfcParameterValue_type = 0;
type_declaration* IFC2X3_IfcPlanarForceMeasure_type = 0;
type_declaration* IFC2X3_IfcPlaneAngleMeasure_type = 0;
type_declaration* IFC2X3_IfcPositiveLengthMeasure_type = 0;
type_declaration* IFC2X3_IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IFC2X3_IfcPositiveRatioMeasure_type = 0;
type_declaration* IFC2X3_IfcPowerMeasure_type = 0;
type_declaration* IFC2X3_IfcPresentableText_type = 0;
type_declaration* IFC2X3_IfcPressureMeasure_type = 0;
type_declaration* IFC2X3_IfcRadioActivityMeasure_type = 0;
type_declaration* IFC2X3_IfcRatioMeasure_type = 0;
type_declaration* IFC2X3_IfcReal_type = 0;
type_declaration* IFC2X3_IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IFC2X3_IfcRotationalMassMeasure_type = 0;
type_declaration* IFC2X3_IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IFC2X3_IfcSecondInMinute_type = 0;
type_declaration* IFC2X3_IfcSectionModulusMeasure_type = 0;
type_declaration* IFC2X3_IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IFC2X3_IfcShearModulusMeasure_type = 0;
type_declaration* IFC2X3_IfcSolidAngleMeasure_type = 0;
type_declaration* IFC2X3_IfcSoundPowerMeasure_type = 0;
type_declaration* IFC2X3_IfcSoundPressureMeasure_type = 0;
type_declaration* IFC2X3_IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IFC2X3_IfcSpecularExponent_type = 0;
type_declaration* IFC2X3_IfcSpecularRoughness_type = 0;
type_declaration* IFC2X3_IfcTemperatureGradientMeasure_type = 0;
type_declaration* IFC2X3_IfcText_type = 0;
type_declaration* IFC2X3_IfcTextAlignment_type = 0;
type_declaration* IFC2X3_IfcTextDecoration_type = 0;
type_declaration* IFC2X3_IfcTextFontName_type = 0;
type_declaration* IFC2X3_IfcTextTransformation_type = 0;
type_declaration* IFC2X3_IfcThermalAdmittanceMeasure_type = 0;
type_declaration* IFC2X3_IfcThermalConductivityMeasure_type = 0;
type_declaration* IFC2X3_IfcThermalExpansionCoefficientMeasure_type = 0;
type_declaration* IFC2X3_IfcThermalResistanceMeasure_type = 0;
type_declaration* IFC2X3_IfcThermalTransmittanceMeasure_type = 0;
type_declaration* IFC2X3_IfcThermodynamicTemperatureMeasure_type = 0;
type_declaration* IFC2X3_IfcTimeMeasure_type = 0;
type_declaration* IFC2X3_IfcTimeStamp_type = 0;
type_declaration* IFC2X3_IfcTorqueMeasure_type = 0;
type_declaration* IFC2X3_IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IFC2X3_IfcVolumeMeasure_type = 0;
type_declaration* IFC2X3_IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IFC2X3_IfcWarpingConstantMeasure_type = 0;
type_declaration* IFC2X3_IfcWarpingMomentMeasure_type = 0;
type_declaration* IFC2X3_IfcYearNumber_type = 0;
select_type* IFC2X3_IfcActorSelect_type = 0;
select_type* IFC2X3_IfcAppliedValueSelect_type = 0;
select_type* IFC2X3_IfcAxis2Placement_type = 0;
select_type* IFC2X3_IfcBooleanOperand_type = 0;
select_type* IFC2X3_IfcCharacterStyleSelect_type = 0;
select_type* IFC2X3_IfcClassificationNotationSelect_type = 0;
select_type* IFC2X3_IfcColour_type = 0;
select_type* IFC2X3_IfcColourOrFactor_type = 0;
select_type* IFC2X3_IfcConditionCriterionSelect_type = 0;
select_type* IFC2X3_IfcCsgSelect_type = 0;
select_type* IFC2X3_IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IFC2X3_IfcCurveOrEdgeCurve_type = 0;
select_type* IFC2X3_IfcCurveStyleFontSelect_type = 0;
select_type* IFC2X3_IfcDateTimeSelect_type = 0;
select_type* IFC2X3_IfcDefinedSymbolSelect_type = 0;
select_type* IFC2X3_IfcDerivedMeasureValue_type = 0;
select_type* IFC2X3_IfcDocumentSelect_type = 0;
select_type* IFC2X3_IfcDraughtingCalloutElement_type = 0;
select_type* IFC2X3_IfcFillAreaStyleTileShapeSelect_type = 0;
select_type* IFC2X3_IfcFillStyleSelect_type = 0;
select_type* IFC2X3_IfcGeometricSetSelect_type = 0;
select_type* IFC2X3_IfcHatchLineDistanceSelect_type = 0;
select_type* IFC2X3_IfcLayeredItem_type = 0;
select_type* IFC2X3_IfcLibrarySelect_type = 0;
select_type* IFC2X3_IfcLightDistributionDataSourceSelect_type = 0;
select_type* IFC2X3_IfcMaterialSelect_type = 0;
select_type* IFC2X3_IfcMeasureValue_type = 0;
select_type* IFC2X3_IfcMetricValueSelect_type = 0;
select_type* IFC2X3_IfcObjectReferenceSelect_type = 0;
select_type* IFC2X3_IfcOrientationSelect_type = 0;
select_type* IFC2X3_IfcPointOrVertexPoint_type = 0;
select_type* IFC2X3_IfcPresentationStyleSelect_type = 0;
select_type* IFC2X3_IfcShell_type = 0;
select_type* IFC2X3_IfcSimpleValue_type = 0;
select_type* IFC2X3_IfcSizeSelect_type = 0;
select_type* IFC2X3_IfcSpecularHighlightSelect_type = 0;
select_type* IFC2X3_IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IFC2X3_IfcSurfaceOrFaceSurface_type = 0;
select_type* IFC2X3_IfcSurfaceStyleElementSelect_type = 0;
select_type* IFC2X3_IfcSymbolStyleSelect_type = 0;
select_type* IFC2X3_IfcTextFontSelect_type = 0;
select_type* IFC2X3_IfcTextStyleSelect_type = 0;
select_type* IFC2X3_IfcTrimmingSelect_type = 0;
select_type* IFC2X3_IfcUnit_type = 0;
select_type* IFC2X3_IfcValue_type = 0;
select_type* IFC2X3_IfcVectorOrDirection_type = 0;
enumeration_type* IFC2X3_IfcActionSourceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcActionTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcActuatorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAddressTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAheadOrBehind_type = 0;
enumeration_type* IFC2X3_IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAlarmTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IFC2X3_IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IFC2X3_IfcBSplineCurveForm_type = 0;
enumeration_type* IFC2X3_IfcBeamTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcBenchmarkEnum_type = 0;
enumeration_type* IFC2X3_IfcBoilerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcBooleanOperator_type = 0;
enumeration_type* IFC2X3_IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcChangeActionEnum_type = 0;
enumeration_type* IFC2X3_IfcChillerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCoilTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcColumnTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCompressorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCondenserTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcConnectionTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcConstraintEnum_type = 0;
enumeration_type* IFC2X3_IfcControllerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCoveringTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcCurrencyEnum_type = 0;
enumeration_type* IFC2X3_IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcDamperTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcDataOriginEnum_type = 0;
enumeration_type* IFC2X3_IfcDerivedUnitEnum_type = 0;
enumeration_type* IFC2X3_IfcDimensionExtentUsage_type = 0;
enumeration_type* IFC2X3_IfcDirectionSenseEnum_type = 0;
enumeration_type* IFC2X3_IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IFC2X3_IfcDocumentStatusEnum_type = 0;
enumeration_type* IFC2X3_IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IFC2X3_IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IFC2X3_IfcDoorStyleConstructionEnum_type = 0;
enumeration_type* IFC2X3_IfcDoorStyleOperationEnum_type = 0;
enumeration_type* IFC2X3_IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricCurrentEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricDistributionPointFunctionEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricHeaterTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcElementCompositionEnum_type = 0;
enumeration_type* IFC2X3_IfcEnergySequenceEnum_type = 0;
enumeration_type* IFC2X3_IfcEnvironmentalImpactCategoryEnum_type = 0;
enumeration_type* IFC2X3_IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcFanTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcFilterTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcFlowDirectionEnum_type = 0;
enumeration_type* IFC2X3_IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcFootingTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcGasTerminalTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcGeometricProjectionEnum_type = 0;
enumeration_type* IFC2X3_IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IFC2X3_IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcHumidifierTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcInternalOrExternalEnum_type = 0;
enumeration_type* IFC2X3_IfcInventoryTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcLampTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IFC2X3_IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IFC2X3_IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IFC2X3_IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcLogicalOperatorEnum_type = 0;
enumeration_type* IFC2X3_IfcMemberTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcNullStyle_type = 0;
enumeration_type* IFC2X3_IfcObjectTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcObjectiveEnum_type = 0;
enumeration_type* IFC2X3_IfcOccupantTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcOutletTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IFC2X3_IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IFC2X3_IfcPileConstructionEnum_type = 0;
enumeration_type* IFC2X3_IfcPileTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcPlateTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcProcedureTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcProfileTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcProjectOrderRecordTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IFC2X3_IfcPropertySourceEnum_type = 0;
enumeration_type* IFC2X3_IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcPumpTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcRailingTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcRampFlightTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcRampTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcReflectanceMethodEnum_type = 0;
enumeration_type* IFC2X3_IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IFC2X3_IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IFC2X3_IfcResourceConsumptionEnum_type = 0;
enumeration_type* IFC2X3_IfcRibPlateDirectionEnum_type = 0;
enumeration_type* IFC2X3_IfcRoleEnum_type = 0;
enumeration_type* IFC2X3_IfcRoofTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSIPrefix_type = 0;
enumeration_type* IFC2X3_IfcSIUnitName_type = 0;
enumeration_type* IFC2X3_IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSectionTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSensorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSequenceEnum_type = 0;
enumeration_type* IFC2X3_IfcServiceLifeFactorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcServiceLifeTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSlabTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSoundScaleEnum_type = 0;
enumeration_type* IFC2X3_IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSpaceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcStairFlightTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcStairTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcStateEnum_type = 0;
enumeration_type* IFC2X3_IfcStructuralCurveTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcStructuralSurfaceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcSurfaceSide_type = 0;
enumeration_type* IFC2X3_IfcSurfaceTextureEnum_type = 0;
enumeration_type* IFC2X3_IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTankTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTendonTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTextPath_type = 0;
enumeration_type* IFC2X3_IfcThermalLoadSourceEnum_type = 0;
enumeration_type* IFC2X3_IfcThermalLoadTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTimeSeriesScheduleTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTransformerTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTransitionCode_type = 0;
enumeration_type* IFC2X3_IfcTransportElementTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcTrimmingPreference_type = 0;
enumeration_type* IFC2X3_IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcUnitEnum_type = 0;
enumeration_type* IFC2X3_IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcValveTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcWallTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IFC2X3_IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IFC2X3_IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IFC2X3_IfcWindowStyleConstructionEnum_type = 0;
enumeration_type* IFC2X3_IfcWindowStyleOperationEnum_type = 0;
enumeration_type* IFC2X3_IfcWorkControlTypeEnum_type = 0;

class IFC2X3_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc2x3::Ifc2DCompositeCurve(data);
            case 1: return new ::Ifc2x3::IfcAbsorbedDoseMeasure(data);
            case 2: return new ::Ifc2x3::IfcAccelerationMeasure(data);
            case 3: return new ::Ifc2x3::IfcActionRequest(data);
            case 6: return new ::Ifc2x3::IfcActor(data);
            case 7: return new ::Ifc2x3::IfcActorRole(data);
            case 9: return new ::Ifc2x3::IfcActuatorType(data);
            case 11: return new ::Ifc2x3::IfcAddress(data);
            case 14: return new ::Ifc2x3::IfcAirTerminalBoxType(data);
            case 16: return new ::Ifc2x3::IfcAirTerminalType(data);
            case 18: return new ::Ifc2x3::IfcAirToAirHeatRecoveryType(data);
            case 20: return new ::Ifc2x3::IfcAlarmType(data);
            case 22: return new ::Ifc2x3::IfcAmountOfSubstanceMeasure(data);
            case 25: return new ::Ifc2x3::IfcAngularDimension(data);
            case 26: return new ::Ifc2x3::IfcAngularVelocityMeasure(data);
            case 27: return new ::Ifc2x3::IfcAnnotation(data);
            case 28: return new ::Ifc2x3::IfcAnnotationCurveOccurrence(data);
            case 29: return new ::Ifc2x3::IfcAnnotationFillArea(data);
            case 30: return new ::Ifc2x3::IfcAnnotationFillAreaOccurrence(data);
            case 31: return new ::Ifc2x3::IfcAnnotationOccurrence(data);
            case 32: return new ::Ifc2x3::IfcAnnotationSurface(data);
            case 33: return new ::Ifc2x3::IfcAnnotationSurfaceOccurrence(data);
            case 34: return new ::Ifc2x3::IfcAnnotationSymbolOccurrence(data);
            case 35: return new ::Ifc2x3::IfcAnnotationTextOccurrence(data);
            case 36: return new ::Ifc2x3::IfcApplication(data);
            case 37: return new ::Ifc2x3::IfcAppliedValue(data);
            case 38: return new ::Ifc2x3::IfcAppliedValueRelationship(data);
            case 40: return new ::Ifc2x3::IfcApproval(data);
            case 41: return new ::Ifc2x3::IfcApprovalActorRelationship(data);
            case 42: return new ::Ifc2x3::IfcApprovalPropertyRelationship(data);
            case 43: return new ::Ifc2x3::IfcApprovalRelationship(data);
            case 44: return new ::Ifc2x3::IfcArbitraryClosedProfileDef(data);
            case 45: return new ::Ifc2x3::IfcArbitraryOpenProfileDef(data);
            case 46: return new ::Ifc2x3::IfcArbitraryProfileDefWithVoids(data);
            case 47: return new ::Ifc2x3::IfcAreaMeasure(data);
            case 50: return new ::Ifc2x3::IfcAsset(data);
            case 51: return new ::Ifc2x3::IfcAsymmetricIShapeProfileDef(data);
            case 52: return new ::Ifc2x3::IfcAxis1Placement(data);
            case 54: return new ::Ifc2x3::IfcAxis2Placement2D(data);
            case 55: return new ::Ifc2x3::IfcAxis2Placement3D(data);
            case 56: return new ::Ifc2x3::IfcBeam(data);
            case 57: return new ::Ifc2x3::IfcBeamType(data);
            case 60: return new ::Ifc2x3::IfcBezierCurve(data);
            case 61: return new ::Ifc2x3::IfcBlobTexture(data);
            case 62: return new ::Ifc2x3::IfcBlock(data);
            case 63: return new ::Ifc2x3::IfcBoilerType(data);
            case 65: return new ::Ifc2x3::IfcBoolean(data);
            case 66: return new ::Ifc2x3::IfcBooleanClippingResult(data);
            case 69: return new ::Ifc2x3::IfcBooleanResult(data);
            case 70: return new ::Ifc2x3::IfcBoundaryCondition(data);
            case 71: return new ::Ifc2x3::IfcBoundaryEdgeCondition(data);
            case 72: return new ::Ifc2x3::IfcBoundaryFaceCondition(data);
            case 73: return new ::Ifc2x3::IfcBoundaryNodeCondition(data);
            case 74: return new ::Ifc2x3::IfcBoundaryNodeConditionWarping(data);
            case 75: return new ::Ifc2x3::IfcBoundedCurve(data);
            case 76: return new ::Ifc2x3::IfcBoundedSurface(data);
            case 77: return new ::Ifc2x3::IfcBoundingBox(data);
            case 78: return new ::Ifc2x3::IfcBoxAlignment(data);
            case 79: return new ::Ifc2x3::IfcBoxedHalfSpace(data);
            case 80: return new ::Ifc2x3::IfcBSplineCurve(data);
            case 82: return new ::Ifc2x3::IfcBuilding(data);
            case 83: return new ::Ifc2x3::IfcBuildingElement(data);
            case 84: return new ::Ifc2x3::IfcBuildingElementComponent(data);
            case 85: return new ::Ifc2x3::IfcBuildingElementPart(data);
            case 86: return new ::Ifc2x3::IfcBuildingElementProxy(data);
            case 87: return new ::Ifc2x3::IfcBuildingElementProxyType(data);
            case 89: return new ::Ifc2x3::IfcBuildingElementType(data);
            case 90: return new ::Ifc2x3::IfcBuildingStorey(data);
            case 91: return new ::Ifc2x3::IfcCableCarrierFittingType(data);
            case 93: return new ::Ifc2x3::IfcCableCarrierSegmentType(data);
            case 95: return new ::Ifc2x3::IfcCableSegmentType(data);
            case 97: return new ::Ifc2x3::IfcCalendarDate(data);
            case 98: return new ::Ifc2x3::IfcCartesianPoint(data);
            case 99: return new ::Ifc2x3::IfcCartesianTransformationOperator(data);
            case 100: return new ::Ifc2x3::IfcCartesianTransformationOperator2D(data);
            case 101: return new ::Ifc2x3::IfcCartesianTransformationOperator2DnonUniform(data);
            case 102: return new ::Ifc2x3::IfcCartesianTransformationOperator3D(data);
            case 103: return new ::Ifc2x3::IfcCartesianTransformationOperator3DnonUniform(data);
            case 104: return new ::Ifc2x3::IfcCenterLineProfileDef(data);
            case 105: return new ::Ifc2x3::IfcChamferEdgeFeature(data);
            case 108: return new ::Ifc2x3::IfcChillerType(data);
            case 110: return new ::Ifc2x3::IfcCircle(data);
            case 111: return new ::Ifc2x3::IfcCircleHollowProfileDef(data);
            case 112: return new ::Ifc2x3::IfcCircleProfileDef(data);
            case 113: return new ::Ifc2x3::IfcClassification(data);
            case 114: return new ::Ifc2x3::IfcClassificationItem(data);
            case 115: return new ::Ifc2x3::IfcClassificationItemRelationship(data);
            case 116: return new ::Ifc2x3::IfcClassificationNotation(data);
            case 117: return new ::Ifc2x3::IfcClassificationNotationFacet(data);
            case 119: return new ::Ifc2x3::IfcClassificationReference(data);
            case 120: return new ::Ifc2x3::IfcClosedShell(data);
            case 121: return new ::Ifc2x3::IfcCoilType(data);
            case 125: return new ::Ifc2x3::IfcColourRgb(data);
            case 126: return new ::Ifc2x3::IfcColourSpecification(data);
            case 127: return new ::Ifc2x3::IfcColumn(data);
            case 128: return new ::Ifc2x3::IfcColumnType(data);
            case 130: return new ::Ifc2x3::IfcComplexNumber(data);
            case 131: return new ::Ifc2x3::IfcComplexProperty(data);
            case 132: return new ::Ifc2x3::IfcCompositeCurve(data);
            case 133: return new ::Ifc2x3::IfcCompositeCurveSegment(data);
            case 134: return new ::Ifc2x3::IfcCompositeProfileDef(data);
            case 135: return new ::Ifc2x3::IfcCompoundPlaneAngleMeasure(data);
            case 136: return new ::Ifc2x3::IfcCompressorType(data);
            case 138: return new ::Ifc2x3::IfcCondenserType(data);
            case 140: return new ::Ifc2x3::IfcCondition(data);
            case 141: return new ::Ifc2x3::IfcConditionCriterion(data);
            case 143: return new ::Ifc2x3::IfcConic(data);
            case 144: return new ::Ifc2x3::IfcConnectedFaceSet(data);
            case 145: return new ::Ifc2x3::IfcConnectionCurveGeometry(data);
            case 146: return new ::Ifc2x3::IfcConnectionGeometry(data);
            case 147: return new ::Ifc2x3::IfcConnectionPointEccentricity(data);
            case 148: return new ::Ifc2x3::IfcConnectionPointGeometry(data);
            case 149: return new ::Ifc2x3::IfcConnectionPortGeometry(data);
            case 150: return new ::Ifc2x3::IfcConnectionSurfaceGeometry(data);
            case 152: return new ::Ifc2x3::IfcConstraint(data);
            case 153: return new ::Ifc2x3::IfcConstraintAggregationRelationship(data);
            case 154: return new ::Ifc2x3::IfcConstraintClassificationRelationship(data);
            case 156: return new ::Ifc2x3::IfcConstraintRelationship(data);
            case 157: return new ::Ifc2x3::IfcConstructionEquipmentResource(data);
            case 158: return new ::Ifc2x3::IfcConstructionMaterialResource(data);
            case 159: return new ::Ifc2x3::IfcConstructionProductResource(data);
            case 160: return new ::Ifc2x3::IfcConstructionResource(data);
            case 161: return new ::Ifc2x3::IfcContextDependentMeasure(data);
            case 162: return new ::Ifc2x3::IfcContextDependentUnit(data);
            case 163: return new ::Ifc2x3::IfcControl(data);
            case 164: return new ::Ifc2x3::IfcControllerType(data);
            case 166: return new ::Ifc2x3::IfcConversionBasedUnit(data);
            case 167: return new ::Ifc2x3::IfcCooledBeamType(data);
            case 169: return new ::Ifc2x3::IfcCoolingTowerType(data);
            case 171: return new ::Ifc2x3::IfcCoordinatedUniversalTimeOffset(data);
            case 172: return new ::Ifc2x3::IfcCostItem(data);
            case 173: return new ::Ifc2x3::IfcCostSchedule(data);
            case 175: return new ::Ifc2x3::IfcCostValue(data);
            case 176: return new ::Ifc2x3::IfcCountMeasure(data);
            case 177: return new ::Ifc2x3::IfcCovering(data);
            case 178: return new ::Ifc2x3::IfcCoveringType(data);
            case 180: return new ::Ifc2x3::IfcCraneRailAShapeProfileDef(data);
            case 181: return new ::Ifc2x3::IfcCraneRailFShapeProfileDef(data);
            case 182: return new ::Ifc2x3::IfcCrewResource(data);
            case 183: return new ::Ifc2x3::IfcCsgPrimitive3D(data);
            case 185: return new ::Ifc2x3::IfcCsgSolid(data);
            case 186: return new ::Ifc2x3::IfcCShapeProfileDef(data);
            case 188: return new ::Ifc2x3::IfcCurrencyRelationship(data);
            case 189: return new ::Ifc2x3::IfcCurtainWall(data);
            case 190: return new ::Ifc2x3::IfcCurtainWallType(data);
            case 192: return new ::Ifc2x3::IfcCurvatureMeasure(data);
            case 193: return new ::Ifc2x3::IfcCurve(data);
            case 194: return new ::Ifc2x3::IfcCurveBoundedPlane(data);
            case 197: return new ::Ifc2x3::IfcCurveStyle(data);
            case 198: return new ::Ifc2x3::IfcCurveStyleFont(data);
            case 199: return new ::Ifc2x3::IfcCurveStyleFontAndScaling(data);
            case 200: return new ::Ifc2x3::IfcCurveStyleFontPattern(data);
            case 202: return new ::Ifc2x3::IfcDamperType(data);
            case 205: return new ::Ifc2x3::IfcDateAndTime(data);
            case 207: return new ::Ifc2x3::IfcDayInMonthNumber(data);
            case 208: return new ::Ifc2x3::IfcDaylightSavingHour(data);
            case 209: return new ::Ifc2x3::IfcDefinedSymbol(data);
            case 212: return new ::Ifc2x3::IfcDerivedProfileDef(data);
            case 213: return new ::Ifc2x3::IfcDerivedUnit(data);
            case 214: return new ::Ifc2x3::IfcDerivedUnitElement(data);
            case 216: return new ::Ifc2x3::IfcDescriptiveMeasure(data);
            case 217: return new ::Ifc2x3::IfcDiameterDimension(data);
            case 218: return new ::Ifc2x3::IfcDimensionalExponents(data);
            case 219: return new ::Ifc2x3::IfcDimensionCalloutRelationship(data);
            case 220: return new ::Ifc2x3::IfcDimensionCount(data);
            case 221: return new ::Ifc2x3::IfcDimensionCurve(data);
            case 222: return new ::Ifc2x3::IfcDimensionCurveDirectedCallout(data);
            case 223: return new ::Ifc2x3::IfcDimensionCurveTerminator(data);
            case 225: return new ::Ifc2x3::IfcDimensionPair(data);
            case 226: return new ::Ifc2x3::IfcDirection(data);
            case 228: return new ::Ifc2x3::IfcDiscreteAccessory(data);
            case 229: return new ::Ifc2x3::IfcDiscreteAccessoryType(data);
            case 230: return new ::Ifc2x3::IfcDistributionChamberElement(data);
            case 231: return new ::Ifc2x3::IfcDistributionChamberElementType(data);
            case 233: return new ::Ifc2x3::IfcDistributionControlElement(data);
            case 234: return new ::Ifc2x3::IfcDistributionControlElementType(data);
            case 235: return new ::Ifc2x3::IfcDistributionElement(data);
            case 236: return new ::Ifc2x3::IfcDistributionElementType(data);
            case 237: return new ::Ifc2x3::IfcDistributionFlowElement(data);
            case 238: return new ::Ifc2x3::IfcDistributionFlowElementType(data);
            case 239: return new ::Ifc2x3::IfcDistributionPort(data);
            case 241: return new ::Ifc2x3::IfcDocumentElectronicFormat(data);
            case 242: return new ::Ifc2x3::IfcDocumentInformation(data);
            case 243: return new ::Ifc2x3::IfcDocumentInformationRelationship(data);
            case 244: return new ::Ifc2x3::IfcDocumentReference(data);
            case 247: return new ::Ifc2x3::IfcDoor(data);
            case 248: return new ::Ifc2x3::IfcDoorLiningProperties(data);
            case 251: return new ::Ifc2x3::IfcDoorPanelProperties(data);
            case 252: return new ::Ifc2x3::IfcDoorStyle(data);
            case 255: return new ::Ifc2x3::IfcDoseEquivalentMeasure(data);
            case 256: return new ::Ifc2x3::IfcDraughtingCallout(data);
            case 258: return new ::Ifc2x3::IfcDraughtingCalloutRelationship(data);
            case 259: return new ::Ifc2x3::IfcDraughtingPreDefinedColour(data);
            case 260: return new ::Ifc2x3::IfcDraughtingPreDefinedCurveFont(data);
            case 261: return new ::Ifc2x3::IfcDraughtingPreDefinedTextFont(data);
            case 262: return new ::Ifc2x3::IfcDuctFittingType(data);
            case 264: return new ::Ifc2x3::IfcDuctSegmentType(data);
            case 266: return new ::Ifc2x3::IfcDuctSilencerType(data);
            case 268: return new ::Ifc2x3::IfcDynamicViscosityMeasure(data);
            case 269: return new ::Ifc2x3::IfcEdge(data);
            case 270: return new ::Ifc2x3::IfcEdgeCurve(data);
            case 271: return new ::Ifc2x3::IfcEdgeFeature(data);
            case 272: return new ::Ifc2x3::IfcEdgeLoop(data);
            case 273: return new ::Ifc2x3::IfcElectricalBaseProperties(data);
            case 274: return new ::Ifc2x3::IfcElectricalCircuit(data);
            case 275: return new ::Ifc2x3::IfcElectricalElement(data);
            case 276: return new ::Ifc2x3::IfcElectricApplianceType(data);
            case 278: return new ::Ifc2x3::IfcElectricCapacitanceMeasure(data);
            case 279: return new ::Ifc2x3::IfcElectricChargeMeasure(data);
            case 280: return new ::Ifc2x3::IfcElectricConductanceMeasure(data);
            case 282: return new ::Ifc2x3::IfcElectricCurrentMeasure(data);
            case 283: return new ::Ifc2x3::IfcElectricDistributionPoint(data);
            case 285: return new ::Ifc2x3::IfcElectricFlowStorageDeviceType(data);
            case 287: return new ::Ifc2x3::IfcElectricGeneratorType(data);
            case 289: return new ::Ifc2x3::IfcElectricHeaterType(data);
            case 291: return new ::Ifc2x3::IfcElectricMotorType(data);
            case 293: return new ::Ifc2x3::IfcElectricResistanceMeasure(data);
            case 294: return new ::Ifc2x3::IfcElectricTimeControlType(data);
            case 296: return new ::Ifc2x3::IfcElectricVoltageMeasure(data);
            case 297: return new ::Ifc2x3::IfcElement(data);
            case 298: return new ::Ifc2x3::IfcElementarySurface(data);
            case 299: return new ::Ifc2x3::IfcElementAssembly(data);
            case 301: return new ::Ifc2x3::IfcElementComponent(data);
            case 302: return new ::Ifc2x3::IfcElementComponentType(data);
            case 304: return new ::Ifc2x3::IfcElementQuantity(data);
            case 305: return new ::Ifc2x3::IfcElementType(data);
            case 306: return new ::Ifc2x3::IfcEllipse(data);
            case 307: return new ::Ifc2x3::IfcEllipseProfileDef(data);
            case 308: return new ::Ifc2x3::IfcEnergyConversionDevice(data);
            case 309: return new ::Ifc2x3::IfcEnergyConversionDeviceType(data);
            case 310: return new ::Ifc2x3::IfcEnergyMeasure(data);
            case 311: return new ::Ifc2x3::IfcEnergyProperties(data);
            case 314: return new ::Ifc2x3::IfcEnvironmentalImpactValue(data);
            case 315: return new ::Ifc2x3::IfcEquipmentElement(data);
            case 316: return new ::Ifc2x3::IfcEquipmentStandard(data);
            case 317: return new ::Ifc2x3::IfcEvaporativeCoolerType(data);
            case 319: return new ::Ifc2x3::IfcEvaporatorType(data);
            case 321: return new ::Ifc2x3::IfcExtendedMaterialProperties(data);
            case 322: return new ::Ifc2x3::IfcExternallyDefinedHatchStyle(data);
            case 323: return new ::Ifc2x3::IfcExternallyDefinedSurfaceStyle(data);
            case 324: return new ::Ifc2x3::IfcExternallyDefinedSymbol(data);
            case 325: return new ::Ifc2x3::IfcExternallyDefinedTextFont(data);
            case 326: return new ::Ifc2x3::IfcExternalReference(data);
            case 327: return new ::Ifc2x3::IfcExtrudedAreaSolid(data);
            case 328: return new ::Ifc2x3::IfcFace(data);
            case 329: return new ::Ifc2x3::IfcFaceBasedSurfaceModel(data);
            case 330: return new ::Ifc2x3::IfcFaceBound(data);
            case 331: return new ::Ifc2x3::IfcFaceOuterBound(data);
            case 332: return new ::Ifc2x3::IfcFaceSurface(data);
            case 333: return new ::Ifc2x3::IfcFacetedBrep(data);
            case 334: return new ::Ifc2x3::IfcFacetedBrepWithVoids(data);
            case 335: return new ::Ifc2x3::IfcFailureConnectionCondition(data);
            case 336: return new ::Ifc2x3::IfcFanType(data);
            case 338: return new ::Ifc2x3::IfcFastener(data);
            case 339: return new ::Ifc2x3::IfcFastenerType(data);
            case 340: return new ::Ifc2x3::IfcFeatureElement(data);
            case 341: return new ::Ifc2x3::IfcFeatureElementAddition(data);
            case 342: return new ::Ifc2x3::IfcFeatureElementSubtraction(data);
            case 343: return new ::Ifc2x3::IfcFillAreaStyle(data);
            case 344: return new ::Ifc2x3::IfcFillAreaStyleHatching(data);
            case 345: return new ::Ifc2x3::IfcFillAreaStyleTiles(data);
            case 347: return new ::Ifc2x3::IfcFillAreaStyleTileSymbolWithStyle(data);
            case 349: return new ::Ifc2x3::IfcFilterType(data);
            case 351: return new ::Ifc2x3::IfcFireSuppressionTerminalType(data);
            case 353: return new ::Ifc2x3::IfcFlowController(data);
            case 354: return new ::Ifc2x3::IfcFlowControllerType(data);
            case 356: return new ::Ifc2x3::IfcFlowFitting(data);
            case 357: return new ::Ifc2x3::IfcFlowFittingType(data);
            case 358: return new ::Ifc2x3::IfcFlowInstrumentType(data);
            case 360: return new ::Ifc2x3::IfcFlowMeterType(data);
            case 362: return new ::Ifc2x3::IfcFlowMovingDevice(data);
            case 363: return new ::Ifc2x3::IfcFlowMovingDeviceType(data);
            case 364: return new ::Ifc2x3::IfcFlowSegment(data);
            case 365: return new ::Ifc2x3::IfcFlowSegmentType(data);
            case 366: return new ::Ifc2x3::IfcFlowStorageDevice(data);
            case 367: return new ::Ifc2x3::IfcFlowStorageDeviceType(data);
            case 368: return new ::Ifc2x3::IfcFlowTerminal(data);
            case 369: return new ::Ifc2x3::IfcFlowTerminalType(data);
            case 370: return new ::Ifc2x3::IfcFlowTreatmentDevice(data);
            case 371: return new ::Ifc2x3::IfcFlowTreatmentDeviceType(data);
            case 372: return new ::Ifc2x3::IfcFluidFlowProperties(data);
            case 373: return new ::Ifc2x3::IfcFontStyle(data);
            case 374: return new ::Ifc2x3::IfcFontVariant(data);
            case 375: return new ::Ifc2x3::IfcFontWeight(data);
            case 376: return new ::Ifc2x3::IfcFooting(data);
            case 378: return new ::Ifc2x3::IfcForceMeasure(data);
            case 379: return new ::Ifc2x3::IfcFrequencyMeasure(data);
            case 380: return new ::Ifc2x3::IfcFuelProperties(data);
            case 381: return new ::Ifc2x3::IfcFurnishingElement(data);
            case 382: return new ::Ifc2x3::IfcFurnishingElementType(data);
            case 383: return new ::Ifc2x3::IfcFurnitureStandard(data);
            case 384: return new ::Ifc2x3::IfcFurnitureType(data);
            case 385: return new ::Ifc2x3::IfcGasTerminalType(data);
            case 387: return new ::Ifc2x3::IfcGeneralMaterialProperties(data);
            case 388: return new ::Ifc2x3::IfcGeneralProfileProperties(data);
            case 389: return new ::Ifc2x3::IfcGeometricCurveSet(data);
            case 391: return new ::Ifc2x3::IfcGeometricRepresentationContext(data);
            case 392: return new ::Ifc2x3::IfcGeometricRepresentationItem(data);
            case 393: return new ::Ifc2x3::IfcGeometricRepresentationSubContext(data);
            case 394: return new ::Ifc2x3::IfcGeometricSet(data);
            case 396: return new ::Ifc2x3::IfcGloballyUniqueId(data);
            case 398: return new ::Ifc2x3::IfcGrid(data);
            case 399: return new ::Ifc2x3::IfcGridAxis(data);
            case 400: return new ::Ifc2x3::IfcGridPlacement(data);
            case 401: return new ::Ifc2x3::IfcGroup(data);
            case 402: return new ::Ifc2x3::IfcHalfSpaceSolid(data);
            case 404: return new ::Ifc2x3::IfcHeatExchangerType(data);
            case 406: return new ::Ifc2x3::IfcHeatFluxDensityMeasure(data);
            case 407: return new ::Ifc2x3::IfcHeatingValueMeasure(data);
            case 408: return new ::Ifc2x3::IfcHourInDay(data);
            case 409: return new ::Ifc2x3::IfcHumidifierType(data);
            case 411: return new ::Ifc2x3::IfcHygroscopicMaterialProperties(data);
            case 412: return new ::Ifc2x3::IfcIdentifier(data);
            case 413: return new ::Ifc2x3::IfcIlluminanceMeasure(data);
            case 414: return new ::Ifc2x3::IfcImageTexture(data);
            case 415: return new ::Ifc2x3::IfcInductanceMeasure(data);
            case 416: return new ::Ifc2x3::IfcInteger(data);
            case 417: return new ::Ifc2x3::IfcIntegerCountRateMeasure(data);
            case 419: return new ::Ifc2x3::IfcInventory(data);
            case 421: return new ::Ifc2x3::IfcIonConcentrationMeasure(data);
            case 422: return new ::Ifc2x3::IfcIrregularTimeSeries(data);
            case 423: return new ::Ifc2x3::IfcIrregularTimeSeriesValue(data);
            case 424: return new ::Ifc2x3::IfcIShapeProfileDef(data);
            case 425: return new ::Ifc2x3::IfcIsothermalMoistureCapacityMeasure(data);
            case 426: return new ::Ifc2x3::IfcJunctionBoxType(data);
            case 428: return new ::Ifc2x3::IfcKinematicViscosityMeasure(data);
            case 429: return new ::Ifc2x3::IfcLabel(data);
            case 430: return new ::Ifc2x3::IfcLaborResource(data);
            case 431: return new ::Ifc2x3::IfcLampType(data);
            case 435: return new ::Ifc2x3::IfcLengthMeasure(data);
            case 436: return new ::Ifc2x3::IfcLibraryInformation(data);
            case 437: return new ::Ifc2x3::IfcLibraryReference(data);
            case 440: return new ::Ifc2x3::IfcLightDistributionData(data);
            case 443: return new ::Ifc2x3::IfcLightFixtureType(data);
            case 445: return new ::Ifc2x3::IfcLightIntensityDistribution(data);
            case 446: return new ::Ifc2x3::IfcLightSource(data);
            case 447: return new ::Ifc2x3::IfcLightSourceAmbient(data);
            case 448: return new ::Ifc2x3::IfcLightSourceDirectional(data);
            case 449: return new ::Ifc2x3::IfcLightSourceGoniometric(data);
            case 450: return new ::Ifc2x3::IfcLightSourcePositional(data);
            case 451: return new ::Ifc2x3::IfcLightSourceSpot(data);
            case 452: return new ::Ifc2x3::IfcLine(data);
            case 453: return new ::Ifc2x3::IfcLinearDimension(data);
            case 454: return new ::Ifc2x3::IfcLinearForceMeasure(data);
            case 455: return new ::Ifc2x3::IfcLinearMomentMeasure(data);
            case 456: return new ::Ifc2x3::IfcLinearStiffnessMeasure(data);
            case 457: return new ::Ifc2x3::IfcLinearVelocityMeasure(data);
            case 459: return new ::Ifc2x3::IfcLocalPlacement(data);
            case 460: return new ::Ifc2x3::IfcLocalTime(data);
            case 461: return new ::Ifc2x3::IfcLogical(data);
            case 463: return new ::Ifc2x3::IfcLoop(data);
            case 464: return new ::Ifc2x3::IfcLShapeProfileDef(data);
            case 465: return new ::Ifc2x3::IfcLuminousFluxMeasure(data);
            case 466: return new ::Ifc2x3::IfcLuminousIntensityDistributionMeasure(data);
            case 467: return new ::Ifc2x3::IfcLuminousIntensityMeasure(data);
            case 468: return new ::Ifc2x3::IfcMagneticFluxDensityMeasure(data);
            case 469: return new ::Ifc2x3::IfcMagneticFluxMeasure(data);
            case 470: return new ::Ifc2x3::IfcManifoldSolidBrep(data);
            case 471: return new ::Ifc2x3::IfcMappedItem(data);
            case 472: return new ::Ifc2x3::IfcMassDensityMeasure(data);
            case 473: return new ::Ifc2x3::IfcMassFlowRateMeasure(data);
            case 474: return new ::Ifc2x3::IfcMassMeasure(data);
            case 475: return new ::Ifc2x3::IfcMassPerLengthMeasure(data);
            case 476: return new ::Ifc2x3::IfcMaterial(data);
            case 477: return new ::Ifc2x3::IfcMaterialClassificationRelationship(data);
            case 478: return new ::Ifc2x3::IfcMaterialDefinitionRepresentation(data);
            case 479: return new ::Ifc2x3::IfcMaterialLayer(data);
            case 480: return new ::Ifc2x3::IfcMaterialLayerSet(data);
            case 481: return new ::Ifc2x3::IfcMaterialLayerSetUsage(data);
            case 482: return new ::Ifc2x3::IfcMaterialList(data);
            case 483: return new ::Ifc2x3::IfcMaterialProperties(data);
            case 486: return new ::Ifc2x3::IfcMeasureWithUnit(data);
            case 487: return new ::Ifc2x3::IfcMechanicalConcreteMaterialProperties(data);
            case 488: return new ::Ifc2x3::IfcMechanicalFastener(data);
            case 489: return new ::Ifc2x3::IfcMechanicalFastenerType(data);
            case 490: return new ::Ifc2x3::IfcMechanicalMaterialProperties(data);
            case 491: return new ::Ifc2x3::IfcMechanicalSteelMaterialProperties(data);
            case 492: return new ::Ifc2x3::IfcMember(data);
            case 493: return new ::Ifc2x3::IfcMemberType(data);
            case 495: return new ::Ifc2x3::IfcMetric(data);
            case 497: return new ::Ifc2x3::IfcMinuteInHour(data);
            case 498: return new ::Ifc2x3::IfcModulusOfElasticityMeasure(data);
            case 499: return new ::Ifc2x3::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 500: return new ::Ifc2x3::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 501: return new ::Ifc2x3::IfcModulusOfSubgradeReactionMeasure(data);
            case 502: return new ::Ifc2x3::IfcMoistureDiffusivityMeasure(data);
            case 503: return new ::Ifc2x3::IfcMolecularWeightMeasure(data);
            case 504: return new ::Ifc2x3::IfcMomentOfInertiaMeasure(data);
            case 505: return new ::Ifc2x3::IfcMonetaryMeasure(data);
            case 506: return new ::Ifc2x3::IfcMonetaryUnit(data);
            case 507: return new ::Ifc2x3::IfcMonthInYearNumber(data);
            case 508: return new ::Ifc2x3::IfcMotorConnectionType(data);
            case 510: return new ::Ifc2x3::IfcMove(data);
            case 511: return new ::Ifc2x3::IfcNamedUnit(data);
            case 512: return new ::Ifc2x3::IfcNormalisedRatioMeasure(data);
            case 514: return new ::Ifc2x3::IfcNumericMeasure(data);
            case 515: return new ::Ifc2x3::IfcObject(data);
            case 516: return new ::Ifc2x3::IfcObjectDefinition(data);
            case 517: return new ::Ifc2x3::IfcObjective(data);
            case 519: return new ::Ifc2x3::IfcObjectPlacement(data);
            case 522: return new ::Ifc2x3::IfcOccupant(data);
            case 524: return new ::Ifc2x3::IfcOffsetCurve2D(data);
            case 525: return new ::Ifc2x3::IfcOffsetCurve3D(data);
            case 526: return new ::Ifc2x3::IfcOneDirectionRepeatFactor(data);
            case 527: return new ::Ifc2x3::IfcOpeningElement(data);
            case 528: return new ::Ifc2x3::IfcOpenShell(data);
            case 529: return new ::Ifc2x3::IfcOpticalMaterialProperties(data);
            case 530: return new ::Ifc2x3::IfcOrderAction(data);
            case 531: return new ::Ifc2x3::IfcOrganization(data);
            case 532: return new ::Ifc2x3::IfcOrganizationRelationship(data);
            case 534: return new ::Ifc2x3::IfcOrientedEdge(data);
            case 535: return new ::Ifc2x3::IfcOutletType(data);
            case 537: return new ::Ifc2x3::IfcOwnerHistory(data);
            case 538: return new ::Ifc2x3::IfcParameterizedProfileDef(data);
            case 539: return new ::Ifc2x3::IfcParameterValue(data);
            case 540: return new ::Ifc2x3::IfcPath(data);
            case 541: return new ::Ifc2x3::IfcPerformanceHistory(data);
            case 543: return new ::Ifc2x3::IfcPermeableCoveringProperties(data);
            case 544: return new ::Ifc2x3::IfcPermit(data);
            case 545: return new ::Ifc2x3::IfcPerson(data);
            case 546: return new ::Ifc2x3::IfcPersonAndOrganization(data);
            case 547: return new ::Ifc2x3::IfcPHMeasure(data);
            case 548: return new ::Ifc2x3::IfcPhysicalComplexQuantity(data);
            case 550: return new ::Ifc2x3::IfcPhysicalQuantity(data);
            case 551: return new ::Ifc2x3::IfcPhysicalSimpleQuantity(data);
            case 552: return new ::Ifc2x3::IfcPile(data);
            case 555: return new ::Ifc2x3::IfcPipeFittingType(data);
            case 557: return new ::Ifc2x3::IfcPipeSegmentType(data);
            case 559: return new ::Ifc2x3::IfcPixelTexture(data);
            case 560: return new ::Ifc2x3::IfcPlacement(data);
            case 561: return new ::Ifc2x3::IfcPlanarBox(data);
            case 562: return new ::Ifc2x3::IfcPlanarExtent(data);
            case 563: return new ::Ifc2x3::IfcPlanarForceMeasure(data);
            case 564: return new ::Ifc2x3::IfcPlane(data);
            case 565: return new ::Ifc2x3::IfcPlaneAngleMeasure(data);
            case 566: return new ::Ifc2x3::IfcPlate(data);
            case 567: return new ::Ifc2x3::IfcPlateType(data);
            case 569: return new ::Ifc2x3::IfcPoint(data);
            case 570: return new ::Ifc2x3::IfcPointOnCurve(data);
            case 571: return new ::Ifc2x3::IfcPointOnSurface(data);
            case 573: return new ::Ifc2x3::IfcPolygonalBoundedHalfSpace(data);
            case 574: return new ::Ifc2x3::IfcPolyline(data);
            case 575: return new ::Ifc2x3::IfcPolyLoop(data);
            case 576: return new ::Ifc2x3::IfcPort(data);
            case 577: return new ::Ifc2x3::IfcPositiveLengthMeasure(data);
            case 578: return new ::Ifc2x3::IfcPositivePlaneAngleMeasure(data);
            case 579: return new ::Ifc2x3::IfcPositiveRatioMeasure(data);
            case 580: return new ::Ifc2x3::IfcPostalAddress(data);
            case 581: return new ::Ifc2x3::IfcPowerMeasure(data);
            case 582: return new ::Ifc2x3::IfcPreDefinedColour(data);
            case 583: return new ::Ifc2x3::IfcPreDefinedCurveFont(data);
            case 584: return new ::Ifc2x3::IfcPreDefinedDimensionSymbol(data);
            case 585: return new ::Ifc2x3::IfcPreDefinedItem(data);
            case 586: return new ::Ifc2x3::IfcPreDefinedPointMarkerSymbol(data);
            case 587: return new ::Ifc2x3::IfcPreDefinedSymbol(data);
            case 588: return new ::Ifc2x3::IfcPreDefinedTerminatorSymbol(data);
            case 589: return new ::Ifc2x3::IfcPreDefinedTextFont(data);
            case 590: return new ::Ifc2x3::IfcPresentableText(data);
            case 591: return new ::Ifc2x3::IfcPresentationLayerAssignment(data);
            case 592: return new ::Ifc2x3::IfcPresentationLayerWithStyle(data);
            case 593: return new ::Ifc2x3::IfcPresentationStyle(data);
            case 594: return new ::Ifc2x3::IfcPresentationStyleAssignment(data);
            case 596: return new ::Ifc2x3::IfcPressureMeasure(data);
            case 597: return new ::Ifc2x3::IfcProcedure(data);
            case 599: return new ::Ifc2x3::IfcProcess(data);
            case 600: return new ::Ifc2x3::IfcProduct(data);
            case 601: return new ::Ifc2x3::IfcProductDefinitionShape(data);
            case 602: return new ::Ifc2x3::IfcProductRepresentation(data);
            case 603: return new ::Ifc2x3::IfcProductsOfCombustionProperties(data);
            case 604: return new ::Ifc2x3::IfcProfileDef(data);
            case 605: return new ::Ifc2x3::IfcProfileProperties(data);
            case 607: return new ::Ifc2x3::IfcProject(data);
            case 609: return new ::Ifc2x3::IfcProjectionCurve(data);
            case 610: return new ::Ifc2x3::IfcProjectionElement(data);
            case 611: return new ::Ifc2x3::IfcProjectOrder(data);
            case 612: return new ::Ifc2x3::IfcProjectOrderRecord(data);
            case 615: return new ::Ifc2x3::IfcProperty(data);
            case 616: return new ::Ifc2x3::IfcPropertyBoundedValue(data);
            case 617: return new ::Ifc2x3::IfcPropertyConstraintRelationship(data);
            case 618: return new ::Ifc2x3::IfcPropertyDefinition(data);
            case 619: return new ::Ifc2x3::IfcPropertyDependencyRelationship(data);
            case 620: return new ::Ifc2x3::IfcPropertyEnumeratedValue(data);
            case 621: return new ::Ifc2x3::IfcPropertyEnumeration(data);
            case 622: return new ::Ifc2x3::IfcPropertyListValue(data);
            case 623: return new ::Ifc2x3::IfcPropertyReferenceValue(data);
            case 624: return new ::Ifc2x3::IfcPropertySet(data);
            case 625: return new ::Ifc2x3::IfcPropertySetDefinition(data);
            case 626: return new ::Ifc2x3::IfcPropertySingleValue(data);
            case 628: return new ::Ifc2x3::IfcPropertyTableValue(data);
            case 629: return new ::Ifc2x3::IfcProtectiveDeviceType(data);
            case 631: return new ::Ifc2x3::IfcProxy(data);
            case 632: return new ::Ifc2x3::IfcPumpType(data);
            case 634: return new ::Ifc2x3::IfcQuantityArea(data);
            case 635: return new ::Ifc2x3::IfcQuantityCount(data);
            case 636: return new ::Ifc2x3::IfcQuantityLength(data);
            case 637: return new ::Ifc2x3::IfcQuantityTime(data);
            case 638: return new ::Ifc2x3::IfcQuantityVolume(data);
            case 639: return new ::Ifc2x3::IfcQuantityWeight(data);
            case 640: return new ::Ifc2x3::IfcRadioActivityMeasure(data);
            case 641: return new ::Ifc2x3::IfcRadiusDimension(data);
            case 642: return new ::Ifc2x3::IfcRailing(data);
            case 643: return new ::Ifc2x3::IfcRailingType(data);
            case 645: return new ::Ifc2x3::IfcRamp(data);
            case 646: return new ::Ifc2x3::IfcRampFlight(data);
            case 647: return new ::Ifc2x3::IfcRampFlightType(data);
            case 650: return new ::Ifc2x3::IfcRatioMeasure(data);
            case 651: return new ::Ifc2x3::IfcRationalBezierCurve(data);
            case 652: return new ::Ifc2x3::IfcReal(data);
            case 653: return new ::Ifc2x3::IfcRectangleHollowProfileDef(data);
            case 654: return new ::Ifc2x3::IfcRectangleProfileDef(data);
            case 655: return new ::Ifc2x3::IfcRectangularPyramid(data);
            case 656: return new ::Ifc2x3::IfcRectangularTrimmedSurface(data);
            case 657: return new ::Ifc2x3::IfcReferencesValueDocument(data);
            case 659: return new ::Ifc2x3::IfcRegularTimeSeries(data);
            case 660: return new ::Ifc2x3::IfcReinforcementBarProperties(data);
            case 661: return new ::Ifc2x3::IfcReinforcementDefinitionProperties(data);
            case 662: return new ::Ifc2x3::IfcReinforcingBar(data);
            case 665: return new ::Ifc2x3::IfcReinforcingElement(data);
            case 666: return new ::Ifc2x3::IfcReinforcingMesh(data);
            case 667: return new ::Ifc2x3::IfcRelAggregates(data);
            case 668: return new ::Ifc2x3::IfcRelAssigns(data);
            case 669: return new ::Ifc2x3::IfcRelAssignsTasks(data);
            case 670: return new ::Ifc2x3::IfcRelAssignsToActor(data);
            case 671: return new ::Ifc2x3::IfcRelAssignsToControl(data);
            case 672: return new ::Ifc2x3::IfcRelAssignsToGroup(data);
            case 673: return new ::Ifc2x3::IfcRelAssignsToProcess(data);
            case 674: return new ::Ifc2x3::IfcRelAssignsToProduct(data);
            case 675: return new ::Ifc2x3::IfcRelAssignsToProjectOrder(data);
            case 676: return new ::Ifc2x3::IfcRelAssignsToResource(data);
            case 677: return new ::Ifc2x3::IfcRelAssociates(data);
            case 678: return new ::Ifc2x3::IfcRelAssociatesAppliedValue(data);
            case 679: return new ::Ifc2x3::IfcRelAssociatesApproval(data);
            case 680: return new ::Ifc2x3::IfcRelAssociatesClassification(data);
            case 681: return new ::Ifc2x3::IfcRelAssociatesConstraint(data);
            case 682: return new ::Ifc2x3::IfcRelAssociatesDocument(data);
            case 683: return new ::Ifc2x3::IfcRelAssociatesLibrary(data);
            case 684: return new ::Ifc2x3::IfcRelAssociatesMaterial(data);
            case 685: return new ::Ifc2x3::IfcRelAssociatesProfileProperties(data);
            case 686: return new ::Ifc2x3::IfcRelationship(data);
            case 687: return new ::Ifc2x3::IfcRelaxation(data);
            case 688: return new ::Ifc2x3::IfcRelConnects(data);
            case 689: return new ::Ifc2x3::IfcRelConnectsElements(data);
            case 690: return new ::Ifc2x3::IfcRelConnectsPathElements(data);
            case 691: return new ::Ifc2x3::IfcRelConnectsPorts(data);
            case 692: return new ::Ifc2x3::IfcRelConnectsPortToElement(data);
            case 693: return new ::Ifc2x3::IfcRelConnectsStructuralActivity(data);
            case 694: return new ::Ifc2x3::IfcRelConnectsStructuralElement(data);
            case 695: return new ::Ifc2x3::IfcRelConnectsStructuralMember(data);
            case 696: return new ::Ifc2x3::IfcRelConnectsWithEccentricity(data);
            case 697: return new ::Ifc2x3::IfcRelConnectsWithRealizingElements(data);
            case 698: return new ::Ifc2x3::IfcRelContainedInSpatialStructure(data);
            case 699: return new ::Ifc2x3::IfcRelCoversBldgElements(data);
            case 700: return new ::Ifc2x3::IfcRelCoversSpaces(data);
            case 701: return new ::Ifc2x3::IfcRelDecomposes(data);
            case 702: return new ::Ifc2x3::IfcRelDefines(data);
            case 703: return new ::Ifc2x3::IfcRelDefinesByProperties(data);
            case 704: return new ::Ifc2x3::IfcRelDefinesByType(data);
            case 705: return new ::Ifc2x3::IfcRelFillsElement(data);
            case 706: return new ::Ifc2x3::IfcRelFlowControlElements(data);
            case 707: return new ::Ifc2x3::IfcRelInteractionRequirements(data);
            case 708: return new ::Ifc2x3::IfcRelNests(data);
            case 709: return new ::Ifc2x3::IfcRelOccupiesSpaces(data);
            case 710: return new ::Ifc2x3::IfcRelOverridesProperties(data);
            case 711: return new ::Ifc2x3::IfcRelProjectsElement(data);
            case 712: return new ::Ifc2x3::IfcRelReferencedInSpatialStructure(data);
            case 713: return new ::Ifc2x3::IfcRelSchedulesCostItems(data);
            case 714: return new ::Ifc2x3::IfcRelSequence(data);
            case 715: return new ::Ifc2x3::IfcRelServicesBuildings(data);
            case 716: return new ::Ifc2x3::IfcRelSpaceBoundary(data);
            case 717: return new ::Ifc2x3::IfcRelVoidsElement(data);
            case 718: return new ::Ifc2x3::IfcRepresentation(data);
            case 719: return new ::Ifc2x3::IfcRepresentationContext(data);
            case 720: return new ::Ifc2x3::IfcRepresentationItem(data);
            case 721: return new ::Ifc2x3::IfcRepresentationMap(data);
            case 722: return new ::Ifc2x3::IfcResource(data);
            case 724: return new ::Ifc2x3::IfcRevolvedAreaSolid(data);
            case 726: return new ::Ifc2x3::IfcRibPlateProfileProperties(data);
            case 727: return new ::Ifc2x3::IfcRightCircularCone(data);
            case 728: return new ::Ifc2x3::IfcRightCircularCylinder(data);
            case 730: return new ::Ifc2x3::IfcRoof(data);
            case 732: return new ::Ifc2x3::IfcRoot(data);
            case 733: return new ::Ifc2x3::IfcRotationalFrequencyMeasure(data);
            case 734: return new ::Ifc2x3::IfcRotationalMassMeasure(data);
            case 735: return new ::Ifc2x3::IfcRotationalStiffnessMeasure(data);
            case 736: return new ::Ifc2x3::IfcRoundedEdgeFeature(data);
            case 737: return new ::Ifc2x3::IfcRoundedRectangleProfileDef(data);
            case 738: return new ::Ifc2x3::IfcSanitaryTerminalType(data);
            case 740: return new ::Ifc2x3::IfcScheduleTimeControl(data);
            case 741: return new ::Ifc2x3::IfcSecondInMinute(data);
            case 742: return new ::Ifc2x3::IfcSectionalAreaIntegralMeasure(data);
            case 743: return new ::Ifc2x3::IfcSectionedSpine(data);
            case 744: return new ::Ifc2x3::IfcSectionModulusMeasure(data);
            case 745: return new ::Ifc2x3::IfcSectionProperties(data);
            case 746: return new ::Ifc2x3::IfcSectionReinforcementProperties(data);
            case 748: return new ::Ifc2x3::IfcSensorType(data);
            case 751: return new ::Ifc2x3::IfcServiceLife(data);
            case 752: return new ::Ifc2x3::IfcServiceLifeFactor(data);
            case 755: return new ::Ifc2x3::IfcShapeAspect(data);
            case 756: return new ::Ifc2x3::IfcShapeModel(data);
            case 757: return new ::Ifc2x3::IfcShapeRepresentation(data);
            case 758: return new ::Ifc2x3::IfcShearModulusMeasure(data);
            case 760: return new ::Ifc2x3::IfcShellBasedSurfaceModel(data);
            case 761: return new ::Ifc2x3::IfcSimpleProperty(data);
            case 764: return new ::Ifc2x3::IfcSite(data);
            case 765: return new ::Ifc2x3::IfcSIUnit(data);
            case 768: return new ::Ifc2x3::IfcSlab(data);
            case 769: return new ::Ifc2x3::IfcSlabType(data);
            case 771: return new ::Ifc2x3::IfcSlippageConnectionCondition(data);
            case 772: return new ::Ifc2x3::IfcSolidAngleMeasure(data);
            case 773: return new ::Ifc2x3::IfcSolidModel(data);
            case 774: return new ::Ifc2x3::IfcSoundPowerMeasure(data);
            case 775: return new ::Ifc2x3::IfcSoundPressureMeasure(data);
            case 776: return new ::Ifc2x3::IfcSoundProperties(data);
            case 778: return new ::Ifc2x3::IfcSoundValue(data);
            case 779: return new ::Ifc2x3::IfcSpace(data);
            case 780: return new ::Ifc2x3::IfcSpaceHeaterType(data);
            case 782: return new ::Ifc2x3::IfcSpaceProgram(data);
            case 783: return new ::Ifc2x3::IfcSpaceThermalLoadProperties(data);
            case 784: return new ::Ifc2x3::IfcSpaceType(data);
            case 786: return new ::Ifc2x3::IfcSpatialStructureElement(data);
            case 787: return new ::Ifc2x3::IfcSpatialStructureElementType(data);
            case 788: return new ::Ifc2x3::IfcSpecificHeatCapacityMeasure(data);
            case 789: return new ::Ifc2x3::IfcSpecularExponent(data);
            case 791: return new ::Ifc2x3::IfcSpecularRoughness(data);
            case 792: return new ::Ifc2x3::IfcSphere(data);
            case 793: return new ::Ifc2x3::IfcStackTerminalType(data);
            case 795: return new ::Ifc2x3::IfcStair(data);
            case 796: return new ::Ifc2x3::IfcStairFlight(data);
            case 797: return new ::Ifc2x3::IfcStairFlightType(data);
            case 801: return new ::Ifc2x3::IfcStructuralAction(data);
            case 802: return new ::Ifc2x3::IfcStructuralActivity(data);
            case 804: return new ::Ifc2x3::IfcStructuralAnalysisModel(data);
            case 805: return new ::Ifc2x3::IfcStructuralConnection(data);
            case 806: return new ::Ifc2x3::IfcStructuralConnectionCondition(data);
            case 807: return new ::Ifc2x3::IfcStructuralCurveConnection(data);
            case 808: return new ::Ifc2x3::IfcStructuralCurveMember(data);
            case 809: return new ::Ifc2x3::IfcStructuralCurveMemberVarying(data);
            case 811: return new ::Ifc2x3::IfcStructuralItem(data);
            case 812: return new ::Ifc2x3::IfcStructuralLinearAction(data);
            case 813: return new ::Ifc2x3::IfcStructuralLinearActionVarying(data);
            case 814: return new ::Ifc2x3::IfcStructuralLoad(data);
            case 815: return new ::Ifc2x3::IfcStructuralLoadGroup(data);
            case 816: return new ::Ifc2x3::IfcStructuralLoadLinearForce(data);
            case 817: return new ::Ifc2x3::IfcStructuralLoadPlanarForce(data);
            case 818: return new ::Ifc2x3::IfcStructuralLoadSingleDisplacement(data);
            case 819: return new ::Ifc2x3::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 820: return new ::Ifc2x3::IfcStructuralLoadSingleForce(data);
            case 821: return new ::Ifc2x3::IfcStructuralLoadSingleForceWarping(data);
            case 822: return new ::Ifc2x3::IfcStructuralLoadStatic(data);
            case 823: return new ::Ifc2x3::IfcStructuralLoadTemperature(data);
            case 824: return new ::Ifc2x3::IfcStructuralMember(data);
            case 825: return new ::Ifc2x3::IfcStructuralPlanarAction(data);
            case 826: return new ::Ifc2x3::IfcStructuralPlanarActionVarying(data);
            case 827: return new ::Ifc2x3::IfcStructuralPointAction(data);
            case 828: return new ::Ifc2x3::IfcStructuralPointConnection(data);
            case 829: return new ::Ifc2x3::IfcStructuralPointReaction(data);
            case 830: return new ::Ifc2x3::IfcStructuralProfileProperties(data);
            case 831: return new ::Ifc2x3::IfcStructuralReaction(data);
            case 832: return new ::Ifc2x3::IfcStructuralResultGroup(data);
            case 833: return new ::Ifc2x3::IfcStructuralSteelProfileProperties(data);
            case 834: return new ::Ifc2x3::IfcStructuralSurfaceConnection(data);
            case 835: return new ::Ifc2x3::IfcStructuralSurfaceMember(data);
            case 836: return new ::Ifc2x3::IfcStructuralSurfaceMemberVarying(data);
            case 838: return new ::Ifc2x3::IfcStructuredDimensionCallout(data);
            case 839: return new ::Ifc2x3::IfcStyledItem(data);
            case 840: return new ::Ifc2x3::IfcStyledRepresentation(data);
            case 841: return new ::Ifc2x3::IfcStyleModel(data);
            case 842: return new ::Ifc2x3::IfcSubContractResource(data);
            case 843: return new ::Ifc2x3::IfcSubedge(data);
            case 844: return new ::Ifc2x3::IfcSurface(data);
            case 845: return new ::Ifc2x3::IfcSurfaceCurveSweptAreaSolid(data);
            case 846: return new ::Ifc2x3::IfcSurfaceOfLinearExtrusion(data);
            case 847: return new ::Ifc2x3::IfcSurfaceOfRevolution(data);
            case 850: return new ::Ifc2x3::IfcSurfaceStyle(data);
            case 852: return new ::Ifc2x3::IfcSurfaceStyleLighting(data);
            case 853: return new ::Ifc2x3::IfcSurfaceStyleRefraction(data);
            case 854: return new ::Ifc2x3::IfcSurfaceStyleRendering(data);
            case 855: return new ::Ifc2x3::IfcSurfaceStyleShading(data);
            case 856: return new ::Ifc2x3::IfcSurfaceStyleWithTextures(data);
            case 857: return new ::Ifc2x3::IfcSurfaceTexture(data);
            case 859: return new ::Ifc2x3::IfcSweptAreaSolid(data);
            case 860: return new ::Ifc2x3::IfcSweptDiskSolid(data);
            case 861: return new ::Ifc2x3::IfcSweptSurface(data);
            case 862: return new ::Ifc2x3::IfcSwitchingDeviceType(data);
            case 864: return new ::Ifc2x3::IfcSymbolStyle(data);
            case 866: return new ::Ifc2x3::IfcSystem(data);
            case 867: return new ::Ifc2x3::IfcSystemFurnitureElementType(data);
            case 868: return new ::Ifc2x3::IfcTable(data);
            case 869: return new ::Ifc2x3::IfcTableRow(data);
            case 870: return new ::Ifc2x3::IfcTankType(data);
            case 872: return new ::Ifc2x3::IfcTask(data);
            case 873: return new ::Ifc2x3::IfcTelecomAddress(data);
            case 874: return new ::Ifc2x3::IfcTemperatureGradientMeasure(data);
            case 875: return new ::Ifc2x3::IfcTendon(data);
            case 876: return new ::Ifc2x3::IfcTendonAnchor(data);
            case 878: return new ::Ifc2x3::IfcTerminatorSymbol(data);
            case 879: return new ::Ifc2x3::IfcText(data);
            case 880: return new ::Ifc2x3::IfcTextAlignment(data);
            case 881: return new ::Ifc2x3::IfcTextDecoration(data);
            case 882: return new ::Ifc2x3::IfcTextFontName(data);
            case 884: return new ::Ifc2x3::IfcTextLiteral(data);
            case 885: return new ::Ifc2x3::IfcTextLiteralWithExtent(data);
            case 887: return new ::Ifc2x3::IfcTextStyle(data);
            case 888: return new ::Ifc2x3::IfcTextStyleFontModel(data);
            case 889: return new ::Ifc2x3::IfcTextStyleForDefinedFont(data);
            case 891: return new ::Ifc2x3::IfcTextStyleTextModel(data);
            case 892: return new ::Ifc2x3::IfcTextStyleWithBoxCharacteristics(data);
            case 893: return new ::Ifc2x3::IfcTextTransformation(data);
            case 894: return new ::Ifc2x3::IfcTextureCoordinate(data);
            case 895: return new ::Ifc2x3::IfcTextureCoordinateGenerator(data);
            case 896: return new ::Ifc2x3::IfcTextureMap(data);
            case 897: return new ::Ifc2x3::IfcTextureVertex(data);
            case 898: return new ::Ifc2x3::IfcThermalAdmittanceMeasure(data);
            case 899: return new ::Ifc2x3::IfcThermalConductivityMeasure(data);
            case 900: return new ::Ifc2x3::IfcThermalExpansionCoefficientMeasure(data);
            case 903: return new ::Ifc2x3::IfcThermalMaterialProperties(data);
            case 904: return new ::Ifc2x3::IfcThermalResistanceMeasure(data);
            case 905: return new ::Ifc2x3::IfcThermalTransmittanceMeasure(data);
            case 906: return new ::Ifc2x3::IfcThermodynamicTemperatureMeasure(data);
            case 907: return new ::Ifc2x3::IfcTimeMeasure(data);
            case 908: return new ::Ifc2x3::IfcTimeSeries(data);
            case 910: return new ::Ifc2x3::IfcTimeSeriesReferenceRelationship(data);
            case 911: return new ::Ifc2x3::IfcTimeSeriesSchedule(data);
            case 913: return new ::Ifc2x3::IfcTimeSeriesValue(data);
            case 914: return new ::Ifc2x3::IfcTimeStamp(data);
            case 915: return new ::Ifc2x3::IfcTopologicalRepresentationItem(data);
            case 916: return new ::Ifc2x3::IfcTopologyRepresentation(data);
            case 917: return new ::Ifc2x3::IfcTorqueMeasure(data);
            case 918: return new ::Ifc2x3::IfcTransformerType(data);
            case 921: return new ::Ifc2x3::IfcTransportElement(data);
            case 922: return new ::Ifc2x3::IfcTransportElementType(data);
            case 924: return new ::Ifc2x3::IfcTrapeziumProfileDef(data);
            case 925: return new ::Ifc2x3::IfcTrimmedCurve(data);
            case 928: return new ::Ifc2x3::IfcTShapeProfileDef(data);
            case 929: return new ::Ifc2x3::IfcTubeBundleType(data);
            case 931: return new ::Ifc2x3::IfcTwoDirectionRepeatFactor(data);
            case 932: return new ::Ifc2x3::IfcTypeObject(data);
            case 933: return new ::Ifc2x3::IfcTypeProduct(data);
            case 935: return new ::Ifc2x3::IfcUnitaryEquipmentType(data);
            case 937: return new ::Ifc2x3::IfcUnitAssignment(data);
            case 939: return new ::Ifc2x3::IfcUShapeProfileDef(data);
            case 941: return new ::Ifc2x3::IfcValveType(data);
            case 943: return new ::Ifc2x3::IfcVaporPermeabilityMeasure(data);
            case 944: return new ::Ifc2x3::IfcVector(data);
            case 946: return new ::Ifc2x3::IfcVertex(data);
            case 947: return new ::Ifc2x3::IfcVertexBasedTextureMap(data);
            case 948: return new ::Ifc2x3::IfcVertexLoop(data);
            case 949: return new ::Ifc2x3::IfcVertexPoint(data);
            case 950: return new ::Ifc2x3::IfcVibrationIsolatorType(data);
            case 952: return new ::Ifc2x3::IfcVirtualElement(data);
            case 953: return new ::Ifc2x3::IfcVirtualGridIntersection(data);
            case 954: return new ::Ifc2x3::IfcVolumeMeasure(data);
            case 955: return new ::Ifc2x3::IfcVolumetricFlowRateMeasure(data);
            case 956: return new ::Ifc2x3::IfcWall(data);
            case 957: return new ::Ifc2x3::IfcWallStandardCase(data);
            case 958: return new ::Ifc2x3::IfcWallType(data);
            case 960: return new ::Ifc2x3::IfcWarpingConstantMeasure(data);
            case 961: return new ::Ifc2x3::IfcWarpingMomentMeasure(data);
            case 962: return new ::Ifc2x3::IfcWasteTerminalType(data);
            case 964: return new ::Ifc2x3::IfcWaterProperties(data);
            case 965: return new ::Ifc2x3::IfcWindow(data);
            case 966: return new ::Ifc2x3::IfcWindowLiningProperties(data);
            case 969: return new ::Ifc2x3::IfcWindowPanelProperties(data);
            case 970: return new ::Ifc2x3::IfcWindowStyle(data);
            case 973: return new ::Ifc2x3::IfcWorkControl(data);
            case 975: return new ::Ifc2x3::IfcWorkPlan(data);
            case 976: return new ::Ifc2x3::IfcWorkSchedule(data);
            case 977: return new ::Ifc2x3::IfcYearNumber(data);
            case 978: return new ::Ifc2x3::IfcZone(data);
            case 979: return new ::Ifc2x3::IfcZShapeProfileDef(data);
            default: throw IfcParse::IfcException(data->type()->name() + " cannot be instantiated");
        }

    }
};


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC2X3_populate_schema() {
    IFC2X3_IfcAbsorbedDoseMeasure_type = new type_declaration("IfcAbsorbedDoseMeasure", 1, new simple_type(simple_type::real_type));
    IFC2X3_IfcAccelerationMeasure_type = new type_declaration("IfcAccelerationMeasure", 2, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcActionSourceTypeEnum_type = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IFC2X3_IfcActionTypeEnum_type = new enumeration_type("IfcActionTypeEnum", 5, items);
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
        IFC2X3_IfcActuatorTypeEnum_type = new enumeration_type("IfcActuatorTypeEnum", 10, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC2X3_IfcAddressTypeEnum_type = new enumeration_type("IfcAddressTypeEnum", 12, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AHEAD");
        items.push_back("BEHIND");
        IFC2X3_IfcAheadOrBehind_type = new enumeration_type("IfcAheadOrBehind", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IFC2X3_IfcAirTerminalBoxTypeEnum_type = new enumeration_type("IfcAirTerminalBoxTypeEnum", 15, items);
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
        IFC2X3_IfcAirTerminalTypeEnum_type = new enumeration_type("IfcAirTerminalTypeEnum", 17, items);
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
        IFC2X3_IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 19, items);
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
        IFC2X3_IfcAlarmTypeEnum_type = new enumeration_type("IfcAlarmTypeEnum", 21, items);
    }
    IFC2X3_IfcAmountOfSubstanceMeasure_type = new type_declaration("IfcAmountOfSubstanceMeasure", 22, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IFC2X3_IfcAnalysisModelTypeEnum_type = new enumeration_type("IfcAnalysisModelTypeEnum", 23, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IFC2X3_IfcAnalysisTheoryTypeEnum_type = new enumeration_type("IfcAnalysisTheoryTypeEnum", 24, items);
    }
    IFC2X3_IfcAngularVelocityMeasure_type = new type_declaration("IfcAngularVelocityMeasure", 26, new simple_type(simple_type::real_type));
    IFC2X3_IfcAreaMeasure_type = new type_declaration("IfcAreaMeasure", 47, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IFC2X3_IfcArithmeticOperatorEnum_type = new enumeration_type("IfcArithmeticOperatorEnum", 48, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IFC2X3_IfcAssemblyPlaceEnum_type = new enumeration_type("IfcAssemblyPlaceEnum", 49, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IFC2X3_IfcBSplineCurveForm_type = new enumeration_type("IfcBSplineCurveForm", 81, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEAM");
        items.push_back("JOIST");
        items.push_back("LINTEL");
        items.push_back("NOTDEFINED");
        items.push_back("T_BEAM");
        items.push_back("USERDEFINED");
        IFC2X3_IfcBeamTypeEnum_type = new enumeration_type("IfcBeamTypeEnum", 58, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EQUALTO");
        items.push_back("GREATERTHAN");
        items.push_back("GREATERTHANOREQUALTO");
        items.push_back("LESSTHAN");
        items.push_back("LESSTHANOREQUALTO");
        items.push_back("NOTEQUALTO");
        IFC2X3_IfcBenchmarkEnum_type = new enumeration_type("IfcBenchmarkEnum", 59, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IFC2X3_IfcBoilerTypeEnum_type = new enumeration_type("IfcBoilerTypeEnum", 64, items);
    }
    IFC2X3_IfcBoolean_type = new type_declaration("IfcBoolean", 65, new simple_type(simple_type::boolean_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IFC2X3_IfcBooleanOperator_type = new enumeration_type("IfcBooleanOperator", 68, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcBuildingElementProxyTypeEnum_type = new enumeration_type("IfcBuildingElementProxyTypeEnum", 88, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IFC2X3_IfcCableCarrierFittingTypeEnum_type = new enumeration_type("IfcCableCarrierFittingTypeEnum", 92, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcCableCarrierSegmentTypeEnum_type = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 94, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcCableSegmentTypeEnum_type = new enumeration_type("IfcCableSegmentTypeEnum", 96, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("MODIFIEDADDED");
        items.push_back("MODIFIEDDELETED");
        items.push_back("NOCHANGE");
        IFC2X3_IfcChangeActionEnum_type = new enumeration_type("IfcChangeActionEnum", 106, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IFC2X3_IfcChillerTypeEnum_type = new enumeration_type("IfcChillerTypeEnum", 109, items);
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
        IFC2X3_IfcCoilTypeEnum_type = new enumeration_type("IfcCoilTypeEnum", 122, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcColumnTypeEnum_type = new enumeration_type("IfcColumnTypeEnum", 129, items);
    }
    IFC2X3_IfcComplexNumber_type = new type_declaration("IfcComplexNumber", 130, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC2X3_IfcCompoundPlaneAngleMeasure_type = new type_declaration("IfcCompoundPlaneAngleMeasure", 135, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
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
        IFC2X3_IfcCompressorTypeEnum_type = new enumeration_type("IfcCompressorTypeEnum", 137, items);
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
        IFC2X3_IfcCondenserTypeEnum_type = new enumeration_type("IfcCondenserTypeEnum", 139, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IFC2X3_IfcConnectionTypeEnum_type = new enumeration_type("IfcConnectionTypeEnum", 151, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IFC2X3_IfcConstraintEnum_type = new enumeration_type("IfcConstraintEnum", 155, items);
    }
    IFC2X3_IfcContextDependentMeasure_type = new type_declaration("IfcContextDependentMeasure", 161, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcControllerTypeEnum_type = new enumeration_type("IfcControllerTypeEnum", 165, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IFC2X3_IfcCooledBeamTypeEnum_type = new enumeration_type("IfcCooledBeamTypeEnum", 168, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcCoolingTowerTypeEnum_type = new enumeration_type("IfcCoolingTowerTypeEnum", 170, items);
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
        IFC2X3_IfcCostScheduleTypeEnum_type = new enumeration_type("IfcCostScheduleTypeEnum", 174, items);
    }
    IFC2X3_IfcCountMeasure_type = new type_declaration("IfcCountMeasure", 176, new simple_type(simple_type::number_type));
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
        IFC2X3_IfcCoveringTypeEnum_type = new enumeration_type("IfcCoveringTypeEnum", 179, items);
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
        IFC2X3_IfcCurrencyEnum_type = new enumeration_type("IfcCurrencyEnum", 187, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcCurtainWallTypeEnum_type = new enumeration_type("IfcCurtainWallTypeEnum", 191, items);
    }
    IFC2X3_IfcCurvatureMeasure_type = new type_declaration("IfcCurvatureMeasure", 192, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcDamperTypeEnum_type = new enumeration_type("IfcDamperTypeEnum", 203, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcDataOriginEnum_type = new enumeration_type("IfcDataOriginEnum", 204, items);
    }
    IFC2X3_IfcDayInMonthNumber_type = new type_declaration("IfcDayInMonthNumber", 207, new simple_type(simple_type::integer_type));
    IFC2X3_IfcDaylightSavingHour_type = new type_declaration("IfcDaylightSavingHour", 208, new simple_type(simple_type::integer_type));
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
        IFC2X3_IfcDerivedUnitEnum_type = new enumeration_type("IfcDerivedUnitEnum", 215, items);
    }
    IFC2X3_IfcDescriptiveMeasure_type = new type_declaration("IfcDescriptiveMeasure", 216, new simple_type(simple_type::string_type));
    IFC2X3_IfcDimensionCount_type = new type_declaration("IfcDimensionCount", 220, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("ORIGIN");
        items.push_back("TARGET");
        IFC2X3_IfcDimensionExtentUsage_type = new enumeration_type("IfcDimensionExtentUsage", 224, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC2X3_IfcDirectionSenseEnum_type = new enumeration_type("IfcDirectionSenseEnum", 227, items);
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
        IFC2X3_IfcDistributionChamberElementTypeEnum_type = new enumeration_type("IfcDistributionChamberElementTypeEnum", 232, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcDocumentConfidentialityEnum_type = new enumeration_type("IfcDocumentConfidentialityEnum", 240, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IFC2X3_IfcDocumentStatusEnum_type = new enumeration_type("IfcDocumentStatusEnum", 246, items);
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
        IFC2X3_IfcDoorPanelOperationEnum_type = new enumeration_type("IfcDoorPanelOperationEnum", 249, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IFC2X3_IfcDoorPanelPositionEnum_type = new enumeration_type("IfcDoorPanelPositionEnum", 250, items);
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
        IFC2X3_IfcDoorStyleConstructionEnum_type = new enumeration_type("IfcDoorStyleConstructionEnum", 253, items);
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
        IFC2X3_IfcDoorStyleOperationEnum_type = new enumeration_type("IfcDoorStyleOperationEnum", 254, items);
    }
    IFC2X3_IfcDoseEquivalentMeasure_type = new type_declaration("IfcDoseEquivalentMeasure", 255, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcDuctFittingTypeEnum_type = new enumeration_type("IfcDuctFittingTypeEnum", 263, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IFC2X3_IfcDuctSegmentTypeEnum_type = new enumeration_type("IfcDuctSegmentTypeEnum", 265, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IFC2X3_IfcDuctSilencerTypeEnum_type = new enumeration_type("IfcDuctSilencerTypeEnum", 267, items);
    }
    IFC2X3_IfcDynamicViscosityMeasure_type = new type_declaration("IfcDynamicViscosityMeasure", 268, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcElectricApplianceTypeEnum_type = new enumeration_type("IfcElectricApplianceTypeEnum", 277, items);
    }
    IFC2X3_IfcElectricCapacitanceMeasure_type = new type_declaration("IfcElectricCapacitanceMeasure", 278, new simple_type(simple_type::real_type));
    IFC2X3_IfcElectricChargeMeasure_type = new type_declaration("IfcElectricChargeMeasure", 279, new simple_type(simple_type::real_type));
    IFC2X3_IfcElectricConductanceMeasure_type = new type_declaration("IfcElectricConductanceMeasure", 280, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ALTERNATING");
        items.push_back("DIRECT");
        items.push_back("NOTDEFINED");
        IFC2X3_IfcElectricCurrentEnum_type = new enumeration_type("IfcElectricCurrentEnum", 281, items);
    }
    IFC2X3_IfcElectricCurrentMeasure_type = new type_declaration("IfcElectricCurrentMeasure", 282, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcElectricDistributionPointFunctionEnum_type = new enumeration_type("IfcElectricDistributionPointFunctionEnum", 284, items);
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
        IFC2X3_IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 286, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcElectricGeneratorTypeEnum_type = new enumeration_type("IfcElectricGeneratorTypeEnum", 288, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELECTRICCABLEHEATER");
        items.push_back("ELECTRICMATHEATER");
        items.push_back("ELECTRICPOINTHEATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcElectricHeaterTypeEnum_type = new enumeration_type("IfcElectricHeaterTypeEnum", 290, items);
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
        IFC2X3_IfcElectricMotorTypeEnum_type = new enumeration_type("IfcElectricMotorTypeEnum", 292, items);
    }
    IFC2X3_IfcElectricResistanceMeasure_type = new type_declaration("IfcElectricResistanceMeasure", 293, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IFC2X3_IfcElectricTimeControlTypeEnum_type = new enumeration_type("IfcElectricTimeControlTypeEnum", 295, items);
    }
    IFC2X3_IfcElectricVoltageMeasure_type = new type_declaration("IfcElectricVoltageMeasure", 296, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcElementAssemblyTypeEnum_type = new enumeration_type("IfcElementAssemblyTypeEnum", 300, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IFC2X3_IfcElementCompositionEnum_type = new enumeration_type("IfcElementCompositionEnum", 303, items);
    }
    IFC2X3_IfcEnergyMeasure_type = new type_declaration("IfcEnergyMeasure", 310, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AUXILIARY");
        items.push_back("NOTDEFINED");
        items.push_back("PRIMARY");
        items.push_back("SECONDARY");
        items.push_back("TERTIARY");
        items.push_back("USERDEFINED");
        IFC2X3_IfcEnergySequenceEnum_type = new enumeration_type("IfcEnergySequenceEnum", 312, items);
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
        IFC2X3_IfcEnvironmentalImpactCategoryEnum_type = new enumeration_type("IfcEnvironmentalImpactCategoryEnum", 313, items);
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
        IFC2X3_IfcEvaporativeCoolerTypeEnum_type = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 318, items);
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
        IFC2X3_IfcEvaporatorTypeEnum_type = new enumeration_type("IfcEvaporatorTypeEnum", 320, items);
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
        IFC2X3_IfcFanTypeEnum_type = new enumeration_type("IfcFanTypeEnum", 337, items);
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
        IFC2X3_IfcFilterTypeEnum_type = new enumeration_type("IfcFilterTypeEnum", 350, items);
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
        IFC2X3_IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 352, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IFC2X3_IfcFlowDirectionEnum_type = new enumeration_type("IfcFlowDirectionEnum", 355, items);
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
        IFC2X3_IfcFlowInstrumentTypeEnum_type = new enumeration_type("IfcFlowInstrumentTypeEnum", 359, items);
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
        IFC2X3_IfcFlowMeterTypeEnum_type = new enumeration_type("IfcFlowMeterTypeEnum", 361, items);
    }
    IFC2X3_IfcFontStyle_type = new type_declaration("IfcFontStyle", 373, new simple_type(simple_type::string_type));
    IFC2X3_IfcFontVariant_type = new type_declaration("IfcFontVariant", 374, new simple_type(simple_type::string_type));
    IFC2X3_IfcFontWeight_type = new type_declaration("IfcFontWeight", 375, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IFC2X3_IfcFootingTypeEnum_type = new enumeration_type("IfcFootingTypeEnum", 377, items);
    }
    IFC2X3_IfcForceMeasure_type = new type_declaration("IfcForceMeasure", 378, new simple_type(simple_type::real_type));
    IFC2X3_IfcFrequencyMeasure_type = new type_declaration("IfcFrequencyMeasure", 379, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GASAPPLIANCE");
        items.push_back("GASBOOSTER");
        items.push_back("GASBURNER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcGasTerminalTypeEnum_type = new enumeration_type("IfcGasTerminalTypeEnum", 386, items);
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
        IFC2X3_IfcGeometricProjectionEnum_type = new enumeration_type("IfcGeometricProjectionEnum", 390, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IFC2X3_IfcGlobalOrLocalEnum_type = new enumeration_type("IfcGlobalOrLocalEnum", 397, items);
    }
    IFC2X3_IfcGloballyUniqueId_type = new type_declaration("IfcGloballyUniqueId", 396, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IFC2X3_IfcHeatExchangerTypeEnum_type = new enumeration_type("IfcHeatExchangerTypeEnum", 405, items);
    }
    IFC2X3_IfcHeatFluxDensityMeasure_type = new type_declaration("IfcHeatFluxDensityMeasure", 406, new simple_type(simple_type::real_type));
    IFC2X3_IfcHeatingValueMeasure_type = new type_declaration("IfcHeatingValueMeasure", 407, new simple_type(simple_type::real_type));
    IFC2X3_IfcHourInDay_type = new type_declaration("IfcHourInDay", 408, new simple_type(simple_type::integer_type));
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
        IFC2X3_IfcHumidifierTypeEnum_type = new enumeration_type("IfcHumidifierTypeEnum", 410, items);
    }
    IFC2X3_IfcIdentifier_type = new type_declaration("IfcIdentifier", 412, new simple_type(simple_type::string_type));
    IFC2X3_IfcIlluminanceMeasure_type = new type_declaration("IfcIlluminanceMeasure", 413, new simple_type(simple_type::real_type));
    IFC2X3_IfcInductanceMeasure_type = new type_declaration("IfcInductanceMeasure", 415, new simple_type(simple_type::real_type));
    IFC2X3_IfcInteger_type = new type_declaration("IfcInteger", 416, new simple_type(simple_type::integer_type));
    IFC2X3_IfcIntegerCountRateMeasure_type = new type_declaration("IfcIntegerCountRateMeasure", 417, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("EXTERNAL");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IFC2X3_IfcInternalOrExternalEnum_type = new enumeration_type("IfcInternalOrExternalEnum", 418, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IFC2X3_IfcInventoryTypeEnum_type = new enumeration_type("IfcInventoryTypeEnum", 420, items);
    }
    IFC2X3_IfcIonConcentrationMeasure_type = new type_declaration("IfcIonConcentrationMeasure", 421, new simple_type(simple_type::real_type));
    IFC2X3_IfcIsothermalMoistureCapacityMeasure_type = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 425, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcJunctionBoxTypeEnum_type = new enumeration_type("IfcJunctionBoxTypeEnum", 427, items);
    }
    IFC2X3_IfcKinematicViscosityMeasure_type = new type_declaration("IfcKinematicViscosityMeasure", 428, new simple_type(simple_type::real_type));
    IFC2X3_IfcLabel_type = new type_declaration("IfcLabel", 429, new simple_type(simple_type::string_type));
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
        IFC2X3_IfcLampTypeEnum_type = new enumeration_type("IfcLampTypeEnum", 432, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IFC2X3_IfcLayerSetDirectionEnum_type = new enumeration_type("IfcLayerSetDirectionEnum", 434, items);
    }
    IFC2X3_IfcLengthMeasure_type = new type_declaration("IfcLengthMeasure", 435, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IFC2X3_IfcLightDistributionCurveEnum_type = new enumeration_type("IfcLightDistributionCurveEnum", 439, items);
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
        IFC2X3_IfcLightEmissionSourceEnum_type = new enumeration_type("IfcLightEmissionSourceEnum", 442, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("USERDEFINED");
        IFC2X3_IfcLightFixtureTypeEnum_type = new enumeration_type("IfcLightFixtureTypeEnum", 444, items);
    }
    IFC2X3_IfcLinearForceMeasure_type = new type_declaration("IfcLinearForceMeasure", 454, new simple_type(simple_type::real_type));
    IFC2X3_IfcLinearMomentMeasure_type = new type_declaration("IfcLinearMomentMeasure", 455, new simple_type(simple_type::real_type));
    IFC2X3_IfcLinearStiffnessMeasure_type = new type_declaration("IfcLinearStiffnessMeasure", 456, new simple_type(simple_type::real_type));
    IFC2X3_IfcLinearVelocityMeasure_type = new type_declaration("IfcLinearVelocityMeasure", 457, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_COMBINATION_GROUP");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcLoadGroupTypeEnum_type = new enumeration_type("IfcLoadGroupTypeEnum", 458, items);
    }
    IFC2X3_IfcLogical_type = new type_declaration("IfcLogical", 461, new simple_type(simple_type::logical_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALOR");
        IFC2X3_IfcLogicalOperatorEnum_type = new enumeration_type("IfcLogicalOperatorEnum", 462, items);
    }
    IFC2X3_IfcLuminousFluxMeasure_type = new type_declaration("IfcLuminousFluxMeasure", 465, new simple_type(simple_type::real_type));
    IFC2X3_IfcLuminousIntensityDistributionMeasure_type = new type_declaration("IfcLuminousIntensityDistributionMeasure", 466, new simple_type(simple_type::real_type));
    IFC2X3_IfcLuminousIntensityMeasure_type = new type_declaration("IfcLuminousIntensityMeasure", 467, new simple_type(simple_type::real_type));
    IFC2X3_IfcMagneticFluxDensityMeasure_type = new type_declaration("IfcMagneticFluxDensityMeasure", 468, new simple_type(simple_type::real_type));
    IFC2X3_IfcMagneticFluxMeasure_type = new type_declaration("IfcMagneticFluxMeasure", 469, new simple_type(simple_type::real_type));
    IFC2X3_IfcMassDensityMeasure_type = new type_declaration("IfcMassDensityMeasure", 472, new simple_type(simple_type::real_type));
    IFC2X3_IfcMassFlowRateMeasure_type = new type_declaration("IfcMassFlowRateMeasure", 473, new simple_type(simple_type::real_type));
    IFC2X3_IfcMassMeasure_type = new type_declaration("IfcMassMeasure", 474, new simple_type(simple_type::real_type));
    IFC2X3_IfcMassPerLengthMeasure_type = new type_declaration("IfcMassPerLengthMeasure", 475, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcMemberTypeEnum_type = new enumeration_type("IfcMemberTypeEnum", 494, items);
    }
    IFC2X3_IfcMinuteInHour_type = new type_declaration("IfcMinuteInHour", 497, new simple_type(simple_type::integer_type));
    IFC2X3_IfcModulusOfElasticityMeasure_type = new type_declaration("IfcModulusOfElasticityMeasure", 498, new simple_type(simple_type::real_type));
    IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 499, new simple_type(simple_type::real_type));
    IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 500, new simple_type(simple_type::real_type));
    IFC2X3_IfcModulusOfSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 501, new simple_type(simple_type::real_type));
    IFC2X3_IfcMoistureDiffusivityMeasure_type = new type_declaration("IfcMoistureDiffusivityMeasure", 502, new simple_type(simple_type::real_type));
    IFC2X3_IfcMolecularWeightMeasure_type = new type_declaration("IfcMolecularWeightMeasure", 503, new simple_type(simple_type::real_type));
    IFC2X3_IfcMomentOfInertiaMeasure_type = new type_declaration("IfcMomentOfInertiaMeasure", 504, new simple_type(simple_type::real_type));
    IFC2X3_IfcMonetaryMeasure_type = new type_declaration("IfcMonetaryMeasure", 505, new simple_type(simple_type::real_type));
    IFC2X3_IfcMonthInYearNumber_type = new type_declaration("IfcMonthInYearNumber", 507, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcMotorConnectionTypeEnum_type = new enumeration_type("IfcMotorConnectionTypeEnum", 509, items);
    }
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IFC2X3_IfcNullStyle_type = new enumeration_type("IfcNullStyle", 513, items);
    }
    IFC2X3_IfcNumericMeasure_type = new type_declaration("IfcNumericMeasure", 514, new simple_type(simple_type::number_type));
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
        IFC2X3_IfcObjectTypeEnum_type = new enumeration_type("IfcObjectTypeEnum", 521, items);
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
        IFC2X3_IfcObjectiveEnum_type = new enumeration_type("IfcObjectiveEnum", 518, items);
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
        IFC2X3_IfcOccupantTypeEnum_type = new enumeration_type("IfcOccupantTypeEnum", 523, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AUDIOVISUALOUTLET");
        items.push_back("COMMUNICATIONSOUTLET");
        items.push_back("NOTDEFINED");
        items.push_back("POWEROUTLET");
        items.push_back("USERDEFINED");
        IFC2X3_IfcOutletTypeEnum_type = new enumeration_type("IfcOutletTypeEnum", 536, items);
    }
    IFC2X3_IfcPHMeasure_type = new type_declaration("IfcPHMeasure", 547, new simple_type(simple_type::real_type));
    IFC2X3_IfcParameterValue_type = new type_declaration("IfcParameterValue", 539, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IFC2X3_IfcPermeableCoveringOperationEnum_type = new enumeration_type("IfcPermeableCoveringOperationEnum", 542, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IFC2X3_IfcPhysicalOrVirtualEnum_type = new enumeration_type("IfcPhysicalOrVirtualEnum", 549, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IFC2X3_IfcPileConstructionEnum_type = new enumeration_type("IfcPileConstructionEnum", 553, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COHESION");
        items.push_back("FRICTION");
        items.push_back("NOTDEFINED");
        items.push_back("SUPPORT");
        items.push_back("USERDEFINED");
        IFC2X3_IfcPileTypeEnum_type = new enumeration_type("IfcPileTypeEnum", 554, items);
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
        IFC2X3_IfcPipeFittingTypeEnum_type = new enumeration_type("IfcPipeFittingTypeEnum", 556, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("GUTTER");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("SPOOL");
        items.push_back("USERDEFINED");
        IFC2X3_IfcPipeSegmentTypeEnum_type = new enumeration_type("IfcPipeSegmentTypeEnum", 558, items);
    }
    IFC2X3_IfcPlanarForceMeasure_type = new type_declaration("IfcPlanarForceMeasure", 563, new simple_type(simple_type::real_type));
    IFC2X3_IfcPlaneAngleMeasure_type = new type_declaration("IfcPlaneAngleMeasure", 565, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IFC2X3_IfcPlateTypeEnum_type = new enumeration_type("IfcPlateTypeEnum", 568, items);
    }
    IFC2X3_IfcPositiveLengthMeasure_type = new type_declaration("IfcPositiveLengthMeasure", 577, new named_type(IFC2X3_IfcLengthMeasure_type));
    IFC2X3_IfcPositivePlaneAngleMeasure_type = new type_declaration("IfcPositivePlaneAngleMeasure", 578, new named_type(IFC2X3_IfcPlaneAngleMeasure_type));
    IFC2X3_IfcPowerMeasure_type = new type_declaration("IfcPowerMeasure", 581, new simple_type(simple_type::real_type));
    IFC2X3_IfcPresentableText_type = new type_declaration("IfcPresentableText", 590, new simple_type(simple_type::string_type));
    IFC2X3_IfcPressureMeasure_type = new type_declaration("IfcPressureMeasure", 596, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcProcedureTypeEnum_type = new enumeration_type("IfcProcedureTypeEnum", 598, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IFC2X3_IfcProfileTypeEnum_type = new enumeration_type("IfcProfileTypeEnum", 606, items);
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
        IFC2X3_IfcProjectOrderRecordTypeEnum_type = new enumeration_type("IfcProjectOrderRecordTypeEnum", 613, items);
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
        IFC2X3_IfcProjectOrderTypeEnum_type = new enumeration_type("IfcProjectOrderTypeEnum", 614, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IFC2X3_IfcProjectedOrTrueLengthEnum_type = new enumeration_type("IfcProjectedOrTrueLengthEnum", 608, items);
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
        IFC2X3_IfcPropertySourceEnum_type = new enumeration_type("IfcPropertySourceEnum", 627, items);
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
        IFC2X3_IfcProtectiveDeviceTypeEnum_type = new enumeration_type("IfcProtectiveDeviceTypeEnum", 630, items);
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
        IFC2X3_IfcPumpTypeEnum_type = new enumeration_type("IfcPumpTypeEnum", 633, items);
    }
    IFC2X3_IfcRadioActivityMeasure_type = new type_declaration("IfcRadioActivityMeasure", 640, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcRailingTypeEnum_type = new enumeration_type("IfcRailingTypeEnum", 644, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IFC2X3_IfcRampFlightTypeEnum_type = new enumeration_type("IfcRampFlightTypeEnum", 648, items);
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
        IFC2X3_IfcRampTypeEnum_type = new enumeration_type("IfcRampTypeEnum", 649, items);
    }
    IFC2X3_IfcRatioMeasure_type = new type_declaration("IfcRatioMeasure", 650, new simple_type(simple_type::real_type));
    IFC2X3_IfcReal_type = new type_declaration("IfcReal", 652, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcReflectanceMethodEnum_type = new enumeration_type("IfcReflectanceMethodEnum", 658, items);
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
        IFC2X3_IfcReinforcingBarRoleEnum_type = new enumeration_type("IfcReinforcingBarRoleEnum", 663, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IFC2X3_IfcReinforcingBarSurfaceEnum_type = new enumeration_type("IfcReinforcingBarSurfaceEnum", 664, items);
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
        IFC2X3_IfcResourceConsumptionEnum_type = new enumeration_type("IfcResourceConsumptionEnum", 723, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("DIRECTION_X");
        items.push_back("DIRECTION_Y");
        IFC2X3_IfcRibPlateDirectionEnum_type = new enumeration_type("IfcRibPlateDirectionEnum", 725, items);
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
        IFC2X3_IfcRoleEnum_type = new enumeration_type("IfcRoleEnum", 729, items);
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
        IFC2X3_IfcRoofTypeEnum_type = new enumeration_type("IfcRoofTypeEnum", 731, items);
    }
    IFC2X3_IfcRotationalFrequencyMeasure_type = new type_declaration("IfcRotationalFrequencyMeasure", 733, new simple_type(simple_type::real_type));
    IFC2X3_IfcRotationalMassMeasure_type = new type_declaration("IfcRotationalMassMeasure", 734, new simple_type(simple_type::real_type));
    IFC2X3_IfcRotationalStiffnessMeasure_type = new type_declaration("IfcRotationalStiffnessMeasure", 735, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcSIPrefix_type = new enumeration_type("IfcSIPrefix", 763, items);
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
        IFC2X3_IfcSIUnitName_type = new enumeration_type("IfcSIUnitName", 766, items);
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
        IFC2X3_IfcSanitaryTerminalTypeEnum_type = new enumeration_type("IfcSanitaryTerminalTypeEnum", 739, items);
    }
    IFC2X3_IfcSecondInMinute_type = new type_declaration("IfcSecondInMinute", 741, new simple_type(simple_type::real_type));
    IFC2X3_IfcSectionModulusMeasure_type = new type_declaration("IfcSectionModulusMeasure", 744, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IFC2X3_IfcSectionTypeEnum_type = new enumeration_type("IfcSectionTypeEnum", 747, items);
    }
    IFC2X3_IfcSectionalAreaIntegralMeasure_type = new type_declaration("IfcSectionalAreaIntegralMeasure", 742, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcSensorTypeEnum_type = new enumeration_type("IfcSensorTypeEnum", 749, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        IFC2X3_IfcSequenceEnum_type = new enumeration_type("IfcSequenceEnum", 750, items);
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
        IFC2X3_IfcServiceLifeFactorTypeEnum_type = new enumeration_type("IfcServiceLifeFactorTypeEnum", 753, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUALSERVICELIFE");
        items.push_back("EXPECTEDSERVICELIFE");
        items.push_back("OPTIMISTICREFERENCESERVICELIFE");
        items.push_back("PESSIMISTICREFERENCESERVICELIFE");
        items.push_back("REFERENCESERVICELIFE");
        IFC2X3_IfcServiceLifeTypeEnum_type = new enumeration_type("IfcServiceLifeTypeEnum", 754, items);
    }
    IFC2X3_IfcShearModulusMeasure_type = new type_declaration("IfcShearModulusMeasure", 758, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IFC2X3_IfcSlabTypeEnum_type = new enumeration_type("IfcSlabTypeEnum", 770, items);
    }
    IFC2X3_IfcSolidAngleMeasure_type = new type_declaration("IfcSolidAngleMeasure", 772, new simple_type(simple_type::real_type));
    IFC2X3_IfcSoundPowerMeasure_type = new type_declaration("IfcSoundPowerMeasure", 774, new simple_type(simple_type::real_type));
    IFC2X3_IfcSoundPressureMeasure_type = new type_declaration("IfcSoundPressureMeasure", 775, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DBA");
        items.push_back("DBB");
        items.push_back("DBC");
        items.push_back("NC");
        items.push_back("NOTDEFINED");
        items.push_back("NR");
        items.push_back("USERDEFINED");
        IFC2X3_IfcSoundScaleEnum_type = new enumeration_type("IfcSoundScaleEnum", 777, items);
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
        IFC2X3_IfcSpaceHeaterTypeEnum_type = new enumeration_type("IfcSpaceHeaterTypeEnum", 781, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcSpaceTypeEnum_type = new enumeration_type("IfcSpaceTypeEnum", 785, items);
    }
    IFC2X3_IfcSpecificHeatCapacityMeasure_type = new type_declaration("IfcSpecificHeatCapacityMeasure", 788, new simple_type(simple_type::real_type));
    IFC2X3_IfcSpecularExponent_type = new type_declaration("IfcSpecularExponent", 789, new simple_type(simple_type::real_type));
    IFC2X3_IfcSpecularRoughness_type = new type_declaration("IfcSpecularRoughness", 791, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IFC2X3_IfcStackTerminalTypeEnum_type = new enumeration_type("IfcStackTerminalTypeEnum", 794, items);
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
        IFC2X3_IfcStairFlightTypeEnum_type = new enumeration_type("IfcStairFlightTypeEnum", 798, items);
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
        IFC2X3_IfcStairTypeEnum_type = new enumeration_type("IfcStairTypeEnum", 799, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IFC2X3_IfcStateEnum_type = new enumeration_type("IfcStateEnum", 800, items);
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
        IFC2X3_IfcStructuralCurveTypeEnum_type = new enumeration_type("IfcStructuralCurveTypeEnum", 810, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IFC2X3_IfcStructuralSurfaceTypeEnum_type = new enumeration_type("IfcStructuralSurfaceTypeEnum", 837, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC2X3_IfcSurfaceSide_type = new enumeration_type("IfcSurfaceSide", 849, items);
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
        IFC2X3_IfcSurfaceTextureEnum_type = new enumeration_type("IfcSurfaceTextureEnum", 858, items);
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
        IFC2X3_IfcSwitchingDeviceTypeEnum_type = new enumeration_type("IfcSwitchingDeviceTypeEnum", 863, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXPANSION");
        items.push_back("NOTDEFINED");
        items.push_back("PREFORMED");
        items.push_back("PRESSUREVESSEL");
        items.push_back("SECTIONAL");
        items.push_back("USERDEFINED");
        IFC2X3_IfcTankTypeEnum_type = new enumeration_type("IfcTankTypeEnum", 871, items);
    }
    IFC2X3_IfcTemperatureGradientMeasure_type = new type_declaration("IfcTemperatureGradientMeasure", 874, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IFC2X3_IfcTendonTypeEnum_type = new enumeration_type("IfcTendonTypeEnum", 877, items);
    }
    IFC2X3_IfcText_type = new type_declaration("IfcText", 879, new simple_type(simple_type::string_type));
    IFC2X3_IfcTextAlignment_type = new type_declaration("IfcTextAlignment", 880, new simple_type(simple_type::string_type));
    IFC2X3_IfcTextDecoration_type = new type_declaration("IfcTextDecoration", 881, new simple_type(simple_type::string_type));
    IFC2X3_IfcTextFontName_type = new type_declaration("IfcTextFontName", 882, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IFC2X3_IfcTextPath_type = new enumeration_type("IfcTextPath", 886, items);
    }
    IFC2X3_IfcTextTransformation_type = new type_declaration("IfcTextTransformation", 893, new simple_type(simple_type::string_type));
    IFC2X3_IfcThermalAdmittanceMeasure_type = new type_declaration("IfcThermalAdmittanceMeasure", 898, new simple_type(simple_type::real_type));
    IFC2X3_IfcThermalConductivityMeasure_type = new type_declaration("IfcThermalConductivityMeasure", 899, new simple_type(simple_type::real_type));
    IFC2X3_IfcThermalExpansionCoefficientMeasure_type = new type_declaration("IfcThermalExpansionCoefficientMeasure", 900, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcThermalLoadSourceEnum_type = new enumeration_type("IfcThermalLoadSourceEnum", 901, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LATENT");
        items.push_back("NOTDEFINED");
        items.push_back("RADIANT");
        items.push_back("SENSIBLE");
        IFC2X3_IfcThermalLoadTypeEnum_type = new enumeration_type("IfcThermalLoadTypeEnum", 902, items);
    }
    IFC2X3_IfcThermalResistanceMeasure_type = new type_declaration("IfcThermalResistanceMeasure", 904, new simple_type(simple_type::real_type));
    IFC2X3_IfcThermalTransmittanceMeasure_type = new type_declaration("IfcThermalTransmittanceMeasure", 905, new simple_type(simple_type::real_type));
    IFC2X3_IfcThermodynamicTemperatureMeasure_type = new type_declaration("IfcThermodynamicTemperatureMeasure", 906, new simple_type(simple_type::real_type));
    IFC2X3_IfcTimeMeasure_type = new type_declaration("IfcTimeMeasure", 907, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONTINUOUS");
        items.push_back("DISCRETE");
        items.push_back("DISCRETEBINARY");
        items.push_back("NOTDEFINED");
        items.push_back("PIECEWISEBINARY");
        items.push_back("PIECEWISECONSTANT");
        items.push_back("PIECEWISECONTINUOUS");
        IFC2X3_IfcTimeSeriesDataTypeEnum_type = new enumeration_type("IfcTimeSeriesDataTypeEnum", 909, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ANNUAL");
        items.push_back("DAILY");
        items.push_back("MONTHLY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WEEKLY");
        IFC2X3_IfcTimeSeriesScheduleTypeEnum_type = new enumeration_type("IfcTimeSeriesScheduleTypeEnum", 912, items);
    }
    IFC2X3_IfcTimeStamp_type = new type_declaration("IfcTimeStamp", 914, new simple_type(simple_type::integer_type));
    IFC2X3_IfcTorqueMeasure_type = new type_declaration("IfcTorqueMeasure", 917, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IFC2X3_IfcTransformerTypeEnum_type = new enumeration_type("IfcTransformerTypeEnum", 919, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IFC2X3_IfcTransitionCode_type = new enumeration_type("IfcTransitionCode", 920, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELEVATOR");
        items.push_back("ESCALATOR");
        items.push_back("MOVINGWALKWAY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcTransportElementTypeEnum_type = new enumeration_type("IfcTransportElementTypeEnum", 923, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IFC2X3_IfcTrimmingPreference_type = new enumeration_type("IfcTrimmingPreference", 926, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcTubeBundleTypeEnum_type = new enumeration_type("IfcTubeBundleTypeEnum", 930, items);
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
        IFC2X3_IfcUnitEnum_type = new enumeration_type("IfcUnitEnum", 938, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AIRCONDITIONINGUNIT");
        items.push_back("AIRHANDLER");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFTOPUNIT");
        items.push_back("SPLITSYSTEM");
        items.push_back("USERDEFINED");
        IFC2X3_IfcUnitaryEquipmentTypeEnum_type = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 936, items);
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
        IFC2X3_IfcValveTypeEnum_type = new enumeration_type("IfcValveTypeEnum", 942, items);
    }
    IFC2X3_IfcVaporPermeabilityMeasure_type = new type_declaration("IfcVaporPermeabilityMeasure", 943, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IFC2X3_IfcVibrationIsolatorTypeEnum_type = new enumeration_type("IfcVibrationIsolatorTypeEnum", 951, items);
    }
    IFC2X3_IfcVolumeMeasure_type = new type_declaration("IfcVolumeMeasure", 954, new simple_type(simple_type::real_type));
    IFC2X3_IfcVolumetricFlowRateMeasure_type = new type_declaration("IfcVolumetricFlowRateMeasure", 955, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("ELEMENTEDWALL");
        items.push_back("NOTDEFINED");
        items.push_back("PLUMBINGWALL");
        items.push_back("POLYGONAL");
        items.push_back("SHEAR");
        items.push_back("STANDARD");
        items.push_back("USERDEFINED");
        IFC2X3_IfcWallTypeEnum_type = new enumeration_type("IfcWallTypeEnum", 959, items);
    }
    IFC2X3_IfcWarpingConstantMeasure_type = new type_declaration("IfcWarpingConstantMeasure", 960, new simple_type(simple_type::real_type));
    IFC2X3_IfcWarpingMomentMeasure_type = new type_declaration("IfcWarpingMomentMeasure", 961, new simple_type(simple_type::real_type));
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
        IFC2X3_IfcWasteTerminalTypeEnum_type = new enumeration_type("IfcWasteTerminalTypeEnum", 963, items);
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
        IFC2X3_IfcWindowPanelOperationEnum_type = new enumeration_type("IfcWindowPanelOperationEnum", 967, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IFC2X3_IfcWindowPanelPositionEnum_type = new enumeration_type("IfcWindowPanelPositionEnum", 968, items);
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
        IFC2X3_IfcWindowStyleConstructionEnum_type = new enumeration_type("IfcWindowStyleConstructionEnum", 971, items);
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
        IFC2X3_IfcWindowStyleOperationEnum_type = new enumeration_type("IfcWindowStyleOperationEnum", 972, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC2X3_IfcWorkControlTypeEnum_type = new enumeration_type("IfcWorkControlTypeEnum", 974, items);
    }
    IFC2X3_IfcYearNumber_type = new type_declaration("IfcYearNumber", 977, new simple_type(simple_type::integer_type));
    IFC2X3_IfcActorRole_type = new entity("IfcActorRole", 7, 0);
    IFC2X3_IfcAddress_type = new entity("IfcAddress", 11, 0);
    IFC2X3_IfcApplication_type = new entity("IfcApplication", 36, 0);
    IFC2X3_IfcAppliedValue_type = new entity("IfcAppliedValue", 37, 0);
    IFC2X3_IfcAppliedValueRelationship_type = new entity("IfcAppliedValueRelationship", 38, 0);
    IFC2X3_IfcApproval_type = new entity("IfcApproval", 40, 0);
    IFC2X3_IfcApprovalActorRelationship_type = new entity("IfcApprovalActorRelationship", 41, 0);
    IFC2X3_IfcApprovalPropertyRelationship_type = new entity("IfcApprovalPropertyRelationship", 42, 0);
    IFC2X3_IfcApprovalRelationship_type = new entity("IfcApprovalRelationship", 43, 0);
    IFC2X3_IfcBoundaryCondition_type = new entity("IfcBoundaryCondition", 70, 0);
    IFC2X3_IfcBoundaryEdgeCondition_type = new entity("IfcBoundaryEdgeCondition", 71, IFC2X3_IfcBoundaryCondition_type);
    IFC2X3_IfcBoundaryFaceCondition_type = new entity("IfcBoundaryFaceCondition", 72, IFC2X3_IfcBoundaryCondition_type);
    IFC2X3_IfcBoundaryNodeCondition_type = new entity("IfcBoundaryNodeCondition", 73, IFC2X3_IfcBoundaryCondition_type);
    IFC2X3_IfcBoundaryNodeConditionWarping_type = new entity("IfcBoundaryNodeConditionWarping", 74, IFC2X3_IfcBoundaryNodeCondition_type);
    IFC2X3_IfcCalendarDate_type = new entity("IfcCalendarDate", 97, 0);
    IFC2X3_IfcClassification_type = new entity("IfcClassification", 113, 0);
    IFC2X3_IfcClassificationItem_type = new entity("IfcClassificationItem", 114, 0);
    IFC2X3_IfcClassificationItemRelationship_type = new entity("IfcClassificationItemRelationship", 115, 0);
    IFC2X3_IfcClassificationNotation_type = new entity("IfcClassificationNotation", 116, 0);
    IFC2X3_IfcClassificationNotationFacet_type = new entity("IfcClassificationNotationFacet", 117, 0);
    IFC2X3_IfcColourSpecification_type = new entity("IfcColourSpecification", 126, 0);
    IFC2X3_IfcConnectionGeometry_type = new entity("IfcConnectionGeometry", 146, 0);
    IFC2X3_IfcConnectionPointGeometry_type = new entity("IfcConnectionPointGeometry", 148, IFC2X3_IfcConnectionGeometry_type);
    IFC2X3_IfcConnectionPortGeometry_type = new entity("IfcConnectionPortGeometry", 149, IFC2X3_IfcConnectionGeometry_type);
    IFC2X3_IfcConnectionSurfaceGeometry_type = new entity("IfcConnectionSurfaceGeometry", 150, IFC2X3_IfcConnectionGeometry_type);
    IFC2X3_IfcConstraint_type = new entity("IfcConstraint", 152, 0);
    IFC2X3_IfcConstraintAggregationRelationship_type = new entity("IfcConstraintAggregationRelationship", 153, 0);
    IFC2X3_IfcConstraintClassificationRelationship_type = new entity("IfcConstraintClassificationRelationship", 154, 0);
    IFC2X3_IfcConstraintRelationship_type = new entity("IfcConstraintRelationship", 156, 0);
    IFC2X3_IfcCoordinatedUniversalTimeOffset_type = new entity("IfcCoordinatedUniversalTimeOffset", 171, 0);
    IFC2X3_IfcCostValue_type = new entity("IfcCostValue", 175, IFC2X3_IfcAppliedValue_type);
    IFC2X3_IfcCurrencyRelationship_type = new entity("IfcCurrencyRelationship", 188, 0);
    IFC2X3_IfcCurveStyleFont_type = new entity("IfcCurveStyleFont", 198, 0);
    IFC2X3_IfcCurveStyleFontAndScaling_type = new entity("IfcCurveStyleFontAndScaling", 199, 0);
    IFC2X3_IfcCurveStyleFontPattern_type = new entity("IfcCurveStyleFontPattern", 200, 0);
    IFC2X3_IfcDateAndTime_type = new entity("IfcDateAndTime", 205, 0);
    IFC2X3_IfcDerivedUnit_type = new entity("IfcDerivedUnit", 213, 0);
    IFC2X3_IfcDerivedUnitElement_type = new entity("IfcDerivedUnitElement", 214, 0);
    IFC2X3_IfcDimensionalExponents_type = new entity("IfcDimensionalExponents", 218, 0);
    IFC2X3_IfcDocumentElectronicFormat_type = new entity("IfcDocumentElectronicFormat", 241, 0);
    IFC2X3_IfcDocumentInformation_type = new entity("IfcDocumentInformation", 242, 0);
    IFC2X3_IfcDocumentInformationRelationship_type = new entity("IfcDocumentInformationRelationship", 243, 0);
    IFC2X3_IfcDraughtingCalloutRelationship_type = new entity("IfcDraughtingCalloutRelationship", 258, 0);
    IFC2X3_IfcEnvironmentalImpactValue_type = new entity("IfcEnvironmentalImpactValue", 314, IFC2X3_IfcAppliedValue_type);
    IFC2X3_IfcExternalReference_type = new entity("IfcExternalReference", 326, 0);
    IFC2X3_IfcExternallyDefinedHatchStyle_type = new entity("IfcExternallyDefinedHatchStyle", 322, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcExternallyDefinedSurfaceStyle_type = new entity("IfcExternallyDefinedSurfaceStyle", 323, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcExternallyDefinedSymbol_type = new entity("IfcExternallyDefinedSymbol", 324, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcExternallyDefinedTextFont_type = new entity("IfcExternallyDefinedTextFont", 325, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcGridAxis_type = new entity("IfcGridAxis", 399, 0);
    IFC2X3_IfcIrregularTimeSeriesValue_type = new entity("IfcIrregularTimeSeriesValue", 423, 0);
    IFC2X3_IfcLibraryInformation_type = new entity("IfcLibraryInformation", 436, 0);
    IFC2X3_IfcLibraryReference_type = new entity("IfcLibraryReference", 437, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcLightDistributionData_type = new entity("IfcLightDistributionData", 440, 0);
    IFC2X3_IfcLightIntensityDistribution_type = new entity("IfcLightIntensityDistribution", 445, 0);
    IFC2X3_IfcLocalTime_type = new entity("IfcLocalTime", 460, 0);
    IFC2X3_IfcMaterial_type = new entity("IfcMaterial", 476, 0);
    IFC2X3_IfcMaterialClassificationRelationship_type = new entity("IfcMaterialClassificationRelationship", 477, 0);
    IFC2X3_IfcMaterialLayer_type = new entity("IfcMaterialLayer", 479, 0);
    IFC2X3_IfcMaterialLayerSet_type = new entity("IfcMaterialLayerSet", 480, 0);
    IFC2X3_IfcMaterialLayerSetUsage_type = new entity("IfcMaterialLayerSetUsage", 481, 0);
    IFC2X3_IfcMaterialList_type = new entity("IfcMaterialList", 482, 0);
    IFC2X3_IfcMaterialProperties_type = new entity("IfcMaterialProperties", 483, 0);
    IFC2X3_IfcMeasureWithUnit_type = new entity("IfcMeasureWithUnit", 486, 0);
    IFC2X3_IfcMechanicalMaterialProperties_type = new entity("IfcMechanicalMaterialProperties", 490, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcMechanicalSteelMaterialProperties_type = new entity("IfcMechanicalSteelMaterialProperties", 491, IFC2X3_IfcMechanicalMaterialProperties_type);
    IFC2X3_IfcMetric_type = new entity("IfcMetric", 495, IFC2X3_IfcConstraint_type);
    IFC2X3_IfcMonetaryUnit_type = new entity("IfcMonetaryUnit", 506, 0);
    IFC2X3_IfcNamedUnit_type = new entity("IfcNamedUnit", 511, 0);
    IFC2X3_IfcObjectPlacement_type = new entity("IfcObjectPlacement", 519, 0);
    IFC2X3_IfcObjective_type = new entity("IfcObjective", 517, IFC2X3_IfcConstraint_type);
    IFC2X3_IfcOpticalMaterialProperties_type = new entity("IfcOpticalMaterialProperties", 529, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcOrganization_type = new entity("IfcOrganization", 531, 0);
    IFC2X3_IfcOrganizationRelationship_type = new entity("IfcOrganizationRelationship", 532, 0);
    IFC2X3_IfcOwnerHistory_type = new entity("IfcOwnerHistory", 537, 0);
    IFC2X3_IfcPerson_type = new entity("IfcPerson", 545, 0);
    IFC2X3_IfcPersonAndOrganization_type = new entity("IfcPersonAndOrganization", 546, 0);
    IFC2X3_IfcPhysicalQuantity_type = new entity("IfcPhysicalQuantity", 550, 0);
    IFC2X3_IfcPhysicalSimpleQuantity_type = new entity("IfcPhysicalSimpleQuantity", 551, IFC2X3_IfcPhysicalQuantity_type);
    IFC2X3_IfcPostalAddress_type = new entity("IfcPostalAddress", 580, IFC2X3_IfcAddress_type);
    IFC2X3_IfcPreDefinedItem_type = new entity("IfcPreDefinedItem", 585, 0);
    IFC2X3_IfcPreDefinedSymbol_type = new entity("IfcPreDefinedSymbol", 587, IFC2X3_IfcPreDefinedItem_type);
    IFC2X3_IfcPreDefinedTerminatorSymbol_type = new entity("IfcPreDefinedTerminatorSymbol", 588, IFC2X3_IfcPreDefinedSymbol_type);
    IFC2X3_IfcPreDefinedTextFont_type = new entity("IfcPreDefinedTextFont", 589, IFC2X3_IfcPreDefinedItem_type);
    IFC2X3_IfcPresentationLayerAssignment_type = new entity("IfcPresentationLayerAssignment", 591, 0);
    IFC2X3_IfcPresentationLayerWithStyle_type = new entity("IfcPresentationLayerWithStyle", 592, IFC2X3_IfcPresentationLayerAssignment_type);
    IFC2X3_IfcPresentationStyle_type = new entity("IfcPresentationStyle", 593, 0);
    IFC2X3_IfcPresentationStyleAssignment_type = new entity("IfcPresentationStyleAssignment", 594, 0);
    IFC2X3_IfcProductRepresentation_type = new entity("IfcProductRepresentation", 602, 0);
    IFC2X3_IfcProductsOfCombustionProperties_type = new entity("IfcProductsOfCombustionProperties", 603, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcProfileDef_type = new entity("IfcProfileDef", 604, 0);
    IFC2X3_IfcProfileProperties_type = new entity("IfcProfileProperties", 605, 0);
    IFC2X3_IfcProperty_type = new entity("IfcProperty", 615, 0);
    IFC2X3_IfcPropertyConstraintRelationship_type = new entity("IfcPropertyConstraintRelationship", 617, 0);
    IFC2X3_IfcPropertyDependencyRelationship_type = new entity("IfcPropertyDependencyRelationship", 619, 0);
    IFC2X3_IfcPropertyEnumeration_type = new entity("IfcPropertyEnumeration", 621, 0);
    IFC2X3_IfcQuantityArea_type = new entity("IfcQuantityArea", 634, IFC2X3_IfcPhysicalSimpleQuantity_type);
    IFC2X3_IfcQuantityCount_type = new entity("IfcQuantityCount", 635, IFC2X3_IfcPhysicalSimpleQuantity_type);
    IFC2X3_IfcQuantityLength_type = new entity("IfcQuantityLength", 636, IFC2X3_IfcPhysicalSimpleQuantity_type);
    IFC2X3_IfcQuantityTime_type = new entity("IfcQuantityTime", 637, IFC2X3_IfcPhysicalSimpleQuantity_type);
    IFC2X3_IfcQuantityVolume_type = new entity("IfcQuantityVolume", 638, IFC2X3_IfcPhysicalSimpleQuantity_type);
    IFC2X3_IfcQuantityWeight_type = new entity("IfcQuantityWeight", 639, IFC2X3_IfcPhysicalSimpleQuantity_type);
    IFC2X3_IfcReferencesValueDocument_type = new entity("IfcReferencesValueDocument", 657, 0);
    IFC2X3_IfcReinforcementBarProperties_type = new entity("IfcReinforcementBarProperties", 660, 0);
    IFC2X3_IfcRelaxation_type = new entity("IfcRelaxation", 687, 0);
    IFC2X3_IfcRepresentation_type = new entity("IfcRepresentation", 718, 0);
    IFC2X3_IfcRepresentationContext_type = new entity("IfcRepresentationContext", 719, 0);
    IFC2X3_IfcRepresentationItem_type = new entity("IfcRepresentationItem", 720, 0);
    IFC2X3_IfcRepresentationMap_type = new entity("IfcRepresentationMap", 721, 0);
    IFC2X3_IfcRibPlateProfileProperties_type = new entity("IfcRibPlateProfileProperties", 726, IFC2X3_IfcProfileProperties_type);
    IFC2X3_IfcRoot_type = new entity("IfcRoot", 732, 0);
    IFC2X3_IfcSIUnit_type = new entity("IfcSIUnit", 765, IFC2X3_IfcNamedUnit_type);
    IFC2X3_IfcSectionProperties_type = new entity("IfcSectionProperties", 745, 0);
    IFC2X3_IfcSectionReinforcementProperties_type = new entity("IfcSectionReinforcementProperties", 746, 0);
    IFC2X3_IfcShapeAspect_type = new entity("IfcShapeAspect", 755, 0);
    IFC2X3_IfcShapeModel_type = new entity("IfcShapeModel", 756, IFC2X3_IfcRepresentation_type);
    IFC2X3_IfcShapeRepresentation_type = new entity("IfcShapeRepresentation", 757, IFC2X3_IfcShapeModel_type);
    IFC2X3_IfcSimpleProperty_type = new entity("IfcSimpleProperty", 761, IFC2X3_IfcProperty_type);
    IFC2X3_IfcStructuralConnectionCondition_type = new entity("IfcStructuralConnectionCondition", 806, 0);
    IFC2X3_IfcStructuralLoad_type = new entity("IfcStructuralLoad", 814, 0);
    IFC2X3_IfcStructuralLoadStatic_type = new entity("IfcStructuralLoadStatic", 822, IFC2X3_IfcStructuralLoad_type);
    IFC2X3_IfcStructuralLoadTemperature_type = new entity("IfcStructuralLoadTemperature", 823, IFC2X3_IfcStructuralLoadStatic_type);
    IFC2X3_IfcStyleModel_type = new entity("IfcStyleModel", 841, IFC2X3_IfcRepresentation_type);
    IFC2X3_IfcStyledItem_type = new entity("IfcStyledItem", 839, IFC2X3_IfcRepresentationItem_type);
    IFC2X3_IfcStyledRepresentation_type = new entity("IfcStyledRepresentation", 840, IFC2X3_IfcStyleModel_type);
    IFC2X3_IfcSurfaceStyle_type = new entity("IfcSurfaceStyle", 850, IFC2X3_IfcPresentationStyle_type);
    IFC2X3_IfcSurfaceStyleLighting_type = new entity("IfcSurfaceStyleLighting", 852, 0);
    IFC2X3_IfcSurfaceStyleRefraction_type = new entity("IfcSurfaceStyleRefraction", 853, 0);
    IFC2X3_IfcSurfaceStyleShading_type = new entity("IfcSurfaceStyleShading", 855, 0);
    IFC2X3_IfcSurfaceStyleWithTextures_type = new entity("IfcSurfaceStyleWithTextures", 856, 0);
    IFC2X3_IfcSurfaceTexture_type = new entity("IfcSurfaceTexture", 857, 0);
    IFC2X3_IfcSymbolStyle_type = new entity("IfcSymbolStyle", 864, IFC2X3_IfcPresentationStyle_type);
    IFC2X3_IfcTable_type = new entity("IfcTable", 868, 0);
    IFC2X3_IfcTableRow_type = new entity("IfcTableRow", 869, 0);
    IFC2X3_IfcTelecomAddress_type = new entity("IfcTelecomAddress", 873, IFC2X3_IfcAddress_type);
    IFC2X3_IfcTextStyle_type = new entity("IfcTextStyle", 887, IFC2X3_IfcPresentationStyle_type);
    IFC2X3_IfcTextStyleFontModel_type = new entity("IfcTextStyleFontModel", 888, IFC2X3_IfcPreDefinedTextFont_type);
    IFC2X3_IfcTextStyleForDefinedFont_type = new entity("IfcTextStyleForDefinedFont", 889, 0);
    IFC2X3_IfcTextStyleTextModel_type = new entity("IfcTextStyleTextModel", 891, 0);
    IFC2X3_IfcTextStyleWithBoxCharacteristics_type = new entity("IfcTextStyleWithBoxCharacteristics", 892, 0);
    IFC2X3_IfcTextureCoordinate_type = new entity("IfcTextureCoordinate", 894, 0);
    IFC2X3_IfcTextureCoordinateGenerator_type = new entity("IfcTextureCoordinateGenerator", 895, IFC2X3_IfcTextureCoordinate_type);
    IFC2X3_IfcTextureMap_type = new entity("IfcTextureMap", 896, IFC2X3_IfcTextureCoordinate_type);
    IFC2X3_IfcTextureVertex_type = new entity("IfcTextureVertex", 897, 0);
    IFC2X3_IfcThermalMaterialProperties_type = new entity("IfcThermalMaterialProperties", 903, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcTimeSeries_type = new entity("IfcTimeSeries", 908, 0);
    IFC2X3_IfcTimeSeriesReferenceRelationship_type = new entity("IfcTimeSeriesReferenceRelationship", 910, 0);
    IFC2X3_IfcTimeSeriesValue_type = new entity("IfcTimeSeriesValue", 913, 0);
    IFC2X3_IfcTopologicalRepresentationItem_type = new entity("IfcTopologicalRepresentationItem", 915, IFC2X3_IfcRepresentationItem_type);
    IFC2X3_IfcTopologyRepresentation_type = new entity("IfcTopologyRepresentation", 916, IFC2X3_IfcShapeModel_type);
    IFC2X3_IfcUnitAssignment_type = new entity("IfcUnitAssignment", 937, 0);
    IFC2X3_IfcVertex_type = new entity("IfcVertex", 946, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcVertexBasedTextureMap_type = new entity("IfcVertexBasedTextureMap", 947, 0);
    IFC2X3_IfcVertexPoint_type = new entity("IfcVertexPoint", 949, IFC2X3_IfcVertex_type);
    IFC2X3_IfcVirtualGridIntersection_type = new entity("IfcVirtualGridIntersection", 953, 0);
    IFC2X3_IfcWaterProperties_type = new entity("IfcWaterProperties", 964, IFC2X3_IfcMaterialProperties_type);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcOrganization_type);
        items.push_back(IFC2X3_IfcPerson_type);
        items.push_back(IFC2X3_IfcPersonAndOrganization_type);
        IFC2X3_IfcActorSelect_type = new select_type("IfcActorSelect", 8, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcMeasureWithUnit_type);
        items.push_back(IFC2X3_IfcMonetaryMeasure_type);
        items.push_back(IFC2X3_IfcRatioMeasure_type);
        IFC2X3_IfcAppliedValueSelect_type = new select_type("IfcAppliedValueSelect", 39, items);
    }
    IFC2X3_IfcBoxAlignment_type = new type_declaration("IfcBoxAlignment", 78, new named_type(IFC2X3_IfcLabel_type));
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IFC2X3_IfcTextStyleForDefinedFont_type);
        IFC2X3_IfcCharacterStyleSelect_type = new select_type("IfcCharacterStyleSelect", 107, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcLabel_type);
        items.push_back(IFC2X3_IfcMeasureWithUnit_type);
        IFC2X3_IfcConditionCriterionSelect_type = new select_type("IfcConditionCriterionSelect", 142, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcCalendarDate_type);
        items.push_back(IFC2X3_IfcDateAndTime_type);
        items.push_back(IFC2X3_IfcLocalTime_type);
        IFC2X3_IfcDateTimeSelect_type = new select_type("IfcDateTimeSelect", 206, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcExternallyDefinedSymbol_type);
        items.push_back(IFC2X3_IfcPreDefinedSymbol_type);
        IFC2X3_IfcDefinedSymbolSelect_type = new select_type("IfcDefinedSymbolSelect", 210, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(68);
        items.push_back(IFC2X3_IfcAbsorbedDoseMeasure_type);
        items.push_back(IFC2X3_IfcAccelerationMeasure_type);
        items.push_back(IFC2X3_IfcAngularVelocityMeasure_type);
        items.push_back(IFC2X3_IfcCompoundPlaneAngleMeasure_type);
        items.push_back(IFC2X3_IfcCurvatureMeasure_type);
        items.push_back(IFC2X3_IfcDoseEquivalentMeasure_type);
        items.push_back(IFC2X3_IfcDynamicViscosityMeasure_type);
        items.push_back(IFC2X3_IfcElectricCapacitanceMeasure_type);
        items.push_back(IFC2X3_IfcElectricChargeMeasure_type);
        items.push_back(IFC2X3_IfcElectricConductanceMeasure_type);
        items.push_back(IFC2X3_IfcElectricResistanceMeasure_type);
        items.push_back(IFC2X3_IfcElectricVoltageMeasure_type);
        items.push_back(IFC2X3_IfcEnergyMeasure_type);
        items.push_back(IFC2X3_IfcForceMeasure_type);
        items.push_back(IFC2X3_IfcFrequencyMeasure_type);
        items.push_back(IFC2X3_IfcHeatFluxDensityMeasure_type);
        items.push_back(IFC2X3_IfcHeatingValueMeasure_type);
        items.push_back(IFC2X3_IfcIlluminanceMeasure_type);
        items.push_back(IFC2X3_IfcInductanceMeasure_type);
        items.push_back(IFC2X3_IfcIntegerCountRateMeasure_type);
        items.push_back(IFC2X3_IfcIonConcentrationMeasure_type);
        items.push_back(IFC2X3_IfcIsothermalMoistureCapacityMeasure_type);
        items.push_back(IFC2X3_IfcKinematicViscosityMeasure_type);
        items.push_back(IFC2X3_IfcLinearForceMeasure_type);
        items.push_back(IFC2X3_IfcLinearMomentMeasure_type);
        items.push_back(IFC2X3_IfcLinearStiffnessMeasure_type);
        items.push_back(IFC2X3_IfcLinearVelocityMeasure_type);
        items.push_back(IFC2X3_IfcLuminousFluxMeasure_type);
        items.push_back(IFC2X3_IfcLuminousIntensityDistributionMeasure_type);
        items.push_back(IFC2X3_IfcMagneticFluxDensityMeasure_type);
        items.push_back(IFC2X3_IfcMagneticFluxMeasure_type);
        items.push_back(IFC2X3_IfcMassDensityMeasure_type);
        items.push_back(IFC2X3_IfcMassFlowRateMeasure_type);
        items.push_back(IFC2X3_IfcMassPerLengthMeasure_type);
        items.push_back(IFC2X3_IfcModulusOfElasticityMeasure_type);
        items.push_back(IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type);
        items.push_back(IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type);
        items.push_back(IFC2X3_IfcModulusOfSubgradeReactionMeasure_type);
        items.push_back(IFC2X3_IfcMoistureDiffusivityMeasure_type);
        items.push_back(IFC2X3_IfcMolecularWeightMeasure_type);
        items.push_back(IFC2X3_IfcMomentOfInertiaMeasure_type);
        items.push_back(IFC2X3_IfcMonetaryMeasure_type);
        items.push_back(IFC2X3_IfcPHMeasure_type);
        items.push_back(IFC2X3_IfcPlanarForceMeasure_type);
        items.push_back(IFC2X3_IfcPowerMeasure_type);
        items.push_back(IFC2X3_IfcPressureMeasure_type);
        items.push_back(IFC2X3_IfcRadioActivityMeasure_type);
        items.push_back(IFC2X3_IfcRotationalFrequencyMeasure_type);
        items.push_back(IFC2X3_IfcRotationalMassMeasure_type);
        items.push_back(IFC2X3_IfcRotationalStiffnessMeasure_type);
        items.push_back(IFC2X3_IfcSectionModulusMeasure_type);
        items.push_back(IFC2X3_IfcSectionalAreaIntegralMeasure_type);
        items.push_back(IFC2X3_IfcShearModulusMeasure_type);
        items.push_back(IFC2X3_IfcSoundPowerMeasure_type);
        items.push_back(IFC2X3_IfcSoundPressureMeasure_type);
        items.push_back(IFC2X3_IfcSpecificHeatCapacityMeasure_type);
        items.push_back(IFC2X3_IfcTemperatureGradientMeasure_type);
        items.push_back(IFC2X3_IfcThermalAdmittanceMeasure_type);
        items.push_back(IFC2X3_IfcThermalConductivityMeasure_type);
        items.push_back(IFC2X3_IfcThermalExpansionCoefficientMeasure_type);
        items.push_back(IFC2X3_IfcThermalResistanceMeasure_type);
        items.push_back(IFC2X3_IfcThermalTransmittanceMeasure_type);
        items.push_back(IFC2X3_IfcTimeStamp_type);
        items.push_back(IFC2X3_IfcTorqueMeasure_type);
        items.push_back(IFC2X3_IfcVaporPermeabilityMeasure_type);
        items.push_back(IFC2X3_IfcVolumetricFlowRateMeasure_type);
        items.push_back(IFC2X3_IfcWarpingConstantMeasure_type);
        items.push_back(IFC2X3_IfcWarpingMomentMeasure_type);
        IFC2X3_IfcDerivedMeasureValue_type = new select_type("IfcDerivedMeasureValue", 211, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcRepresentation_type);
        items.push_back(IFC2X3_IfcRepresentationItem_type);
        IFC2X3_IfcLayeredItem_type = new select_type("IfcLayeredItem", 433, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcLibraryInformation_type);
        items.push_back(IFC2X3_IfcLibraryReference_type);
        IFC2X3_IfcLibrarySelect_type = new select_type("IfcLibrarySelect", 438, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcExternalReference_type);
        items.push_back(IFC2X3_IfcLightIntensityDistribution_type);
        IFC2X3_IfcLightDistributionDataSourceSelect_type = new select_type("IfcLightDistributionDataSourceSelect", 441, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC2X3_IfcMaterial_type);
        items.push_back(IFC2X3_IfcMaterialLayer_type);
        items.push_back(IFC2X3_IfcMaterialLayerSet_type);
        items.push_back(IFC2X3_IfcMaterialLayerSetUsage_type);
        items.push_back(IFC2X3_IfcMaterialList_type);
        IFC2X3_IfcMaterialSelect_type = new select_type("IfcMaterialSelect", 484, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC2X3_IfcCostValue_type);
        items.push_back(IFC2X3_IfcDateTimeSelect_type);
        items.push_back(IFC2X3_IfcMeasureWithUnit_type);
        items.push_back(IFC2X3_IfcTable_type);
        items.push_back(IFC2X3_IfcText_type);
        items.push_back(IFC2X3_IfcTimeSeries_type);
        IFC2X3_IfcMetricValueSelect_type = new select_type("IfcMetricValueSelect", 496, items);
    }
    IFC2X3_IfcNormalisedRatioMeasure_type = new type_declaration("IfcNormalisedRatioMeasure", 512, new named_type(IFC2X3_IfcRatioMeasure_type));
    {
        std::vector<const declaration*> items; items.reserve(13);
        items.push_back(IFC2X3_IfcAddress_type);
        items.push_back(IFC2X3_IfcAppliedValue_type);
        items.push_back(IFC2X3_IfcCalendarDate_type);
        items.push_back(IFC2X3_IfcDateAndTime_type);
        items.push_back(IFC2X3_IfcExternalReference_type);
        items.push_back(IFC2X3_IfcLocalTime_type);
        items.push_back(IFC2X3_IfcMaterial_type);
        items.push_back(IFC2X3_IfcMaterialLayer_type);
        items.push_back(IFC2X3_IfcMaterialList_type);
        items.push_back(IFC2X3_IfcOrganization_type);
        items.push_back(IFC2X3_IfcPerson_type);
        items.push_back(IFC2X3_IfcPersonAndOrganization_type);
        items.push_back(IFC2X3_IfcTimeSeries_type);
        IFC2X3_IfcObjectReferenceSelect_type = new select_type("IfcObjectReferenceSelect", 520, items);
    }
    IFC2X3_IfcPositiveRatioMeasure_type = new type_declaration("IfcPositiveRatioMeasure", 579, new named_type(IFC2X3_IfcRatioMeasure_type));
    {
        std::vector<const declaration*> items; items.reserve(7);
        items.push_back(IFC2X3_IfcBoolean_type);
        items.push_back(IFC2X3_IfcIdentifier_type);
        items.push_back(IFC2X3_IfcInteger_type);
        items.push_back(IFC2X3_IfcLabel_type);
        items.push_back(IFC2X3_IfcLogical_type);
        items.push_back(IFC2X3_IfcReal_type);
        items.push_back(IFC2X3_IfcText_type);
        IFC2X3_IfcSimpleValue_type = new select_type("IfcSimpleValue", 762, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC2X3_IfcDescriptiveMeasure_type);
        items.push_back(IFC2X3_IfcLengthMeasure_type);
        items.push_back(IFC2X3_IfcNormalisedRatioMeasure_type);
        items.push_back(IFC2X3_IfcPositiveLengthMeasure_type);
        items.push_back(IFC2X3_IfcPositiveRatioMeasure_type);
        items.push_back(IFC2X3_IfcRatioMeasure_type);
        IFC2X3_IfcSizeSelect_type = new select_type("IfcSizeSelect", 767, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcSpecularExponent_type);
        items.push_back(IFC2X3_IfcSpecularRoughness_type);
        IFC2X3_IfcSpecularHighlightSelect_type = new select_type("IfcSpecularHighlightSelect", 790, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC2X3_IfcExternallyDefinedSurfaceStyle_type);
        items.push_back(IFC2X3_IfcSurfaceStyleLighting_type);
        items.push_back(IFC2X3_IfcSurfaceStyleRefraction_type);
        items.push_back(IFC2X3_IfcSurfaceStyleShading_type);
        items.push_back(IFC2X3_IfcSurfaceStyleWithTextures_type);
        IFC2X3_IfcSurfaceStyleElementSelect_type = new select_type("IfcSurfaceStyleElementSelect", 851, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcExternallyDefinedTextFont_type);
        items.push_back(IFC2X3_IfcPreDefinedTextFont_type);
        IFC2X3_IfcTextFontSelect_type = new select_type("IfcTextFontSelect", 883, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcTextStyleTextModel_type);
        items.push_back(IFC2X3_IfcTextStyleWithBoxCharacteristics_type);
        IFC2X3_IfcTextStyleSelect_type = new select_type("IfcTextStyleSelect", 890, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcDerivedUnit_type);
        items.push_back(IFC2X3_IfcMonetaryUnit_type);
        items.push_back(IFC2X3_IfcNamedUnit_type);
        IFC2X3_IfcUnit_type = new select_type("IfcUnit", 934, items);
    }
    IFC2X3_IfcAnnotationOccurrence_type = new entity("IfcAnnotationOccurrence", 31, IFC2X3_IfcStyledItem_type);
    IFC2X3_IfcAnnotationSurfaceOccurrence_type = new entity("IfcAnnotationSurfaceOccurrence", 33, IFC2X3_IfcAnnotationOccurrence_type);
    IFC2X3_IfcAnnotationSymbolOccurrence_type = new entity("IfcAnnotationSymbolOccurrence", 34, IFC2X3_IfcAnnotationOccurrence_type);
    IFC2X3_IfcAnnotationTextOccurrence_type = new entity("IfcAnnotationTextOccurrence", 35, IFC2X3_IfcAnnotationOccurrence_type);
    IFC2X3_IfcArbitraryClosedProfileDef_type = new entity("IfcArbitraryClosedProfileDef", 44, IFC2X3_IfcProfileDef_type);
    IFC2X3_IfcArbitraryOpenProfileDef_type = new entity("IfcArbitraryOpenProfileDef", 45, IFC2X3_IfcProfileDef_type);
    IFC2X3_IfcArbitraryProfileDefWithVoids_type = new entity("IfcArbitraryProfileDefWithVoids", 46, IFC2X3_IfcArbitraryClosedProfileDef_type);
    IFC2X3_IfcBlobTexture_type = new entity("IfcBlobTexture", 61, IFC2X3_IfcSurfaceTexture_type);
    IFC2X3_IfcCenterLineProfileDef_type = new entity("IfcCenterLineProfileDef", 104, IFC2X3_IfcArbitraryOpenProfileDef_type);
    IFC2X3_IfcClassificationReference_type = new entity("IfcClassificationReference", 119, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcColourRgb_type = new entity("IfcColourRgb", 125, IFC2X3_IfcColourSpecification_type);
    IFC2X3_IfcComplexProperty_type = new entity("IfcComplexProperty", 131, IFC2X3_IfcProperty_type);
    IFC2X3_IfcCompositeProfileDef_type = new entity("IfcCompositeProfileDef", 134, IFC2X3_IfcProfileDef_type);
    IFC2X3_IfcConnectedFaceSet_type = new entity("IfcConnectedFaceSet", 144, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcConnectionCurveGeometry_type = new entity("IfcConnectionCurveGeometry", 145, IFC2X3_IfcConnectionGeometry_type);
    IFC2X3_IfcConnectionPointEccentricity_type = new entity("IfcConnectionPointEccentricity", 147, IFC2X3_IfcConnectionPointGeometry_type);
    IFC2X3_IfcContextDependentUnit_type = new entity("IfcContextDependentUnit", 162, IFC2X3_IfcNamedUnit_type);
    IFC2X3_IfcConversionBasedUnit_type = new entity("IfcConversionBasedUnit", 166, IFC2X3_IfcNamedUnit_type);
    IFC2X3_IfcCurveStyle_type = new entity("IfcCurveStyle", 197, IFC2X3_IfcPresentationStyle_type);
    IFC2X3_IfcDerivedProfileDef_type = new entity("IfcDerivedProfileDef", 212, IFC2X3_IfcProfileDef_type);
    IFC2X3_IfcDimensionCalloutRelationship_type = new entity("IfcDimensionCalloutRelationship", 219, IFC2X3_IfcDraughtingCalloutRelationship_type);
    IFC2X3_IfcDimensionPair_type = new entity("IfcDimensionPair", 225, IFC2X3_IfcDraughtingCalloutRelationship_type);
    IFC2X3_IfcDocumentReference_type = new entity("IfcDocumentReference", 244, IFC2X3_IfcExternalReference_type);
    IFC2X3_IfcDraughtingPreDefinedTextFont_type = new entity("IfcDraughtingPreDefinedTextFont", 261, IFC2X3_IfcPreDefinedTextFont_type);
    IFC2X3_IfcEdge_type = new entity("IfcEdge", 269, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcEdgeCurve_type = new entity("IfcEdgeCurve", 270, IFC2X3_IfcEdge_type);
    IFC2X3_IfcExtendedMaterialProperties_type = new entity("IfcExtendedMaterialProperties", 321, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcFace_type = new entity("IfcFace", 328, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcFaceBound_type = new entity("IfcFaceBound", 330, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcFaceOuterBound_type = new entity("IfcFaceOuterBound", 331, IFC2X3_IfcFaceBound_type);
    IFC2X3_IfcFaceSurface_type = new entity("IfcFaceSurface", 332, IFC2X3_IfcFace_type);
    IFC2X3_IfcFailureConnectionCondition_type = new entity("IfcFailureConnectionCondition", 335, IFC2X3_IfcStructuralConnectionCondition_type);
    IFC2X3_IfcFillAreaStyle_type = new entity("IfcFillAreaStyle", 343, IFC2X3_IfcPresentationStyle_type);
    IFC2X3_IfcFuelProperties_type = new entity("IfcFuelProperties", 380, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcGeneralMaterialProperties_type = new entity("IfcGeneralMaterialProperties", 387, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcGeneralProfileProperties_type = new entity("IfcGeneralProfileProperties", 388, IFC2X3_IfcProfileProperties_type);
    IFC2X3_IfcGeometricRepresentationContext_type = new entity("IfcGeometricRepresentationContext", 391, IFC2X3_IfcRepresentationContext_type);
    IFC2X3_IfcGeometricRepresentationItem_type = new entity("IfcGeometricRepresentationItem", 392, IFC2X3_IfcRepresentationItem_type);
    IFC2X3_IfcGeometricRepresentationSubContext_type = new entity("IfcGeometricRepresentationSubContext", 393, IFC2X3_IfcGeometricRepresentationContext_type);
    IFC2X3_IfcGeometricSet_type = new entity("IfcGeometricSet", 394, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcGridPlacement_type = new entity("IfcGridPlacement", 400, IFC2X3_IfcObjectPlacement_type);
    IFC2X3_IfcHalfSpaceSolid_type = new entity("IfcHalfSpaceSolid", 402, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcHygroscopicMaterialProperties_type = new entity("IfcHygroscopicMaterialProperties", 411, IFC2X3_IfcMaterialProperties_type);
    IFC2X3_IfcImageTexture_type = new entity("IfcImageTexture", 414, IFC2X3_IfcSurfaceTexture_type);
    IFC2X3_IfcIrregularTimeSeries_type = new entity("IfcIrregularTimeSeries", 422, IFC2X3_IfcTimeSeries_type);
    IFC2X3_IfcLightSource_type = new entity("IfcLightSource", 446, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcLightSourceAmbient_type = new entity("IfcLightSourceAmbient", 447, IFC2X3_IfcLightSource_type);
    IFC2X3_IfcLightSourceDirectional_type = new entity("IfcLightSourceDirectional", 448, IFC2X3_IfcLightSource_type);
    IFC2X3_IfcLightSourceGoniometric_type = new entity("IfcLightSourceGoniometric", 449, IFC2X3_IfcLightSource_type);
    IFC2X3_IfcLightSourcePositional_type = new entity("IfcLightSourcePositional", 450, IFC2X3_IfcLightSource_type);
    IFC2X3_IfcLightSourceSpot_type = new entity("IfcLightSourceSpot", 451, IFC2X3_IfcLightSourcePositional_type);
    IFC2X3_IfcLocalPlacement_type = new entity("IfcLocalPlacement", 459, IFC2X3_IfcObjectPlacement_type);
    IFC2X3_IfcLoop_type = new entity("IfcLoop", 463, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcMappedItem_type = new entity("IfcMappedItem", 471, IFC2X3_IfcRepresentationItem_type);
    IFC2X3_IfcMaterialDefinitionRepresentation_type = new entity("IfcMaterialDefinitionRepresentation", 478, IFC2X3_IfcProductRepresentation_type);
    IFC2X3_IfcMechanicalConcreteMaterialProperties_type = new entity("IfcMechanicalConcreteMaterialProperties", 487, IFC2X3_IfcMechanicalMaterialProperties_type);
    IFC2X3_IfcObjectDefinition_type = new entity("IfcObjectDefinition", 516, IFC2X3_IfcRoot_type);
    IFC2X3_IfcOneDirectionRepeatFactor_type = new entity("IfcOneDirectionRepeatFactor", 526, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcOpenShell_type = new entity("IfcOpenShell", 528, IFC2X3_IfcConnectedFaceSet_type);
    IFC2X3_IfcOrientedEdge_type = new entity("IfcOrientedEdge", 534, IFC2X3_IfcEdge_type);
    IFC2X3_IfcParameterizedProfileDef_type = new entity("IfcParameterizedProfileDef", 538, IFC2X3_IfcProfileDef_type);
    IFC2X3_IfcPath_type = new entity("IfcPath", 540, IFC2X3_IfcTopologicalRepresentationItem_type);
    IFC2X3_IfcPhysicalComplexQuantity_type = new entity("IfcPhysicalComplexQuantity", 548, IFC2X3_IfcPhysicalQuantity_type);
    IFC2X3_IfcPixelTexture_type = new entity("IfcPixelTexture", 559, IFC2X3_IfcSurfaceTexture_type);
    IFC2X3_IfcPlacement_type = new entity("IfcPlacement", 560, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcPlanarExtent_type = new entity("IfcPlanarExtent", 562, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcPoint_type = new entity("IfcPoint", 569, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcPointOnCurve_type = new entity("IfcPointOnCurve", 570, IFC2X3_IfcPoint_type);
    IFC2X3_IfcPointOnSurface_type = new entity("IfcPointOnSurface", 571, IFC2X3_IfcPoint_type);
    IFC2X3_IfcPolyLoop_type = new entity("IfcPolyLoop", 575, IFC2X3_IfcLoop_type);
    IFC2X3_IfcPolygonalBoundedHalfSpace_type = new entity("IfcPolygonalBoundedHalfSpace", 573, IFC2X3_IfcHalfSpaceSolid_type);
    IFC2X3_IfcPreDefinedColour_type = new entity("IfcPreDefinedColour", 582, IFC2X3_IfcPreDefinedItem_type);
    IFC2X3_IfcPreDefinedCurveFont_type = new entity("IfcPreDefinedCurveFont", 583, IFC2X3_IfcPreDefinedItem_type);
    IFC2X3_IfcPreDefinedDimensionSymbol_type = new entity("IfcPreDefinedDimensionSymbol", 584, IFC2X3_IfcPreDefinedSymbol_type);
    IFC2X3_IfcPreDefinedPointMarkerSymbol_type = new entity("IfcPreDefinedPointMarkerSymbol", 586, IFC2X3_IfcPreDefinedSymbol_type);
    IFC2X3_IfcProductDefinitionShape_type = new entity("IfcProductDefinitionShape", 601, IFC2X3_IfcProductRepresentation_type);
    IFC2X3_IfcPropertyBoundedValue_type = new entity("IfcPropertyBoundedValue", 616, IFC2X3_IfcSimpleProperty_type);
    IFC2X3_IfcPropertyDefinition_type = new entity("IfcPropertyDefinition", 618, IFC2X3_IfcRoot_type);
    IFC2X3_IfcPropertyEnumeratedValue_type = new entity("IfcPropertyEnumeratedValue", 620, IFC2X3_IfcSimpleProperty_type);
    IFC2X3_IfcPropertyListValue_type = new entity("IfcPropertyListValue", 622, IFC2X3_IfcSimpleProperty_type);
    IFC2X3_IfcPropertyReferenceValue_type = new entity("IfcPropertyReferenceValue", 623, IFC2X3_IfcSimpleProperty_type);
    IFC2X3_IfcPropertySetDefinition_type = new entity("IfcPropertySetDefinition", 625, IFC2X3_IfcPropertyDefinition_type);
    IFC2X3_IfcPropertySingleValue_type = new entity("IfcPropertySingleValue", 626, IFC2X3_IfcSimpleProperty_type);
    IFC2X3_IfcPropertyTableValue_type = new entity("IfcPropertyTableValue", 628, IFC2X3_IfcSimpleProperty_type);
    IFC2X3_IfcRectangleProfileDef_type = new entity("IfcRectangleProfileDef", 654, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcRegularTimeSeries_type = new entity("IfcRegularTimeSeries", 659, IFC2X3_IfcTimeSeries_type);
    IFC2X3_IfcReinforcementDefinitionProperties_type = new entity("IfcReinforcementDefinitionProperties", 661, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcRelationship_type = new entity("IfcRelationship", 686, IFC2X3_IfcRoot_type);
    IFC2X3_IfcRoundedRectangleProfileDef_type = new entity("IfcRoundedRectangleProfileDef", 737, IFC2X3_IfcRectangleProfileDef_type);
    IFC2X3_IfcSectionedSpine_type = new entity("IfcSectionedSpine", 743, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcServiceLifeFactor_type = new entity("IfcServiceLifeFactor", 752, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcShellBasedSurfaceModel_type = new entity("IfcShellBasedSurfaceModel", 760, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcSlippageConnectionCondition_type = new entity("IfcSlippageConnectionCondition", 771, IFC2X3_IfcStructuralConnectionCondition_type);
    IFC2X3_IfcSolidModel_type = new entity("IfcSolidModel", 773, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcSoundProperties_type = new entity("IfcSoundProperties", 776, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcSoundValue_type = new entity("IfcSoundValue", 778, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcSpaceThermalLoadProperties_type = new entity("IfcSpaceThermalLoadProperties", 783, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcStructuralLoadLinearForce_type = new entity("IfcStructuralLoadLinearForce", 816, IFC2X3_IfcStructuralLoadStatic_type);
    IFC2X3_IfcStructuralLoadPlanarForce_type = new entity("IfcStructuralLoadPlanarForce", 817, IFC2X3_IfcStructuralLoadStatic_type);
    IFC2X3_IfcStructuralLoadSingleDisplacement_type = new entity("IfcStructuralLoadSingleDisplacement", 818, IFC2X3_IfcStructuralLoadStatic_type);
    IFC2X3_IfcStructuralLoadSingleDisplacementDistortion_type = new entity("IfcStructuralLoadSingleDisplacementDistortion", 819, IFC2X3_IfcStructuralLoadSingleDisplacement_type);
    IFC2X3_IfcStructuralLoadSingleForce_type = new entity("IfcStructuralLoadSingleForce", 820, IFC2X3_IfcStructuralLoadStatic_type);
    IFC2X3_IfcStructuralLoadSingleForceWarping_type = new entity("IfcStructuralLoadSingleForceWarping", 821, IFC2X3_IfcStructuralLoadSingleForce_type);
    IFC2X3_IfcStructuralProfileProperties_type = new entity("IfcStructuralProfileProperties", 830, IFC2X3_IfcGeneralProfileProperties_type);
    IFC2X3_IfcStructuralSteelProfileProperties_type = new entity("IfcStructuralSteelProfileProperties", 833, IFC2X3_IfcStructuralProfileProperties_type);
    IFC2X3_IfcSubedge_type = new entity("IfcSubedge", 843, IFC2X3_IfcEdge_type);
    IFC2X3_IfcSurface_type = new entity("IfcSurface", 844, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcSurfaceStyleRendering_type = new entity("IfcSurfaceStyleRendering", 854, IFC2X3_IfcSurfaceStyleShading_type);
    IFC2X3_IfcSweptAreaSolid_type = new entity("IfcSweptAreaSolid", 859, IFC2X3_IfcSolidModel_type);
    IFC2X3_IfcSweptDiskSolid_type = new entity("IfcSweptDiskSolid", 860, IFC2X3_IfcSolidModel_type);
    IFC2X3_IfcSweptSurface_type = new entity("IfcSweptSurface", 861, IFC2X3_IfcSurface_type);
    IFC2X3_IfcTShapeProfileDef_type = new entity("IfcTShapeProfileDef", 928, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcTerminatorSymbol_type = new entity("IfcTerminatorSymbol", 878, IFC2X3_IfcAnnotationSymbolOccurrence_type);
    IFC2X3_IfcTextLiteral_type = new entity("IfcTextLiteral", 884, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcTextLiteralWithExtent_type = new entity("IfcTextLiteralWithExtent", 885, IFC2X3_IfcTextLiteral_type);
    IFC2X3_IfcTrapeziumProfileDef_type = new entity("IfcTrapeziumProfileDef", 924, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcTwoDirectionRepeatFactor_type = new entity("IfcTwoDirectionRepeatFactor", 931, IFC2X3_IfcOneDirectionRepeatFactor_type);
    IFC2X3_IfcTypeObject_type = new entity("IfcTypeObject", 932, IFC2X3_IfcObjectDefinition_type);
    IFC2X3_IfcTypeProduct_type = new entity("IfcTypeProduct", 933, IFC2X3_IfcTypeObject_type);
    IFC2X3_IfcUShapeProfileDef_type = new entity("IfcUShapeProfileDef", 939, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcVector_type = new entity("IfcVector", 944, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcVertexLoop_type = new entity("IfcVertexLoop", 948, IFC2X3_IfcLoop_type);
    IFC2X3_IfcWindowLiningProperties_type = new entity("IfcWindowLiningProperties", 966, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcWindowPanelProperties_type = new entity("IfcWindowPanelProperties", 969, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcWindowStyle_type = new entity("IfcWindowStyle", 970, IFC2X3_IfcTypeProduct_type);
    IFC2X3_IfcZShapeProfileDef_type = new entity("IfcZShapeProfileDef", 979, IFC2X3_IfcParameterizedProfileDef_type);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcClassificationNotation_type);
        items.push_back(IFC2X3_IfcClassificationReference_type);
        IFC2X3_IfcClassificationNotationSelect_type = new select_type("IfcClassificationNotationSelect", 118, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcColourSpecification_type);
        items.push_back(IFC2X3_IfcPreDefinedColour_type);
        IFC2X3_IfcColour_type = new select_type("IfcColour", 123, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcColourRgb_type);
        items.push_back(IFC2X3_IfcNormalisedRatioMeasure_type);
        IFC2X3_IfcColourOrFactor_type = new select_type("IfcColourOrFactor", 124, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcCurveStyleFont_type);
        items.push_back(IFC2X3_IfcPreDefinedCurveFont_type);
        IFC2X3_IfcCurveStyleFontSelect_type = new select_type("IfcCurveStyleFontSelect", 201, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcDocumentInformation_type);
        items.push_back(IFC2X3_IfcDocumentReference_type);
        IFC2X3_IfcDocumentSelect_type = new select_type("IfcDocumentSelect", 245, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcOneDirectionRepeatFactor_type);
        items.push_back(IFC2X3_IfcPositiveLengthMeasure_type);
        IFC2X3_IfcHatchLineDistanceSelect_type = new select_type("IfcHatchLineDistanceSelect", 403, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(22);
        items.push_back(IFC2X3_IfcAmountOfSubstanceMeasure_type);
        items.push_back(IFC2X3_IfcAreaMeasure_type);
        items.push_back(IFC2X3_IfcComplexNumber_type);
        items.push_back(IFC2X3_IfcContextDependentMeasure_type);
        items.push_back(IFC2X3_IfcCountMeasure_type);
        items.push_back(IFC2X3_IfcDescriptiveMeasure_type);
        items.push_back(IFC2X3_IfcElectricCurrentMeasure_type);
        items.push_back(IFC2X3_IfcLengthMeasure_type);
        items.push_back(IFC2X3_IfcLuminousIntensityMeasure_type);
        items.push_back(IFC2X3_IfcMassMeasure_type);
        items.push_back(IFC2X3_IfcNormalisedRatioMeasure_type);
        items.push_back(IFC2X3_IfcNumericMeasure_type);
        items.push_back(IFC2X3_IfcParameterValue_type);
        items.push_back(IFC2X3_IfcPlaneAngleMeasure_type);
        items.push_back(IFC2X3_IfcPositiveLengthMeasure_type);
        items.push_back(IFC2X3_IfcPositivePlaneAngleMeasure_type);
        items.push_back(IFC2X3_IfcPositiveRatioMeasure_type);
        items.push_back(IFC2X3_IfcRatioMeasure_type);
        items.push_back(IFC2X3_IfcSolidAngleMeasure_type);
        items.push_back(IFC2X3_IfcThermodynamicTemperatureMeasure_type);
        items.push_back(IFC2X3_IfcTimeMeasure_type);
        items.push_back(IFC2X3_IfcVolumeMeasure_type);
        IFC2X3_IfcMeasureValue_type = new select_type("IfcMeasureValue", 485, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcPoint_type);
        items.push_back(IFC2X3_IfcVertexPoint_type);
        IFC2X3_IfcPointOrVertexPoint_type = new select_type("IfcPointOrVertexPoint", 572, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC2X3_IfcCurveStyle_type);
        items.push_back(IFC2X3_IfcFillAreaStyle_type);
        items.push_back(IFC2X3_IfcNullStyle_type);
        items.push_back(IFC2X3_IfcSurfaceStyle_type);
        items.push_back(IFC2X3_IfcSymbolStyle_type);
        items.push_back(IFC2X3_IfcTextStyle_type);
        IFC2X3_IfcPresentationStyleSelect_type = new select_type("IfcPresentationStyleSelect", 595, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IFC2X3_IfcColour_type);
        IFC2X3_IfcSymbolStyleSelect_type = new select_type("IfcSymbolStyleSelect", 865, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcDerivedMeasureValue_type);
        items.push_back(IFC2X3_IfcMeasureValue_type);
        items.push_back(IFC2X3_IfcSimpleValue_type);
        IFC2X3_IfcValue_type = new select_type("IfcValue", 940, items);
    }
    IFC2X3_IfcAnnotationCurveOccurrence_type = new entity("IfcAnnotationCurveOccurrence", 28, IFC2X3_IfcAnnotationOccurrence_type);
    IFC2X3_IfcAnnotationFillArea_type = new entity("IfcAnnotationFillArea", 29, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcAnnotationFillAreaOccurrence_type = new entity("IfcAnnotationFillAreaOccurrence", 30, IFC2X3_IfcAnnotationOccurrence_type);
    IFC2X3_IfcAnnotationSurface_type = new entity("IfcAnnotationSurface", 32, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcAxis1Placement_type = new entity("IfcAxis1Placement", 52, IFC2X3_IfcPlacement_type);
    IFC2X3_IfcAxis2Placement2D_type = new entity("IfcAxis2Placement2D", 54, IFC2X3_IfcPlacement_type);
    IFC2X3_IfcAxis2Placement3D_type = new entity("IfcAxis2Placement3D", 55, IFC2X3_IfcPlacement_type);
    IFC2X3_IfcBooleanResult_type = new entity("IfcBooleanResult", 69, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcBoundedSurface_type = new entity("IfcBoundedSurface", 76, IFC2X3_IfcSurface_type);
    IFC2X3_IfcBoundingBox_type = new entity("IfcBoundingBox", 77, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcBoxedHalfSpace_type = new entity("IfcBoxedHalfSpace", 79, IFC2X3_IfcHalfSpaceSolid_type);
    IFC2X3_IfcCShapeProfileDef_type = new entity("IfcCShapeProfileDef", 186, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcCartesianPoint_type = new entity("IfcCartesianPoint", 98, IFC2X3_IfcPoint_type);
    IFC2X3_IfcCartesianTransformationOperator_type = new entity("IfcCartesianTransformationOperator", 99, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcCartesianTransformationOperator2D_type = new entity("IfcCartesianTransformationOperator2D", 100, IFC2X3_IfcCartesianTransformationOperator_type);
    IFC2X3_IfcCartesianTransformationOperator2DnonUniform_type = new entity("IfcCartesianTransformationOperator2DnonUniform", 101, IFC2X3_IfcCartesianTransformationOperator2D_type);
    IFC2X3_IfcCartesianTransformationOperator3D_type = new entity("IfcCartesianTransformationOperator3D", 102, IFC2X3_IfcCartesianTransformationOperator_type);
    IFC2X3_IfcCartesianTransformationOperator3DnonUniform_type = new entity("IfcCartesianTransformationOperator3DnonUniform", 103, IFC2X3_IfcCartesianTransformationOperator3D_type);
    IFC2X3_IfcCircleProfileDef_type = new entity("IfcCircleProfileDef", 112, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcClosedShell_type = new entity("IfcClosedShell", 120, IFC2X3_IfcConnectedFaceSet_type);
    IFC2X3_IfcCompositeCurveSegment_type = new entity("IfcCompositeCurveSegment", 133, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcCraneRailAShapeProfileDef_type = new entity("IfcCraneRailAShapeProfileDef", 180, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcCraneRailFShapeProfileDef_type = new entity("IfcCraneRailFShapeProfileDef", 181, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcCsgPrimitive3D_type = new entity("IfcCsgPrimitive3D", 183, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcCsgSolid_type = new entity("IfcCsgSolid", 185, IFC2X3_IfcSolidModel_type);
    IFC2X3_IfcCurve_type = new entity("IfcCurve", 193, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcCurveBoundedPlane_type = new entity("IfcCurveBoundedPlane", 194, IFC2X3_IfcBoundedSurface_type);
    IFC2X3_IfcDefinedSymbol_type = new entity("IfcDefinedSymbol", 209, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcDimensionCurve_type = new entity("IfcDimensionCurve", 221, IFC2X3_IfcAnnotationCurveOccurrence_type);
    IFC2X3_IfcDimensionCurveTerminator_type = new entity("IfcDimensionCurveTerminator", 223, IFC2X3_IfcTerminatorSymbol_type);
    IFC2X3_IfcDirection_type = new entity("IfcDirection", 226, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcDoorLiningProperties_type = new entity("IfcDoorLiningProperties", 248, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcDoorPanelProperties_type = new entity("IfcDoorPanelProperties", 251, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcDoorStyle_type = new entity("IfcDoorStyle", 252, IFC2X3_IfcTypeProduct_type);
    IFC2X3_IfcDraughtingCallout_type = new entity("IfcDraughtingCallout", 256, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcDraughtingPreDefinedColour_type = new entity("IfcDraughtingPreDefinedColour", 259, IFC2X3_IfcPreDefinedColour_type);
    IFC2X3_IfcDraughtingPreDefinedCurveFont_type = new entity("IfcDraughtingPreDefinedCurveFont", 260, IFC2X3_IfcPreDefinedCurveFont_type);
    IFC2X3_IfcEdgeLoop_type = new entity("IfcEdgeLoop", 272, IFC2X3_IfcLoop_type);
    IFC2X3_IfcElementQuantity_type = new entity("IfcElementQuantity", 304, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcElementType_type = new entity("IfcElementType", 305, IFC2X3_IfcTypeProduct_type);
    IFC2X3_IfcElementarySurface_type = new entity("IfcElementarySurface", 298, IFC2X3_IfcSurface_type);
    IFC2X3_IfcEllipseProfileDef_type = new entity("IfcEllipseProfileDef", 307, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcEnergyProperties_type = new entity("IfcEnergyProperties", 311, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcExtrudedAreaSolid_type = new entity("IfcExtrudedAreaSolid", 327, IFC2X3_IfcSweptAreaSolid_type);
    IFC2X3_IfcFaceBasedSurfaceModel_type = new entity("IfcFaceBasedSurfaceModel", 329, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcFillAreaStyleHatching_type = new entity("IfcFillAreaStyleHatching", 344, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcFillAreaStyleTileSymbolWithStyle_type = new entity("IfcFillAreaStyleTileSymbolWithStyle", 347, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcFillAreaStyleTiles_type = new entity("IfcFillAreaStyleTiles", 345, IFC2X3_IfcGeometricRepresentationItem_type);
    IFC2X3_IfcFluidFlowProperties_type = new entity("IfcFluidFlowProperties", 372, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcFurnishingElementType_type = new entity("IfcFurnishingElementType", 382, IFC2X3_IfcElementType_type);
    IFC2X3_IfcFurnitureType_type = new entity("IfcFurnitureType", 384, IFC2X3_IfcFurnishingElementType_type);
    IFC2X3_IfcGeometricCurveSet_type = new entity("IfcGeometricCurveSet", 389, IFC2X3_IfcGeometricSet_type);
    IFC2X3_IfcIShapeProfileDef_type = new entity("IfcIShapeProfileDef", 424, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcLShapeProfileDef_type = new entity("IfcLShapeProfileDef", 464, IFC2X3_IfcParameterizedProfileDef_type);
    IFC2X3_IfcLine_type = new entity("IfcLine", 452, IFC2X3_IfcCurve_type);
    IFC2X3_IfcManifoldSolidBrep_type = new entity("IfcManifoldSolidBrep", 470, IFC2X3_IfcSolidModel_type);
    IFC2X3_IfcObject_type = new entity("IfcObject", 515, IFC2X3_IfcObjectDefinition_type);
    IFC2X3_IfcOffsetCurve2D_type = new entity("IfcOffsetCurve2D", 524, IFC2X3_IfcCurve_type);
    IFC2X3_IfcOffsetCurve3D_type = new entity("IfcOffsetCurve3D", 525, IFC2X3_IfcCurve_type);
    IFC2X3_IfcPermeableCoveringProperties_type = new entity("IfcPermeableCoveringProperties", 543, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcPlanarBox_type = new entity("IfcPlanarBox", 561, IFC2X3_IfcPlanarExtent_type);
    IFC2X3_IfcPlane_type = new entity("IfcPlane", 564, IFC2X3_IfcElementarySurface_type);
    IFC2X3_IfcProcess_type = new entity("IfcProcess", 599, IFC2X3_IfcObject_type);
    IFC2X3_IfcProduct_type = new entity("IfcProduct", 600, IFC2X3_IfcObject_type);
    IFC2X3_IfcProject_type = new entity("IfcProject", 607, IFC2X3_IfcObject_type);
    IFC2X3_IfcProjectionCurve_type = new entity("IfcProjectionCurve", 609, IFC2X3_IfcAnnotationCurveOccurrence_type);
    IFC2X3_IfcPropertySet_type = new entity("IfcPropertySet", 624, IFC2X3_IfcPropertySetDefinition_type);
    IFC2X3_IfcProxy_type = new entity("IfcProxy", 631, IFC2X3_IfcProduct_type);
    IFC2X3_IfcRectangleHollowProfileDef_type = new entity("IfcRectangleHollowProfileDef", 653, IFC2X3_IfcRectangleProfileDef_type);
    IFC2X3_IfcRectangularPyramid_type = new entity("IfcRectangularPyramid", 655, IFC2X3_IfcCsgPrimitive3D_type);
    IFC2X3_IfcRectangularTrimmedSurface_type = new entity("IfcRectangularTrimmedSurface", 656, IFC2X3_IfcBoundedSurface_type);
    IFC2X3_IfcRelAssigns_type = new entity("IfcRelAssigns", 668, IFC2X3_IfcRelationship_type);
    IFC2X3_IfcRelAssignsToActor_type = new entity("IfcRelAssignsToActor", 670, IFC2X3_IfcRelAssigns_type);
    IFC2X3_IfcRelAssignsToControl_type = new entity("IfcRelAssignsToControl", 671, IFC2X3_IfcRelAssigns_type);
    IFC2X3_IfcRelAssignsToGroup_type = new entity("IfcRelAssignsToGroup", 672, IFC2X3_IfcRelAssigns_type);
    IFC2X3_IfcRelAssignsToProcess_type = new entity("IfcRelAssignsToProcess", 673, IFC2X3_IfcRelAssigns_type);
    IFC2X3_IfcRelAssignsToProduct_type = new entity("IfcRelAssignsToProduct", 674, IFC2X3_IfcRelAssigns_type);
    IFC2X3_IfcRelAssignsToProjectOrder_type = new entity("IfcRelAssignsToProjectOrder", 675, IFC2X3_IfcRelAssignsToControl_type);
    IFC2X3_IfcRelAssignsToResource_type = new entity("IfcRelAssignsToResource", 676, IFC2X3_IfcRelAssigns_type);
    IFC2X3_IfcRelAssociates_type = new entity("IfcRelAssociates", 677, IFC2X3_IfcRelationship_type);
    IFC2X3_IfcRelAssociatesAppliedValue_type = new entity("IfcRelAssociatesAppliedValue", 678, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesApproval_type = new entity("IfcRelAssociatesApproval", 679, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesClassification_type = new entity("IfcRelAssociatesClassification", 680, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesConstraint_type = new entity("IfcRelAssociatesConstraint", 681, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesDocument_type = new entity("IfcRelAssociatesDocument", 682, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesLibrary_type = new entity("IfcRelAssociatesLibrary", 683, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesMaterial_type = new entity("IfcRelAssociatesMaterial", 684, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelAssociatesProfileProperties_type = new entity("IfcRelAssociatesProfileProperties", 685, IFC2X3_IfcRelAssociates_type);
    IFC2X3_IfcRelConnects_type = new entity("IfcRelConnects", 688, IFC2X3_IfcRelationship_type);
    IFC2X3_IfcRelConnectsElements_type = new entity("IfcRelConnectsElements", 689, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelConnectsPathElements_type = new entity("IfcRelConnectsPathElements", 690, IFC2X3_IfcRelConnectsElements_type);
    IFC2X3_IfcRelConnectsPortToElement_type = new entity("IfcRelConnectsPortToElement", 692, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelConnectsPorts_type = new entity("IfcRelConnectsPorts", 691, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelConnectsStructuralActivity_type = new entity("IfcRelConnectsStructuralActivity", 693, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelConnectsStructuralElement_type = new entity("IfcRelConnectsStructuralElement", 694, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelConnectsStructuralMember_type = new entity("IfcRelConnectsStructuralMember", 695, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelConnectsWithEccentricity_type = new entity("IfcRelConnectsWithEccentricity", 696, IFC2X3_IfcRelConnectsStructuralMember_type);
    IFC2X3_IfcRelConnectsWithRealizingElements_type = new entity("IfcRelConnectsWithRealizingElements", 697, IFC2X3_IfcRelConnectsElements_type);
    IFC2X3_IfcRelContainedInSpatialStructure_type = new entity("IfcRelContainedInSpatialStructure", 698, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelCoversBldgElements_type = new entity("IfcRelCoversBldgElements", 699, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelCoversSpaces_type = new entity("IfcRelCoversSpaces", 700, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelDecomposes_type = new entity("IfcRelDecomposes", 701, IFC2X3_IfcRelationship_type);
    IFC2X3_IfcRelDefines_type = new entity("IfcRelDefines", 702, IFC2X3_IfcRelationship_type);
    IFC2X3_IfcRelDefinesByProperties_type = new entity("IfcRelDefinesByProperties", 703, IFC2X3_IfcRelDefines_type);
    IFC2X3_IfcRelDefinesByType_type = new entity("IfcRelDefinesByType", 704, IFC2X3_IfcRelDefines_type);
    IFC2X3_IfcRelFillsElement_type = new entity("IfcRelFillsElement", 705, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelFlowControlElements_type = new entity("IfcRelFlowControlElements", 706, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelInteractionRequirements_type = new entity("IfcRelInteractionRequirements", 707, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelNests_type = new entity("IfcRelNests", 708, IFC2X3_IfcRelDecomposes_type);
    IFC2X3_IfcRelOccupiesSpaces_type = new entity("IfcRelOccupiesSpaces", 709, IFC2X3_IfcRelAssignsToActor_type);
    IFC2X3_IfcRelOverridesProperties_type = new entity("IfcRelOverridesProperties", 710, IFC2X3_IfcRelDefinesByProperties_type);
    IFC2X3_IfcRelProjectsElement_type = new entity("IfcRelProjectsElement", 711, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelReferencedInSpatialStructure_type = new entity("IfcRelReferencedInSpatialStructure", 712, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelSchedulesCostItems_type = new entity("IfcRelSchedulesCostItems", 713, IFC2X3_IfcRelAssignsToControl_type);
    IFC2X3_IfcRelSequence_type = new entity("IfcRelSequence", 714, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelServicesBuildings_type = new entity("IfcRelServicesBuildings", 715, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelSpaceBoundary_type = new entity("IfcRelSpaceBoundary", 716, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcRelVoidsElement_type = new entity("IfcRelVoidsElement", 717, IFC2X3_IfcRelConnects_type);
    IFC2X3_IfcResource_type = new entity("IfcResource", 722, IFC2X3_IfcObject_type);
    IFC2X3_IfcRevolvedAreaSolid_type = new entity("IfcRevolvedAreaSolid", 724, IFC2X3_IfcSweptAreaSolid_type);
    IFC2X3_IfcRightCircularCone_type = new entity("IfcRightCircularCone", 727, IFC2X3_IfcCsgPrimitive3D_type);
    IFC2X3_IfcRightCircularCylinder_type = new entity("IfcRightCircularCylinder", 728, IFC2X3_IfcCsgPrimitive3D_type);
    IFC2X3_IfcSpatialStructureElement_type = new entity("IfcSpatialStructureElement", 786, IFC2X3_IfcProduct_type);
    IFC2X3_IfcSpatialStructureElementType_type = new entity("IfcSpatialStructureElementType", 787, IFC2X3_IfcElementType_type);
    IFC2X3_IfcSphere_type = new entity("IfcSphere", 792, IFC2X3_IfcCsgPrimitive3D_type);
    IFC2X3_IfcStructuralActivity_type = new entity("IfcStructuralActivity", 802, IFC2X3_IfcProduct_type);
    IFC2X3_IfcStructuralItem_type = new entity("IfcStructuralItem", 811, IFC2X3_IfcProduct_type);
    IFC2X3_IfcStructuralMember_type = new entity("IfcStructuralMember", 824, IFC2X3_IfcStructuralItem_type);
    IFC2X3_IfcStructuralReaction_type = new entity("IfcStructuralReaction", 831, IFC2X3_IfcStructuralActivity_type);
    IFC2X3_IfcStructuralSurfaceMember_type = new entity("IfcStructuralSurfaceMember", 835, IFC2X3_IfcStructuralMember_type);
    IFC2X3_IfcStructuralSurfaceMemberVarying_type = new entity("IfcStructuralSurfaceMemberVarying", 836, IFC2X3_IfcStructuralSurfaceMember_type);
    IFC2X3_IfcStructuredDimensionCallout_type = new entity("IfcStructuredDimensionCallout", 838, IFC2X3_IfcDraughtingCallout_type);
    IFC2X3_IfcSurfaceCurveSweptAreaSolid_type = new entity("IfcSurfaceCurveSweptAreaSolid", 845, IFC2X3_IfcSweptAreaSolid_type);
    IFC2X3_IfcSurfaceOfLinearExtrusion_type = new entity("IfcSurfaceOfLinearExtrusion", 846, IFC2X3_IfcSweptSurface_type);
    IFC2X3_IfcSurfaceOfRevolution_type = new entity("IfcSurfaceOfRevolution", 847, IFC2X3_IfcSweptSurface_type);
    IFC2X3_IfcSystemFurnitureElementType_type = new entity("IfcSystemFurnitureElementType", 867, IFC2X3_IfcFurnishingElementType_type);
    IFC2X3_IfcTask_type = new entity("IfcTask", 872, IFC2X3_IfcProcess_type);
    IFC2X3_IfcTransportElementType_type = new entity("IfcTransportElementType", 922, IFC2X3_IfcElementType_type);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcAxis2Placement2D_type);
        items.push_back(IFC2X3_IfcAxis2Placement3D_type);
        IFC2X3_IfcAxis2Placement_type = new select_type("IfcAxis2Placement", 53, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC2X3_IfcBooleanResult_type);
        items.push_back(IFC2X3_IfcCsgPrimitive3D_type);
        items.push_back(IFC2X3_IfcHalfSpaceSolid_type);
        items.push_back(IFC2X3_IfcSolidModel_type);
        IFC2X3_IfcBooleanOperand_type = new select_type("IfcBooleanOperand", 67, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcBooleanResult_type);
        items.push_back(IFC2X3_IfcCsgPrimitive3D_type);
        IFC2X3_IfcCsgSelect_type = new select_type("IfcCsgSelect", 184, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcCurveStyleFontAndScaling_type);
        items.push_back(IFC2X3_IfcCurveStyleFontSelect_type);
        IFC2X3_IfcCurveFontOrScaledCurveFontSelect_type = new select_type("IfcCurveFontOrScaledCurveFontSelect", 195, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcAnnotationCurveOccurrence_type);
        items.push_back(IFC2X3_IfcAnnotationSymbolOccurrence_type);
        items.push_back(IFC2X3_IfcAnnotationTextOccurrence_type);
        IFC2X3_IfcDraughtingCalloutElement_type = new select_type("IfcDraughtingCalloutElement", 257, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IFC2X3_IfcFillAreaStyleTileSymbolWithStyle_type);
        IFC2X3_IfcFillAreaStyleTileShapeSelect_type = new select_type("IfcFillAreaStyleTileShapeSelect", 346, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC2X3_IfcColour_type);
        items.push_back(IFC2X3_IfcExternallyDefinedHatchStyle_type);
        items.push_back(IFC2X3_IfcFillAreaStyleHatching_type);
        items.push_back(IFC2X3_IfcFillAreaStyleTiles_type);
        IFC2X3_IfcFillStyleSelect_type = new select_type("IfcFillStyleSelect", 348, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcCurve_type);
        items.push_back(IFC2X3_IfcPoint_type);
        items.push_back(IFC2X3_IfcSurface_type);
        IFC2X3_IfcGeometricSetSelect_type = new select_type("IfcGeometricSetSelect", 395, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcDirection_type);
        items.push_back(IFC2X3_IfcPlaneAngleMeasure_type);
        IFC2X3_IfcOrientationSelect_type = new select_type("IfcOrientationSelect", 533, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcClosedShell_type);
        items.push_back(IFC2X3_IfcOpenShell_type);
        IFC2X3_IfcShell_type = new select_type("IfcShell", 759, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_IfcFaceBasedSurfaceModel_type);
        items.push_back(IFC2X3_IfcFaceSurface_type);
        items.push_back(IFC2X3_IfcSurface_type);
        IFC2X3_IfcSurfaceOrFaceSurface_type = new select_type("IfcSurfaceOrFaceSurface", 848, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcCartesianPoint_type);
        items.push_back(IFC2X3_IfcParameterValue_type);
        IFC2X3_IfcTrimmingSelect_type = new select_type("IfcTrimmingSelect", 927, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcDirection_type);
        items.push_back(IFC2X3_IfcVector_type);
        IFC2X3_IfcVectorOrDirection_type = new select_type("IfcVectorOrDirection", 945, items);
    }
    IFC2X3_IfcActor_type = new entity("IfcActor", 6, IFC2X3_IfcObject_type);
    IFC2X3_IfcAnnotation_type = new entity("IfcAnnotation", 27, IFC2X3_IfcProduct_type);
    IFC2X3_IfcAsymmetricIShapeProfileDef_type = new entity("IfcAsymmetricIShapeProfileDef", 51, IFC2X3_IfcIShapeProfileDef_type);
    IFC2X3_IfcBlock_type = new entity("IfcBlock", 62, IFC2X3_IfcCsgPrimitive3D_type);
    IFC2X3_IfcBooleanClippingResult_type = new entity("IfcBooleanClippingResult", 66, IFC2X3_IfcBooleanResult_type);
    IFC2X3_IfcBoundedCurve_type = new entity("IfcBoundedCurve", 75, IFC2X3_IfcCurve_type);
    IFC2X3_IfcBuilding_type = new entity("IfcBuilding", 82, IFC2X3_IfcSpatialStructureElement_type);
    IFC2X3_IfcBuildingElementType_type = new entity("IfcBuildingElementType", 89, IFC2X3_IfcElementType_type);
    IFC2X3_IfcBuildingStorey_type = new entity("IfcBuildingStorey", 90, IFC2X3_IfcSpatialStructureElement_type);
    IFC2X3_IfcCircleHollowProfileDef_type = new entity("IfcCircleHollowProfileDef", 111, IFC2X3_IfcCircleProfileDef_type);
    IFC2X3_IfcColumnType_type = new entity("IfcColumnType", 128, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcCompositeCurve_type = new entity("IfcCompositeCurve", 132, IFC2X3_IfcBoundedCurve_type);
    IFC2X3_IfcConic_type = new entity("IfcConic", 143, IFC2X3_IfcCurve_type);
    IFC2X3_IfcConstructionResource_type = new entity("IfcConstructionResource", 160, IFC2X3_IfcResource_type);
    IFC2X3_IfcControl_type = new entity("IfcControl", 163, IFC2X3_IfcObject_type);
    IFC2X3_IfcCostItem_type = new entity("IfcCostItem", 172, IFC2X3_IfcControl_type);
    IFC2X3_IfcCostSchedule_type = new entity("IfcCostSchedule", 173, IFC2X3_IfcControl_type);
    IFC2X3_IfcCoveringType_type = new entity("IfcCoveringType", 178, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcCrewResource_type = new entity("IfcCrewResource", 182, IFC2X3_IfcConstructionResource_type);
    IFC2X3_IfcCurtainWallType_type = new entity("IfcCurtainWallType", 190, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcDimensionCurveDirectedCallout_type = new entity("IfcDimensionCurveDirectedCallout", 222, IFC2X3_IfcDraughtingCallout_type);
    IFC2X3_IfcDistributionElementType_type = new entity("IfcDistributionElementType", 236, IFC2X3_IfcElementType_type);
    IFC2X3_IfcDistributionFlowElementType_type = new entity("IfcDistributionFlowElementType", 238, IFC2X3_IfcDistributionElementType_type);
    IFC2X3_IfcElectricalBaseProperties_type = new entity("IfcElectricalBaseProperties", 273, IFC2X3_IfcEnergyProperties_type);
    IFC2X3_IfcElement_type = new entity("IfcElement", 297, IFC2X3_IfcProduct_type);
    IFC2X3_IfcElementAssembly_type = new entity("IfcElementAssembly", 299, IFC2X3_IfcElement_type);
    IFC2X3_IfcElementComponent_type = new entity("IfcElementComponent", 301, IFC2X3_IfcElement_type);
    IFC2X3_IfcElementComponentType_type = new entity("IfcElementComponentType", 302, IFC2X3_IfcElementType_type);
    IFC2X3_IfcEllipse_type = new entity("IfcEllipse", 306, IFC2X3_IfcConic_type);
    IFC2X3_IfcEnergyConversionDeviceType_type = new entity("IfcEnergyConversionDeviceType", 309, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcEquipmentElement_type = new entity("IfcEquipmentElement", 315, IFC2X3_IfcElement_type);
    IFC2X3_IfcEquipmentStandard_type = new entity("IfcEquipmentStandard", 316, IFC2X3_IfcControl_type);
    IFC2X3_IfcEvaporativeCoolerType_type = new entity("IfcEvaporativeCoolerType", 317, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcEvaporatorType_type = new entity("IfcEvaporatorType", 319, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcFacetedBrep_type = new entity("IfcFacetedBrep", 333, IFC2X3_IfcManifoldSolidBrep_type);
    IFC2X3_IfcFacetedBrepWithVoids_type = new entity("IfcFacetedBrepWithVoids", 334, IFC2X3_IfcManifoldSolidBrep_type);
    IFC2X3_IfcFastener_type = new entity("IfcFastener", 338, IFC2X3_IfcElementComponent_type);
    IFC2X3_IfcFastenerType_type = new entity("IfcFastenerType", 339, IFC2X3_IfcElementComponentType_type);
    IFC2X3_IfcFeatureElement_type = new entity("IfcFeatureElement", 340, IFC2X3_IfcElement_type);
    IFC2X3_IfcFeatureElementAddition_type = new entity("IfcFeatureElementAddition", 341, IFC2X3_IfcFeatureElement_type);
    IFC2X3_IfcFeatureElementSubtraction_type = new entity("IfcFeatureElementSubtraction", 342, IFC2X3_IfcFeatureElement_type);
    IFC2X3_IfcFlowControllerType_type = new entity("IfcFlowControllerType", 354, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFlowFittingType_type = new entity("IfcFlowFittingType", 357, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFlowMeterType_type = new entity("IfcFlowMeterType", 360, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcFlowMovingDeviceType_type = new entity("IfcFlowMovingDeviceType", 363, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFlowSegmentType_type = new entity("IfcFlowSegmentType", 365, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFlowStorageDeviceType_type = new entity("IfcFlowStorageDeviceType", 367, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFlowTerminalType_type = new entity("IfcFlowTerminalType", 369, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFlowTreatmentDeviceType_type = new entity("IfcFlowTreatmentDeviceType", 371, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcFurnishingElement_type = new entity("IfcFurnishingElement", 381, IFC2X3_IfcElement_type);
    IFC2X3_IfcFurnitureStandard_type = new entity("IfcFurnitureStandard", 383, IFC2X3_IfcControl_type);
    IFC2X3_IfcGasTerminalType_type = new entity("IfcGasTerminalType", 385, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcGrid_type = new entity("IfcGrid", 398, IFC2X3_IfcProduct_type);
    IFC2X3_IfcGroup_type = new entity("IfcGroup", 401, IFC2X3_IfcObject_type);
    IFC2X3_IfcHeatExchangerType_type = new entity("IfcHeatExchangerType", 404, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcHumidifierType_type = new entity("IfcHumidifierType", 409, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcInventory_type = new entity("IfcInventory", 419, IFC2X3_IfcGroup_type);
    IFC2X3_IfcJunctionBoxType_type = new entity("IfcJunctionBoxType", 426, IFC2X3_IfcFlowFittingType_type);
    IFC2X3_IfcLaborResource_type = new entity("IfcLaborResource", 430, IFC2X3_IfcConstructionResource_type);
    IFC2X3_IfcLampType_type = new entity("IfcLampType", 431, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcLightFixtureType_type = new entity("IfcLightFixtureType", 443, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcLinearDimension_type = new entity("IfcLinearDimension", 453, IFC2X3_IfcDimensionCurveDirectedCallout_type);
    IFC2X3_IfcMechanicalFastener_type = new entity("IfcMechanicalFastener", 488, IFC2X3_IfcFastener_type);
    IFC2X3_IfcMechanicalFastenerType_type = new entity("IfcMechanicalFastenerType", 489, IFC2X3_IfcFastenerType_type);
    IFC2X3_IfcMemberType_type = new entity("IfcMemberType", 493, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcMotorConnectionType_type = new entity("IfcMotorConnectionType", 508, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcMove_type = new entity("IfcMove", 510, IFC2X3_IfcTask_type);
    IFC2X3_IfcOccupant_type = new entity("IfcOccupant", 522, IFC2X3_IfcActor_type);
    IFC2X3_IfcOpeningElement_type = new entity("IfcOpeningElement", 527, IFC2X3_IfcFeatureElementSubtraction_type);
    IFC2X3_IfcOrderAction_type = new entity("IfcOrderAction", 530, IFC2X3_IfcTask_type);
    IFC2X3_IfcOutletType_type = new entity("IfcOutletType", 535, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcPerformanceHistory_type = new entity("IfcPerformanceHistory", 541, IFC2X3_IfcControl_type);
    IFC2X3_IfcPermit_type = new entity("IfcPermit", 544, IFC2X3_IfcControl_type);
    IFC2X3_IfcPipeFittingType_type = new entity("IfcPipeFittingType", 555, IFC2X3_IfcFlowFittingType_type);
    IFC2X3_IfcPipeSegmentType_type = new entity("IfcPipeSegmentType", 557, IFC2X3_IfcFlowSegmentType_type);
    IFC2X3_IfcPlateType_type = new entity("IfcPlateType", 567, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcPolyline_type = new entity("IfcPolyline", 574, IFC2X3_IfcBoundedCurve_type);
    IFC2X3_IfcPort_type = new entity("IfcPort", 576, IFC2X3_IfcProduct_type);
    IFC2X3_IfcProcedure_type = new entity("IfcProcedure", 597, IFC2X3_IfcProcess_type);
    IFC2X3_IfcProjectOrder_type = new entity("IfcProjectOrder", 611, IFC2X3_IfcControl_type);
    IFC2X3_IfcProjectOrderRecord_type = new entity("IfcProjectOrderRecord", 612, IFC2X3_IfcControl_type);
    IFC2X3_IfcProjectionElement_type = new entity("IfcProjectionElement", 610, IFC2X3_IfcFeatureElementAddition_type);
    IFC2X3_IfcProtectiveDeviceType_type = new entity("IfcProtectiveDeviceType", 629, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcPumpType_type = new entity("IfcPumpType", 632, IFC2X3_IfcFlowMovingDeviceType_type);
    IFC2X3_IfcRadiusDimension_type = new entity("IfcRadiusDimension", 641, IFC2X3_IfcDimensionCurveDirectedCallout_type);
    IFC2X3_IfcRailingType_type = new entity("IfcRailingType", 643, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcRampFlightType_type = new entity("IfcRampFlightType", 647, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcRelAggregates_type = new entity("IfcRelAggregates", 667, IFC2X3_IfcRelDecomposes_type);
    IFC2X3_IfcRelAssignsTasks_type = new entity("IfcRelAssignsTasks", 669, IFC2X3_IfcRelAssignsToControl_type);
    IFC2X3_IfcSanitaryTerminalType_type = new entity("IfcSanitaryTerminalType", 738, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcScheduleTimeControl_type = new entity("IfcScheduleTimeControl", 740, IFC2X3_IfcControl_type);
    IFC2X3_IfcServiceLife_type = new entity("IfcServiceLife", 751, IFC2X3_IfcControl_type);
    IFC2X3_IfcSite_type = new entity("IfcSite", 764, IFC2X3_IfcSpatialStructureElement_type);
    IFC2X3_IfcSlabType_type = new entity("IfcSlabType", 769, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcSpace_type = new entity("IfcSpace", 779, IFC2X3_IfcSpatialStructureElement_type);
    IFC2X3_IfcSpaceHeaterType_type = new entity("IfcSpaceHeaterType", 780, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcSpaceProgram_type = new entity("IfcSpaceProgram", 782, IFC2X3_IfcControl_type);
    IFC2X3_IfcSpaceType_type = new entity("IfcSpaceType", 784, IFC2X3_IfcSpatialStructureElementType_type);
    IFC2X3_IfcStackTerminalType_type = new entity("IfcStackTerminalType", 793, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcStairFlightType_type = new entity("IfcStairFlightType", 797, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcStructuralAction_type = new entity("IfcStructuralAction", 801, IFC2X3_IfcStructuralActivity_type);
    IFC2X3_IfcStructuralConnection_type = new entity("IfcStructuralConnection", 805, IFC2X3_IfcStructuralItem_type);
    IFC2X3_IfcStructuralCurveConnection_type = new entity("IfcStructuralCurveConnection", 807, IFC2X3_IfcStructuralConnection_type);
    IFC2X3_IfcStructuralCurveMember_type = new entity("IfcStructuralCurveMember", 808, IFC2X3_IfcStructuralMember_type);
    IFC2X3_IfcStructuralCurveMemberVarying_type = new entity("IfcStructuralCurveMemberVarying", 809, IFC2X3_IfcStructuralCurveMember_type);
    IFC2X3_IfcStructuralLinearAction_type = new entity("IfcStructuralLinearAction", 812, IFC2X3_IfcStructuralAction_type);
    IFC2X3_IfcStructuralLinearActionVarying_type = new entity("IfcStructuralLinearActionVarying", 813, IFC2X3_IfcStructuralLinearAction_type);
    IFC2X3_IfcStructuralLoadGroup_type = new entity("IfcStructuralLoadGroup", 815, IFC2X3_IfcGroup_type);
    IFC2X3_IfcStructuralPlanarAction_type = new entity("IfcStructuralPlanarAction", 825, IFC2X3_IfcStructuralAction_type);
    IFC2X3_IfcStructuralPlanarActionVarying_type = new entity("IfcStructuralPlanarActionVarying", 826, IFC2X3_IfcStructuralPlanarAction_type);
    IFC2X3_IfcStructuralPointAction_type = new entity("IfcStructuralPointAction", 827, IFC2X3_IfcStructuralAction_type);
    IFC2X3_IfcStructuralPointConnection_type = new entity("IfcStructuralPointConnection", 828, IFC2X3_IfcStructuralConnection_type);
    IFC2X3_IfcStructuralPointReaction_type = new entity("IfcStructuralPointReaction", 829, IFC2X3_IfcStructuralReaction_type);
    IFC2X3_IfcStructuralResultGroup_type = new entity("IfcStructuralResultGroup", 832, IFC2X3_IfcGroup_type);
    IFC2X3_IfcStructuralSurfaceConnection_type = new entity("IfcStructuralSurfaceConnection", 834, IFC2X3_IfcStructuralConnection_type);
    IFC2X3_IfcSubContractResource_type = new entity("IfcSubContractResource", 842, IFC2X3_IfcConstructionResource_type);
    IFC2X3_IfcSwitchingDeviceType_type = new entity("IfcSwitchingDeviceType", 862, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcSystem_type = new entity("IfcSystem", 866, IFC2X3_IfcGroup_type);
    IFC2X3_IfcTankType_type = new entity("IfcTankType", 870, IFC2X3_IfcFlowStorageDeviceType_type);
    IFC2X3_IfcTimeSeriesSchedule_type = new entity("IfcTimeSeriesSchedule", 911, IFC2X3_IfcControl_type);
    IFC2X3_IfcTransformerType_type = new entity("IfcTransformerType", 918, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcTransportElement_type = new entity("IfcTransportElement", 921, IFC2X3_IfcElement_type);
    IFC2X3_IfcTrimmedCurve_type = new entity("IfcTrimmedCurve", 925, IFC2X3_IfcBoundedCurve_type);
    IFC2X3_IfcTubeBundleType_type = new entity("IfcTubeBundleType", 929, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcUnitaryEquipmentType_type = new entity("IfcUnitaryEquipmentType", 935, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcValveType_type = new entity("IfcValveType", 941, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcVirtualElement_type = new entity("IfcVirtualElement", 952, IFC2X3_IfcElement_type);
    IFC2X3_IfcWallType_type = new entity("IfcWallType", 958, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcWasteTerminalType_type = new entity("IfcWasteTerminalType", 962, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcWorkControl_type = new entity("IfcWorkControl", 973, IFC2X3_IfcControl_type);
    IFC2X3_IfcWorkPlan_type = new entity("IfcWorkPlan", 975, IFC2X3_IfcWorkControl_type);
    IFC2X3_IfcWorkSchedule_type = new entity("IfcWorkSchedule", 976, IFC2X3_IfcWorkControl_type);
    IFC2X3_IfcZone_type = new entity("IfcZone", 978, IFC2X3_IfcGroup_type);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcBoundedCurve_type);
        items.push_back(IFC2X3_IfcEdgeCurve_type);
        IFC2X3_IfcCurveOrEdgeCurve_type = new select_type("IfcCurveOrEdgeCurve", 196, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_IfcElement_type);
        items.push_back(IFC2X3_IfcStructuralItem_type);
        IFC2X3_IfcStructuralActivityAssignmentSelect_type = new select_type("IfcStructuralActivityAssignmentSelect", 803, items);
    }
    IFC2X3_Ifc2DCompositeCurve_type = new entity("Ifc2DCompositeCurve", 0, IFC2X3_IfcCompositeCurve_type);
    IFC2X3_IfcActionRequest_type = new entity("IfcActionRequest", 3, IFC2X3_IfcControl_type);
    IFC2X3_IfcAirTerminalBoxType_type = new entity("IfcAirTerminalBoxType", 14, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcAirTerminalType_type = new entity("IfcAirTerminalType", 16, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcAirToAirHeatRecoveryType_type = new entity("IfcAirToAirHeatRecoveryType", 18, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcAngularDimension_type = new entity("IfcAngularDimension", 25, IFC2X3_IfcDimensionCurveDirectedCallout_type);
    IFC2X3_IfcAsset_type = new entity("IfcAsset", 50, IFC2X3_IfcGroup_type);
    IFC2X3_IfcBSplineCurve_type = new entity("IfcBSplineCurve", 80, IFC2X3_IfcBoundedCurve_type);
    IFC2X3_IfcBeamType_type = new entity("IfcBeamType", 57, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcBezierCurve_type = new entity("IfcBezierCurve", 60, IFC2X3_IfcBSplineCurve_type);
    IFC2X3_IfcBoilerType_type = new entity("IfcBoilerType", 63, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcBuildingElement_type = new entity("IfcBuildingElement", 83, IFC2X3_IfcElement_type);
    IFC2X3_IfcBuildingElementComponent_type = new entity("IfcBuildingElementComponent", 84, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcBuildingElementPart_type = new entity("IfcBuildingElementPart", 85, IFC2X3_IfcBuildingElementComponent_type);
    IFC2X3_IfcBuildingElementProxy_type = new entity("IfcBuildingElementProxy", 86, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcBuildingElementProxyType_type = new entity("IfcBuildingElementProxyType", 87, IFC2X3_IfcBuildingElementType_type);
    IFC2X3_IfcCableCarrierFittingType_type = new entity("IfcCableCarrierFittingType", 91, IFC2X3_IfcFlowFittingType_type);
    IFC2X3_IfcCableCarrierSegmentType_type = new entity("IfcCableCarrierSegmentType", 93, IFC2X3_IfcFlowSegmentType_type);
    IFC2X3_IfcCableSegmentType_type = new entity("IfcCableSegmentType", 95, IFC2X3_IfcFlowSegmentType_type);
    IFC2X3_IfcChillerType_type = new entity("IfcChillerType", 108, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcCircle_type = new entity("IfcCircle", 110, IFC2X3_IfcConic_type);
    IFC2X3_IfcCoilType_type = new entity("IfcCoilType", 121, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcColumn_type = new entity("IfcColumn", 127, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcCompressorType_type = new entity("IfcCompressorType", 136, IFC2X3_IfcFlowMovingDeviceType_type);
    IFC2X3_IfcCondenserType_type = new entity("IfcCondenserType", 138, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcCondition_type = new entity("IfcCondition", 140, IFC2X3_IfcGroup_type);
    IFC2X3_IfcConditionCriterion_type = new entity("IfcConditionCriterion", 141, IFC2X3_IfcControl_type);
    IFC2X3_IfcConstructionEquipmentResource_type = new entity("IfcConstructionEquipmentResource", 157, IFC2X3_IfcConstructionResource_type);
    IFC2X3_IfcConstructionMaterialResource_type = new entity("IfcConstructionMaterialResource", 158, IFC2X3_IfcConstructionResource_type);
    IFC2X3_IfcConstructionProductResource_type = new entity("IfcConstructionProductResource", 159, IFC2X3_IfcConstructionResource_type);
    IFC2X3_IfcCooledBeamType_type = new entity("IfcCooledBeamType", 167, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcCoolingTowerType_type = new entity("IfcCoolingTowerType", 169, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcCovering_type = new entity("IfcCovering", 177, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcCurtainWall_type = new entity("IfcCurtainWall", 189, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcDamperType_type = new entity("IfcDamperType", 202, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcDiameterDimension_type = new entity("IfcDiameterDimension", 217, IFC2X3_IfcDimensionCurveDirectedCallout_type);
    IFC2X3_IfcDiscreteAccessory_type = new entity("IfcDiscreteAccessory", 228, IFC2X3_IfcElementComponent_type);
    IFC2X3_IfcDiscreteAccessoryType_type = new entity("IfcDiscreteAccessoryType", 229, IFC2X3_IfcElementComponentType_type);
    IFC2X3_IfcDistributionChamberElementType_type = new entity("IfcDistributionChamberElementType", 231, IFC2X3_IfcDistributionFlowElementType_type);
    IFC2X3_IfcDistributionControlElementType_type = new entity("IfcDistributionControlElementType", 234, IFC2X3_IfcDistributionElementType_type);
    IFC2X3_IfcDistributionElement_type = new entity("IfcDistributionElement", 235, IFC2X3_IfcElement_type);
    IFC2X3_IfcDistributionFlowElement_type = new entity("IfcDistributionFlowElement", 237, IFC2X3_IfcDistributionElement_type);
    IFC2X3_IfcDistributionPort_type = new entity("IfcDistributionPort", 239, IFC2X3_IfcPort_type);
    IFC2X3_IfcDoor_type = new entity("IfcDoor", 247, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcDuctFittingType_type = new entity("IfcDuctFittingType", 262, IFC2X3_IfcFlowFittingType_type);
    IFC2X3_IfcDuctSegmentType_type = new entity("IfcDuctSegmentType", 264, IFC2X3_IfcFlowSegmentType_type);
    IFC2X3_IfcDuctSilencerType_type = new entity("IfcDuctSilencerType", 266, IFC2X3_IfcFlowTreatmentDeviceType_type);
    IFC2X3_IfcEdgeFeature_type = new entity("IfcEdgeFeature", 271, IFC2X3_IfcFeatureElementSubtraction_type);
    IFC2X3_IfcElectricApplianceType_type = new entity("IfcElectricApplianceType", 276, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcElectricFlowStorageDeviceType_type = new entity("IfcElectricFlowStorageDeviceType", 285, IFC2X3_IfcFlowStorageDeviceType_type);
    IFC2X3_IfcElectricGeneratorType_type = new entity("IfcElectricGeneratorType", 287, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcElectricHeaterType_type = new entity("IfcElectricHeaterType", 289, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcElectricMotorType_type = new entity("IfcElectricMotorType", 291, IFC2X3_IfcEnergyConversionDeviceType_type);
    IFC2X3_IfcElectricTimeControlType_type = new entity("IfcElectricTimeControlType", 294, IFC2X3_IfcFlowControllerType_type);
    IFC2X3_IfcElectricalCircuit_type = new entity("IfcElectricalCircuit", 274, IFC2X3_IfcSystem_type);
    IFC2X3_IfcElectricalElement_type = new entity("IfcElectricalElement", 275, IFC2X3_IfcElement_type);
    IFC2X3_IfcEnergyConversionDevice_type = new entity("IfcEnergyConversionDevice", 308, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFanType_type = new entity("IfcFanType", 336, IFC2X3_IfcFlowMovingDeviceType_type);
    IFC2X3_IfcFilterType_type = new entity("IfcFilterType", 349, IFC2X3_IfcFlowTreatmentDeviceType_type);
    IFC2X3_IfcFireSuppressionTerminalType_type = new entity("IfcFireSuppressionTerminalType", 351, IFC2X3_IfcFlowTerminalType_type);
    IFC2X3_IfcFlowController_type = new entity("IfcFlowController", 353, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFlowFitting_type = new entity("IfcFlowFitting", 356, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFlowInstrumentType_type = new entity("IfcFlowInstrumentType", 358, IFC2X3_IfcDistributionControlElementType_type);
    IFC2X3_IfcFlowMovingDevice_type = new entity("IfcFlowMovingDevice", 362, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFlowSegment_type = new entity("IfcFlowSegment", 364, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFlowStorageDevice_type = new entity("IfcFlowStorageDevice", 366, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFlowTerminal_type = new entity("IfcFlowTerminal", 368, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFlowTreatmentDevice_type = new entity("IfcFlowTreatmentDevice", 370, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcFooting_type = new entity("IfcFooting", 376, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcMember_type = new entity("IfcMember", 492, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcPile_type = new entity("IfcPile", 552, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcPlate_type = new entity("IfcPlate", 566, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcRailing_type = new entity("IfcRailing", 642, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcRamp_type = new entity("IfcRamp", 645, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcRampFlight_type = new entity("IfcRampFlight", 646, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcRationalBezierCurve_type = new entity("IfcRationalBezierCurve", 651, IFC2X3_IfcBezierCurve_type);
    IFC2X3_IfcReinforcingElement_type = new entity("IfcReinforcingElement", 665, IFC2X3_IfcBuildingElementComponent_type);
    IFC2X3_IfcReinforcingMesh_type = new entity("IfcReinforcingMesh", 666, IFC2X3_IfcReinforcingElement_type);
    IFC2X3_IfcRoof_type = new entity("IfcRoof", 730, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcRoundedEdgeFeature_type = new entity("IfcRoundedEdgeFeature", 736, IFC2X3_IfcEdgeFeature_type);
    IFC2X3_IfcSensorType_type = new entity("IfcSensorType", 748, IFC2X3_IfcDistributionControlElementType_type);
    IFC2X3_IfcSlab_type = new entity("IfcSlab", 768, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcStair_type = new entity("IfcStair", 795, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcStairFlight_type = new entity("IfcStairFlight", 796, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcStructuralAnalysisModel_type = new entity("IfcStructuralAnalysisModel", 804, IFC2X3_IfcSystem_type);
    IFC2X3_IfcTendon_type = new entity("IfcTendon", 875, IFC2X3_IfcReinforcingElement_type);
    IFC2X3_IfcTendonAnchor_type = new entity("IfcTendonAnchor", 876, IFC2X3_IfcReinforcingElement_type);
    IFC2X3_IfcVibrationIsolatorType_type = new entity("IfcVibrationIsolatorType", 950, IFC2X3_IfcDiscreteAccessoryType_type);
    IFC2X3_IfcWall_type = new entity("IfcWall", 956, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcWallStandardCase_type = new entity("IfcWallStandardCase", 957, IFC2X3_IfcWall_type);
    IFC2X3_IfcWindow_type = new entity("IfcWindow", 965, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcActuatorType_type = new entity("IfcActuatorType", 9, IFC2X3_IfcDistributionControlElementType_type);
    IFC2X3_IfcAlarmType_type = new entity("IfcAlarmType", 20, IFC2X3_IfcDistributionControlElementType_type);
    IFC2X3_IfcBeam_type = new entity("IfcBeam", 56, IFC2X3_IfcBuildingElement_type);
    IFC2X3_IfcChamferEdgeFeature_type = new entity("IfcChamferEdgeFeature", 105, IFC2X3_IfcEdgeFeature_type);
    IFC2X3_IfcControllerType_type = new entity("IfcControllerType", 164, IFC2X3_IfcDistributionControlElementType_type);
    IFC2X3_IfcDistributionChamberElement_type = new entity("IfcDistributionChamberElement", 230, IFC2X3_IfcDistributionFlowElement_type);
    IFC2X3_IfcDistributionControlElement_type = new entity("IfcDistributionControlElement", 233, IFC2X3_IfcDistributionElement_type);
    IFC2X3_IfcElectricDistributionPoint_type = new entity("IfcElectricDistributionPoint", 283, IFC2X3_IfcFlowController_type);
    IFC2X3_IfcReinforcingBar_type = new entity("IfcReinforcingBar", 662, IFC2X3_IfcReinforcingElement_type);
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_Ifc2DCompositeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RequestID", new named_type(IFC2X3_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcActionRequest_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TheActor", new named_type(IFC2X3_IfcActorSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcActor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Role", new named_type(IFC2X3_IfcRoleEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedRole", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcActorRole_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcActuatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcActuatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC2X3_IfcAddressTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPurpose", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcAirTerminalBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAirTerminalBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcAirTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAirTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcAirToAirHeatRecoveryTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAirToAirHeatRecoveryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcAlarmTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAlarmType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcAngularDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationCurveOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OuterBoundary", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcCurve_type)), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationFillArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FillStyleTarget", new named_type(IFC2X3_IfcPoint_type), true));
        attributes.push_back(new entity::attribute("GlobalOrLocal", new named_type(IFC2X3_IfcGlobalOrLocalEnum_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationFillAreaOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Item", new named_type(IFC2X3_IfcGeometricRepresentationItem_type), false));
        attributes.push_back(new entity::attribute("TextureCoordinates", new named_type(IFC2X3_IfcTextureCoordinate_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationSurfaceOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationSymbolOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAnnotationTextOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ApplicationDeveloper", new named_type(IFC2X3_IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ApplicationFullName", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ApplicationIdentifier", new named_type(IFC2X3_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcApplication_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("AppliedValue", new named_type(IFC2X3_IfcAppliedValueSelect_type), true));
        attributes.push_back(new entity::attribute("UnitBasis", new named_type(IFC2X3_IfcMeasureWithUnit_type), true));
        attributes.push_back(new entity::attribute("ApplicableDate", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("FixedUntilDate", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAppliedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ComponentOfTotal", new named_type(IFC2X3_IfcAppliedValue_type), false));
        attributes.push_back(new entity::attribute("Components", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcAppliedValue_type)), false));
        attributes.push_back(new entity::attribute("ArithmeticOperator", new named_type(IFC2X3_IfcArithmeticOperatorEnum_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAppliedValueRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("ApprovalDateTime", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("ApprovalStatus", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ApprovalLevel", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ApprovalQualifier", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Identifier", new named_type(IFC2X3_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Actor", new named_type(IFC2X3_IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("Approval", new named_type(IFC2X3_IfcApproval_type), false));
        attributes.push_back(new entity::attribute("Role", new named_type(IFC2X3_IfcActorRole_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcApprovalActorRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ApprovedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProperty_type)), false));
        attributes.push_back(new entity::attribute("Approval", new named_type(IFC2X3_IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcApprovalPropertyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatedApproval", new named_type(IFC2X3_IfcApproval_type), false));
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IFC2X3_IfcApproval_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcApprovalRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OuterCurve", new named_type(IFC2X3_IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcArbitraryClosedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Curve", new named_type(IFC2X3_IfcBoundedCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcArbitraryOpenProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcCurve_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcArbitraryProfileDefWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("AssetID", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IFC2X3_IfcCostValue_type), false));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IFC2X3_IfcCostValue_type), false));
        attributes.push_back(new entity::attribute("TotalReplacementCost", new named_type(IFC2X3_IfcCostValue_type), false));
        attributes.push_back(new entity::attribute("Owner", new named_type(IFC2X3_IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("User", new named_type(IFC2X3_IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("ResponsiblePerson", new named_type(IFC2X3_IfcPerson_type), false));
        attributes.push_back(new entity::attribute("IncorporationDate", new named_type(IFC2X3_IfcCalendarDate_type), false));
        attributes.push_back(new entity::attribute("DepreciatedValue", new named_type(IFC2X3_IfcCostValue_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAsset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("TopFlangeWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopFlangeThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeFilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAsymmetricIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC2X3_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAxis1Placement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IFC2X3_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAxis2Placement2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC2X3_IfcDirection_type), true));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IFC2X3_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcAxis2Placement3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Degree", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_IfcCartesianPoint_type)), false));
        attributes.push_back(new entity::attribute("CurveForm", new named_type(IFC2X3_IfcBSplineCurveForm_type), false));
        attributes.push_back(new entity::attribute("ClosedCurve", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBSplineCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBeam_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBezierCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RasterFormat", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("RasterCode", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBlobTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("XLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ZLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBlock_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcBoilerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoilerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBooleanClippingResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Operator", new named_type(IFC2X3_IfcBooleanOperator_type), false));
        attributes.push_back(new entity::attribute("FirstOperand", new named_type(IFC2X3_IfcBooleanOperand_type), false));
        attributes.push_back(new entity::attribute("SecondOperand", new named_type(IFC2X3_IfcBooleanOperand_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBooleanResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcBoundaryCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearStiffnessByLengthX", new named_type(IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByLengthY", new named_type(IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByLengthZ", new named_type(IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthX", new named_type(IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthY", new named_type(IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthZ", new named_type(IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoundaryEdgeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("LinearStiffnessByAreaX", new named_type(IFC2X3_IfcModulusOfSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByAreaY", new named_type(IFC2X3_IfcModulusOfSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByAreaZ", new named_type(IFC2X3_IfcModulusOfSubgradeReactionMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoundaryFaceCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearStiffnessX", new named_type(IFC2X3_IfcLinearStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessY", new named_type(IFC2X3_IfcLinearStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessZ", new named_type(IFC2X3_IfcLinearStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessX", new named_type(IFC2X3_IfcRotationalStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessY", new named_type(IFC2X3_IfcRotationalStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessZ", new named_type(IFC2X3_IfcRotationalStiffnessMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoundaryNodeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingStiffness", new named_type(IFC2X3_IfcWarpingMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoundaryNodeConditionWarping_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcBoundedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcBoundedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Corner", new named_type(IFC2X3_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("XDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ZDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoundingBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Enclosure", new named_type(IFC2X3_IfcBoundingBox_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBoxedHalfSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ElevationOfRefHeight", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ElevationOfTerrain", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BuildingAddress", new named_type(IFC2X3_IfcPostalAddress_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuilding_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingElementComponent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingElementPart_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CompositionType", new named_type(IFC2X3_IfcElementCompositionEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingElementProxy_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcBuildingElementProxyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingElementProxyType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Elevation", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcBuildingStorey_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Girth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InternalFilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCableCarrierFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCableCarrierFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCableCarrierSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCableCarrierSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCableSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCableSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DayComponent", new named_type(IFC2X3_IfcDayInMonthNumber_type), false));
        attributes.push_back(new entity::attribute("MonthComponent", new named_type(IFC2X3_IfcMonthInYearNumber_type), false));
        attributes.push_back(new entity::attribute("YearComponent", new named_type(IFC2X3_IfcYearNumber_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCalendarDate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC2X3_IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcCartesianPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Axis1", new named_type(IFC2X3_IfcDirection_type), true));
        attributes.push_back(new entity::attribute("Axis2", new named_type(IFC2X3_IfcDirection_type), true));
        attributes.push_back(new entity::attribute("LocalOrigin", new named_type(IFC2X3_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Scale", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCartesianTransformationOperator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCartesianTransformationOperator2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Scale2", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCartesianTransformationOperator2DnonUniform_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis3", new named_type(IFC2X3_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCartesianTransformationOperator3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Scale2", new simple_type(simple_type::real_type), true));
        attributes.push_back(new entity::attribute("Scale3", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCartesianTransformationOperator3DnonUniform_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCenterLineProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Width", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Height", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcChamferEdgeFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcChillerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcChillerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCircle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCircleHollowProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCircleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Source", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Edition", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("EditionDate", new named_type(IFC2X3_IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Notation", new named_type(IFC2X3_IfcClassificationNotationFacet_type), false));
        attributes.push_back(new entity::attribute("ItemOf", new named_type(IFC2X3_IfcClassification_type), true));
        attributes.push_back(new entity::attribute("Title", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcClassificationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingItem", new named_type(IFC2X3_IfcClassificationItem_type), false));
        attributes.push_back(new entity::attribute("RelatedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcClassificationItem_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcClassificationItemRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("NotationFacets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcClassificationNotationFacet_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcClassificationNotation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("NotationValue", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcClassificationNotationFacet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ReferencedSource", new named_type(IFC2X3_IfcClassification_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcClassificationReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcClosedShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCoilTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCoilType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Red", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("Green", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("Blue", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcColourRgb_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcColourSpecification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcColumn_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcColumnTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcColumnType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcComplexProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcCompositeCurveSegment_type)), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCompositeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Transition", new named_type(IFC2X3_IfcTransitionCode_type), false));
        attributes.push_back(new entity::attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("ParentCurve", new named_type(IFC2X3_IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCompositeCurveSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC2X3_IfcProfileDef_type)), false));
        attributes.push_back(new entity::attribute("Label", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCompositeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCompressorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCompressorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCondenserTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCondenserType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Criterion", new named_type(IFC2X3_IfcConditionCriterionSelect_type), false));
        attributes.push_back(new entity::attribute("CriterionDateTime", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConditionCriterion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcConic_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcFace_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcConnectedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CurveOnRelatingElement", new named_type(IFC2X3_IfcCurveOrEdgeCurve_type), false));
        attributes.push_back(new entity::attribute("CurveOnRelatedElement", new named_type(IFC2X3_IfcCurveOrEdgeCurve_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConnectionCurveGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcConnectionGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("EccentricityInX", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EccentricityInY", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EccentricityInZ", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConnectionPointEccentricity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PointOnRelatingElement", new named_type(IFC2X3_IfcPointOrVertexPoint_type), false));
        attributes.push_back(new entity::attribute("PointOnRelatedElement", new named_type(IFC2X3_IfcPointOrVertexPoint_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConnectionPointGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("LocationAtRelatingElement", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("LocationAtRelatedElement", new named_type(IFC2X3_IfcAxis2Placement_type), true));
        attributes.push_back(new entity::attribute("ProfileOfPort", new named_type(IFC2X3_IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConnectionPortGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SurfaceOnRelatingElement", new named_type(IFC2X3_IfcSurfaceOrFaceSurface_type), false));
        attributes.push_back(new entity::attribute("SurfaceOnRelatedElement", new named_type(IFC2X3_IfcSurfaceOrFaceSurface_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConnectionSurfaceGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("ConstraintGrade", new named_type(IFC2X3_IfcConstraintEnum_type), false));
        attributes.push_back(new entity::attribute("ConstraintSource", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CreatingActor", new named_type(IFC2X3_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("UserDefinedGrade", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IFC2X3_IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedConstraints", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcConstraint_type)), false));
        attributes.push_back(new entity::attribute("LogicalAggregator", new named_type(IFC2X3_IfcLogicalOperatorEnum_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstraintAggregationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ClassifiedConstraint", new named_type(IFC2X3_IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcClassificationNotationSelect_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstraintClassificationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IFC2X3_IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedConstraints", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcConstraint_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstraintRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstructionEquipmentResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Suppliers", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("UsageRatio", new named_type(IFC2X3_IfcRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstructionMaterialResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstructionProductResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ResourceIdentifier", new named_type(IFC2X3_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("ResourceGroup", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ResourceConsumption", new named_type(IFC2X3_IfcResourceConsumptionEnum_type), true));
        attributes.push_back(new entity::attribute("BaseQuantity", new named_type(IFC2X3_IfcMeasureWithUnit_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConstructionResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcContextDependentUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcControllerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcControllerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ConversionFactor", new named_type(IFC2X3_IfcMeasureWithUnit_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcConversionBasedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCooledBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCooledBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCoolingTowerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCoolingTowerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("HourOffset", new named_type(IFC2X3_IfcHourInDay_type), false));
        attributes.push_back(new entity::attribute("MinuteOffset", new named_type(IFC2X3_IfcMinuteInHour_type), true));
        attributes.push_back(new entity::attribute("Sense", new named_type(IFC2X3_IfcAheadOrBehind_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCoordinatedUniversalTimeOffset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCostItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("SubmittedBy", new named_type(IFC2X3_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("PreparedBy", new named_type(IFC2X3_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("SubmittedOn", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("TargetUsers", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("UpdateDate", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ID", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCostScheduleTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCostSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CostType", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Condition", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCostValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCoveringTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCovering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCoveringTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCoveringType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseWidth2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("HeadWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadDepth2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadDepth3", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseWidth4", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth1", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth3", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCraneRailAShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("HeadDepth2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadDepth3", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth1", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCraneRailFShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCrewResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcCsgPrimitive3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TreeRootExpression", new named_type(IFC2X3_IfcCsgSelect_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcCsgSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingMonetaryUnit", new named_type(IFC2X3_IfcMonetaryUnit_type), false));
        attributes.push_back(new entity::attribute("RelatedMonetaryUnit", new named_type(IFC2X3_IfcMonetaryUnit_type), false));
        attributes.push_back(new entity::attribute("ExchangeRate", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("RateDateTime", new named_type(IFC2X3_IfcDateAndTime_type), false));
        attributes.push_back(new entity::attribute("RateSource", new named_type(IFC2X3_IfcLibraryInformation_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurrencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurtainWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcCurtainWallTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurtainWallType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC2X3_IfcPlane_type), false));
        attributes.push_back(new entity::attribute("OuterBoundary", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC2X3_IfcCurve_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurveBoundedPlane_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IFC2X3_IfcCurveFontOrScaledCurveFontSelect_type), true));
        attributes.push_back(new entity::attribute("CurveWidth", new named_type(IFC2X3_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("CurveColour", new named_type(IFC2X3_IfcColour_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurveStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcCurveStyleFontPattern_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurveStyleFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IFC2X3_IfcCurveStyleFontSelect_type), false));
        attributes.push_back(new entity::attribute("CurveFontScaling", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurveStyleFontAndScaling_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VisibleSegmentLength", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InvisibleSegmentLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcCurveStyleFontPattern_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcDamperTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDamperType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DateComponent", new named_type(IFC2X3_IfcCalendarDate_type), false));
        attributes.push_back(new entity::attribute("TimeComponent", new named_type(IFC2X3_IfcLocalTime_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDateAndTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Definition", new named_type(IFC2X3_IfcDefinedSymbolSelect_type), false));
        attributes.push_back(new entity::attribute("Target", new named_type(IFC2X3_IfcCartesianTransformationOperator2D_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDefinedSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ParentProfile", new named_type(IFC2X3_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Operator", new named_type(IFC2X3_IfcCartesianTransformationOperator2D_type), false));
        attributes.push_back(new entity::attribute("Label", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDerivedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcDerivedUnitElement_type)), false));
        attributes.push_back(new entity::attribute("UnitType", new named_type(IFC2X3_IfcDerivedUnitEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDerivedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcNamedUnit_type), false));
        attributes.push_back(new entity::attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDerivedUnitElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDiameterDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDimensionCalloutRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDimensionCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDimensionCurveDirectedCallout_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Role", new named_type(IFC2X3_IfcDimensionExtentUsage_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDimensionCurveTerminator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDimensionPair_type->set_attributes(attributes, derived);
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
        IFC2X3_IfcDimensionalExponents_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new simple_type(simple_type::real_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDirection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDiscreteAccessory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDiscreteAccessoryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionChamberElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcDistributionChamberElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionChamberElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ControlElementId", new named_type(IFC2X3_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionControlElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionControlElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionFlowElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionFlowElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FlowDirection", new named_type(IFC2X3_IfcFlowDirectionEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDistributionPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("FileExtension", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MimeContentType", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MimeSubtype", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDocumentElectronicFormat_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new entity::attribute("DocumentId", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("DocumentReferences", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcDocumentReference_type)), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("IntendedUse", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Scope", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Revision", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DocumentOwner", new named_type(IFC2X3_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IFC2X3_IfcDateAndTime_type), true));
        attributes.push_back(new entity::attribute("LastRevisionTime", new named_type(IFC2X3_IfcDateAndTime_type), true));
        attributes.push_back(new entity::attribute("ElectronicFormat", new named_type(IFC2X3_IfcDocumentElectronicFormat_type), true));
        attributes.push_back(new entity::attribute("ValidFrom", new named_type(IFC2X3_IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("ValidUntil", new named_type(IFC2X3_IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("Confidentiality", new named_type(IFC2X3_IfcDocumentConfidentialityEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC2X3_IfcDocumentStatusEnum_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDocumentInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingDocument", new named_type(IFC2X3_IfcDocumentInformation_type), false));
        attributes.push_back(new entity::attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcDocumentInformation_type)), false));
        attributes.push_back(new entity::attribute("RelationshipType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDocumentInformationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDocumentReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDoor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomOffset", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningOffset", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdOffset", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC2X3_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDoorLiningProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PanelDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PanelOperation", new named_type(IFC2X3_IfcDoorPanelOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelWidth", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IFC2X3_IfcDoorPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC2X3_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDoorPanelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC2X3_IfcDoorStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IFC2X3_IfcDoorStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDoorStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Contents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcDraughtingCalloutElement_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDraughtingCallout_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingDraughtingCallout", new named_type(IFC2X3_IfcDraughtingCallout_type), false));
        attributes.push_back(new entity::attribute("RelatedDraughtingCallout", new named_type(IFC2X3_IfcDraughtingCallout_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDraughtingCalloutRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDraughtingPreDefinedColour_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDraughtingPreDefinedCurveFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcDraughtingPreDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcDuctFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDuctFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcDuctSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDuctSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcDuctSilencerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcDuctSilencerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeStart", new named_type(IFC2X3_IfcVertex_type), false));
        attributes.push_back(new entity::attribute("EdgeEnd", new named_type(IFC2X3_IfcVertex_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeGeometry", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEdgeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FeatureLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEdgeFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcOrientedEdge_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcEdgeLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElectricApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricApplianceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DistributionPointFunction", new named_type(IFC2X3_IfcElectricDistributionPointFunctionEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedFunction", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricDistributionPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElectricFlowStorageDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricFlowStorageDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElectricGeneratorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricGeneratorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElectricHeaterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricHeaterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElectricMotorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricMotorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElectricTimeControlTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricTimeControlType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("ElectricCurrentType", new named_type(IFC2X3_IfcElectricCurrentEnum_type), true));
        attributes.push_back(new entity::attribute("InputVoltage", new named_type(IFC2X3_IfcElectricVoltageMeasure_type), false));
        attributes.push_back(new entity::attribute("InputFrequency", new named_type(IFC2X3_IfcFrequencyMeasure_type), false));
        attributes.push_back(new entity::attribute("FullLoadCurrent", new named_type(IFC2X3_IfcElectricCurrentMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumCircuitCurrent", new named_type(IFC2X3_IfcElectricCurrentMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumPowerInput", new named_type(IFC2X3_IfcPowerMeasure_type), true));
        attributes.push_back(new entity::attribute("RatedPowerInput", new named_type(IFC2X3_IfcPowerMeasure_type), true));
        attributes.push_back(new entity::attribute("InputPhase", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricalBaseProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricalCircuit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElectricalElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Tag", new named_type(IFC2X3_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IFC2X3_IfcAssemblyPlaceEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcElementAssemblyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElementAssembly_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElementComponent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElementComponentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MethodOfMeasurement", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPhysicalQuantity_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElementQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ElementType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcElementarySurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SemiAxis1", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SemiAxis2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEllipse_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SemiAxis1", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SemiAxis2", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEllipseProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEnergyConversionDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEnergyConversionDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EnergySequence", new named_type(IFC2X3_IfcEnergySequenceEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedEnergySequence", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEnergyProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ImpactType", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Category", new named_type(IFC2X3_IfcEnvironmentalImpactCategoryEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedCategory", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEnvironmentalImpactValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEquipmentElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEquipmentStandard_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcEvaporativeCoolerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEvaporativeCoolerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcEvaporatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcEvaporatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ExtendedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProperty_type)), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExtendedMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Location", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ItemReference", new named_type(IFC2X3_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExternalReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExternallyDefinedHatchStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExternallyDefinedSurfaceStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExternallyDefinedSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExternallyDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ExtrudedDirection", new named_type(IFC2X3_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcExtrudedAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcFaceBound_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcFace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcConnectedFaceSet_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcFaceBasedSurfaceModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Bound", new named_type(IFC2X3_IfcLoop_type), false));
        attributes.push_back(new entity::attribute("Orientation", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFaceBound_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFaceOuterBound_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FaceSurface", new named_type(IFC2X3_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFaceSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcFacetedBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcClosedShell_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFacetedBrepWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TensionFailureX", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionFailureY", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionFailureZ", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureX", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureY", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureZ", new named_type(IFC2X3_IfcForceMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFailureConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcFanTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFanType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFeatureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFeatureElementAddition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFeatureElementSubtraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcFillStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFillAreaStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("HatchLineAppearance", new named_type(IFC2X3_IfcCurveStyle_type), false));
        attributes.push_back(new entity::attribute("StartOfNextHatchLine", new named_type(IFC2X3_IfcHatchLineDistanceSelect_type), false));
        attributes.push_back(new entity::attribute("PointOfReferenceHatchLine", new named_type(IFC2X3_IfcCartesianPoint_type), true));
        attributes.push_back(new entity::attribute("PatternStart", new named_type(IFC2X3_IfcCartesianPoint_type), true));
        attributes.push_back(new entity::attribute("HatchLineAngle", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFillAreaStyleHatching_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Symbol", new named_type(IFC2X3_IfcAnnotationSymbolOccurrence_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcFillAreaStyleTileSymbolWithStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TilingPattern", new named_type(IFC2X3_IfcOneDirectionRepeatFactor_type), false));
        attributes.push_back(new entity::attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcFillAreaStyleTileShapeSelect_type)), false));
        attributes.push_back(new entity::attribute("TilingScale", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFillAreaStyleTiles_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcFilterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFilterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcFireSuppressionTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFireSuppressionTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowController_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowControllerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcFlowInstrumentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowInstrumentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcFlowMeterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowMeterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowMovingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowMovingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowStorageDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowStorageDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowTreatmentDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFlowTreatmentDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new entity::attribute("PropertySource", new named_type(IFC2X3_IfcPropertySourceEnum_type), false));
        attributes.push_back(new entity::attribute("FlowConditionTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("VelocityTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("FlowrateTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("Fluid", new named_type(IFC2X3_IfcMaterial_type), false));
        attributes.push_back(new entity::attribute("PressureTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPropertySource", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("TemperatureSingleValue", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("WetBulbTemperatureSingleValue", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("WetBulbTemperatureTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("TemperatureTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("FlowrateSingleValue", new named_type(IFC2X3_IfcDerivedMeasureValue_type), true));
        attributes.push_back(new entity::attribute("FlowConditionSingleValue", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("VelocitySingleValue", new named_type(IFC2X3_IfcLinearVelocityMeasure_type), true));
        attributes.push_back(new entity::attribute("PressureSingleValue", new named_type(IFC2X3_IfcPressureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(19);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFluidFlowProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcFootingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFooting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CombustionTemperature", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("CarbonContent", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("LowerHeatingValue", new named_type(IFC2X3_IfcHeatingValueMeasure_type), true));
        attributes.push_back(new entity::attribute("HigherHeatingValue", new named_type(IFC2X3_IfcHeatingValueMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFuelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFurnishingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFurnishingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFurnitureStandard_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IFC2X3_IfcAssemblyPlaceEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcFurnitureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcGasTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGasTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MolecularWeight", new named_type(IFC2X3_IfcMolecularWeightMeasure_type), true));
        attributes.push_back(new entity::attribute("Porosity", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("MassDensity", new named_type(IFC2X3_IfcMassDensityMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGeneralMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PhysicalWeight", new named_type(IFC2X3_IfcMassPerLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Perimeter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumPlateThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumPlateThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGeneralProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcGeometricCurveSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CoordinateSpaceDimension", new named_type(IFC2X3_IfcDimensionCount_type), false));
        attributes.push_back(new entity::attribute("Precision", new simple_type(simple_type::real_type), true));
        attributes.push_back(new entity::attribute("WorldCoordinateSystem", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("TrueNorth", new named_type(IFC2X3_IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGeometricRepresentationContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcGeometricRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ParentContext", new named_type(IFC2X3_IfcGeometricRepresentationContext_type), false));
        attributes.push_back(new entity::attribute("TargetScale", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("TargetView", new named_type(IFC2X3_IfcGeometricProjectionEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedTargetView", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGeometricRepresentationSubContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcGeometricSetSelect_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcGeometricSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcGridAxis_type)), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGrid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("AxisTag", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AxisCurve", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IFC2X3_IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGridAxis_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementLocation", new named_type(IFC2X3_IfcVirtualGridIntersection_type), false));
        attributes.push_back(new entity::attribute("PlacementRefDirection", new named_type(IFC2X3_IfcVirtualGridIntersection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGridPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BaseSurface", new named_type(IFC2X3_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("AgreementFlag", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcHalfSpaceSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcHeatExchangerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcHeatExchangerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcHumidifierTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcHumidifierType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("UpperVaporResistanceFactor", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("LowerVaporResistanceFactor", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("IsothermalMoistureCapacity", new named_type(IFC2X3_IfcIsothermalMoistureCapacityMeasure_type), true));
        attributes.push_back(new entity::attribute("VaporPermeability", new named_type(IFC2X3_IfcVaporPermeabilityMeasure_type), true));
        attributes.push_back(new entity::attribute("MoistureDiffusivity", new named_type(IFC2X3_IfcMoistureDiffusivityMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcHygroscopicMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OverallDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("UrlReference", new named_type(IFC2X3_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcImageTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("InventoryType", new named_type(IFC2X3_IfcInventoryTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Jurisdiction", new named_type(IFC2X3_IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPerson_type)), false));
        attributes.push_back(new entity::attribute("LastUpdateDate", new named_type(IFC2X3_IfcCalendarDate_type), false));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IFC2X3_IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IFC2X3_IfcCostValue_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcInventory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcIrregularTimeSeriesValue_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcIrregularTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeStamp", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcIrregularTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcJunctionBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcJunctionBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LegSlope", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SkillSet", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLaborResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcLampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLampType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Publisher", new named_type(IFC2X3_IfcOrganization_type), true));
        attributes.push_back(new entity::attribute("VersionDate", new named_type(IFC2X3_IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("LibraryReference", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcLibraryReference_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLibraryInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLibraryReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MainPlaneAngle", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), false));
        attributes.push_back(new entity::attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcPlaneAngleMeasure_type)), false));
        attributes.push_back(new entity::attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLuminousIntensityDistributionMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightDistributionData_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcLightFixtureTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightFixtureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LightDistributionCurve", new named_type(IFC2X3_IfcLightDistributionCurveEnum_type), false));
        attributes.push_back(new entity::attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLightDistributionData_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightIntensityDistribution_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LightColour", new named_type(IFC2X3_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("AmbientIntensity", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Intensity", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightSource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightSourceAmbient_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC2X3_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightSourceDirectional_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement3D_type), false));
        attributes.push_back(new entity::attribute("ColourAppearance", new named_type(IFC2X3_IfcColourRgb_type), true));
        attributes.push_back(new entity::attribute("ColourTemperature", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), false));
        attributes.push_back(new entity::attribute("LuminousFlux", new named_type(IFC2X3_IfcLuminousFluxMeasure_type), false));
        attributes.push_back(new entity::attribute("LightEmissionSource", new named_type(IFC2X3_IfcLightEmissionSourceEnum_type), false));
        attributes.push_back(new entity::attribute("LightDistributionDataSource", new named_type(IFC2X3_IfcLightDistributionDataSourceSelect_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightSourceGoniometric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ConstantAttenuation", new named_type(IFC2X3_IfcReal_type), false));
        attributes.push_back(new entity::attribute("DistanceAttenuation", new named_type(IFC2X3_IfcReal_type), false));
        attributes.push_back(new entity::attribute("QuadricAttenuation", new named_type(IFC2X3_IfcReal_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightSourcePositional_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC2X3_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("ConcentrationExponent", new named_type(IFC2X3_IfcReal_type), true));
        attributes.push_back(new entity::attribute("SpreadAngle", new named_type(IFC2X3_IfcPositivePlaneAngleMeasure_type), false));
        attributes.push_back(new entity::attribute("BeamWidthAngle", new named_type(IFC2X3_IfcPositivePlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLightSourceSpot_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Pnt", new named_type(IFC2X3_IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Dir", new named_type(IFC2X3_IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcLinearDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementRelTo", new named_type(IFC2X3_IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("RelativePlacement", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLocalPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("HourComponent", new named_type(IFC2X3_IfcHourInDay_type), false));
        attributes.push_back(new entity::attribute("MinuteComponent", new named_type(IFC2X3_IfcMinuteInHour_type), true));
        attributes.push_back(new entity::attribute("SecondComponent", new named_type(IFC2X3_IfcSecondInMinute_type), true));
        attributes.push_back(new entity::attribute("Zone", new named_type(IFC2X3_IfcCoordinatedUniversalTimeOffset_type), true));
        attributes.push_back(new entity::attribute("DaylightSavingOffset", new named_type(IFC2X3_IfcDaylightSavingHour_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcLocalTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Outer", new named_type(IFC2X3_IfcClosedShell_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcManifoldSolidBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappingSource", new named_type(IFC2X3_IfcRepresentationMap_type), false));
        attributes.push_back(new entity::attribute("MappingTarget", new named_type(IFC2X3_IfcCartesianTransformationOperator_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMappedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcClassificationNotationSelect_type)), false));
        attributes.push_back(new entity::attribute("ClassifiedMaterial", new named_type(IFC2X3_IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMaterialClassificationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RepresentedMaterial", new named_type(IFC2X3_IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMaterialDefinitionRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Material", new named_type(IFC2X3_IfcMaterial_type), true));
        attributes.push_back(new entity::attribute("LayerThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("IsVentilated", new named_type(IFC2X3_IfcLogical_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMaterialLayer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcMaterialLayer_type)), false));
        attributes.push_back(new entity::attribute("LayerSetName", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMaterialLayerSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ForLayerSet", new named_type(IFC2X3_IfcMaterialLayerSet_type), false));
        attributes.push_back(new entity::attribute("LayerSetDirection", new named_type(IFC2X3_IfcLayerSetDirectionEnum_type), false));
        attributes.push_back(new entity::attribute("DirectionSense", new named_type(IFC2X3_IfcDirectionSenseEnum_type), false));
        attributes.push_back(new entity::attribute("OffsetFromReferenceLine", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMaterialLayerSetUsage_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcMaterial_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcMaterialList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Material", new named_type(IFC2X3_IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ValueComponent", new named_type(IFC2X3_IfcValue_type), false));
        attributes.push_back(new entity::attribute("UnitComponent", new named_type(IFC2X3_IfcUnit_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMeasureWithUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("CompressiveStrength", new named_type(IFC2X3_IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("MaxAggregateSize", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("AdmixturesDescription", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Workability", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("ProtectivePoreRatio", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("WaterImpermeability", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMechanicalConcreteMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMechanicalFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMechanicalFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DynamicViscosity", new named_type(IFC2X3_IfcDynamicViscosityMeasure_type), true));
        attributes.push_back(new entity::attribute("YoungModulus", new named_type(IFC2X3_IfcModulusOfElasticityMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearModulus", new named_type(IFC2X3_IfcModulusOfElasticityMeasure_type), true));
        attributes.push_back(new entity::attribute("PoissonRatio", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalExpansionCoefficient", new named_type(IFC2X3_IfcThermalExpansionCoefficientMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMechanicalMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("YieldStress", new named_type(IFC2X3_IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("UltimateStress", new named_type(IFC2X3_IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("UltimateStrain", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("HardeningModule", new named_type(IFC2X3_IfcModulusOfElasticityMeasure_type), true));
        attributes.push_back(new entity::attribute("ProportionalStress", new named_type(IFC2X3_IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("PlasticStrain", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Relaxations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcRelaxation_type)), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMechanicalSteelMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcMemberTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMemberType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Benchmark", new named_type(IFC2X3_IfcBenchmarkEnum_type), false));
        attributes.push_back(new entity::attribute("ValueSource", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DataValue", new named_type(IFC2X3_IfcMetricValueSelect_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMetric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Currency", new named_type(IFC2X3_IfcCurrencyEnum_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcMonetaryUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcMotorConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMotorConnectionType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MoveFrom", new named_type(IFC2X3_IfcSpatialStructureElement_type), false));
        attributes.push_back(new entity::attribute("MoveTo", new named_type(IFC2X3_IfcSpatialStructureElement_type), false));
        attributes.push_back(new entity::attribute("PunchList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcText_type)), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcMove_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Dimensions", new named_type(IFC2X3_IfcDimensionalExponents_type), false));
        attributes.push_back(new entity::attribute("UnitType", new named_type(IFC2X3_IfcUnitEnum_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcNamedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ObjectType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcObjectDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcObjectPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BenchmarkValues", new named_type(IFC2X3_IfcMetric_type), true));
        attributes.push_back(new entity::attribute("ResultValues", new named_type(IFC2X3_IfcMetric_type), true));
        attributes.push_back(new entity::attribute("ObjectiveQualifier", new named_type(IFC2X3_IfcObjectiveEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedQualifier", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcObjective_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcOccupantTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOccupant_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOffsetCurve2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IFC2X3_IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOffsetCurve3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RepeatFactor", new named_type(IFC2X3_IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcOneDirectionRepeatFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcOpenShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOpeningElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("VisibleTransmittance", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SolarTransmittance", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalIrTransmittance", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalIrEmissivityBack", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalIrEmissivityFront", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("VisibleReflectanceBack", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("VisibleReflectanceFront", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SolarReflectanceFront", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SolarReflectanceBack", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOpticalMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ActionID", new named_type(IFC2X3_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOrderAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Id", new named_type(IFC2X3_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingOrganization", new named_type(IFC2X3_IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcOrganization_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOrganizationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeElement", new named_type(IFC2X3_IfcEdge_type), false));
        attributes.push_back(new entity::attribute("Orientation", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOrientedEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcOutletTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOutletType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("OwningUser", new named_type(IFC2X3_IfcPersonAndOrganization_type), false));
        attributes.push_back(new entity::attribute("OwningApplication", new named_type(IFC2X3_IfcApplication_type), false));
        attributes.push_back(new entity::attribute("State", new named_type(IFC2X3_IfcStateEnum_type), true));
        attributes.push_back(new entity::attribute("ChangeAction", new named_type(IFC2X3_IfcChangeActionEnum_type), false));
        attributes.push_back(new entity::attribute("LastModifiedDate", new named_type(IFC2X3_IfcTimeStamp_type), true));
        attributes.push_back(new entity::attribute("LastModifyingUser", new named_type(IFC2X3_IfcPersonAndOrganization_type), true));
        attributes.push_back(new entity::attribute("LastModifyingApplication", new named_type(IFC2X3_IfcApplication_type), true));
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IFC2X3_IfcTimeStamp_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcOwnerHistory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement2D_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcParameterizedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcOrientedEdge_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPath_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LifeCyclePhase", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPerformanceHistory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC2X3_IfcPermeableCoveringOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IFC2X3_IfcWindowPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("FrameDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FrameThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC2X3_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPermeableCoveringProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PermitID", new named_type(IFC2X3_IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPermit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Id", new named_type(IFC2X3_IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("FamilyName", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("GivenName", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPerson_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ThePerson", new named_type(IFC2X3_IfcPerson_type), false));
        attributes.push_back(new entity::attribute("TheOrganization", new named_type(IFC2X3_IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcActorRole_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPersonAndOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPhysicalQuantity_type)), false));
        attributes.push_back(new entity::attribute("Discrimination", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Quality", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Usage", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPhysicalComplexQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPhysicalQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcNamedUnit_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPhysicalSimpleQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcPileTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IFC2X3_IfcPileConstructionEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPile_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcPipeFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPipeFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcPipeSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPipeSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Width", new named_type(IFC2X3_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("Height", new named_type(IFC2X3_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ColourComponents", new named_type(IFC2X3_IfcInteger_type), false));
        attributes.push_back(new entity::attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::binary_type)), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPixelTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Location", new named_type(IFC2X3_IfcCartesianPoint_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Placement", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPlanarBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SizeInX", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SizeInY", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPlanarExtent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPlane_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPlate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcPlateTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPlateType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("PointParameter", new named_type(IFC2X3_IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPointOnCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC2X3_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("PointParameterU", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("PointParameterV", new named_type(IFC2X3_IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPointOnSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC2X3_IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPolyLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement3D_type), false));
        attributes.push_back(new entity::attribute("PolygonalBoundary", new named_type(IFC2X3_IfcBoundedCurve_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPolygonalBoundedHalfSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPolyline_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("InternalLocation", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PostalBox", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Town", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Region", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PostalCode", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Country", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPostalAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedColour_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedCurveFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedDimensionSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedPointMarkerSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedTerminatorSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPreDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcLayeredItem_type)), false));
        attributes.push_back(new entity::attribute("Identifier", new named_type(IFC2X3_IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPresentationLayerAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("LayerOn", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("LayerFrozen", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("LayerBlocked", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC2X3_IfcPresentationStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPresentationLayerWithStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPresentationStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPresentationStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcPresentationStyleAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ProcedureID", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("ProcedureType", new named_type(IFC2X3_IfcProcedureTypeEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedProcedureType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProcedure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ObjectPlacement", new named_type(IFC2X3_IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("Representation", new named_type(IFC2X3_IfcProductRepresentation_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProductDefinitionShape_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcRepresentation_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProductRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("SpecificHeatCapacity", new named_type(IFC2X3_IfcSpecificHeatCapacityMeasure_type), true));
        attributes.push_back(new entity::attribute("N20Content", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("COContent", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("CO2Content", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProductsOfCombustionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProfileType", new named_type(IFC2X3_IfcProfileTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ProfileName", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProfileName", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ProfileDefinition", new named_type(IFC2X3_IfcProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Phase", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcRepresentationContext_type)), false));
        attributes.push_back(new entity::attribute("UnitsInContext", new named_type(IFC2X3_IfcUnitAssignment_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ID", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcProjectOrderTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProjectOrder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Records", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcRelAssignsToProjectOrder_type)), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcProjectOrderRecordTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProjectOrderRecord_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProjectionCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProjectionElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("UpperBoundValue", new named_type(IFC2X3_IfcValue_type), true));
        attributes.push_back(new entity::attribute("LowerBoundValue", new named_type(IFC2X3_IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyBoundedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IFC2X3_IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProperty_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyConstraintRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DependingProperty", new named_type(IFC2X3_IfcProperty_type), false));
        attributes.push_back(new entity::attribute("DependantProperty", new named_type(IFC2X3_IfcProperty_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("Expression", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyDependencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("EnumerationReference", new named_type(IFC2X3_IfcPropertyEnumeration_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyEnumeratedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyEnumeration_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyListValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PropertyReference", new named_type(IFC2X3_IfcObjectReferenceSelect_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyReferenceValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertySetDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("NominalValue", new named_type(IFC2X3_IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertySingleValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Expression", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("DefiningUnit", new named_type(IFC2X3_IfcUnit_type), true));
        attributes.push_back(new entity::attribute("DefinedUnit", new named_type(IFC2X3_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPropertyTableValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcProtectiveDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProtectiveDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProxyType", new named_type(IFC2X3_IfcObjectTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Tag", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcProxy_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcPumpTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcPumpType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AreaValue", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcQuantityArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CountValue", new named_type(IFC2X3_IfcCountMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcQuantityCount_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LengthValue", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcQuantityLength_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TimeValue", new named_type(IFC2X3_IfcTimeMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcQuantityTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("VolumeValue", new named_type(IFC2X3_IfcVolumeMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcQuantityVolume_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightValue", new named_type(IFC2X3_IfcMassMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcQuantityWeight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcRadiusDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcRailingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRailing_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcRailingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRailingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ShapeType", new named_type(IFC2X3_IfcRampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRamp_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRampFlight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcRampFlightTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRampFlightType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new simple_type(simple_type::real_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRationalBezierCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerFilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OuterFilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRectangleHollowProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("XDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRectangleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("XLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Height", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRectangularPyramid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IFC2X3_IfcSurface_type), false));
        attributes.push_back(new entity::attribute("U1", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("V1", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("U2", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("V2", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("Usense", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Vsense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRectangularTrimmedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ReferencedDocument", new named_type(IFC2X3_IfcDocumentSelect_type), false));
        attributes.push_back(new entity::attribute("ReferencingValues", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcAppliedValue_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcReferencesValueDocument_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeStep", new named_type(IFC2X3_IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcTimeSeriesValue_type)), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRegularTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TotalCrossSectionArea", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IFC2X3_IfcReinforcingBarSurfaceEnum_type), true));
        attributes.push_back(new entity::attribute("EffectiveDepth", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalBarDiameter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarCount", new named_type(IFC2X3_IfcCountMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcReinforcementBarProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DefinitionType", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcSectionReinforcementProperties_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcReinforcementDefinitionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("BarLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarRole", new named_type(IFC2X3_IfcReinforcingBarRoleEnum_type), false));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IFC2X3_IfcReinforcingBarSurfaceEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcReinforcingBar_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcReinforcingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("MeshLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MeshWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarNominalDiameter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransverseBarNominalDiameter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalBarCrossSectionArea", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("TransverseBarCrossSectionArea", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalBarSpacing", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransverseBarSpacing", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcReinforcingMesh_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAggregates_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcObjectDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatedObjectsType", new named_type(IFC2X3_IfcObjectTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssigns_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TimeForTask", new named_type(IFC2X3_IfcScheduleTimeControl_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsTasks_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingActor", new named_type(IFC2X3_IfcActor_type), false));
        attributes.push_back(new entity::attribute("ActingRole", new named_type(IFC2X3_IfcActorRole_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToActor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingControl", new named_type(IFC2X3_IfcControl_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingGroup", new named_type(IFC2X3_IfcGroup_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IFC2X3_IfcProcess_type), false));
        attributes.push_back(new entity::attribute("QuantityInProcess", new named_type(IFC2X3_IfcMeasureWithUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingProduct", new named_type(IFC2X3_IfcProduct_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToProjectOrder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingResource", new named_type(IFC2X3_IfcResource_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssignsToResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcRoot_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociates_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingAppliedValue", new named_type(IFC2X3_IfcAppliedValue_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesAppliedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IFC2X3_IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingClassification", new named_type(IFC2X3_IfcClassificationNotationSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Intent", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IFC2X3_IfcConstraint_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingDocument", new named_type(IFC2X3_IfcDocumentSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesDocument_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingLibrary", new named_type(IFC2X3_IfcLibrarySelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesLibrary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingMaterial", new named_type(IFC2X3_IfcMaterialSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingProfileProperties", new named_type(IFC2X3_IfcProfileProperties_type), false));
        attributes.push_back(new entity::attribute("ProfileSectionLocation", new named_type(IFC2X3_IfcShapeAspect_type), true));
        attributes.push_back(new entity::attribute("ProfileOrientation", new named_type(IFC2X3_IfcOrientationSelect_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelAssociatesProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnects_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IFC2X3_IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC2X3_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IFC2X3_IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new simple_type(simple_type::integer_type)), false));
        attributes.push_back(new entity::attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new simple_type(simple_type::integer_type)), false));
        attributes.push_back(new entity::attribute("RelatedConnectionType", new named_type(IFC2X3_IfcConnectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("RelatingConnectionType", new named_type(IFC2X3_IfcConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsPathElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IFC2X3_IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IFC2X3_IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsPortToElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IFC2X3_IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedPort", new named_type(IFC2X3_IfcPort_type), false));
        attributes.push_back(new entity::attribute("RealizingElement", new named_type(IFC2X3_IfcElement_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsPorts_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC2X3_IfcStructuralActivityAssignmentSelect_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralActivity", new named_type(IFC2X3_IfcStructuralActivity_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsStructuralActivity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC2X3_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralMember", new named_type(IFC2X3_IfcStructuralMember_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsStructuralElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("RelatingStructuralMember", new named_type(IFC2X3_IfcStructuralMember_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralConnection", new named_type(IFC2X3_IfcStructuralConnection_type), false));
        attributes.push_back(new entity::attribute("AppliedCondition", new named_type(IFC2X3_IfcBoundaryCondition_type), true));
        attributes.push_back(new entity::attribute("AdditionalConditions", new named_type(IFC2X3_IfcStructuralConnectionCondition_type), true));
        attributes.push_back(new entity::attribute("SupportedLength", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ConditionCoordinateSystem", new named_type(IFC2X3_IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsStructuralMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ConnectionConstraint", new named_type(IFC2X3_IfcConnectionGeometry_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsWithEccentricity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcElement_type)), false));
        attributes.push_back(new entity::attribute("ConnectionType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelConnectsWithRealizingElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProduct_type)), false));
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IFC2X3_IfcSpatialStructureElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelContainedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingBuildingElement", new named_type(IFC2X3_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelCoversBldgElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedSpace", new named_type(IFC2X3_IfcSpace_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelCoversSpaces_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IFC2X3_IfcObjectDefinition_type), false));
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcObjectDefinition_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelDecomposes_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcObject_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelDefines_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingPropertyDefinition", new named_type(IFC2X3_IfcPropertySetDefinition_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelDefinesByProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingType", new named_type(IFC2X3_IfcTypeObject_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelDefinesByType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingOpeningElement", new named_type(IFC2X3_IfcOpeningElement_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IFC2X3_IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelFillsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcDistributionControlElement_type)), false));
        attributes.push_back(new entity::attribute("RelatingFlowElement", new named_type(IFC2X3_IfcDistributionFlowElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelFlowControlElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DailyInteraction", new named_type(IFC2X3_IfcCountMeasure_type), true));
        attributes.push_back(new entity::attribute("ImportanceRating", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("LocationOfInteraction", new named_type(IFC2X3_IfcSpatialStructureElement_type), true));
        attributes.push_back(new entity::attribute("RelatedSpaceProgram", new named_type(IFC2X3_IfcSpaceProgram_type), false));
        attributes.push_back(new entity::attribute("RelatingSpaceProgram", new named_type(IFC2X3_IfcSpaceProgram_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelInteractionRequirements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelNests_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelOccupiesSpaces_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OverridingProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelOverridesProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IFC2X3_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedFeatureElement", new named_type(IFC2X3_IfcFeatureElementAddition_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelProjectsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcProduct_type)), false));
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IFC2X3_IfcSpatialStructureElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelReferencedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelSchedulesCostItems_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IFC2X3_IfcProcess_type), false));
        attributes.push_back(new entity::attribute("RelatedProcess", new named_type(IFC2X3_IfcProcess_type), false));
        attributes.push_back(new entity::attribute("TimeLag", new named_type(IFC2X3_IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("SequenceType", new named_type(IFC2X3_IfcSequenceEnum_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelSequence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingSystem", new named_type(IFC2X3_IfcSystem_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcSpatialStructureElement_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelServicesBuildings_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingSpace", new named_type(IFC2X3_IfcSpace_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IFC2X3_IfcElement_type), true));
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IFC2X3_IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("PhysicalOrVirtualBoundary", new named_type(IFC2X3_IfcPhysicalOrVirtualEnum_type), false));
        attributes.push_back(new entity::attribute("InternalOrExternalBoundary", new named_type(IFC2X3_IfcInternalOrExternalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelSpaceBoundary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingBuildingElement", new named_type(IFC2X3_IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedOpeningElement", new named_type(IFC2X3_IfcFeatureElementSubtraction_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelVoidsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelaxationValue", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("InitialStress", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRelaxation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ContextOfItems", new named_type(IFC2X3_IfcRepresentationContext_type), false));
        attributes.push_back(new entity::attribute("RepresentationIdentifier", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationType", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcRepresentationItem_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ContextIdentifier", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ContextType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRepresentationContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappingOrigin", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("MappedRepresentation", new named_type(IFC2X3_IfcRepresentation_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRepresentationMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Axis", new named_type(IFC2X3_IfcAxis1Placement_type), false));
        attributes.push_back(new entity::attribute("Angle", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRevolvedAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RibHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RibWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RibSpacing", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Direction", new named_type(IFC2X3_IfcRibPlateDirectionEnum_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRibPlateProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Height", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRightCircularCone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Height", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRightCircularCylinder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ShapeType", new named_type(IFC2X3_IfcRoofTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRoof_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("GlobalId", new named_type(IFC2X3_IfcGloballyUniqueId_type), false));
        attributes.push_back(new entity::attribute("OwnerHistory", new named_type(IFC2X3_IfcOwnerHistory_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRoot_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRoundedEdgeFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RoundingRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcRoundedRectangleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Prefix", new named_type(IFC2X3_IfcSIPrefix_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcSIUnitName_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSIUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSanitaryTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSanitaryTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(18);
        attributes.push_back(new entity::attribute("ActualStart", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("EarlyStart", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("LateStart", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ScheduleStart", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ActualFinish", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("EarlyFinish", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("LateFinish", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ScheduleFinish", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ScheduleDuration", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("ActualDuration", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("RemainingTime", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("FreeFloat", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("IsCritical", new simple_type(simple_type::boolean_type), true));
        attributes.push_back(new entity::attribute("StatusTime", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("StartFloat", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("FinishFloat", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("Completion", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(23);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcScheduleTimeControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SectionType", new named_type(IFC2X3_IfcSectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("StartProfile", new named_type(IFC2X3_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("EndProfile", new named_type(IFC2X3_IfcProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSectionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LongitudinalStartPosition", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalEndPosition", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransversePosition", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ReinforcementRole", new named_type(IFC2X3_IfcReinforcingBarRoleEnum_type), false));
        attributes.push_back(new entity::attribute("SectionDefinition", new named_type(IFC2X3_IfcSectionProperties_type), false));
        attributes.push_back(new entity::attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcReinforcementBarProperties_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSectionReinforcementProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SpineCurve", new named_type(IFC2X3_IfcCompositeCurve_type), false));
        attributes.push_back(new entity::attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_IfcProfileDef_type)), false));
        attributes.push_back(new entity::attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_IfcAxis2Placement3D_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSectionedSpine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSensorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSensorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ServiceLifeType", new named_type(IFC2X3_IfcServiceLifeTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ServiceLifeDuration", new named_type(IFC2X3_IfcTimeMeasure_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcServiceLife_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcServiceLifeFactorTypeEnum_type), false));
        attributes.push_back(new entity::attribute("UpperValue", new named_type(IFC2X3_IfcMeasureValue_type), true));
        attributes.push_back(new entity::attribute("MostUsedValue", new named_type(IFC2X3_IfcMeasureValue_type), false));
        attributes.push_back(new entity::attribute("LowerValue", new named_type(IFC2X3_IfcMeasureValue_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcServiceLifeFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcShapeModel_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("ProductDefinitional", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("PartOfProductDefinitionShape", new named_type(IFC2X3_IfcProductDefinitionShape_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcShapeAspect_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcShapeModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcShapeRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcShell_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcShellBasedSurfaceModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSimpleProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RefLatitude", new named_type(IFC2X3_IfcCompoundPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RefLongitude", new named_type(IFC2X3_IfcCompoundPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RefElevation", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LandTitleNumber", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SiteAddress", new named_type(IFC2X3_IfcPostalAddress_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSite_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSlabTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSlab_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSlabTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSlabType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SlippageX", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("SlippageY", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("SlippageZ", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSlippageConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcSolidModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("IsAttenuating", new named_type(IFC2X3_IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("SoundScale", new named_type(IFC2X3_IfcSoundScaleEnum_type), true));
        attributes.push_back(new entity::attribute("SoundValues", new aggregation_type(aggregation_type::list_type, 1, 8, new named_type(IFC2X3_IfcSoundValue_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSoundProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SoundLevelTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("Frequency", new named_type(IFC2X3_IfcFrequencyMeasure_type), false));
        attributes.push_back(new entity::attribute("SoundLevelSingleValue", new named_type(IFC2X3_IfcDerivedMeasureValue_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSoundValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("InteriorOrExteriorSpace", new named_type(IFC2X3_IfcInternalOrExternalEnum_type), false));
        attributes.push_back(new entity::attribute("ElevationWithFlooring", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSpaceHeaterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpaceHeaterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("SpaceProgramIdentifier", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("MaxRequiredArea", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("MinRequiredArea", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("RequestedLocation", new named_type(IFC2X3_IfcSpatialStructureElement_type), true));
        attributes.push_back(new entity::attribute("StandardRequiredArea", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpaceProgram_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("ApplicableValueRatio", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalLoadSource", new named_type(IFC2X3_IfcThermalLoadSourceEnum_type), false));
        attributes.push_back(new entity::attribute("PropertySource", new named_type(IFC2X3_IfcPropertySourceEnum_type), false));
        attributes.push_back(new entity::attribute("SourceDescription", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("MaximumValue", new named_type(IFC2X3_IfcPowerMeasure_type), false));
        attributes.push_back(new entity::attribute("MinimumValue", new named_type(IFC2X3_IfcPowerMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalLoadTimeSeriesValues", new named_type(IFC2X3_IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("UserDefinedThermalLoadSource", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPropertySource", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ThermalLoadType", new named_type(IFC2X3_IfcThermalLoadTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpaceThermalLoadProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSpaceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpaceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LongName", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CompositionType", new named_type(IFC2X3_IfcElementCompositionEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpatialStructureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSpatialStructureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSphere_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcStackTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStackTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ShapeType", new named_type(IFC2X3_IfcStairTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStair_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("NumberOfRiser", new simple_type(simple_type::integer_type), true));
        attributes.push_back(new entity::attribute("NumberOfTreads", new simple_type(simple_type::integer_type), true));
        attributes.push_back(new entity::attribute("RiserHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TreadLength", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStairFlight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcStairFlightTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStairFlightType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DestabilizingLoad", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("CausedBy", new named_type(IFC2X3_IfcStructuralReaction_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AppliedLoad", new named_type(IFC2X3_IfcStructuralLoad_type), false));
        attributes.push_back(new entity::attribute("GlobalOrLocal", new named_type(IFC2X3_IfcGlobalOrLocalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralActivity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcAnalysisModelTypeEnum_type), false));
        attributes.push_back(new entity::attribute("OrientationOf2DPlane", new named_type(IFC2X3_IfcAxis2Placement3D_type), true));
        attributes.push_back(new entity::attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcStructuralLoadGroup_type)), true));
        attributes.push_back(new entity::attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcStructuralResultGroup_type)), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralAnalysisModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AppliedCondition", new named_type(IFC2X3_IfcBoundaryCondition_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcStructuralConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralCurveConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcStructuralCurveTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralCurveMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralCurveMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IFC2X3_IfcProjectedOrTrueLengthEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLinearAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VaryingAppliedLoadLocation", new named_type(IFC2X3_IfcShapeAspect_type), false));
        attributes.push_back(new entity::attribute("SubsequentAppliedLoads", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcStructuralLoad_type)), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLinearActionVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcStructuralLoad_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcLoadGroupTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ActionType", new named_type(IFC2X3_IfcActionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ActionSource", new named_type(IFC2X3_IfcActionSourceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Coefficient", new named_type(IFC2X3_IfcRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearForceX", new named_type(IFC2X3_IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearForceY", new named_type(IFC2X3_IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearForceZ", new named_type(IFC2X3_IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentX", new named_type(IFC2X3_IfcLinearMomentMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentY", new named_type(IFC2X3_IfcLinearMomentMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentZ", new named_type(IFC2X3_IfcLinearMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadLinearForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PlanarForceX", new named_type(IFC2X3_IfcPlanarForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PlanarForceY", new named_type(IFC2X3_IfcPlanarForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PlanarForceZ", new named_type(IFC2X3_IfcPlanarForceMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadPlanarForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("DisplacementX", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("DisplacementY", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("DisplacementZ", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRX", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRY", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRZ", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadSingleDisplacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Distortion", new named_type(IFC2X3_IfcCurvatureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("ForceX", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("ForceY", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("ForceZ", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentX", new named_type(IFC2X3_IfcTorqueMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentY", new named_type(IFC2X3_IfcTorqueMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentZ", new named_type(IFC2X3_IfcTorqueMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadSingleForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingMoment", new named_type(IFC2X3_IfcWarpingMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadSingleForceWarping_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcStructuralLoadStatic_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DeltaT_Constant", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaT_Y", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaT_Z", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralLoadTemperature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IFC2X3_IfcProjectedOrTrueLengthEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralPlanarAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VaryingAppliedLoadLocation", new named_type(IFC2X3_IfcShapeAspect_type), false));
        attributes.push_back(new entity::attribute("SubsequentAppliedLoads", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_IfcStructuralLoad_type)), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralPlanarActionVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralPointAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralPointConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralPointReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(16);
        attributes.push_back(new entity::attribute("TorsionalConstantX", new named_type(IFC2X3_IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentOfInertiaYZ", new named_type(IFC2X3_IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentOfInertiaY", new named_type(IFC2X3_IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentOfInertiaZ", new named_type(IFC2X3_IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("WarpingConstant", new named_type(IFC2X3_IfcWarpingConstantMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearCentreZ", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearCentreY", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearDeformationAreaZ", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearDeformationAreaY", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumSectionModulusY", new named_type(IFC2X3_IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumSectionModulusY", new named_type(IFC2X3_IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumSectionModulusZ", new named_type(IFC2X3_IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumSectionModulusZ", new named_type(IFC2X3_IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("TorsionalSectionModulus", new named_type(IFC2X3_IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IFC2X3_IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(23);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TheoryType", new named_type(IFC2X3_IfcAnalysisTheoryTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ResultForLoadGroup", new named_type(IFC2X3_IfcStructuralLoadGroup_type), true));
        attributes.push_back(new entity::attribute("IsLinear", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralResultGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ShearAreaZ", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearAreaY", new named_type(IFC2X3_IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("PlasticShapeFactorY", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PlasticShapeFactorZ", new named_type(IFC2X3_IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(27);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralSteelProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralSurfaceConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcStructuralSurfaceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralSurfaceMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SubsequentThickness", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_IfcPositiveLengthMeasure_type)), false));
        attributes.push_back(new entity::attribute("VaryingThicknessLocation", new named_type(IFC2X3_IfcShapeAspect_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStructuralSurfaceMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcStructuredDimensionCallout_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStyleModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Item", new named_type(IFC2X3_IfcRepresentationItem_type), true));
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPresentationStyleAssignment_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStyledItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcStyledRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SubContractor", new named_type(IFC2X3_IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("JobDescription", new named_type(IFC2X3_IfcText_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSubContractResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParentEdge", new named_type(IFC2X3_IfcEdge_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSubedge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("ReferenceSurface", new named_type(IFC2X3_IfcSurface_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceCurveSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ExtrudedDirection", new named_type(IFC2X3_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceOfLinearExtrusion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AxisPosition", new named_type(IFC2X3_IfcAxis1Placement_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceOfRevolution_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Side", new named_type(IFC2X3_IfcSurfaceSide_type), false));
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC2X3_IfcSurfaceStyleElementSelect_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("DiffuseTransmissionColour", new named_type(IFC2X3_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("DiffuseReflectionColour", new named_type(IFC2X3_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("TransmissionColour", new named_type(IFC2X3_IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("ReflectanceColour", new named_type(IFC2X3_IfcColourRgb_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceStyleLighting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RefractionIndex", new named_type(IFC2X3_IfcReal_type), true));
        attributes.push_back(new entity::attribute("DispersionFactor", new named_type(IFC2X3_IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceStyleRefraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Transparency", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("DiffuseColour", new named_type(IFC2X3_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("TransmissionColour", new named_type(IFC2X3_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("DiffuseTransmissionColour", new named_type(IFC2X3_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("ReflectionColour", new named_type(IFC2X3_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("SpecularColour", new named_type(IFC2X3_IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("SpecularHighlight", new named_type(IFC2X3_IfcSpecularHighlightSelect_type), true));
        attributes.push_back(new entity::attribute("ReflectanceMethod", new named_type(IFC2X3_IfcReflectanceMethodEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceStyleRendering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SurfaceColour", new named_type(IFC2X3_IfcColourRgb_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcSurfaceStyleShading_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcSurfaceTexture_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcSurfaceStyleWithTextures_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RepeatS", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("RepeatT", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("TextureType", new named_type(IFC2X3_IfcSurfaceTextureEnum_type), false));
        attributes.push_back(new entity::attribute("TextureTransform", new named_type(IFC2X3_IfcCartesianTransformationOperator2D_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSurfaceTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptArea", new named_type(IFC2X3_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IFC2X3_IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IFC2X3_IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSweptDiskSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptCurve", new named_type(IFC2X3_IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IFC2X3_IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSweptSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcSwitchingDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSwitchingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("StyleOfSymbol", new named_type(IFC2X3_IfcSymbolStyleSelect_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSymbolStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcSystemFurnitureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeEdgeRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebEdgeRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebSlope", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new simple_type(simple_type::string_type), false));
        attributes.push_back(new entity::attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcTableRow_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTable_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        attributes.push_back(new entity::attribute("IsHeading", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTableRow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcTankTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTankType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("TaskId", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Status", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("WorkMethod", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("IsMilestone", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Priority", new simple_type(simple_type::integer_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTask_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PagerNumber", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("WWWHomePageURL", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTelecomAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcTendonTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IFC2X3_IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("TensionForce", new named_type(IFC2X3_IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PreStress", new named_type(IFC2X3_IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("FrictionCoefficient", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("AnchorageSlip", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MinCurvatureRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTendon_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTendonAnchor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AnnotatedCurve", new named_type(IFC2X3_IfcAnnotationCurveOccurrence_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTerminatorSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Literal", new named_type(IFC2X3_IfcPresentableText_type), false));
        attributes.push_back(new entity::attribute("Placement", new named_type(IFC2X3_IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("Path", new named_type(IFC2X3_IfcTextPath_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextLiteral_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Extent", new named_type(IFC2X3_IfcPlanarExtent_type), false));
        attributes.push_back(new entity::attribute("BoxAlignment", new named_type(IFC2X3_IfcBoxAlignment_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextLiteralWithExtent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TextCharacterAppearance", new named_type(IFC2X3_IfcCharacterStyleSelect_type), true));
        attributes.push_back(new entity::attribute("TextStyle", new named_type(IFC2X3_IfcTextStyleSelect_type), true));
        attributes.push_back(new entity::attribute("TextFontStyle", new named_type(IFC2X3_IfcTextFontSelect_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcTextFontName_type)), true));
        attributes.push_back(new entity::attribute("FontStyle", new named_type(IFC2X3_IfcFontStyle_type), true));
        attributes.push_back(new entity::attribute("FontVariant", new named_type(IFC2X3_IfcFontVariant_type), true));
        attributes.push_back(new entity::attribute("FontWeight", new named_type(IFC2X3_IfcFontWeight_type), true));
        attributes.push_back(new entity::attribute("FontSize", new named_type(IFC2X3_IfcSizeSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextStyleFontModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Colour", new named_type(IFC2X3_IfcColour_type), false));
        attributes.push_back(new entity::attribute("BackgroundColour", new named_type(IFC2X3_IfcColour_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextStyleForDefinedFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("TextIndent", new named_type(IFC2X3_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("TextAlign", new named_type(IFC2X3_IfcTextAlignment_type), true));
        attributes.push_back(new entity::attribute("TextDecoration", new named_type(IFC2X3_IfcTextDecoration_type), true));
        attributes.push_back(new entity::attribute("LetterSpacing", new named_type(IFC2X3_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("WordSpacing", new named_type(IFC2X3_IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("TextTransform", new named_type(IFC2X3_IfcTextTransformation_type), true));
        attributes.push_back(new entity::attribute("LineHeight", new named_type(IFC2X3_IfcSizeSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextStyleTextModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("BoxHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BoxWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BoxSlantAngle", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("BoxRotateAngle", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CharacterSpacing", new named_type(IFC2X3_IfcSizeSelect_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextStyleWithBoxCharacteristics_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcTextureCoordinate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Mode", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcSimpleValue_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTextureCoordinateGenerator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TextureMaps", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcVertexBasedTextureMap_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC2X3_IfcParameterValue_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcTextureVertex_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("SpecificHeatCapacity", new named_type(IFC2X3_IfcSpecificHeatCapacityMeasure_type), true));
        attributes.push_back(new entity::attribute("BoilingPoint", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("FreezingPoint", new named_type(IFC2X3_IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalConductivity", new named_type(IFC2X3_IfcThermalConductivityMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcThermalMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Name", new named_type(IFC2X3_IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IFC2X3_IfcText_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("EndTime", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("TimeSeriesDataType", new named_type(IFC2X3_IfcTimeSeriesDataTypeEnum_type), false));
        attributes.push_back(new entity::attribute("DataOrigin", new named_type(IFC2X3_IfcDataOriginEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedDataOrigin", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IFC2X3_IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ReferencedTimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), false));
        attributes.push_back(new entity::attribute("TimeSeriesReferences", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcDocumentSelect_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTimeSeriesReferenceRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ApplicableDates", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcDateTimeSelect_type)), true));
        attributes.push_back(new entity::attribute("TimeSeriesScheduleType", new named_type(IFC2X3_IfcTimeSeriesScheduleTypeEnum_type), false));
        attributes.push_back(new entity::attribute("TimeSeries", new named_type(IFC2X3_IfcTimeSeries_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTimeSeriesSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcTopologicalRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTopologyRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcTransformerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTransformerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC2X3_IfcTransportElementTypeEnum_type), true));
        attributes.push_back(new entity::attribute("CapacityByWeight", new named_type(IFC2X3_IfcMassMeasure_type), true));
        attributes.push_back(new entity::attribute("CapacityByNumber", new named_type(IFC2X3_IfcCountMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTransportElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcTransportElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTransportElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BottomXDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopXDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopXOffset", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTrapeziumProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IFC2X3_IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC2X3_IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC2X3_IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("SenseAgreement", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("MasterRepresentation", new named_type(IFC2X3_IfcTrimmingPreference_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTrimmedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcTubeBundleTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTubeBundleType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SecondRepeatFactor", new named_type(IFC2X3_IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTwoDirectionRepeatFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ApplicableOccurrence", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPropertySetDefinition_type)), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTypeObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_IfcRepresentationMap_type)), true));
        attributes.push_back(new entity::attribute("Tag", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcTypeProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IFC2X3_IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcUShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcUnit_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcUnitAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcUnitaryEquipmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcUnitaryEquipmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcValveTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcValveType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IFC2X3_IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Magnitude", new named_type(IFC2X3_IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcVector_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IFC2X3_IfcVertex_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TextureVertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC2X3_IfcTextureVertex_type)), false));
        attributes.push_back(new entity::attribute("TexturePoints", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC2X3_IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcVertexBasedTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LoopVertex", new named_type(IFC2X3_IfcVertex_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcVertexLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("VertexGeometry", new named_type(IFC2X3_IfcPoint_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IFC2X3_IfcVertexPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcVibrationIsolatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcVibrationIsolatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcVirtualElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC2X3_IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC2X3_IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcVirtualGridIntersection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWallStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcWallTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWallType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IFC2X3_IfcWasteTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWasteTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("IsPotable", new simple_type(simple_type::boolean_type), true));
        attributes.push_back(new entity::attribute("Hardness", new named_type(IFC2X3_IfcIonConcentrationMeasure_type), true));
        attributes.push_back(new entity::attribute("AlkalinityConcentration", new named_type(IFC2X3_IfcIonConcentrationMeasure_type), true));
        attributes.push_back(new entity::attribute("AcidityConcentration", new named_type(IFC2X3_IfcIonConcentrationMeasure_type), true));
        attributes.push_back(new entity::attribute("ImpuritiesContent", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PHLevel", new named_type(IFC2X3_IfcPHMeasure_type), true));
        attributes.push_back(new entity::attribute("DissolvedSolidsContent", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWaterProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWindow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MullionThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstTransomOffset", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondTransomOffset", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstMullionOffset", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondMullionOffset", new named_type(IFC2X3_IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC2X3_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWindowLiningProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC2X3_IfcWindowPanelOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IFC2X3_IfcWindowPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("FrameDepth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FrameThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IFC2X3_IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWindowPanelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IFC2X3_IfcWindowStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IFC2X3_IfcWindowStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWindowStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("Identifier", new named_type(IFC2X3_IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_IfcPerson_type)), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IFC2X3_IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Duration", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IFC2X3_IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IFC2X3_IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("FinishTime", new named_type(IFC2X3_IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("WorkControlType", new named_type(IFC2X3_IfcWorkControlTypeEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedControlType", new named_type(IFC2X3_IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWorkControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWorkPlan_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcWorkSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IFC2X3_IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcZShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IFC2X3_IfcZone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsActingUpon", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssignsToActor_type, IFC2X3_IfcRelAssignsToActor_type->attributes()[0]));
        IFC2X3_IfcActor_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("OfPerson", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPerson_type, IFC2X3_IfcPerson_type->attributes()[7]));
        attributes.push_back(new entity::inverse_attribute("OfOrganization", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcOrganization_type, IFC2X3_IfcOrganization_type->attributes()[4]));
        IFC2X3_IfcAddress_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelContainedInSpatialStructure_type, IFC2X3_IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IFC2X3_IfcAnnotation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ValuesReferenced", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcReferencesValueDocument_type, IFC2X3_IfcReferencesValueDocument_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ValueOfComponents", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcAppliedValueRelationship_type, IFC2X3_IfcAppliedValueRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsComponentIn", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcAppliedValueRelationship_type, IFC2X3_IfcAppliedValueRelationship_type->attributes()[1]));
        IFC2X3_IfcAppliedValue_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("Actors", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcApprovalActorRelationship_type, IFC2X3_IfcApprovalActorRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedWith", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcApprovalRelationship_type, IFC2X3_IfcApprovalRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Relates", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcApprovalRelationship_type, IFC2X3_IfcApprovalRelationship_type->attributes()[1]));
        IFC2X3_IfcApproval_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Contains", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcClassificationItem_type, IFC2X3_IfcClassificationItem_type->attributes()[1]));
        IFC2X3_IfcClassification_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsClassifiedItemIn", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcClassificationItemRelationship_type, IFC2X3_IfcClassificationItemRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsClassifyingItemIn", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcClassificationItemRelationship_type, IFC2X3_IfcClassificationItemRelationship_type->attributes()[0]));
        IFC2X3_IfcClassificationItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("UsingCurves", entity::inverse_attribute::set_type, 1, -1, IFC2X3_IfcCompositeCurve_type, IFC2X3_IfcCompositeCurve_type->attributes()[0]));
        IFC2X3_IfcCompositeCurveSegment_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::inverse_attribute("ClassifiedAs", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcConstraintClassificationRelationship_type, IFC2X3_IfcConstraintClassificationRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("RelatesConstraints", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcConstraintRelationship_type, IFC2X3_IfcConstraintRelationship_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedWith", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcConstraintRelationship_type, IFC2X3_IfcConstraintRelationship_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("PropertiesForConstraint", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPropertyConstraintRelationship_type, IFC2X3_IfcPropertyConstraintRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Aggregates", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcConstraintAggregationRelationship_type, IFC2X3_IfcConstraintAggregationRelationship_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("IsAggregatedIn", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcConstraintAggregationRelationship_type, IFC2X3_IfcConstraintAggregationRelationship_type->attributes()[3]));
        IFC2X3_IfcConstraint_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Controls", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssignsToControl_type, IFC2X3_IfcRelAssignsToControl_type->attributes()[0]));
        IFC2X3_IfcControl_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("CoversSpaces", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelCoversSpaces_type, IFC2X3_IfcRelCoversSpaces_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("Covers", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelCoversBldgElements_type, IFC2X3_IfcRelCoversBldgElements_type->attributes()[1]));
        IFC2X3_IfcCovering_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AnnotatedBySymbols", entity::inverse_attribute::set_type, 0, 2, IFC2X3_IfcTerminatorSymbol_type, IFC2X3_IfcTerminatorSymbol_type->attributes()[0]));
        IFC2X3_IfcDimensionCurve_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedToFlowElement", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelFlowControlElements_type, IFC2X3_IfcRelFlowControlElements_type->attributes()[0]));
        IFC2X3_IfcDistributionControlElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasControlElements", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelFlowControlElements_type, IFC2X3_IfcRelFlowControlElements_type->attributes()[1]));
        IFC2X3_IfcDistributionFlowElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsPointedTo", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcDocumentInformationRelationship_type, IFC2X3_IfcDocumentInformationRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsPointer", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcDocumentInformationRelationship_type, IFC2X3_IfcDocumentInformationRelationship_type->attributes()[0]));
        IFC2X3_IfcDocumentInformation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferenceToDocument", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcDocumentInformation_type, IFC2X3_IfcDocumentInformation_type->attributes()[3]));
        IFC2X3_IfcDocumentReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsRelatedFromCallout", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcDraughtingCalloutRelationship_type, IFC2X3_IfcDraughtingCalloutRelationship_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedToCallout", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcDraughtingCalloutRelationship_type, IFC2X3_IfcDraughtingCalloutRelationship_type->attributes()[2]));
        IFC2X3_IfcDraughtingCallout_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::inverse_attribute("HasStructuralMember", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsStructuralElement_type, IFC2X3_IfcRelConnectsStructuralElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("FillsVoids", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelFillsElement_type, IFC2X3_IfcRelFillsElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedTo", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsElements_type, IFC2X3_IfcRelConnectsElements_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasCoverings", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelCoversBldgElements_type, IFC2X3_IfcRelCoversBldgElements_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasProjections", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelProjectsElement_type, IFC2X3_IfcRelProjectsElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ReferencedInStructures", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelReferencedInSpatialStructure_type, IFC2X3_IfcRelReferencedInSpatialStructure_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasPorts", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsPortToElement_type, IFC2X3_IfcRelConnectsPortToElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasOpenings", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelVoidsElement_type, IFC2X3_IfcRelVoidsElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsConnectionRealization", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsWithRealizingElements_type, IFC2X3_IfcRelConnectsWithRealizingElements_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ProvidesBoundaries", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelSpaceBoundary_type, IFC2X3_IfcRelSpaceBoundary_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedFrom", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsElements_type, IFC2X3_IfcRelConnectsElements_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelContainedInSpatialStructure_type, IFC2X3_IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IFC2X3_IfcElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ProjectsElements", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcRelProjectsElement_type, IFC2X3_IfcRelProjectsElement_type->attributes()[1]));
        IFC2X3_IfcFeatureElementAddition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("VoidsElements", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcRelVoidsElement_type, IFC2X3_IfcRelVoidsElement_type->attributes()[1]));
        IFC2X3_IfcFeatureElementSubtraction_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasSubContexts", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcGeometricRepresentationSubContext_type, IFC2X3_IfcGeometricRepresentationSubContext_type->attributes()[0]));
        IFC2X3_IfcGeometricRepresentationContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelContainedInSpatialStructure_type, IFC2X3_IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IFC2X3_IfcGrid_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("PartOfW", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcGrid_type, IFC2X3_IfcGrid_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("PartOfV", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcGrid_type, IFC2X3_IfcGrid_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfU", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcGrid_type, IFC2X3_IfcGrid_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasIntersections", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcVirtualGridIntersection_type, IFC2X3_IfcVirtualGridIntersection_type->attributes()[0]));
        IFC2X3_IfcGridAxis_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsGroupedBy", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcRelAssignsToGroup_type, IFC2X3_IfcRelAssignsToGroup_type->attributes()[0]));
        IFC2X3_IfcGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferenceIntoLibrary", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcLibraryInformation_type, IFC2X3_IfcLibraryInformation_type->attributes()[4]));
        IFC2X3_IfcLibraryReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasRepresentation", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcMaterialDefinitionRepresentation_type, IFC2X3_IfcMaterialDefinitionRepresentation_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ClassifiedAs", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcMaterialClassificationRelationship_type, IFC2X3_IfcMaterialClassificationRelationship_type->attributes()[1]));
        IFC2X3_IfcMaterial_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ToMaterialLayerSet", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcMaterialLayerSet_type, IFC2X3_IfcMaterialLayerSet_type->attributes()[0]));
        IFC2X3_IfcMaterialLayer_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsDefinedBy", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelDefines_type, IFC2X3_IfcRelDefines_type->attributes()[0]));
        IFC2X3_IfcObject_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("HasAssignments", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssigns_type, IFC2X3_IfcRelAssigns_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsDecomposedBy", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelDecomposes_type, IFC2X3_IfcRelDecomposes_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Decomposes", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelDecomposes_type, IFC2X3_IfcRelDecomposes_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasAssociations", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssociates_type, IFC2X3_IfcRelAssociates_type->attributes()[0]));
        IFC2X3_IfcObjectDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("PlacesObject", entity::inverse_attribute::set_type, 1, 1, IFC2X3_IfcProduct_type, IFC2X3_IfcProduct_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ReferencedByPlacements", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcLocalPlacement_type, IFC2X3_IfcLocalPlacement_type->attributes()[0]));
        IFC2X3_IfcObjectPlacement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasFillings", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelFillsElement_type, IFC2X3_IfcRelFillsElement_type->attributes()[0]));
        IFC2X3_IfcOpeningElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("IsRelatedBy", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcOrganizationRelationship_type, IFC2X3_IfcOrganizationRelationship_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("Relates", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcOrganizationRelationship_type, IFC2X3_IfcOrganizationRelationship_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("Engages", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPersonAndOrganization_type, IFC2X3_IfcPersonAndOrganization_type->attributes()[1]));
        IFC2X3_IfcOrganization_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("EngagedIn", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPersonAndOrganization_type, IFC2X3_IfcPersonAndOrganization_type->attributes()[0]));
        IFC2X3_IfcPerson_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("PartOfComplex", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcPhysicalComplexQuantity_type, IFC2X3_IfcPhysicalComplexQuantity_type->attributes()[0]));
        IFC2X3_IfcPhysicalQuantity_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ContainedIn", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcRelConnectsPortToElement_type, IFC2X3_IfcRelConnectsPortToElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ConnectedFrom", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelConnectsPorts_type, IFC2X3_IfcRelConnectsPorts_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedTo", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelConnectsPorts_type, IFC2X3_IfcRelConnectsPorts_type->attributes()[0]));
        IFC2X3_IfcPort_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("OperatesOn", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssignsToProcess_type, IFC2X3_IfcRelAssignsToProcess_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsSuccessorFrom", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelSequence_type, IFC2X3_IfcRelSequence_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsPredecessorTo", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelSequence_type, IFC2X3_IfcRelSequence_type->attributes()[0]));
        IFC2X3_IfcProcess_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferencedBy", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssignsToProduct_type, IFC2X3_IfcRelAssignsToProduct_type->attributes()[0]));
        IFC2X3_IfcProduct_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ShapeOfProduct", entity::inverse_attribute::set_type, 1, 1, IFC2X3_IfcProduct_type, IFC2X3_IfcProduct_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasShapeAspects", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcShapeAspect_type, IFC2X3_IfcShapeAspect_type->attributes()[4]));
        IFC2X3_IfcProductDefinitionShape_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("PropertyForDependance", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPropertyDependencyRelationship_type, IFC2X3_IfcPropertyDependencyRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("PropertyDependsOn", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPropertyDependencyRelationship_type, IFC2X3_IfcPropertyDependencyRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfComplex", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcComplexProperty_type, IFC2X3_IfcComplexProperty_type->attributes()[1]));
        IFC2X3_IfcProperty_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasAssociations", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssociates_type, IFC2X3_IfcRelAssociates_type->attributes()[0]));
        IFC2X3_IfcPropertyDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("PropertyDefinitionOf", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelDefinesByProperties_type, IFC2X3_IfcRelDefinesByProperties_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("DefinesType", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcTypeObject_type, IFC2X3_IfcTypeObject_type->attributes()[1]));
        IFC2X3_IfcPropertySetDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("RepresentationMap", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRepresentationMap_type, IFC2X3_IfcRepresentationMap_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("LayerAssignments", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPresentationLayerAssignment_type, IFC2X3_IfcPresentationLayerAssignment_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("OfProductRepresentation", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcProductRepresentation_type, IFC2X3_IfcProductRepresentation_type->attributes()[2]));
        IFC2X3_IfcRepresentation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("RepresentationsInContext", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRepresentation_type, IFC2X3_IfcRepresentation_type->attributes()[0]));
        IFC2X3_IfcRepresentationContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("LayerAssignments", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcPresentationLayerAssignment_type, IFC2X3_IfcPresentationLayerAssignment_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("StyledByItem", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcStyledItem_type, IFC2X3_IfcStyledItem_type->attributes()[0]));
        IFC2X3_IfcRepresentationItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("MapUsage", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcMappedItem_type, IFC2X3_IfcMappedItem_type->attributes()[0]));
        IFC2X3_IfcRepresentationMap_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResourceOf", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelAssignsToResource_type, IFC2X3_IfcRelAssignsToResource_type->attributes()[0]));
        IFC2X3_IfcResource_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ScheduleTimeControlAssigned", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcRelAssignsTasks_type, IFC2X3_IfcRelAssignsTasks_type->attributes()[0]));
        IFC2X3_IfcScheduleTimeControl_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("OfShapeAspect", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcShapeAspect_type, IFC2X3_IfcShapeAspect_type->attributes()[0]));
        IFC2X3_IfcShapeModel_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasCoverings", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelCoversSpaces_type, IFC2X3_IfcRelCoversSpaces_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("BoundedBy", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelSpaceBoundary_type, IFC2X3_IfcRelSpaceBoundary_type->attributes()[0]));
        IFC2X3_IfcSpace_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasInteractionReqsFrom", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelInteractionRequirements_type, IFC2X3_IfcRelInteractionRequirements_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("HasInteractionReqsTo", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelInteractionRequirements_type, IFC2X3_IfcRelInteractionRequirements_type->attributes()[4]));
        IFC2X3_IfcSpaceProgram_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ReferencesElements", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelReferencedInSpatialStructure_type, IFC2X3_IfcRelReferencedInSpatialStructure_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ServicedBySystems", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelServicesBuildings_type, IFC2X3_IfcRelServicesBuildings_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ContainsElements", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelContainedInSpatialStructure_type, IFC2X3_IfcRelContainedInSpatialStructure_type->attributes()[1]));
        IFC2X3_IfcSpatialStructureElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedToStructuralItem", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcRelConnectsStructuralActivity_type, IFC2X3_IfcRelConnectsStructuralActivity_type->attributes()[1]));
        IFC2X3_IfcStructuralActivity_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ConnectsStructuralMembers", entity::inverse_attribute::set_type, 1, -1, IFC2X3_IfcRelConnectsStructuralMember_type, IFC2X3_IfcRelConnectsStructuralMember_type->attributes()[1]));
        IFC2X3_IfcStructuralConnection_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedStructuralActivity", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsStructuralActivity_type, IFC2X3_IfcRelConnectsStructuralActivity_type->attributes()[0]));
        IFC2X3_IfcStructuralItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("SourceOfResultGroup", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcStructuralResultGroup_type, IFC2X3_IfcStructuralResultGroup_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("LoadGroupFor", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcStructuralAnalysisModel_type, IFC2X3_IfcStructuralAnalysisModel_type->attributes()[2]));
        IFC2X3_IfcStructuralLoadGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ReferencesElement", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsStructuralElement_type, IFC2X3_IfcRelConnectsStructuralElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedBy", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcRelConnectsStructuralMember_type, IFC2X3_IfcRelConnectsStructuralMember_type->attributes()[0]));
        IFC2X3_IfcStructuralMember_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Causes", entity::inverse_attribute::set_type, 0, -1, IFC2X3_IfcStructuralAction_type, IFC2X3_IfcStructuralAction_type->attributes()[1]));
        IFC2X3_IfcStructuralReaction_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResultGroupFor", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcStructuralAnalysisModel_type, IFC2X3_IfcStructuralAnalysisModel_type->attributes()[3]));
        IFC2X3_IfcStructuralResultGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ServicesBuildings", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelServicesBuildings_type, IFC2X3_IfcRelServicesBuildings_type->attributes()[0]));
        IFC2X3_IfcSystem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("OfTable", entity::inverse_attribute::unspecified_type, -1, -1, IFC2X3_IfcTable_type, IFC2X3_IfcTable_type->attributes()[1]));
        IFC2X3_IfcTableRow_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AnnotatedSurface", entity::inverse_attribute::set_type, 1, 1, IFC2X3_IfcAnnotationSurface_type, IFC2X3_IfcAnnotationSurface_type->attributes()[1]));
        IFC2X3_IfcTextureCoordinate_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("DocumentedBy", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcTimeSeriesReferenceRelationship_type, IFC2X3_IfcTimeSeriesReferenceRelationship_type->attributes()[0]));
        IFC2X3_IfcTimeSeries_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ObjectTypeOf", entity::inverse_attribute::set_type, 0, 1, IFC2X3_IfcRelDefinesByType_type, IFC2X3_IfcRelDefinesByType_type->attributes()[0]));
        IFC2X3_IfcTypeObject_type->set_inverse_attributes(attributes);
    }

    std::vector<const declaration*> declarations; declarations.reserve(980);
    declarations.push_back(IFC2X3_IfcAbsorbedDoseMeasure_type);
    declarations.push_back(IFC2X3_IfcAccelerationMeasure_type);
    declarations.push_back(IFC2X3_IfcActionSourceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcActionTypeEnum_type);
    declarations.push_back(IFC2X3_IfcActuatorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAddressTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAheadOrBehind_type);
    declarations.push_back(IFC2X3_IfcAirTerminalBoxTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAirTerminalTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAirToAirHeatRecoveryTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAlarmTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAmountOfSubstanceMeasure_type);
    declarations.push_back(IFC2X3_IfcAnalysisModelTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAnalysisTheoryTypeEnum_type);
    declarations.push_back(IFC2X3_IfcAngularVelocityMeasure_type);
    declarations.push_back(IFC2X3_IfcAreaMeasure_type);
    declarations.push_back(IFC2X3_IfcArithmeticOperatorEnum_type);
    declarations.push_back(IFC2X3_IfcAssemblyPlaceEnum_type);
    declarations.push_back(IFC2X3_IfcBSplineCurveForm_type);
    declarations.push_back(IFC2X3_IfcBeamTypeEnum_type);
    declarations.push_back(IFC2X3_IfcBenchmarkEnum_type);
    declarations.push_back(IFC2X3_IfcBoilerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcBoolean_type);
    declarations.push_back(IFC2X3_IfcBooleanOperator_type);
    declarations.push_back(IFC2X3_IfcBuildingElementProxyTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCableCarrierFittingTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCableCarrierSegmentTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCableSegmentTypeEnum_type);
    declarations.push_back(IFC2X3_IfcChangeActionEnum_type);
    declarations.push_back(IFC2X3_IfcChillerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCoilTypeEnum_type);
    declarations.push_back(IFC2X3_IfcColumnTypeEnum_type);
    declarations.push_back(IFC2X3_IfcComplexNumber_type);
    declarations.push_back(IFC2X3_IfcCompoundPlaneAngleMeasure_type);
    declarations.push_back(IFC2X3_IfcCompressorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCondenserTypeEnum_type);
    declarations.push_back(IFC2X3_IfcConnectionTypeEnum_type);
    declarations.push_back(IFC2X3_IfcConstraintEnum_type);
    declarations.push_back(IFC2X3_IfcContextDependentMeasure_type);
    declarations.push_back(IFC2X3_IfcControllerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCooledBeamTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCoolingTowerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCostScheduleTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCountMeasure_type);
    declarations.push_back(IFC2X3_IfcCoveringTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCurrencyEnum_type);
    declarations.push_back(IFC2X3_IfcCurtainWallTypeEnum_type);
    declarations.push_back(IFC2X3_IfcCurvatureMeasure_type);
    declarations.push_back(IFC2X3_IfcDamperTypeEnum_type);
    declarations.push_back(IFC2X3_IfcDataOriginEnum_type);
    declarations.push_back(IFC2X3_IfcDayInMonthNumber_type);
    declarations.push_back(IFC2X3_IfcDaylightSavingHour_type);
    declarations.push_back(IFC2X3_IfcDerivedUnitEnum_type);
    declarations.push_back(IFC2X3_IfcDescriptiveMeasure_type);
    declarations.push_back(IFC2X3_IfcDimensionCount_type);
    declarations.push_back(IFC2X3_IfcDimensionExtentUsage_type);
    declarations.push_back(IFC2X3_IfcDirectionSenseEnum_type);
    declarations.push_back(IFC2X3_IfcDistributionChamberElementTypeEnum_type);
    declarations.push_back(IFC2X3_IfcDocumentConfidentialityEnum_type);
    declarations.push_back(IFC2X3_IfcDocumentStatusEnum_type);
    declarations.push_back(IFC2X3_IfcDoorPanelOperationEnum_type);
    declarations.push_back(IFC2X3_IfcDoorPanelPositionEnum_type);
    declarations.push_back(IFC2X3_IfcDoorStyleConstructionEnum_type);
    declarations.push_back(IFC2X3_IfcDoorStyleOperationEnum_type);
    declarations.push_back(IFC2X3_IfcDoseEquivalentMeasure_type);
    declarations.push_back(IFC2X3_IfcDuctFittingTypeEnum_type);
    declarations.push_back(IFC2X3_IfcDuctSegmentTypeEnum_type);
    declarations.push_back(IFC2X3_IfcDuctSilencerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcDynamicViscosityMeasure_type);
    declarations.push_back(IFC2X3_IfcElectricApplianceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElectricCapacitanceMeasure_type);
    declarations.push_back(IFC2X3_IfcElectricChargeMeasure_type);
    declarations.push_back(IFC2X3_IfcElectricConductanceMeasure_type);
    declarations.push_back(IFC2X3_IfcElectricCurrentEnum_type);
    declarations.push_back(IFC2X3_IfcElectricCurrentMeasure_type);
    declarations.push_back(IFC2X3_IfcElectricDistributionPointFunctionEnum_type);
    declarations.push_back(IFC2X3_IfcElectricFlowStorageDeviceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElectricGeneratorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElectricHeaterTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElectricMotorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElectricResistanceMeasure_type);
    declarations.push_back(IFC2X3_IfcElectricTimeControlTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElectricVoltageMeasure_type);
    declarations.push_back(IFC2X3_IfcElementAssemblyTypeEnum_type);
    declarations.push_back(IFC2X3_IfcElementCompositionEnum_type);
    declarations.push_back(IFC2X3_IfcEnergyMeasure_type);
    declarations.push_back(IFC2X3_IfcEnergySequenceEnum_type);
    declarations.push_back(IFC2X3_IfcEnvironmentalImpactCategoryEnum_type);
    declarations.push_back(IFC2X3_IfcEvaporativeCoolerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcEvaporatorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcFanTypeEnum_type);
    declarations.push_back(IFC2X3_IfcFilterTypeEnum_type);
    declarations.push_back(IFC2X3_IfcFireSuppressionTerminalTypeEnum_type);
    declarations.push_back(IFC2X3_IfcFlowDirectionEnum_type);
    declarations.push_back(IFC2X3_IfcFlowInstrumentTypeEnum_type);
    declarations.push_back(IFC2X3_IfcFlowMeterTypeEnum_type);
    declarations.push_back(IFC2X3_IfcFontStyle_type);
    declarations.push_back(IFC2X3_IfcFontVariant_type);
    declarations.push_back(IFC2X3_IfcFontWeight_type);
    declarations.push_back(IFC2X3_IfcFootingTypeEnum_type);
    declarations.push_back(IFC2X3_IfcForceMeasure_type);
    declarations.push_back(IFC2X3_IfcFrequencyMeasure_type);
    declarations.push_back(IFC2X3_IfcGasTerminalTypeEnum_type);
    declarations.push_back(IFC2X3_IfcGeometricProjectionEnum_type);
    declarations.push_back(IFC2X3_IfcGlobalOrLocalEnum_type);
    declarations.push_back(IFC2X3_IfcGloballyUniqueId_type);
    declarations.push_back(IFC2X3_IfcHeatExchangerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcHeatFluxDensityMeasure_type);
    declarations.push_back(IFC2X3_IfcHeatingValueMeasure_type);
    declarations.push_back(IFC2X3_IfcHourInDay_type);
    declarations.push_back(IFC2X3_IfcHumidifierTypeEnum_type);
    declarations.push_back(IFC2X3_IfcIdentifier_type);
    declarations.push_back(IFC2X3_IfcIlluminanceMeasure_type);
    declarations.push_back(IFC2X3_IfcInductanceMeasure_type);
    declarations.push_back(IFC2X3_IfcInteger_type);
    declarations.push_back(IFC2X3_IfcIntegerCountRateMeasure_type);
    declarations.push_back(IFC2X3_IfcInternalOrExternalEnum_type);
    declarations.push_back(IFC2X3_IfcInventoryTypeEnum_type);
    declarations.push_back(IFC2X3_IfcIonConcentrationMeasure_type);
    declarations.push_back(IFC2X3_IfcIsothermalMoistureCapacityMeasure_type);
    declarations.push_back(IFC2X3_IfcJunctionBoxTypeEnum_type);
    declarations.push_back(IFC2X3_IfcKinematicViscosityMeasure_type);
    declarations.push_back(IFC2X3_IfcLabel_type);
    declarations.push_back(IFC2X3_IfcLampTypeEnum_type);
    declarations.push_back(IFC2X3_IfcLayerSetDirectionEnum_type);
    declarations.push_back(IFC2X3_IfcLengthMeasure_type);
    declarations.push_back(IFC2X3_IfcLightDistributionCurveEnum_type);
    declarations.push_back(IFC2X3_IfcLightEmissionSourceEnum_type);
    declarations.push_back(IFC2X3_IfcLightFixtureTypeEnum_type);
    declarations.push_back(IFC2X3_IfcLinearForceMeasure_type);
    declarations.push_back(IFC2X3_IfcLinearMomentMeasure_type);
    declarations.push_back(IFC2X3_IfcLinearStiffnessMeasure_type);
    declarations.push_back(IFC2X3_IfcLinearVelocityMeasure_type);
    declarations.push_back(IFC2X3_IfcLoadGroupTypeEnum_type);
    declarations.push_back(IFC2X3_IfcLogical_type);
    declarations.push_back(IFC2X3_IfcLogicalOperatorEnum_type);
    declarations.push_back(IFC2X3_IfcLuminousFluxMeasure_type);
    declarations.push_back(IFC2X3_IfcLuminousIntensityDistributionMeasure_type);
    declarations.push_back(IFC2X3_IfcLuminousIntensityMeasure_type);
    declarations.push_back(IFC2X3_IfcMagneticFluxDensityMeasure_type);
    declarations.push_back(IFC2X3_IfcMagneticFluxMeasure_type);
    declarations.push_back(IFC2X3_IfcMassDensityMeasure_type);
    declarations.push_back(IFC2X3_IfcMassFlowRateMeasure_type);
    declarations.push_back(IFC2X3_IfcMassMeasure_type);
    declarations.push_back(IFC2X3_IfcMassPerLengthMeasure_type);
    declarations.push_back(IFC2X3_IfcMemberTypeEnum_type);
    declarations.push_back(IFC2X3_IfcMinuteInHour_type);
    declarations.push_back(IFC2X3_IfcModulusOfElasticityMeasure_type);
    declarations.push_back(IFC2X3_IfcModulusOfLinearSubgradeReactionMeasure_type);
    declarations.push_back(IFC2X3_IfcModulusOfRotationalSubgradeReactionMeasure_type);
    declarations.push_back(IFC2X3_IfcModulusOfSubgradeReactionMeasure_type);
    declarations.push_back(IFC2X3_IfcMoistureDiffusivityMeasure_type);
    declarations.push_back(IFC2X3_IfcMolecularWeightMeasure_type);
    declarations.push_back(IFC2X3_IfcMomentOfInertiaMeasure_type);
    declarations.push_back(IFC2X3_IfcMonetaryMeasure_type);
    declarations.push_back(IFC2X3_IfcMonthInYearNumber_type);
    declarations.push_back(IFC2X3_IfcMotorConnectionTypeEnum_type);
    declarations.push_back(IFC2X3_IfcNullStyle_type);
    declarations.push_back(IFC2X3_IfcNumericMeasure_type);
    declarations.push_back(IFC2X3_IfcObjectTypeEnum_type);
    declarations.push_back(IFC2X3_IfcObjectiveEnum_type);
    declarations.push_back(IFC2X3_IfcOccupantTypeEnum_type);
    declarations.push_back(IFC2X3_IfcOutletTypeEnum_type);
    declarations.push_back(IFC2X3_IfcPHMeasure_type);
    declarations.push_back(IFC2X3_IfcParameterValue_type);
    declarations.push_back(IFC2X3_IfcPermeableCoveringOperationEnum_type);
    declarations.push_back(IFC2X3_IfcPhysicalOrVirtualEnum_type);
    declarations.push_back(IFC2X3_IfcPileConstructionEnum_type);
    declarations.push_back(IFC2X3_IfcPileTypeEnum_type);
    declarations.push_back(IFC2X3_IfcPipeFittingTypeEnum_type);
    declarations.push_back(IFC2X3_IfcPipeSegmentTypeEnum_type);
    declarations.push_back(IFC2X3_IfcPlanarForceMeasure_type);
    declarations.push_back(IFC2X3_IfcPlaneAngleMeasure_type);
    declarations.push_back(IFC2X3_IfcPlateTypeEnum_type);
    declarations.push_back(IFC2X3_IfcPositiveLengthMeasure_type);
    declarations.push_back(IFC2X3_IfcPositivePlaneAngleMeasure_type);
    declarations.push_back(IFC2X3_IfcPowerMeasure_type);
    declarations.push_back(IFC2X3_IfcPresentableText_type);
    declarations.push_back(IFC2X3_IfcPressureMeasure_type);
    declarations.push_back(IFC2X3_IfcProcedureTypeEnum_type);
    declarations.push_back(IFC2X3_IfcProfileTypeEnum_type);
    declarations.push_back(IFC2X3_IfcProjectOrderRecordTypeEnum_type);
    declarations.push_back(IFC2X3_IfcProjectOrderTypeEnum_type);
    declarations.push_back(IFC2X3_IfcProjectedOrTrueLengthEnum_type);
    declarations.push_back(IFC2X3_IfcPropertySourceEnum_type);
    declarations.push_back(IFC2X3_IfcProtectiveDeviceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcPumpTypeEnum_type);
    declarations.push_back(IFC2X3_IfcRadioActivityMeasure_type);
    declarations.push_back(IFC2X3_IfcRailingTypeEnum_type);
    declarations.push_back(IFC2X3_IfcRampFlightTypeEnum_type);
    declarations.push_back(IFC2X3_IfcRampTypeEnum_type);
    declarations.push_back(IFC2X3_IfcRatioMeasure_type);
    declarations.push_back(IFC2X3_IfcReal_type);
    declarations.push_back(IFC2X3_IfcReflectanceMethodEnum_type);
    declarations.push_back(IFC2X3_IfcReinforcingBarRoleEnum_type);
    declarations.push_back(IFC2X3_IfcReinforcingBarSurfaceEnum_type);
    declarations.push_back(IFC2X3_IfcResourceConsumptionEnum_type);
    declarations.push_back(IFC2X3_IfcRibPlateDirectionEnum_type);
    declarations.push_back(IFC2X3_IfcRoleEnum_type);
    declarations.push_back(IFC2X3_IfcRoofTypeEnum_type);
    declarations.push_back(IFC2X3_IfcRotationalFrequencyMeasure_type);
    declarations.push_back(IFC2X3_IfcRotationalMassMeasure_type);
    declarations.push_back(IFC2X3_IfcRotationalStiffnessMeasure_type);
    declarations.push_back(IFC2X3_IfcSIPrefix_type);
    declarations.push_back(IFC2X3_IfcSIUnitName_type);
    declarations.push_back(IFC2X3_IfcSanitaryTerminalTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSecondInMinute_type);
    declarations.push_back(IFC2X3_IfcSectionModulusMeasure_type);
    declarations.push_back(IFC2X3_IfcSectionTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSectionalAreaIntegralMeasure_type);
    declarations.push_back(IFC2X3_IfcSensorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSequenceEnum_type);
    declarations.push_back(IFC2X3_IfcServiceLifeFactorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcServiceLifeTypeEnum_type);
    declarations.push_back(IFC2X3_IfcShearModulusMeasure_type);
    declarations.push_back(IFC2X3_IfcSlabTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSolidAngleMeasure_type);
    declarations.push_back(IFC2X3_IfcSoundPowerMeasure_type);
    declarations.push_back(IFC2X3_IfcSoundPressureMeasure_type);
    declarations.push_back(IFC2X3_IfcSoundScaleEnum_type);
    declarations.push_back(IFC2X3_IfcSpaceHeaterTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSpaceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSpecificHeatCapacityMeasure_type);
    declarations.push_back(IFC2X3_IfcSpecularExponent_type);
    declarations.push_back(IFC2X3_IfcSpecularRoughness_type);
    declarations.push_back(IFC2X3_IfcStackTerminalTypeEnum_type);
    declarations.push_back(IFC2X3_IfcStairFlightTypeEnum_type);
    declarations.push_back(IFC2X3_IfcStairTypeEnum_type);
    declarations.push_back(IFC2X3_IfcStateEnum_type);
    declarations.push_back(IFC2X3_IfcStructuralCurveTypeEnum_type);
    declarations.push_back(IFC2X3_IfcStructuralSurfaceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcSurfaceSide_type);
    declarations.push_back(IFC2X3_IfcSurfaceTextureEnum_type);
    declarations.push_back(IFC2X3_IfcSwitchingDeviceTypeEnum_type);
    declarations.push_back(IFC2X3_IfcTankTypeEnum_type);
    declarations.push_back(IFC2X3_IfcTemperatureGradientMeasure_type);
    declarations.push_back(IFC2X3_IfcTendonTypeEnum_type);
    declarations.push_back(IFC2X3_IfcText_type);
    declarations.push_back(IFC2X3_IfcTextAlignment_type);
    declarations.push_back(IFC2X3_IfcTextDecoration_type);
    declarations.push_back(IFC2X3_IfcTextFontName_type);
    declarations.push_back(IFC2X3_IfcTextPath_type);
    declarations.push_back(IFC2X3_IfcTextTransformation_type);
    declarations.push_back(IFC2X3_IfcThermalAdmittanceMeasure_type);
    declarations.push_back(IFC2X3_IfcThermalConductivityMeasure_type);
    declarations.push_back(IFC2X3_IfcThermalExpansionCoefficientMeasure_type);
    declarations.push_back(IFC2X3_IfcThermalLoadSourceEnum_type);
    declarations.push_back(IFC2X3_IfcThermalLoadTypeEnum_type);
    declarations.push_back(IFC2X3_IfcThermalResistanceMeasure_type);
    declarations.push_back(IFC2X3_IfcThermalTransmittanceMeasure_type);
    declarations.push_back(IFC2X3_IfcThermodynamicTemperatureMeasure_type);
    declarations.push_back(IFC2X3_IfcTimeMeasure_type);
    declarations.push_back(IFC2X3_IfcTimeSeriesDataTypeEnum_type);
    declarations.push_back(IFC2X3_IfcTimeSeriesScheduleTypeEnum_type);
    declarations.push_back(IFC2X3_IfcTimeStamp_type);
    declarations.push_back(IFC2X3_IfcTorqueMeasure_type);
    declarations.push_back(IFC2X3_IfcTransformerTypeEnum_type);
    declarations.push_back(IFC2X3_IfcTransitionCode_type);
    declarations.push_back(IFC2X3_IfcTransportElementTypeEnum_type);
    declarations.push_back(IFC2X3_IfcTrimmingPreference_type);
    declarations.push_back(IFC2X3_IfcTubeBundleTypeEnum_type);
    declarations.push_back(IFC2X3_IfcUnitEnum_type);
    declarations.push_back(IFC2X3_IfcUnitaryEquipmentTypeEnum_type);
    declarations.push_back(IFC2X3_IfcValveTypeEnum_type);
    declarations.push_back(IFC2X3_IfcVaporPermeabilityMeasure_type);
    declarations.push_back(IFC2X3_IfcVibrationIsolatorTypeEnum_type);
    declarations.push_back(IFC2X3_IfcVolumeMeasure_type);
    declarations.push_back(IFC2X3_IfcVolumetricFlowRateMeasure_type);
    declarations.push_back(IFC2X3_IfcWallTypeEnum_type);
    declarations.push_back(IFC2X3_IfcWarpingConstantMeasure_type);
    declarations.push_back(IFC2X3_IfcWarpingMomentMeasure_type);
    declarations.push_back(IFC2X3_IfcWasteTerminalTypeEnum_type);
    declarations.push_back(IFC2X3_IfcWindowPanelOperationEnum_type);
    declarations.push_back(IFC2X3_IfcWindowPanelPositionEnum_type);
    declarations.push_back(IFC2X3_IfcWindowStyleConstructionEnum_type);
    declarations.push_back(IFC2X3_IfcWindowStyleOperationEnum_type);
    declarations.push_back(IFC2X3_IfcWorkControlTypeEnum_type);
    declarations.push_back(IFC2X3_IfcYearNumber_type);
    declarations.push_back(IFC2X3_IfcActorRole_type);
    declarations.push_back(IFC2X3_IfcAddress_type);
    declarations.push_back(IFC2X3_IfcApplication_type);
    declarations.push_back(IFC2X3_IfcAppliedValue_type);
    declarations.push_back(IFC2X3_IfcAppliedValueRelationship_type);
    declarations.push_back(IFC2X3_IfcApproval_type);
    declarations.push_back(IFC2X3_IfcApprovalActorRelationship_type);
    declarations.push_back(IFC2X3_IfcApprovalPropertyRelationship_type);
    declarations.push_back(IFC2X3_IfcApprovalRelationship_type);
    declarations.push_back(IFC2X3_IfcBoundaryCondition_type);
    declarations.push_back(IFC2X3_IfcBoundaryEdgeCondition_type);
    declarations.push_back(IFC2X3_IfcBoundaryFaceCondition_type);
    declarations.push_back(IFC2X3_IfcBoundaryNodeCondition_type);
    declarations.push_back(IFC2X3_IfcBoundaryNodeConditionWarping_type);
    declarations.push_back(IFC2X3_IfcCalendarDate_type);
    declarations.push_back(IFC2X3_IfcClassification_type);
    declarations.push_back(IFC2X3_IfcClassificationItem_type);
    declarations.push_back(IFC2X3_IfcClassificationItemRelationship_type);
    declarations.push_back(IFC2X3_IfcClassificationNotation_type);
    declarations.push_back(IFC2X3_IfcClassificationNotationFacet_type);
    declarations.push_back(IFC2X3_IfcColourSpecification_type);
    declarations.push_back(IFC2X3_IfcConnectionGeometry_type);
    declarations.push_back(IFC2X3_IfcConnectionPointGeometry_type);
    declarations.push_back(IFC2X3_IfcConnectionPortGeometry_type);
    declarations.push_back(IFC2X3_IfcConnectionSurfaceGeometry_type);
    declarations.push_back(IFC2X3_IfcConstraint_type);
    declarations.push_back(IFC2X3_IfcConstraintAggregationRelationship_type);
    declarations.push_back(IFC2X3_IfcConstraintClassificationRelationship_type);
    declarations.push_back(IFC2X3_IfcConstraintRelationship_type);
    declarations.push_back(IFC2X3_IfcCoordinatedUniversalTimeOffset_type);
    declarations.push_back(IFC2X3_IfcCostValue_type);
    declarations.push_back(IFC2X3_IfcCurrencyRelationship_type);
    declarations.push_back(IFC2X3_IfcCurveStyleFont_type);
    declarations.push_back(IFC2X3_IfcCurveStyleFontAndScaling_type);
    declarations.push_back(IFC2X3_IfcCurveStyleFontPattern_type);
    declarations.push_back(IFC2X3_IfcDateAndTime_type);
    declarations.push_back(IFC2X3_IfcDerivedUnit_type);
    declarations.push_back(IFC2X3_IfcDerivedUnitElement_type);
    declarations.push_back(IFC2X3_IfcDimensionalExponents_type);
    declarations.push_back(IFC2X3_IfcDocumentElectronicFormat_type);
    declarations.push_back(IFC2X3_IfcDocumentInformation_type);
    declarations.push_back(IFC2X3_IfcDocumentInformationRelationship_type);
    declarations.push_back(IFC2X3_IfcDraughtingCalloutRelationship_type);
    declarations.push_back(IFC2X3_IfcEnvironmentalImpactValue_type);
    declarations.push_back(IFC2X3_IfcExternalReference_type);
    declarations.push_back(IFC2X3_IfcExternallyDefinedHatchStyle_type);
    declarations.push_back(IFC2X3_IfcExternallyDefinedSurfaceStyle_type);
    declarations.push_back(IFC2X3_IfcExternallyDefinedSymbol_type);
    declarations.push_back(IFC2X3_IfcExternallyDefinedTextFont_type);
    declarations.push_back(IFC2X3_IfcGridAxis_type);
    declarations.push_back(IFC2X3_IfcIrregularTimeSeriesValue_type);
    declarations.push_back(IFC2X3_IfcLibraryInformation_type);
    declarations.push_back(IFC2X3_IfcLibraryReference_type);
    declarations.push_back(IFC2X3_IfcLightDistributionData_type);
    declarations.push_back(IFC2X3_IfcLightIntensityDistribution_type);
    declarations.push_back(IFC2X3_IfcLocalTime_type);
    declarations.push_back(IFC2X3_IfcMaterial_type);
    declarations.push_back(IFC2X3_IfcMaterialClassificationRelationship_type);
    declarations.push_back(IFC2X3_IfcMaterialLayer_type);
    declarations.push_back(IFC2X3_IfcMaterialLayerSet_type);
    declarations.push_back(IFC2X3_IfcMaterialLayerSetUsage_type);
    declarations.push_back(IFC2X3_IfcMaterialList_type);
    declarations.push_back(IFC2X3_IfcMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcMeasureWithUnit_type);
    declarations.push_back(IFC2X3_IfcMechanicalMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcMechanicalSteelMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcMetric_type);
    declarations.push_back(IFC2X3_IfcMonetaryUnit_type);
    declarations.push_back(IFC2X3_IfcNamedUnit_type);
    declarations.push_back(IFC2X3_IfcObjectPlacement_type);
    declarations.push_back(IFC2X3_IfcObjective_type);
    declarations.push_back(IFC2X3_IfcOpticalMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcOrganization_type);
    declarations.push_back(IFC2X3_IfcOrganizationRelationship_type);
    declarations.push_back(IFC2X3_IfcOwnerHistory_type);
    declarations.push_back(IFC2X3_IfcPerson_type);
    declarations.push_back(IFC2X3_IfcPersonAndOrganization_type);
    declarations.push_back(IFC2X3_IfcPhysicalQuantity_type);
    declarations.push_back(IFC2X3_IfcPhysicalSimpleQuantity_type);
    declarations.push_back(IFC2X3_IfcPostalAddress_type);
    declarations.push_back(IFC2X3_IfcPreDefinedItem_type);
    declarations.push_back(IFC2X3_IfcPreDefinedSymbol_type);
    declarations.push_back(IFC2X3_IfcPreDefinedTerminatorSymbol_type);
    declarations.push_back(IFC2X3_IfcPreDefinedTextFont_type);
    declarations.push_back(IFC2X3_IfcPresentationLayerAssignment_type);
    declarations.push_back(IFC2X3_IfcPresentationLayerWithStyle_type);
    declarations.push_back(IFC2X3_IfcPresentationStyle_type);
    declarations.push_back(IFC2X3_IfcPresentationStyleAssignment_type);
    declarations.push_back(IFC2X3_IfcProductRepresentation_type);
    declarations.push_back(IFC2X3_IfcProductsOfCombustionProperties_type);
    declarations.push_back(IFC2X3_IfcProfileDef_type);
    declarations.push_back(IFC2X3_IfcProfileProperties_type);
    declarations.push_back(IFC2X3_IfcProperty_type);
    declarations.push_back(IFC2X3_IfcPropertyConstraintRelationship_type);
    declarations.push_back(IFC2X3_IfcPropertyDependencyRelationship_type);
    declarations.push_back(IFC2X3_IfcPropertyEnumeration_type);
    declarations.push_back(IFC2X3_IfcQuantityArea_type);
    declarations.push_back(IFC2X3_IfcQuantityCount_type);
    declarations.push_back(IFC2X3_IfcQuantityLength_type);
    declarations.push_back(IFC2X3_IfcQuantityTime_type);
    declarations.push_back(IFC2X3_IfcQuantityVolume_type);
    declarations.push_back(IFC2X3_IfcQuantityWeight_type);
    declarations.push_back(IFC2X3_IfcReferencesValueDocument_type);
    declarations.push_back(IFC2X3_IfcReinforcementBarProperties_type);
    declarations.push_back(IFC2X3_IfcRelaxation_type);
    declarations.push_back(IFC2X3_IfcRepresentation_type);
    declarations.push_back(IFC2X3_IfcRepresentationContext_type);
    declarations.push_back(IFC2X3_IfcRepresentationItem_type);
    declarations.push_back(IFC2X3_IfcRepresentationMap_type);
    declarations.push_back(IFC2X3_IfcRibPlateProfileProperties_type);
    declarations.push_back(IFC2X3_IfcRoot_type);
    declarations.push_back(IFC2X3_IfcSIUnit_type);
    declarations.push_back(IFC2X3_IfcSectionProperties_type);
    declarations.push_back(IFC2X3_IfcSectionReinforcementProperties_type);
    declarations.push_back(IFC2X3_IfcShapeAspect_type);
    declarations.push_back(IFC2X3_IfcShapeModel_type);
    declarations.push_back(IFC2X3_IfcShapeRepresentation_type);
    declarations.push_back(IFC2X3_IfcSimpleProperty_type);
    declarations.push_back(IFC2X3_IfcStructuralConnectionCondition_type);
    declarations.push_back(IFC2X3_IfcStructuralLoad_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadStatic_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadTemperature_type);
    declarations.push_back(IFC2X3_IfcStyleModel_type);
    declarations.push_back(IFC2X3_IfcStyledItem_type);
    declarations.push_back(IFC2X3_IfcStyledRepresentation_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyle_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyleLighting_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyleRefraction_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyleShading_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyleWithTextures_type);
    declarations.push_back(IFC2X3_IfcSurfaceTexture_type);
    declarations.push_back(IFC2X3_IfcSymbolStyle_type);
    declarations.push_back(IFC2X3_IfcTable_type);
    declarations.push_back(IFC2X3_IfcTableRow_type);
    declarations.push_back(IFC2X3_IfcTelecomAddress_type);
    declarations.push_back(IFC2X3_IfcTextStyle_type);
    declarations.push_back(IFC2X3_IfcTextStyleFontModel_type);
    declarations.push_back(IFC2X3_IfcTextStyleForDefinedFont_type);
    declarations.push_back(IFC2X3_IfcTextStyleTextModel_type);
    declarations.push_back(IFC2X3_IfcTextStyleWithBoxCharacteristics_type);
    declarations.push_back(IFC2X3_IfcTextureCoordinate_type);
    declarations.push_back(IFC2X3_IfcTextureCoordinateGenerator_type);
    declarations.push_back(IFC2X3_IfcTextureMap_type);
    declarations.push_back(IFC2X3_IfcTextureVertex_type);
    declarations.push_back(IFC2X3_IfcThermalMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcTimeSeries_type);
    declarations.push_back(IFC2X3_IfcTimeSeriesReferenceRelationship_type);
    declarations.push_back(IFC2X3_IfcTimeSeriesValue_type);
    declarations.push_back(IFC2X3_IfcTopologicalRepresentationItem_type);
    declarations.push_back(IFC2X3_IfcTopologyRepresentation_type);
    declarations.push_back(IFC2X3_IfcUnitAssignment_type);
    declarations.push_back(IFC2X3_IfcVertex_type);
    declarations.push_back(IFC2X3_IfcVertexBasedTextureMap_type);
    declarations.push_back(IFC2X3_IfcVertexPoint_type);
    declarations.push_back(IFC2X3_IfcVirtualGridIntersection_type);
    declarations.push_back(IFC2X3_IfcWaterProperties_type);
    declarations.push_back(IFC2X3_IfcActorSelect_type);
    declarations.push_back(IFC2X3_IfcAppliedValueSelect_type);
    declarations.push_back(IFC2X3_IfcBoxAlignment_type);
    declarations.push_back(IFC2X3_IfcCharacterStyleSelect_type);
    declarations.push_back(IFC2X3_IfcConditionCriterionSelect_type);
    declarations.push_back(IFC2X3_IfcDateTimeSelect_type);
    declarations.push_back(IFC2X3_IfcDefinedSymbolSelect_type);
    declarations.push_back(IFC2X3_IfcDerivedMeasureValue_type);
    declarations.push_back(IFC2X3_IfcLayeredItem_type);
    declarations.push_back(IFC2X3_IfcLibrarySelect_type);
    declarations.push_back(IFC2X3_IfcLightDistributionDataSourceSelect_type);
    declarations.push_back(IFC2X3_IfcMaterialSelect_type);
    declarations.push_back(IFC2X3_IfcMetricValueSelect_type);
    declarations.push_back(IFC2X3_IfcNormalisedRatioMeasure_type);
    declarations.push_back(IFC2X3_IfcObjectReferenceSelect_type);
    declarations.push_back(IFC2X3_IfcPositiveRatioMeasure_type);
    declarations.push_back(IFC2X3_IfcSimpleValue_type);
    declarations.push_back(IFC2X3_IfcSizeSelect_type);
    declarations.push_back(IFC2X3_IfcSpecularHighlightSelect_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyleElementSelect_type);
    declarations.push_back(IFC2X3_IfcTextFontSelect_type);
    declarations.push_back(IFC2X3_IfcTextStyleSelect_type);
    declarations.push_back(IFC2X3_IfcUnit_type);
    declarations.push_back(IFC2X3_IfcAnnotationOccurrence_type);
    declarations.push_back(IFC2X3_IfcAnnotationSurfaceOccurrence_type);
    declarations.push_back(IFC2X3_IfcAnnotationSymbolOccurrence_type);
    declarations.push_back(IFC2X3_IfcAnnotationTextOccurrence_type);
    declarations.push_back(IFC2X3_IfcArbitraryClosedProfileDef_type);
    declarations.push_back(IFC2X3_IfcArbitraryOpenProfileDef_type);
    declarations.push_back(IFC2X3_IfcArbitraryProfileDefWithVoids_type);
    declarations.push_back(IFC2X3_IfcBlobTexture_type);
    declarations.push_back(IFC2X3_IfcCenterLineProfileDef_type);
    declarations.push_back(IFC2X3_IfcClassificationReference_type);
    declarations.push_back(IFC2X3_IfcColourRgb_type);
    declarations.push_back(IFC2X3_IfcComplexProperty_type);
    declarations.push_back(IFC2X3_IfcCompositeProfileDef_type);
    declarations.push_back(IFC2X3_IfcConnectedFaceSet_type);
    declarations.push_back(IFC2X3_IfcConnectionCurveGeometry_type);
    declarations.push_back(IFC2X3_IfcConnectionPointEccentricity_type);
    declarations.push_back(IFC2X3_IfcContextDependentUnit_type);
    declarations.push_back(IFC2X3_IfcConversionBasedUnit_type);
    declarations.push_back(IFC2X3_IfcCurveStyle_type);
    declarations.push_back(IFC2X3_IfcDerivedProfileDef_type);
    declarations.push_back(IFC2X3_IfcDimensionCalloutRelationship_type);
    declarations.push_back(IFC2X3_IfcDimensionPair_type);
    declarations.push_back(IFC2X3_IfcDocumentReference_type);
    declarations.push_back(IFC2X3_IfcDraughtingPreDefinedTextFont_type);
    declarations.push_back(IFC2X3_IfcEdge_type);
    declarations.push_back(IFC2X3_IfcEdgeCurve_type);
    declarations.push_back(IFC2X3_IfcExtendedMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcFace_type);
    declarations.push_back(IFC2X3_IfcFaceBound_type);
    declarations.push_back(IFC2X3_IfcFaceOuterBound_type);
    declarations.push_back(IFC2X3_IfcFaceSurface_type);
    declarations.push_back(IFC2X3_IfcFailureConnectionCondition_type);
    declarations.push_back(IFC2X3_IfcFillAreaStyle_type);
    declarations.push_back(IFC2X3_IfcFuelProperties_type);
    declarations.push_back(IFC2X3_IfcGeneralMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcGeneralProfileProperties_type);
    declarations.push_back(IFC2X3_IfcGeometricRepresentationContext_type);
    declarations.push_back(IFC2X3_IfcGeometricRepresentationItem_type);
    declarations.push_back(IFC2X3_IfcGeometricRepresentationSubContext_type);
    declarations.push_back(IFC2X3_IfcGeometricSet_type);
    declarations.push_back(IFC2X3_IfcGridPlacement_type);
    declarations.push_back(IFC2X3_IfcHalfSpaceSolid_type);
    declarations.push_back(IFC2X3_IfcHygroscopicMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcImageTexture_type);
    declarations.push_back(IFC2X3_IfcIrregularTimeSeries_type);
    declarations.push_back(IFC2X3_IfcLightSource_type);
    declarations.push_back(IFC2X3_IfcLightSourceAmbient_type);
    declarations.push_back(IFC2X3_IfcLightSourceDirectional_type);
    declarations.push_back(IFC2X3_IfcLightSourceGoniometric_type);
    declarations.push_back(IFC2X3_IfcLightSourcePositional_type);
    declarations.push_back(IFC2X3_IfcLightSourceSpot_type);
    declarations.push_back(IFC2X3_IfcLocalPlacement_type);
    declarations.push_back(IFC2X3_IfcLoop_type);
    declarations.push_back(IFC2X3_IfcMappedItem_type);
    declarations.push_back(IFC2X3_IfcMaterialDefinitionRepresentation_type);
    declarations.push_back(IFC2X3_IfcMechanicalConcreteMaterialProperties_type);
    declarations.push_back(IFC2X3_IfcObjectDefinition_type);
    declarations.push_back(IFC2X3_IfcOneDirectionRepeatFactor_type);
    declarations.push_back(IFC2X3_IfcOpenShell_type);
    declarations.push_back(IFC2X3_IfcOrientedEdge_type);
    declarations.push_back(IFC2X3_IfcParameterizedProfileDef_type);
    declarations.push_back(IFC2X3_IfcPath_type);
    declarations.push_back(IFC2X3_IfcPhysicalComplexQuantity_type);
    declarations.push_back(IFC2X3_IfcPixelTexture_type);
    declarations.push_back(IFC2X3_IfcPlacement_type);
    declarations.push_back(IFC2X3_IfcPlanarExtent_type);
    declarations.push_back(IFC2X3_IfcPoint_type);
    declarations.push_back(IFC2X3_IfcPointOnCurve_type);
    declarations.push_back(IFC2X3_IfcPointOnSurface_type);
    declarations.push_back(IFC2X3_IfcPolyLoop_type);
    declarations.push_back(IFC2X3_IfcPolygonalBoundedHalfSpace_type);
    declarations.push_back(IFC2X3_IfcPreDefinedColour_type);
    declarations.push_back(IFC2X3_IfcPreDefinedCurveFont_type);
    declarations.push_back(IFC2X3_IfcPreDefinedDimensionSymbol_type);
    declarations.push_back(IFC2X3_IfcPreDefinedPointMarkerSymbol_type);
    declarations.push_back(IFC2X3_IfcProductDefinitionShape_type);
    declarations.push_back(IFC2X3_IfcPropertyBoundedValue_type);
    declarations.push_back(IFC2X3_IfcPropertyDefinition_type);
    declarations.push_back(IFC2X3_IfcPropertyEnumeratedValue_type);
    declarations.push_back(IFC2X3_IfcPropertyListValue_type);
    declarations.push_back(IFC2X3_IfcPropertyReferenceValue_type);
    declarations.push_back(IFC2X3_IfcPropertySetDefinition_type);
    declarations.push_back(IFC2X3_IfcPropertySingleValue_type);
    declarations.push_back(IFC2X3_IfcPropertyTableValue_type);
    declarations.push_back(IFC2X3_IfcRectangleProfileDef_type);
    declarations.push_back(IFC2X3_IfcRegularTimeSeries_type);
    declarations.push_back(IFC2X3_IfcReinforcementDefinitionProperties_type);
    declarations.push_back(IFC2X3_IfcRelationship_type);
    declarations.push_back(IFC2X3_IfcRoundedRectangleProfileDef_type);
    declarations.push_back(IFC2X3_IfcSectionedSpine_type);
    declarations.push_back(IFC2X3_IfcServiceLifeFactor_type);
    declarations.push_back(IFC2X3_IfcShellBasedSurfaceModel_type);
    declarations.push_back(IFC2X3_IfcSlippageConnectionCondition_type);
    declarations.push_back(IFC2X3_IfcSolidModel_type);
    declarations.push_back(IFC2X3_IfcSoundProperties_type);
    declarations.push_back(IFC2X3_IfcSoundValue_type);
    declarations.push_back(IFC2X3_IfcSpaceThermalLoadProperties_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadLinearForce_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadPlanarForce_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadSingleDisplacement_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadSingleDisplacementDistortion_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadSingleForce_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadSingleForceWarping_type);
    declarations.push_back(IFC2X3_IfcStructuralProfileProperties_type);
    declarations.push_back(IFC2X3_IfcStructuralSteelProfileProperties_type);
    declarations.push_back(IFC2X3_IfcSubedge_type);
    declarations.push_back(IFC2X3_IfcSurface_type);
    declarations.push_back(IFC2X3_IfcSurfaceStyleRendering_type);
    declarations.push_back(IFC2X3_IfcSweptAreaSolid_type);
    declarations.push_back(IFC2X3_IfcSweptDiskSolid_type);
    declarations.push_back(IFC2X3_IfcSweptSurface_type);
    declarations.push_back(IFC2X3_IfcTShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcTerminatorSymbol_type);
    declarations.push_back(IFC2X3_IfcTextLiteral_type);
    declarations.push_back(IFC2X3_IfcTextLiteralWithExtent_type);
    declarations.push_back(IFC2X3_IfcTrapeziumProfileDef_type);
    declarations.push_back(IFC2X3_IfcTwoDirectionRepeatFactor_type);
    declarations.push_back(IFC2X3_IfcTypeObject_type);
    declarations.push_back(IFC2X3_IfcTypeProduct_type);
    declarations.push_back(IFC2X3_IfcUShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcVector_type);
    declarations.push_back(IFC2X3_IfcVertexLoop_type);
    declarations.push_back(IFC2X3_IfcWindowLiningProperties_type);
    declarations.push_back(IFC2X3_IfcWindowPanelProperties_type);
    declarations.push_back(IFC2X3_IfcWindowStyle_type);
    declarations.push_back(IFC2X3_IfcZShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcClassificationNotationSelect_type);
    declarations.push_back(IFC2X3_IfcColour_type);
    declarations.push_back(IFC2X3_IfcColourOrFactor_type);
    declarations.push_back(IFC2X3_IfcCurveStyleFontSelect_type);
    declarations.push_back(IFC2X3_IfcDocumentSelect_type);
    declarations.push_back(IFC2X3_IfcHatchLineDistanceSelect_type);
    declarations.push_back(IFC2X3_IfcMeasureValue_type);
    declarations.push_back(IFC2X3_IfcPointOrVertexPoint_type);
    declarations.push_back(IFC2X3_IfcPresentationStyleSelect_type);
    declarations.push_back(IFC2X3_IfcSymbolStyleSelect_type);
    declarations.push_back(IFC2X3_IfcValue_type);
    declarations.push_back(IFC2X3_IfcAnnotationCurveOccurrence_type);
    declarations.push_back(IFC2X3_IfcAnnotationFillArea_type);
    declarations.push_back(IFC2X3_IfcAnnotationFillAreaOccurrence_type);
    declarations.push_back(IFC2X3_IfcAnnotationSurface_type);
    declarations.push_back(IFC2X3_IfcAxis1Placement_type);
    declarations.push_back(IFC2X3_IfcAxis2Placement2D_type);
    declarations.push_back(IFC2X3_IfcAxis2Placement3D_type);
    declarations.push_back(IFC2X3_IfcBooleanResult_type);
    declarations.push_back(IFC2X3_IfcBoundedSurface_type);
    declarations.push_back(IFC2X3_IfcBoundingBox_type);
    declarations.push_back(IFC2X3_IfcBoxedHalfSpace_type);
    declarations.push_back(IFC2X3_IfcCShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcCartesianPoint_type);
    declarations.push_back(IFC2X3_IfcCartesianTransformationOperator_type);
    declarations.push_back(IFC2X3_IfcCartesianTransformationOperator2D_type);
    declarations.push_back(IFC2X3_IfcCartesianTransformationOperator2DnonUniform_type);
    declarations.push_back(IFC2X3_IfcCartesianTransformationOperator3D_type);
    declarations.push_back(IFC2X3_IfcCartesianTransformationOperator3DnonUniform_type);
    declarations.push_back(IFC2X3_IfcCircleProfileDef_type);
    declarations.push_back(IFC2X3_IfcClosedShell_type);
    declarations.push_back(IFC2X3_IfcCompositeCurveSegment_type);
    declarations.push_back(IFC2X3_IfcCraneRailAShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcCraneRailFShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcCsgPrimitive3D_type);
    declarations.push_back(IFC2X3_IfcCsgSolid_type);
    declarations.push_back(IFC2X3_IfcCurve_type);
    declarations.push_back(IFC2X3_IfcCurveBoundedPlane_type);
    declarations.push_back(IFC2X3_IfcDefinedSymbol_type);
    declarations.push_back(IFC2X3_IfcDimensionCurve_type);
    declarations.push_back(IFC2X3_IfcDimensionCurveTerminator_type);
    declarations.push_back(IFC2X3_IfcDirection_type);
    declarations.push_back(IFC2X3_IfcDoorLiningProperties_type);
    declarations.push_back(IFC2X3_IfcDoorPanelProperties_type);
    declarations.push_back(IFC2X3_IfcDoorStyle_type);
    declarations.push_back(IFC2X3_IfcDraughtingCallout_type);
    declarations.push_back(IFC2X3_IfcDraughtingPreDefinedColour_type);
    declarations.push_back(IFC2X3_IfcDraughtingPreDefinedCurveFont_type);
    declarations.push_back(IFC2X3_IfcEdgeLoop_type);
    declarations.push_back(IFC2X3_IfcElementQuantity_type);
    declarations.push_back(IFC2X3_IfcElementType_type);
    declarations.push_back(IFC2X3_IfcElementarySurface_type);
    declarations.push_back(IFC2X3_IfcEllipseProfileDef_type);
    declarations.push_back(IFC2X3_IfcEnergyProperties_type);
    declarations.push_back(IFC2X3_IfcExtrudedAreaSolid_type);
    declarations.push_back(IFC2X3_IfcFaceBasedSurfaceModel_type);
    declarations.push_back(IFC2X3_IfcFillAreaStyleHatching_type);
    declarations.push_back(IFC2X3_IfcFillAreaStyleTileSymbolWithStyle_type);
    declarations.push_back(IFC2X3_IfcFillAreaStyleTiles_type);
    declarations.push_back(IFC2X3_IfcFluidFlowProperties_type);
    declarations.push_back(IFC2X3_IfcFurnishingElementType_type);
    declarations.push_back(IFC2X3_IfcFurnitureType_type);
    declarations.push_back(IFC2X3_IfcGeometricCurveSet_type);
    declarations.push_back(IFC2X3_IfcIShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcLShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcLine_type);
    declarations.push_back(IFC2X3_IfcManifoldSolidBrep_type);
    declarations.push_back(IFC2X3_IfcObject_type);
    declarations.push_back(IFC2X3_IfcOffsetCurve2D_type);
    declarations.push_back(IFC2X3_IfcOffsetCurve3D_type);
    declarations.push_back(IFC2X3_IfcPermeableCoveringProperties_type);
    declarations.push_back(IFC2X3_IfcPlanarBox_type);
    declarations.push_back(IFC2X3_IfcPlane_type);
    declarations.push_back(IFC2X3_IfcProcess_type);
    declarations.push_back(IFC2X3_IfcProduct_type);
    declarations.push_back(IFC2X3_IfcProject_type);
    declarations.push_back(IFC2X3_IfcProjectionCurve_type);
    declarations.push_back(IFC2X3_IfcPropertySet_type);
    declarations.push_back(IFC2X3_IfcProxy_type);
    declarations.push_back(IFC2X3_IfcRectangleHollowProfileDef_type);
    declarations.push_back(IFC2X3_IfcRectangularPyramid_type);
    declarations.push_back(IFC2X3_IfcRectangularTrimmedSurface_type);
    declarations.push_back(IFC2X3_IfcRelAssigns_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToActor_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToControl_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToGroup_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToProcess_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToProduct_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToProjectOrder_type);
    declarations.push_back(IFC2X3_IfcRelAssignsToResource_type);
    declarations.push_back(IFC2X3_IfcRelAssociates_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesAppliedValue_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesApproval_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesClassification_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesConstraint_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesDocument_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesLibrary_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesMaterial_type);
    declarations.push_back(IFC2X3_IfcRelAssociatesProfileProperties_type);
    declarations.push_back(IFC2X3_IfcRelConnects_type);
    declarations.push_back(IFC2X3_IfcRelConnectsElements_type);
    declarations.push_back(IFC2X3_IfcRelConnectsPathElements_type);
    declarations.push_back(IFC2X3_IfcRelConnectsPortToElement_type);
    declarations.push_back(IFC2X3_IfcRelConnectsPorts_type);
    declarations.push_back(IFC2X3_IfcRelConnectsStructuralActivity_type);
    declarations.push_back(IFC2X3_IfcRelConnectsStructuralElement_type);
    declarations.push_back(IFC2X3_IfcRelConnectsStructuralMember_type);
    declarations.push_back(IFC2X3_IfcRelConnectsWithEccentricity_type);
    declarations.push_back(IFC2X3_IfcRelConnectsWithRealizingElements_type);
    declarations.push_back(IFC2X3_IfcRelContainedInSpatialStructure_type);
    declarations.push_back(IFC2X3_IfcRelCoversBldgElements_type);
    declarations.push_back(IFC2X3_IfcRelCoversSpaces_type);
    declarations.push_back(IFC2X3_IfcRelDecomposes_type);
    declarations.push_back(IFC2X3_IfcRelDefines_type);
    declarations.push_back(IFC2X3_IfcRelDefinesByProperties_type);
    declarations.push_back(IFC2X3_IfcRelDefinesByType_type);
    declarations.push_back(IFC2X3_IfcRelFillsElement_type);
    declarations.push_back(IFC2X3_IfcRelFlowControlElements_type);
    declarations.push_back(IFC2X3_IfcRelInteractionRequirements_type);
    declarations.push_back(IFC2X3_IfcRelNests_type);
    declarations.push_back(IFC2X3_IfcRelOccupiesSpaces_type);
    declarations.push_back(IFC2X3_IfcRelOverridesProperties_type);
    declarations.push_back(IFC2X3_IfcRelProjectsElement_type);
    declarations.push_back(IFC2X3_IfcRelReferencedInSpatialStructure_type);
    declarations.push_back(IFC2X3_IfcRelSchedulesCostItems_type);
    declarations.push_back(IFC2X3_IfcRelSequence_type);
    declarations.push_back(IFC2X3_IfcRelServicesBuildings_type);
    declarations.push_back(IFC2X3_IfcRelSpaceBoundary_type);
    declarations.push_back(IFC2X3_IfcRelVoidsElement_type);
    declarations.push_back(IFC2X3_IfcResource_type);
    declarations.push_back(IFC2X3_IfcRevolvedAreaSolid_type);
    declarations.push_back(IFC2X3_IfcRightCircularCone_type);
    declarations.push_back(IFC2X3_IfcRightCircularCylinder_type);
    declarations.push_back(IFC2X3_IfcSpatialStructureElement_type);
    declarations.push_back(IFC2X3_IfcSpatialStructureElementType_type);
    declarations.push_back(IFC2X3_IfcSphere_type);
    declarations.push_back(IFC2X3_IfcStructuralActivity_type);
    declarations.push_back(IFC2X3_IfcStructuralItem_type);
    declarations.push_back(IFC2X3_IfcStructuralMember_type);
    declarations.push_back(IFC2X3_IfcStructuralReaction_type);
    declarations.push_back(IFC2X3_IfcStructuralSurfaceMember_type);
    declarations.push_back(IFC2X3_IfcStructuralSurfaceMemberVarying_type);
    declarations.push_back(IFC2X3_IfcStructuredDimensionCallout_type);
    declarations.push_back(IFC2X3_IfcSurfaceCurveSweptAreaSolid_type);
    declarations.push_back(IFC2X3_IfcSurfaceOfLinearExtrusion_type);
    declarations.push_back(IFC2X3_IfcSurfaceOfRevolution_type);
    declarations.push_back(IFC2X3_IfcSystemFurnitureElementType_type);
    declarations.push_back(IFC2X3_IfcTask_type);
    declarations.push_back(IFC2X3_IfcTransportElementType_type);
    declarations.push_back(IFC2X3_IfcAxis2Placement_type);
    declarations.push_back(IFC2X3_IfcBooleanOperand_type);
    declarations.push_back(IFC2X3_IfcCsgSelect_type);
    declarations.push_back(IFC2X3_IfcCurveFontOrScaledCurveFontSelect_type);
    declarations.push_back(IFC2X3_IfcDraughtingCalloutElement_type);
    declarations.push_back(IFC2X3_IfcFillAreaStyleTileShapeSelect_type);
    declarations.push_back(IFC2X3_IfcFillStyleSelect_type);
    declarations.push_back(IFC2X3_IfcGeometricSetSelect_type);
    declarations.push_back(IFC2X3_IfcOrientationSelect_type);
    declarations.push_back(IFC2X3_IfcShell_type);
    declarations.push_back(IFC2X3_IfcSurfaceOrFaceSurface_type);
    declarations.push_back(IFC2X3_IfcTrimmingSelect_type);
    declarations.push_back(IFC2X3_IfcVectorOrDirection_type);
    declarations.push_back(IFC2X3_IfcActor_type);
    declarations.push_back(IFC2X3_IfcAnnotation_type);
    declarations.push_back(IFC2X3_IfcAsymmetricIShapeProfileDef_type);
    declarations.push_back(IFC2X3_IfcBlock_type);
    declarations.push_back(IFC2X3_IfcBooleanClippingResult_type);
    declarations.push_back(IFC2X3_IfcBoundedCurve_type);
    declarations.push_back(IFC2X3_IfcBuilding_type);
    declarations.push_back(IFC2X3_IfcBuildingElementType_type);
    declarations.push_back(IFC2X3_IfcBuildingStorey_type);
    declarations.push_back(IFC2X3_IfcCircleHollowProfileDef_type);
    declarations.push_back(IFC2X3_IfcColumnType_type);
    declarations.push_back(IFC2X3_IfcCompositeCurve_type);
    declarations.push_back(IFC2X3_IfcConic_type);
    declarations.push_back(IFC2X3_IfcConstructionResource_type);
    declarations.push_back(IFC2X3_IfcControl_type);
    declarations.push_back(IFC2X3_IfcCostItem_type);
    declarations.push_back(IFC2X3_IfcCostSchedule_type);
    declarations.push_back(IFC2X3_IfcCoveringType_type);
    declarations.push_back(IFC2X3_IfcCrewResource_type);
    declarations.push_back(IFC2X3_IfcCurtainWallType_type);
    declarations.push_back(IFC2X3_IfcDimensionCurveDirectedCallout_type);
    declarations.push_back(IFC2X3_IfcDistributionElementType_type);
    declarations.push_back(IFC2X3_IfcDistributionFlowElementType_type);
    declarations.push_back(IFC2X3_IfcElectricalBaseProperties_type);
    declarations.push_back(IFC2X3_IfcElement_type);
    declarations.push_back(IFC2X3_IfcElementAssembly_type);
    declarations.push_back(IFC2X3_IfcElementComponent_type);
    declarations.push_back(IFC2X3_IfcElementComponentType_type);
    declarations.push_back(IFC2X3_IfcEllipse_type);
    declarations.push_back(IFC2X3_IfcEnergyConversionDeviceType_type);
    declarations.push_back(IFC2X3_IfcEquipmentElement_type);
    declarations.push_back(IFC2X3_IfcEquipmentStandard_type);
    declarations.push_back(IFC2X3_IfcEvaporativeCoolerType_type);
    declarations.push_back(IFC2X3_IfcEvaporatorType_type);
    declarations.push_back(IFC2X3_IfcFacetedBrep_type);
    declarations.push_back(IFC2X3_IfcFacetedBrepWithVoids_type);
    declarations.push_back(IFC2X3_IfcFastener_type);
    declarations.push_back(IFC2X3_IfcFastenerType_type);
    declarations.push_back(IFC2X3_IfcFeatureElement_type);
    declarations.push_back(IFC2X3_IfcFeatureElementAddition_type);
    declarations.push_back(IFC2X3_IfcFeatureElementSubtraction_type);
    declarations.push_back(IFC2X3_IfcFlowControllerType_type);
    declarations.push_back(IFC2X3_IfcFlowFittingType_type);
    declarations.push_back(IFC2X3_IfcFlowMeterType_type);
    declarations.push_back(IFC2X3_IfcFlowMovingDeviceType_type);
    declarations.push_back(IFC2X3_IfcFlowSegmentType_type);
    declarations.push_back(IFC2X3_IfcFlowStorageDeviceType_type);
    declarations.push_back(IFC2X3_IfcFlowTerminalType_type);
    declarations.push_back(IFC2X3_IfcFlowTreatmentDeviceType_type);
    declarations.push_back(IFC2X3_IfcFurnishingElement_type);
    declarations.push_back(IFC2X3_IfcFurnitureStandard_type);
    declarations.push_back(IFC2X3_IfcGasTerminalType_type);
    declarations.push_back(IFC2X3_IfcGrid_type);
    declarations.push_back(IFC2X3_IfcGroup_type);
    declarations.push_back(IFC2X3_IfcHeatExchangerType_type);
    declarations.push_back(IFC2X3_IfcHumidifierType_type);
    declarations.push_back(IFC2X3_IfcInventory_type);
    declarations.push_back(IFC2X3_IfcJunctionBoxType_type);
    declarations.push_back(IFC2X3_IfcLaborResource_type);
    declarations.push_back(IFC2X3_IfcLampType_type);
    declarations.push_back(IFC2X3_IfcLightFixtureType_type);
    declarations.push_back(IFC2X3_IfcLinearDimension_type);
    declarations.push_back(IFC2X3_IfcMechanicalFastener_type);
    declarations.push_back(IFC2X3_IfcMechanicalFastenerType_type);
    declarations.push_back(IFC2X3_IfcMemberType_type);
    declarations.push_back(IFC2X3_IfcMotorConnectionType_type);
    declarations.push_back(IFC2X3_IfcMove_type);
    declarations.push_back(IFC2X3_IfcOccupant_type);
    declarations.push_back(IFC2X3_IfcOpeningElement_type);
    declarations.push_back(IFC2X3_IfcOrderAction_type);
    declarations.push_back(IFC2X3_IfcOutletType_type);
    declarations.push_back(IFC2X3_IfcPerformanceHistory_type);
    declarations.push_back(IFC2X3_IfcPermit_type);
    declarations.push_back(IFC2X3_IfcPipeFittingType_type);
    declarations.push_back(IFC2X3_IfcPipeSegmentType_type);
    declarations.push_back(IFC2X3_IfcPlateType_type);
    declarations.push_back(IFC2X3_IfcPolyline_type);
    declarations.push_back(IFC2X3_IfcPort_type);
    declarations.push_back(IFC2X3_IfcProcedure_type);
    declarations.push_back(IFC2X3_IfcProjectOrder_type);
    declarations.push_back(IFC2X3_IfcProjectOrderRecord_type);
    declarations.push_back(IFC2X3_IfcProjectionElement_type);
    declarations.push_back(IFC2X3_IfcProtectiveDeviceType_type);
    declarations.push_back(IFC2X3_IfcPumpType_type);
    declarations.push_back(IFC2X3_IfcRadiusDimension_type);
    declarations.push_back(IFC2X3_IfcRailingType_type);
    declarations.push_back(IFC2X3_IfcRampFlightType_type);
    declarations.push_back(IFC2X3_IfcRelAggregates_type);
    declarations.push_back(IFC2X3_IfcRelAssignsTasks_type);
    declarations.push_back(IFC2X3_IfcSanitaryTerminalType_type);
    declarations.push_back(IFC2X3_IfcScheduleTimeControl_type);
    declarations.push_back(IFC2X3_IfcServiceLife_type);
    declarations.push_back(IFC2X3_IfcSite_type);
    declarations.push_back(IFC2X3_IfcSlabType_type);
    declarations.push_back(IFC2X3_IfcSpace_type);
    declarations.push_back(IFC2X3_IfcSpaceHeaterType_type);
    declarations.push_back(IFC2X3_IfcSpaceProgram_type);
    declarations.push_back(IFC2X3_IfcSpaceType_type);
    declarations.push_back(IFC2X3_IfcStackTerminalType_type);
    declarations.push_back(IFC2X3_IfcStairFlightType_type);
    declarations.push_back(IFC2X3_IfcStructuralAction_type);
    declarations.push_back(IFC2X3_IfcStructuralConnection_type);
    declarations.push_back(IFC2X3_IfcStructuralCurveConnection_type);
    declarations.push_back(IFC2X3_IfcStructuralCurveMember_type);
    declarations.push_back(IFC2X3_IfcStructuralCurveMemberVarying_type);
    declarations.push_back(IFC2X3_IfcStructuralLinearAction_type);
    declarations.push_back(IFC2X3_IfcStructuralLinearActionVarying_type);
    declarations.push_back(IFC2X3_IfcStructuralLoadGroup_type);
    declarations.push_back(IFC2X3_IfcStructuralPlanarAction_type);
    declarations.push_back(IFC2X3_IfcStructuralPlanarActionVarying_type);
    declarations.push_back(IFC2X3_IfcStructuralPointAction_type);
    declarations.push_back(IFC2X3_IfcStructuralPointConnection_type);
    declarations.push_back(IFC2X3_IfcStructuralPointReaction_type);
    declarations.push_back(IFC2X3_IfcStructuralResultGroup_type);
    declarations.push_back(IFC2X3_IfcStructuralSurfaceConnection_type);
    declarations.push_back(IFC2X3_IfcSubContractResource_type);
    declarations.push_back(IFC2X3_IfcSwitchingDeviceType_type);
    declarations.push_back(IFC2X3_IfcSystem_type);
    declarations.push_back(IFC2X3_IfcTankType_type);
    declarations.push_back(IFC2X3_IfcTimeSeriesSchedule_type);
    declarations.push_back(IFC2X3_IfcTransformerType_type);
    declarations.push_back(IFC2X3_IfcTransportElement_type);
    declarations.push_back(IFC2X3_IfcTrimmedCurve_type);
    declarations.push_back(IFC2X3_IfcTubeBundleType_type);
    declarations.push_back(IFC2X3_IfcUnitaryEquipmentType_type);
    declarations.push_back(IFC2X3_IfcValveType_type);
    declarations.push_back(IFC2X3_IfcVirtualElement_type);
    declarations.push_back(IFC2X3_IfcWallType_type);
    declarations.push_back(IFC2X3_IfcWasteTerminalType_type);
    declarations.push_back(IFC2X3_IfcWorkControl_type);
    declarations.push_back(IFC2X3_IfcWorkPlan_type);
    declarations.push_back(IFC2X3_IfcWorkSchedule_type);
    declarations.push_back(IFC2X3_IfcZone_type);
    declarations.push_back(IFC2X3_IfcCurveOrEdgeCurve_type);
    declarations.push_back(IFC2X3_IfcStructuralActivityAssignmentSelect_type);
    declarations.push_back(IFC2X3_Ifc2DCompositeCurve_type);
    declarations.push_back(IFC2X3_IfcActionRequest_type);
    declarations.push_back(IFC2X3_IfcAirTerminalBoxType_type);
    declarations.push_back(IFC2X3_IfcAirTerminalType_type);
    declarations.push_back(IFC2X3_IfcAirToAirHeatRecoveryType_type);
    declarations.push_back(IFC2X3_IfcAngularDimension_type);
    declarations.push_back(IFC2X3_IfcAsset_type);
    declarations.push_back(IFC2X3_IfcBSplineCurve_type);
    declarations.push_back(IFC2X3_IfcBeamType_type);
    declarations.push_back(IFC2X3_IfcBezierCurve_type);
    declarations.push_back(IFC2X3_IfcBoilerType_type);
    declarations.push_back(IFC2X3_IfcBuildingElement_type);
    declarations.push_back(IFC2X3_IfcBuildingElementComponent_type);
    declarations.push_back(IFC2X3_IfcBuildingElementPart_type);
    declarations.push_back(IFC2X3_IfcBuildingElementProxy_type);
    declarations.push_back(IFC2X3_IfcBuildingElementProxyType_type);
    declarations.push_back(IFC2X3_IfcCableCarrierFittingType_type);
    declarations.push_back(IFC2X3_IfcCableCarrierSegmentType_type);
    declarations.push_back(IFC2X3_IfcCableSegmentType_type);
    declarations.push_back(IFC2X3_IfcChillerType_type);
    declarations.push_back(IFC2X3_IfcCircle_type);
    declarations.push_back(IFC2X3_IfcCoilType_type);
    declarations.push_back(IFC2X3_IfcColumn_type);
    declarations.push_back(IFC2X3_IfcCompressorType_type);
    declarations.push_back(IFC2X3_IfcCondenserType_type);
    declarations.push_back(IFC2X3_IfcCondition_type);
    declarations.push_back(IFC2X3_IfcConditionCriterion_type);
    declarations.push_back(IFC2X3_IfcConstructionEquipmentResource_type);
    declarations.push_back(IFC2X3_IfcConstructionMaterialResource_type);
    declarations.push_back(IFC2X3_IfcConstructionProductResource_type);
    declarations.push_back(IFC2X3_IfcCooledBeamType_type);
    declarations.push_back(IFC2X3_IfcCoolingTowerType_type);
    declarations.push_back(IFC2X3_IfcCovering_type);
    declarations.push_back(IFC2X3_IfcCurtainWall_type);
    declarations.push_back(IFC2X3_IfcDamperType_type);
    declarations.push_back(IFC2X3_IfcDiameterDimension_type);
    declarations.push_back(IFC2X3_IfcDiscreteAccessory_type);
    declarations.push_back(IFC2X3_IfcDiscreteAccessoryType_type);
    declarations.push_back(IFC2X3_IfcDistributionChamberElementType_type);
    declarations.push_back(IFC2X3_IfcDistributionControlElementType_type);
    declarations.push_back(IFC2X3_IfcDistributionElement_type);
    declarations.push_back(IFC2X3_IfcDistributionFlowElement_type);
    declarations.push_back(IFC2X3_IfcDistributionPort_type);
    declarations.push_back(IFC2X3_IfcDoor_type);
    declarations.push_back(IFC2X3_IfcDuctFittingType_type);
    declarations.push_back(IFC2X3_IfcDuctSegmentType_type);
    declarations.push_back(IFC2X3_IfcDuctSilencerType_type);
    declarations.push_back(IFC2X3_IfcEdgeFeature_type);
    declarations.push_back(IFC2X3_IfcElectricApplianceType_type);
    declarations.push_back(IFC2X3_IfcElectricFlowStorageDeviceType_type);
    declarations.push_back(IFC2X3_IfcElectricGeneratorType_type);
    declarations.push_back(IFC2X3_IfcElectricHeaterType_type);
    declarations.push_back(IFC2X3_IfcElectricMotorType_type);
    declarations.push_back(IFC2X3_IfcElectricTimeControlType_type);
    declarations.push_back(IFC2X3_IfcElectricalCircuit_type);
    declarations.push_back(IFC2X3_IfcElectricalElement_type);
    declarations.push_back(IFC2X3_IfcEnergyConversionDevice_type);
    declarations.push_back(IFC2X3_IfcFanType_type);
    declarations.push_back(IFC2X3_IfcFilterType_type);
    declarations.push_back(IFC2X3_IfcFireSuppressionTerminalType_type);
    declarations.push_back(IFC2X3_IfcFlowController_type);
    declarations.push_back(IFC2X3_IfcFlowFitting_type);
    declarations.push_back(IFC2X3_IfcFlowInstrumentType_type);
    declarations.push_back(IFC2X3_IfcFlowMovingDevice_type);
    declarations.push_back(IFC2X3_IfcFlowSegment_type);
    declarations.push_back(IFC2X3_IfcFlowStorageDevice_type);
    declarations.push_back(IFC2X3_IfcFlowTerminal_type);
    declarations.push_back(IFC2X3_IfcFlowTreatmentDevice_type);
    declarations.push_back(IFC2X3_IfcFooting_type);
    declarations.push_back(IFC2X3_IfcMember_type);
    declarations.push_back(IFC2X3_IfcPile_type);
    declarations.push_back(IFC2X3_IfcPlate_type);
    declarations.push_back(IFC2X3_IfcRailing_type);
    declarations.push_back(IFC2X3_IfcRamp_type);
    declarations.push_back(IFC2X3_IfcRampFlight_type);
    declarations.push_back(IFC2X3_IfcRationalBezierCurve_type);
    declarations.push_back(IFC2X3_IfcReinforcingElement_type);
    declarations.push_back(IFC2X3_IfcReinforcingMesh_type);
    declarations.push_back(IFC2X3_IfcRoof_type);
    declarations.push_back(IFC2X3_IfcRoundedEdgeFeature_type);
    declarations.push_back(IFC2X3_IfcSensorType_type);
    declarations.push_back(IFC2X3_IfcSlab_type);
    declarations.push_back(IFC2X3_IfcStair_type);
    declarations.push_back(IFC2X3_IfcStairFlight_type);
    declarations.push_back(IFC2X3_IfcStructuralAnalysisModel_type);
    declarations.push_back(IFC2X3_IfcTendon_type);
    declarations.push_back(IFC2X3_IfcTendonAnchor_type);
    declarations.push_back(IFC2X3_IfcVibrationIsolatorType_type);
    declarations.push_back(IFC2X3_IfcWall_type);
    declarations.push_back(IFC2X3_IfcWallStandardCase_type);
    declarations.push_back(IFC2X3_IfcWindow_type);
    declarations.push_back(IFC2X3_IfcActuatorType_type);
    declarations.push_back(IFC2X3_IfcAlarmType_type);
    declarations.push_back(IFC2X3_IfcBeam_type);
    declarations.push_back(IFC2X3_IfcChamferEdgeFeature_type);
    declarations.push_back(IFC2X3_IfcControllerType_type);
    declarations.push_back(IFC2X3_IfcDistributionChamberElement_type);
    declarations.push_back(IFC2X3_IfcDistributionControlElement_type);
    declarations.push_back(IFC2X3_IfcElectricDistributionPoint_type);
    declarations.push_back(IFC2X3_IfcReinforcingBar_type);
    return new schema_definition("IFC2X3", declarations, new IFC2X3_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
const schema_definition& Ifc2x3::get_schema() {

    static const schema_definition* s = IFC2X3_populate_schema();
    return *s;
}

