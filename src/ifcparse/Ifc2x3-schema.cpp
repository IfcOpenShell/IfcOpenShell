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

declaration* IFC2X3_types[980] = {nullptr};

class IFC2X3_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc2x3::Ifc2DCompositeCurve(data);
            case 1: return new ::Ifc2x3::IfcAbsorbedDoseMeasure(data);
            case 2: return new ::Ifc2x3::IfcAccelerationMeasure(data);
            case 3: return new ::Ifc2x3::IfcActionRequest(data);
            case 4: return new ::Ifc2x3::IfcActionSourceTypeEnum(data);
            case 5: return new ::Ifc2x3::IfcActionTypeEnum(data);
            case 6: return new ::Ifc2x3::IfcActor(data);
            case 7: return new ::Ifc2x3::IfcActorRole(data);
            case 9: return new ::Ifc2x3::IfcActuatorType(data);
            case 10: return new ::Ifc2x3::IfcActuatorTypeEnum(data);
            case 11: return new ::Ifc2x3::IfcAddress(data);
            case 12: return new ::Ifc2x3::IfcAddressTypeEnum(data);
            case 13: return new ::Ifc2x3::IfcAheadOrBehind(data);
            case 14: return new ::Ifc2x3::IfcAirTerminalBoxType(data);
            case 15: return new ::Ifc2x3::IfcAirTerminalBoxTypeEnum(data);
            case 16: return new ::Ifc2x3::IfcAirTerminalType(data);
            case 17: return new ::Ifc2x3::IfcAirTerminalTypeEnum(data);
            case 18: return new ::Ifc2x3::IfcAirToAirHeatRecoveryType(data);
            case 19: return new ::Ifc2x3::IfcAirToAirHeatRecoveryTypeEnum(data);
            case 20: return new ::Ifc2x3::IfcAlarmType(data);
            case 21: return new ::Ifc2x3::IfcAlarmTypeEnum(data);
            case 22: return new ::Ifc2x3::IfcAmountOfSubstanceMeasure(data);
            case 23: return new ::Ifc2x3::IfcAnalysisModelTypeEnum(data);
            case 24: return new ::Ifc2x3::IfcAnalysisTheoryTypeEnum(data);
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
            case 48: return new ::Ifc2x3::IfcArithmeticOperatorEnum(data);
            case 49: return new ::Ifc2x3::IfcAssemblyPlaceEnum(data);
            case 50: return new ::Ifc2x3::IfcAsset(data);
            case 51: return new ::Ifc2x3::IfcAsymmetricIShapeProfileDef(data);
            case 52: return new ::Ifc2x3::IfcAxis1Placement(data);
            case 54: return new ::Ifc2x3::IfcAxis2Placement2D(data);
            case 55: return new ::Ifc2x3::IfcAxis2Placement3D(data);
            case 56: return new ::Ifc2x3::IfcBeam(data);
            case 57: return new ::Ifc2x3::IfcBeamType(data);
            case 58: return new ::Ifc2x3::IfcBeamTypeEnum(data);
            case 59: return new ::Ifc2x3::IfcBenchmarkEnum(data);
            case 60: return new ::Ifc2x3::IfcBezierCurve(data);
            case 61: return new ::Ifc2x3::IfcBlobTexture(data);
            case 62: return new ::Ifc2x3::IfcBlock(data);
            case 63: return new ::Ifc2x3::IfcBoilerType(data);
            case 64: return new ::Ifc2x3::IfcBoilerTypeEnum(data);
            case 65: return new ::Ifc2x3::IfcBoolean(data);
            case 66: return new ::Ifc2x3::IfcBooleanClippingResult(data);
            case 68: return new ::Ifc2x3::IfcBooleanOperator(data);
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
            case 81: return new ::Ifc2x3::IfcBSplineCurveForm(data);
            case 82: return new ::Ifc2x3::IfcBuilding(data);
            case 83: return new ::Ifc2x3::IfcBuildingElement(data);
            case 84: return new ::Ifc2x3::IfcBuildingElementComponent(data);
            case 85: return new ::Ifc2x3::IfcBuildingElementPart(data);
            case 86: return new ::Ifc2x3::IfcBuildingElementProxy(data);
            case 87: return new ::Ifc2x3::IfcBuildingElementProxyType(data);
            case 88: return new ::Ifc2x3::IfcBuildingElementProxyTypeEnum(data);
            case 89: return new ::Ifc2x3::IfcBuildingElementType(data);
            case 90: return new ::Ifc2x3::IfcBuildingStorey(data);
            case 91: return new ::Ifc2x3::IfcCableCarrierFittingType(data);
            case 92: return new ::Ifc2x3::IfcCableCarrierFittingTypeEnum(data);
            case 93: return new ::Ifc2x3::IfcCableCarrierSegmentType(data);
            case 94: return new ::Ifc2x3::IfcCableCarrierSegmentTypeEnum(data);
            case 95: return new ::Ifc2x3::IfcCableSegmentType(data);
            case 96: return new ::Ifc2x3::IfcCableSegmentTypeEnum(data);
            case 97: return new ::Ifc2x3::IfcCalendarDate(data);
            case 98: return new ::Ifc2x3::IfcCartesianPoint(data);
            case 99: return new ::Ifc2x3::IfcCartesianTransformationOperator(data);
            case 100: return new ::Ifc2x3::IfcCartesianTransformationOperator2D(data);
            case 101: return new ::Ifc2x3::IfcCartesianTransformationOperator2DnonUniform(data);
            case 102: return new ::Ifc2x3::IfcCartesianTransformationOperator3D(data);
            case 103: return new ::Ifc2x3::IfcCartesianTransformationOperator3DnonUniform(data);
            case 104: return new ::Ifc2x3::IfcCenterLineProfileDef(data);
            case 105: return new ::Ifc2x3::IfcChamferEdgeFeature(data);
            case 106: return new ::Ifc2x3::IfcChangeActionEnum(data);
            case 108: return new ::Ifc2x3::IfcChillerType(data);
            case 109: return new ::Ifc2x3::IfcChillerTypeEnum(data);
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
            case 122: return new ::Ifc2x3::IfcCoilTypeEnum(data);
            case 125: return new ::Ifc2x3::IfcColourRgb(data);
            case 126: return new ::Ifc2x3::IfcColourSpecification(data);
            case 127: return new ::Ifc2x3::IfcColumn(data);
            case 128: return new ::Ifc2x3::IfcColumnType(data);
            case 129: return new ::Ifc2x3::IfcColumnTypeEnum(data);
            case 130: return new ::Ifc2x3::IfcComplexNumber(data);
            case 131: return new ::Ifc2x3::IfcComplexProperty(data);
            case 132: return new ::Ifc2x3::IfcCompositeCurve(data);
            case 133: return new ::Ifc2x3::IfcCompositeCurveSegment(data);
            case 134: return new ::Ifc2x3::IfcCompositeProfileDef(data);
            case 135: return new ::Ifc2x3::IfcCompoundPlaneAngleMeasure(data);
            case 136: return new ::Ifc2x3::IfcCompressorType(data);
            case 137: return new ::Ifc2x3::IfcCompressorTypeEnum(data);
            case 138: return new ::Ifc2x3::IfcCondenserType(data);
            case 139: return new ::Ifc2x3::IfcCondenserTypeEnum(data);
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
            case 151: return new ::Ifc2x3::IfcConnectionTypeEnum(data);
            case 152: return new ::Ifc2x3::IfcConstraint(data);
            case 153: return new ::Ifc2x3::IfcConstraintAggregationRelationship(data);
            case 154: return new ::Ifc2x3::IfcConstraintClassificationRelationship(data);
            case 155: return new ::Ifc2x3::IfcConstraintEnum(data);
            case 156: return new ::Ifc2x3::IfcConstraintRelationship(data);
            case 157: return new ::Ifc2x3::IfcConstructionEquipmentResource(data);
            case 158: return new ::Ifc2x3::IfcConstructionMaterialResource(data);
            case 159: return new ::Ifc2x3::IfcConstructionProductResource(data);
            case 160: return new ::Ifc2x3::IfcConstructionResource(data);
            case 161: return new ::Ifc2x3::IfcContextDependentMeasure(data);
            case 162: return new ::Ifc2x3::IfcContextDependentUnit(data);
            case 163: return new ::Ifc2x3::IfcControl(data);
            case 164: return new ::Ifc2x3::IfcControllerType(data);
            case 165: return new ::Ifc2x3::IfcControllerTypeEnum(data);
            case 166: return new ::Ifc2x3::IfcConversionBasedUnit(data);
            case 167: return new ::Ifc2x3::IfcCooledBeamType(data);
            case 168: return new ::Ifc2x3::IfcCooledBeamTypeEnum(data);
            case 169: return new ::Ifc2x3::IfcCoolingTowerType(data);
            case 170: return new ::Ifc2x3::IfcCoolingTowerTypeEnum(data);
            case 171: return new ::Ifc2x3::IfcCoordinatedUniversalTimeOffset(data);
            case 172: return new ::Ifc2x3::IfcCostItem(data);
            case 173: return new ::Ifc2x3::IfcCostSchedule(data);
            case 174: return new ::Ifc2x3::IfcCostScheduleTypeEnum(data);
            case 175: return new ::Ifc2x3::IfcCostValue(data);
            case 176: return new ::Ifc2x3::IfcCountMeasure(data);
            case 177: return new ::Ifc2x3::IfcCovering(data);
            case 178: return new ::Ifc2x3::IfcCoveringType(data);
            case 179: return new ::Ifc2x3::IfcCoveringTypeEnum(data);
            case 180: return new ::Ifc2x3::IfcCraneRailAShapeProfileDef(data);
            case 181: return new ::Ifc2x3::IfcCraneRailFShapeProfileDef(data);
            case 182: return new ::Ifc2x3::IfcCrewResource(data);
            case 183: return new ::Ifc2x3::IfcCsgPrimitive3D(data);
            case 185: return new ::Ifc2x3::IfcCsgSolid(data);
            case 186: return new ::Ifc2x3::IfcCShapeProfileDef(data);
            case 187: return new ::Ifc2x3::IfcCurrencyEnum(data);
            case 188: return new ::Ifc2x3::IfcCurrencyRelationship(data);
            case 189: return new ::Ifc2x3::IfcCurtainWall(data);
            case 190: return new ::Ifc2x3::IfcCurtainWallType(data);
            case 191: return new ::Ifc2x3::IfcCurtainWallTypeEnum(data);
            case 192: return new ::Ifc2x3::IfcCurvatureMeasure(data);
            case 193: return new ::Ifc2x3::IfcCurve(data);
            case 194: return new ::Ifc2x3::IfcCurveBoundedPlane(data);
            case 197: return new ::Ifc2x3::IfcCurveStyle(data);
            case 198: return new ::Ifc2x3::IfcCurveStyleFont(data);
            case 199: return new ::Ifc2x3::IfcCurveStyleFontAndScaling(data);
            case 200: return new ::Ifc2x3::IfcCurveStyleFontPattern(data);
            case 202: return new ::Ifc2x3::IfcDamperType(data);
            case 203: return new ::Ifc2x3::IfcDamperTypeEnum(data);
            case 204: return new ::Ifc2x3::IfcDataOriginEnum(data);
            case 205: return new ::Ifc2x3::IfcDateAndTime(data);
            case 207: return new ::Ifc2x3::IfcDayInMonthNumber(data);
            case 208: return new ::Ifc2x3::IfcDaylightSavingHour(data);
            case 209: return new ::Ifc2x3::IfcDefinedSymbol(data);
            case 212: return new ::Ifc2x3::IfcDerivedProfileDef(data);
            case 213: return new ::Ifc2x3::IfcDerivedUnit(data);
            case 214: return new ::Ifc2x3::IfcDerivedUnitElement(data);
            case 215: return new ::Ifc2x3::IfcDerivedUnitEnum(data);
            case 216: return new ::Ifc2x3::IfcDescriptiveMeasure(data);
            case 217: return new ::Ifc2x3::IfcDiameterDimension(data);
            case 218: return new ::Ifc2x3::IfcDimensionalExponents(data);
            case 219: return new ::Ifc2x3::IfcDimensionCalloutRelationship(data);
            case 220: return new ::Ifc2x3::IfcDimensionCount(data);
            case 221: return new ::Ifc2x3::IfcDimensionCurve(data);
            case 222: return new ::Ifc2x3::IfcDimensionCurveDirectedCallout(data);
            case 223: return new ::Ifc2x3::IfcDimensionCurveTerminator(data);
            case 224: return new ::Ifc2x3::IfcDimensionExtentUsage(data);
            case 225: return new ::Ifc2x3::IfcDimensionPair(data);
            case 226: return new ::Ifc2x3::IfcDirection(data);
            case 227: return new ::Ifc2x3::IfcDirectionSenseEnum(data);
            case 228: return new ::Ifc2x3::IfcDiscreteAccessory(data);
            case 229: return new ::Ifc2x3::IfcDiscreteAccessoryType(data);
            case 230: return new ::Ifc2x3::IfcDistributionChamberElement(data);
            case 231: return new ::Ifc2x3::IfcDistributionChamberElementType(data);
            case 232: return new ::Ifc2x3::IfcDistributionChamberElementTypeEnum(data);
            case 233: return new ::Ifc2x3::IfcDistributionControlElement(data);
            case 234: return new ::Ifc2x3::IfcDistributionControlElementType(data);
            case 235: return new ::Ifc2x3::IfcDistributionElement(data);
            case 236: return new ::Ifc2x3::IfcDistributionElementType(data);
            case 237: return new ::Ifc2x3::IfcDistributionFlowElement(data);
            case 238: return new ::Ifc2x3::IfcDistributionFlowElementType(data);
            case 239: return new ::Ifc2x3::IfcDistributionPort(data);
            case 240: return new ::Ifc2x3::IfcDocumentConfidentialityEnum(data);
            case 241: return new ::Ifc2x3::IfcDocumentElectronicFormat(data);
            case 242: return new ::Ifc2x3::IfcDocumentInformation(data);
            case 243: return new ::Ifc2x3::IfcDocumentInformationRelationship(data);
            case 244: return new ::Ifc2x3::IfcDocumentReference(data);
            case 246: return new ::Ifc2x3::IfcDocumentStatusEnum(data);
            case 247: return new ::Ifc2x3::IfcDoor(data);
            case 248: return new ::Ifc2x3::IfcDoorLiningProperties(data);
            case 249: return new ::Ifc2x3::IfcDoorPanelOperationEnum(data);
            case 250: return new ::Ifc2x3::IfcDoorPanelPositionEnum(data);
            case 251: return new ::Ifc2x3::IfcDoorPanelProperties(data);
            case 252: return new ::Ifc2x3::IfcDoorStyle(data);
            case 253: return new ::Ifc2x3::IfcDoorStyleConstructionEnum(data);
            case 254: return new ::Ifc2x3::IfcDoorStyleOperationEnum(data);
            case 255: return new ::Ifc2x3::IfcDoseEquivalentMeasure(data);
            case 256: return new ::Ifc2x3::IfcDraughtingCallout(data);
            case 258: return new ::Ifc2x3::IfcDraughtingCalloutRelationship(data);
            case 259: return new ::Ifc2x3::IfcDraughtingPreDefinedColour(data);
            case 260: return new ::Ifc2x3::IfcDraughtingPreDefinedCurveFont(data);
            case 261: return new ::Ifc2x3::IfcDraughtingPreDefinedTextFont(data);
            case 262: return new ::Ifc2x3::IfcDuctFittingType(data);
            case 263: return new ::Ifc2x3::IfcDuctFittingTypeEnum(data);
            case 264: return new ::Ifc2x3::IfcDuctSegmentType(data);
            case 265: return new ::Ifc2x3::IfcDuctSegmentTypeEnum(data);
            case 266: return new ::Ifc2x3::IfcDuctSilencerType(data);
            case 267: return new ::Ifc2x3::IfcDuctSilencerTypeEnum(data);
            case 268: return new ::Ifc2x3::IfcDynamicViscosityMeasure(data);
            case 269: return new ::Ifc2x3::IfcEdge(data);
            case 270: return new ::Ifc2x3::IfcEdgeCurve(data);
            case 271: return new ::Ifc2x3::IfcEdgeFeature(data);
            case 272: return new ::Ifc2x3::IfcEdgeLoop(data);
            case 273: return new ::Ifc2x3::IfcElectricalBaseProperties(data);
            case 274: return new ::Ifc2x3::IfcElectricalCircuit(data);
            case 275: return new ::Ifc2x3::IfcElectricalElement(data);
            case 276: return new ::Ifc2x3::IfcElectricApplianceType(data);
            case 277: return new ::Ifc2x3::IfcElectricApplianceTypeEnum(data);
            case 278: return new ::Ifc2x3::IfcElectricCapacitanceMeasure(data);
            case 279: return new ::Ifc2x3::IfcElectricChargeMeasure(data);
            case 280: return new ::Ifc2x3::IfcElectricConductanceMeasure(data);
            case 281: return new ::Ifc2x3::IfcElectricCurrentEnum(data);
            case 282: return new ::Ifc2x3::IfcElectricCurrentMeasure(data);
            case 283: return new ::Ifc2x3::IfcElectricDistributionPoint(data);
            case 284: return new ::Ifc2x3::IfcElectricDistributionPointFunctionEnum(data);
            case 285: return new ::Ifc2x3::IfcElectricFlowStorageDeviceType(data);
            case 286: return new ::Ifc2x3::IfcElectricFlowStorageDeviceTypeEnum(data);
            case 287: return new ::Ifc2x3::IfcElectricGeneratorType(data);
            case 288: return new ::Ifc2x3::IfcElectricGeneratorTypeEnum(data);
            case 289: return new ::Ifc2x3::IfcElectricHeaterType(data);
            case 290: return new ::Ifc2x3::IfcElectricHeaterTypeEnum(data);
            case 291: return new ::Ifc2x3::IfcElectricMotorType(data);
            case 292: return new ::Ifc2x3::IfcElectricMotorTypeEnum(data);
            case 293: return new ::Ifc2x3::IfcElectricResistanceMeasure(data);
            case 294: return new ::Ifc2x3::IfcElectricTimeControlType(data);
            case 295: return new ::Ifc2x3::IfcElectricTimeControlTypeEnum(data);
            case 296: return new ::Ifc2x3::IfcElectricVoltageMeasure(data);
            case 297: return new ::Ifc2x3::IfcElement(data);
            case 298: return new ::Ifc2x3::IfcElementarySurface(data);
            case 299: return new ::Ifc2x3::IfcElementAssembly(data);
            case 300: return new ::Ifc2x3::IfcElementAssemblyTypeEnum(data);
            case 301: return new ::Ifc2x3::IfcElementComponent(data);
            case 302: return new ::Ifc2x3::IfcElementComponentType(data);
            case 303: return new ::Ifc2x3::IfcElementCompositionEnum(data);
            case 304: return new ::Ifc2x3::IfcElementQuantity(data);
            case 305: return new ::Ifc2x3::IfcElementType(data);
            case 306: return new ::Ifc2x3::IfcEllipse(data);
            case 307: return new ::Ifc2x3::IfcEllipseProfileDef(data);
            case 308: return new ::Ifc2x3::IfcEnergyConversionDevice(data);
            case 309: return new ::Ifc2x3::IfcEnergyConversionDeviceType(data);
            case 310: return new ::Ifc2x3::IfcEnergyMeasure(data);
            case 311: return new ::Ifc2x3::IfcEnergyProperties(data);
            case 312: return new ::Ifc2x3::IfcEnergySequenceEnum(data);
            case 313: return new ::Ifc2x3::IfcEnvironmentalImpactCategoryEnum(data);
            case 314: return new ::Ifc2x3::IfcEnvironmentalImpactValue(data);
            case 315: return new ::Ifc2x3::IfcEquipmentElement(data);
            case 316: return new ::Ifc2x3::IfcEquipmentStandard(data);
            case 317: return new ::Ifc2x3::IfcEvaporativeCoolerType(data);
            case 318: return new ::Ifc2x3::IfcEvaporativeCoolerTypeEnum(data);
            case 319: return new ::Ifc2x3::IfcEvaporatorType(data);
            case 320: return new ::Ifc2x3::IfcEvaporatorTypeEnum(data);
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
            case 337: return new ::Ifc2x3::IfcFanTypeEnum(data);
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
            case 350: return new ::Ifc2x3::IfcFilterTypeEnum(data);
            case 351: return new ::Ifc2x3::IfcFireSuppressionTerminalType(data);
            case 352: return new ::Ifc2x3::IfcFireSuppressionTerminalTypeEnum(data);
            case 353: return new ::Ifc2x3::IfcFlowController(data);
            case 354: return new ::Ifc2x3::IfcFlowControllerType(data);
            case 355: return new ::Ifc2x3::IfcFlowDirectionEnum(data);
            case 356: return new ::Ifc2x3::IfcFlowFitting(data);
            case 357: return new ::Ifc2x3::IfcFlowFittingType(data);
            case 358: return new ::Ifc2x3::IfcFlowInstrumentType(data);
            case 359: return new ::Ifc2x3::IfcFlowInstrumentTypeEnum(data);
            case 360: return new ::Ifc2x3::IfcFlowMeterType(data);
            case 361: return new ::Ifc2x3::IfcFlowMeterTypeEnum(data);
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
            case 377: return new ::Ifc2x3::IfcFootingTypeEnum(data);
            case 378: return new ::Ifc2x3::IfcForceMeasure(data);
            case 379: return new ::Ifc2x3::IfcFrequencyMeasure(data);
            case 380: return new ::Ifc2x3::IfcFuelProperties(data);
            case 381: return new ::Ifc2x3::IfcFurnishingElement(data);
            case 382: return new ::Ifc2x3::IfcFurnishingElementType(data);
            case 383: return new ::Ifc2x3::IfcFurnitureStandard(data);
            case 384: return new ::Ifc2x3::IfcFurnitureType(data);
            case 385: return new ::Ifc2x3::IfcGasTerminalType(data);
            case 386: return new ::Ifc2x3::IfcGasTerminalTypeEnum(data);
            case 387: return new ::Ifc2x3::IfcGeneralMaterialProperties(data);
            case 388: return new ::Ifc2x3::IfcGeneralProfileProperties(data);
            case 389: return new ::Ifc2x3::IfcGeometricCurveSet(data);
            case 390: return new ::Ifc2x3::IfcGeometricProjectionEnum(data);
            case 391: return new ::Ifc2x3::IfcGeometricRepresentationContext(data);
            case 392: return new ::Ifc2x3::IfcGeometricRepresentationItem(data);
            case 393: return new ::Ifc2x3::IfcGeometricRepresentationSubContext(data);
            case 394: return new ::Ifc2x3::IfcGeometricSet(data);
            case 396: return new ::Ifc2x3::IfcGloballyUniqueId(data);
            case 397: return new ::Ifc2x3::IfcGlobalOrLocalEnum(data);
            case 398: return new ::Ifc2x3::IfcGrid(data);
            case 399: return new ::Ifc2x3::IfcGridAxis(data);
            case 400: return new ::Ifc2x3::IfcGridPlacement(data);
            case 401: return new ::Ifc2x3::IfcGroup(data);
            case 402: return new ::Ifc2x3::IfcHalfSpaceSolid(data);
            case 404: return new ::Ifc2x3::IfcHeatExchangerType(data);
            case 405: return new ::Ifc2x3::IfcHeatExchangerTypeEnum(data);
            case 406: return new ::Ifc2x3::IfcHeatFluxDensityMeasure(data);
            case 407: return new ::Ifc2x3::IfcHeatingValueMeasure(data);
            case 408: return new ::Ifc2x3::IfcHourInDay(data);
            case 409: return new ::Ifc2x3::IfcHumidifierType(data);
            case 410: return new ::Ifc2x3::IfcHumidifierTypeEnum(data);
            case 411: return new ::Ifc2x3::IfcHygroscopicMaterialProperties(data);
            case 412: return new ::Ifc2x3::IfcIdentifier(data);
            case 413: return new ::Ifc2x3::IfcIlluminanceMeasure(data);
            case 414: return new ::Ifc2x3::IfcImageTexture(data);
            case 415: return new ::Ifc2x3::IfcInductanceMeasure(data);
            case 416: return new ::Ifc2x3::IfcInteger(data);
            case 417: return new ::Ifc2x3::IfcIntegerCountRateMeasure(data);
            case 418: return new ::Ifc2x3::IfcInternalOrExternalEnum(data);
            case 419: return new ::Ifc2x3::IfcInventory(data);
            case 420: return new ::Ifc2x3::IfcInventoryTypeEnum(data);
            case 421: return new ::Ifc2x3::IfcIonConcentrationMeasure(data);
            case 422: return new ::Ifc2x3::IfcIrregularTimeSeries(data);
            case 423: return new ::Ifc2x3::IfcIrregularTimeSeriesValue(data);
            case 424: return new ::Ifc2x3::IfcIShapeProfileDef(data);
            case 425: return new ::Ifc2x3::IfcIsothermalMoistureCapacityMeasure(data);
            case 426: return new ::Ifc2x3::IfcJunctionBoxType(data);
            case 427: return new ::Ifc2x3::IfcJunctionBoxTypeEnum(data);
            case 428: return new ::Ifc2x3::IfcKinematicViscosityMeasure(data);
            case 429: return new ::Ifc2x3::IfcLabel(data);
            case 430: return new ::Ifc2x3::IfcLaborResource(data);
            case 431: return new ::Ifc2x3::IfcLampType(data);
            case 432: return new ::Ifc2x3::IfcLampTypeEnum(data);
            case 434: return new ::Ifc2x3::IfcLayerSetDirectionEnum(data);
            case 435: return new ::Ifc2x3::IfcLengthMeasure(data);
            case 436: return new ::Ifc2x3::IfcLibraryInformation(data);
            case 437: return new ::Ifc2x3::IfcLibraryReference(data);
            case 439: return new ::Ifc2x3::IfcLightDistributionCurveEnum(data);
            case 440: return new ::Ifc2x3::IfcLightDistributionData(data);
            case 442: return new ::Ifc2x3::IfcLightEmissionSourceEnum(data);
            case 443: return new ::Ifc2x3::IfcLightFixtureType(data);
            case 444: return new ::Ifc2x3::IfcLightFixtureTypeEnum(data);
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
            case 458: return new ::Ifc2x3::IfcLoadGroupTypeEnum(data);
            case 459: return new ::Ifc2x3::IfcLocalPlacement(data);
            case 460: return new ::Ifc2x3::IfcLocalTime(data);
            case 461: return new ::Ifc2x3::IfcLogical(data);
            case 462: return new ::Ifc2x3::IfcLogicalOperatorEnum(data);
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
            case 494: return new ::Ifc2x3::IfcMemberTypeEnum(data);
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
            case 509: return new ::Ifc2x3::IfcMotorConnectionTypeEnum(data);
            case 510: return new ::Ifc2x3::IfcMove(data);
            case 511: return new ::Ifc2x3::IfcNamedUnit(data);
            case 512: return new ::Ifc2x3::IfcNormalisedRatioMeasure(data);
            case 513: return new ::Ifc2x3::IfcNullStyle(data);
            case 514: return new ::Ifc2x3::IfcNumericMeasure(data);
            case 515: return new ::Ifc2x3::IfcObject(data);
            case 516: return new ::Ifc2x3::IfcObjectDefinition(data);
            case 517: return new ::Ifc2x3::IfcObjective(data);
            case 518: return new ::Ifc2x3::IfcObjectiveEnum(data);
            case 519: return new ::Ifc2x3::IfcObjectPlacement(data);
            case 521: return new ::Ifc2x3::IfcObjectTypeEnum(data);
            case 522: return new ::Ifc2x3::IfcOccupant(data);
            case 523: return new ::Ifc2x3::IfcOccupantTypeEnum(data);
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
            case 536: return new ::Ifc2x3::IfcOutletTypeEnum(data);
            case 537: return new ::Ifc2x3::IfcOwnerHistory(data);
            case 538: return new ::Ifc2x3::IfcParameterizedProfileDef(data);
            case 539: return new ::Ifc2x3::IfcParameterValue(data);
            case 540: return new ::Ifc2x3::IfcPath(data);
            case 541: return new ::Ifc2x3::IfcPerformanceHistory(data);
            case 542: return new ::Ifc2x3::IfcPermeableCoveringOperationEnum(data);
            case 543: return new ::Ifc2x3::IfcPermeableCoveringProperties(data);
            case 544: return new ::Ifc2x3::IfcPermit(data);
            case 545: return new ::Ifc2x3::IfcPerson(data);
            case 546: return new ::Ifc2x3::IfcPersonAndOrganization(data);
            case 547: return new ::Ifc2x3::IfcPHMeasure(data);
            case 548: return new ::Ifc2x3::IfcPhysicalComplexQuantity(data);
            case 549: return new ::Ifc2x3::IfcPhysicalOrVirtualEnum(data);
            case 550: return new ::Ifc2x3::IfcPhysicalQuantity(data);
            case 551: return new ::Ifc2x3::IfcPhysicalSimpleQuantity(data);
            case 552: return new ::Ifc2x3::IfcPile(data);
            case 553: return new ::Ifc2x3::IfcPileConstructionEnum(data);
            case 554: return new ::Ifc2x3::IfcPileTypeEnum(data);
            case 555: return new ::Ifc2x3::IfcPipeFittingType(data);
            case 556: return new ::Ifc2x3::IfcPipeFittingTypeEnum(data);
            case 557: return new ::Ifc2x3::IfcPipeSegmentType(data);
            case 558: return new ::Ifc2x3::IfcPipeSegmentTypeEnum(data);
            case 559: return new ::Ifc2x3::IfcPixelTexture(data);
            case 560: return new ::Ifc2x3::IfcPlacement(data);
            case 561: return new ::Ifc2x3::IfcPlanarBox(data);
            case 562: return new ::Ifc2x3::IfcPlanarExtent(data);
            case 563: return new ::Ifc2x3::IfcPlanarForceMeasure(data);
            case 564: return new ::Ifc2x3::IfcPlane(data);
            case 565: return new ::Ifc2x3::IfcPlaneAngleMeasure(data);
            case 566: return new ::Ifc2x3::IfcPlate(data);
            case 567: return new ::Ifc2x3::IfcPlateType(data);
            case 568: return new ::Ifc2x3::IfcPlateTypeEnum(data);
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
            case 598: return new ::Ifc2x3::IfcProcedureTypeEnum(data);
            case 599: return new ::Ifc2x3::IfcProcess(data);
            case 600: return new ::Ifc2x3::IfcProduct(data);
            case 601: return new ::Ifc2x3::IfcProductDefinitionShape(data);
            case 602: return new ::Ifc2x3::IfcProductRepresentation(data);
            case 603: return new ::Ifc2x3::IfcProductsOfCombustionProperties(data);
            case 604: return new ::Ifc2x3::IfcProfileDef(data);
            case 605: return new ::Ifc2x3::IfcProfileProperties(data);
            case 606: return new ::Ifc2x3::IfcProfileTypeEnum(data);
            case 607: return new ::Ifc2x3::IfcProject(data);
            case 608: return new ::Ifc2x3::IfcProjectedOrTrueLengthEnum(data);
            case 609: return new ::Ifc2x3::IfcProjectionCurve(data);
            case 610: return new ::Ifc2x3::IfcProjectionElement(data);
            case 611: return new ::Ifc2x3::IfcProjectOrder(data);
            case 612: return new ::Ifc2x3::IfcProjectOrderRecord(data);
            case 613: return new ::Ifc2x3::IfcProjectOrderRecordTypeEnum(data);
            case 614: return new ::Ifc2x3::IfcProjectOrderTypeEnum(data);
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
            case 627: return new ::Ifc2x3::IfcPropertySourceEnum(data);
            case 628: return new ::Ifc2x3::IfcPropertyTableValue(data);
            case 629: return new ::Ifc2x3::IfcProtectiveDeviceType(data);
            case 630: return new ::Ifc2x3::IfcProtectiveDeviceTypeEnum(data);
            case 631: return new ::Ifc2x3::IfcProxy(data);
            case 632: return new ::Ifc2x3::IfcPumpType(data);
            case 633: return new ::Ifc2x3::IfcPumpTypeEnum(data);
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
            case 644: return new ::Ifc2x3::IfcRailingTypeEnum(data);
            case 645: return new ::Ifc2x3::IfcRamp(data);
            case 646: return new ::Ifc2x3::IfcRampFlight(data);
            case 647: return new ::Ifc2x3::IfcRampFlightType(data);
            case 648: return new ::Ifc2x3::IfcRampFlightTypeEnum(data);
            case 649: return new ::Ifc2x3::IfcRampTypeEnum(data);
            case 650: return new ::Ifc2x3::IfcRatioMeasure(data);
            case 651: return new ::Ifc2x3::IfcRationalBezierCurve(data);
            case 652: return new ::Ifc2x3::IfcReal(data);
            case 653: return new ::Ifc2x3::IfcRectangleHollowProfileDef(data);
            case 654: return new ::Ifc2x3::IfcRectangleProfileDef(data);
            case 655: return new ::Ifc2x3::IfcRectangularPyramid(data);
            case 656: return new ::Ifc2x3::IfcRectangularTrimmedSurface(data);
            case 657: return new ::Ifc2x3::IfcReferencesValueDocument(data);
            case 658: return new ::Ifc2x3::IfcReflectanceMethodEnum(data);
            case 659: return new ::Ifc2x3::IfcRegularTimeSeries(data);
            case 660: return new ::Ifc2x3::IfcReinforcementBarProperties(data);
            case 661: return new ::Ifc2x3::IfcReinforcementDefinitionProperties(data);
            case 662: return new ::Ifc2x3::IfcReinforcingBar(data);
            case 663: return new ::Ifc2x3::IfcReinforcingBarRoleEnum(data);
            case 664: return new ::Ifc2x3::IfcReinforcingBarSurfaceEnum(data);
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
            case 723: return new ::Ifc2x3::IfcResourceConsumptionEnum(data);
            case 724: return new ::Ifc2x3::IfcRevolvedAreaSolid(data);
            case 725: return new ::Ifc2x3::IfcRibPlateDirectionEnum(data);
            case 726: return new ::Ifc2x3::IfcRibPlateProfileProperties(data);
            case 727: return new ::Ifc2x3::IfcRightCircularCone(data);
            case 728: return new ::Ifc2x3::IfcRightCircularCylinder(data);
            case 729: return new ::Ifc2x3::IfcRoleEnum(data);
            case 730: return new ::Ifc2x3::IfcRoof(data);
            case 731: return new ::Ifc2x3::IfcRoofTypeEnum(data);
            case 732: return new ::Ifc2x3::IfcRoot(data);
            case 733: return new ::Ifc2x3::IfcRotationalFrequencyMeasure(data);
            case 734: return new ::Ifc2x3::IfcRotationalMassMeasure(data);
            case 735: return new ::Ifc2x3::IfcRotationalStiffnessMeasure(data);
            case 736: return new ::Ifc2x3::IfcRoundedEdgeFeature(data);
            case 737: return new ::Ifc2x3::IfcRoundedRectangleProfileDef(data);
            case 738: return new ::Ifc2x3::IfcSanitaryTerminalType(data);
            case 739: return new ::Ifc2x3::IfcSanitaryTerminalTypeEnum(data);
            case 740: return new ::Ifc2x3::IfcScheduleTimeControl(data);
            case 741: return new ::Ifc2x3::IfcSecondInMinute(data);
            case 742: return new ::Ifc2x3::IfcSectionalAreaIntegralMeasure(data);
            case 743: return new ::Ifc2x3::IfcSectionedSpine(data);
            case 744: return new ::Ifc2x3::IfcSectionModulusMeasure(data);
            case 745: return new ::Ifc2x3::IfcSectionProperties(data);
            case 746: return new ::Ifc2x3::IfcSectionReinforcementProperties(data);
            case 747: return new ::Ifc2x3::IfcSectionTypeEnum(data);
            case 748: return new ::Ifc2x3::IfcSensorType(data);
            case 749: return new ::Ifc2x3::IfcSensorTypeEnum(data);
            case 750: return new ::Ifc2x3::IfcSequenceEnum(data);
            case 751: return new ::Ifc2x3::IfcServiceLife(data);
            case 752: return new ::Ifc2x3::IfcServiceLifeFactor(data);
            case 753: return new ::Ifc2x3::IfcServiceLifeFactorTypeEnum(data);
            case 754: return new ::Ifc2x3::IfcServiceLifeTypeEnum(data);
            case 755: return new ::Ifc2x3::IfcShapeAspect(data);
            case 756: return new ::Ifc2x3::IfcShapeModel(data);
            case 757: return new ::Ifc2x3::IfcShapeRepresentation(data);
            case 758: return new ::Ifc2x3::IfcShearModulusMeasure(data);
            case 760: return new ::Ifc2x3::IfcShellBasedSurfaceModel(data);
            case 761: return new ::Ifc2x3::IfcSimpleProperty(data);
            case 763: return new ::Ifc2x3::IfcSIPrefix(data);
            case 764: return new ::Ifc2x3::IfcSite(data);
            case 765: return new ::Ifc2x3::IfcSIUnit(data);
            case 766: return new ::Ifc2x3::IfcSIUnitName(data);
            case 768: return new ::Ifc2x3::IfcSlab(data);
            case 769: return new ::Ifc2x3::IfcSlabType(data);
            case 770: return new ::Ifc2x3::IfcSlabTypeEnum(data);
            case 771: return new ::Ifc2x3::IfcSlippageConnectionCondition(data);
            case 772: return new ::Ifc2x3::IfcSolidAngleMeasure(data);
            case 773: return new ::Ifc2x3::IfcSolidModel(data);
            case 774: return new ::Ifc2x3::IfcSoundPowerMeasure(data);
            case 775: return new ::Ifc2x3::IfcSoundPressureMeasure(data);
            case 776: return new ::Ifc2x3::IfcSoundProperties(data);
            case 777: return new ::Ifc2x3::IfcSoundScaleEnum(data);
            case 778: return new ::Ifc2x3::IfcSoundValue(data);
            case 779: return new ::Ifc2x3::IfcSpace(data);
            case 780: return new ::Ifc2x3::IfcSpaceHeaterType(data);
            case 781: return new ::Ifc2x3::IfcSpaceHeaterTypeEnum(data);
            case 782: return new ::Ifc2x3::IfcSpaceProgram(data);
            case 783: return new ::Ifc2x3::IfcSpaceThermalLoadProperties(data);
            case 784: return new ::Ifc2x3::IfcSpaceType(data);
            case 785: return new ::Ifc2x3::IfcSpaceTypeEnum(data);
            case 786: return new ::Ifc2x3::IfcSpatialStructureElement(data);
            case 787: return new ::Ifc2x3::IfcSpatialStructureElementType(data);
            case 788: return new ::Ifc2x3::IfcSpecificHeatCapacityMeasure(data);
            case 789: return new ::Ifc2x3::IfcSpecularExponent(data);
            case 791: return new ::Ifc2x3::IfcSpecularRoughness(data);
            case 792: return new ::Ifc2x3::IfcSphere(data);
            case 793: return new ::Ifc2x3::IfcStackTerminalType(data);
            case 794: return new ::Ifc2x3::IfcStackTerminalTypeEnum(data);
            case 795: return new ::Ifc2x3::IfcStair(data);
            case 796: return new ::Ifc2x3::IfcStairFlight(data);
            case 797: return new ::Ifc2x3::IfcStairFlightType(data);
            case 798: return new ::Ifc2x3::IfcStairFlightTypeEnum(data);
            case 799: return new ::Ifc2x3::IfcStairTypeEnum(data);
            case 800: return new ::Ifc2x3::IfcStateEnum(data);
            case 801: return new ::Ifc2x3::IfcStructuralAction(data);
            case 802: return new ::Ifc2x3::IfcStructuralActivity(data);
            case 804: return new ::Ifc2x3::IfcStructuralAnalysisModel(data);
            case 805: return new ::Ifc2x3::IfcStructuralConnection(data);
            case 806: return new ::Ifc2x3::IfcStructuralConnectionCondition(data);
            case 807: return new ::Ifc2x3::IfcStructuralCurveConnection(data);
            case 808: return new ::Ifc2x3::IfcStructuralCurveMember(data);
            case 809: return new ::Ifc2x3::IfcStructuralCurveMemberVarying(data);
            case 810: return new ::Ifc2x3::IfcStructuralCurveTypeEnum(data);
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
            case 837: return new ::Ifc2x3::IfcStructuralSurfaceTypeEnum(data);
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
            case 849: return new ::Ifc2x3::IfcSurfaceSide(data);
            case 850: return new ::Ifc2x3::IfcSurfaceStyle(data);
            case 852: return new ::Ifc2x3::IfcSurfaceStyleLighting(data);
            case 853: return new ::Ifc2x3::IfcSurfaceStyleRefraction(data);
            case 854: return new ::Ifc2x3::IfcSurfaceStyleRendering(data);
            case 855: return new ::Ifc2x3::IfcSurfaceStyleShading(data);
            case 856: return new ::Ifc2x3::IfcSurfaceStyleWithTextures(data);
            case 857: return new ::Ifc2x3::IfcSurfaceTexture(data);
            case 858: return new ::Ifc2x3::IfcSurfaceTextureEnum(data);
            case 859: return new ::Ifc2x3::IfcSweptAreaSolid(data);
            case 860: return new ::Ifc2x3::IfcSweptDiskSolid(data);
            case 861: return new ::Ifc2x3::IfcSweptSurface(data);
            case 862: return new ::Ifc2x3::IfcSwitchingDeviceType(data);
            case 863: return new ::Ifc2x3::IfcSwitchingDeviceTypeEnum(data);
            case 864: return new ::Ifc2x3::IfcSymbolStyle(data);
            case 866: return new ::Ifc2x3::IfcSystem(data);
            case 867: return new ::Ifc2x3::IfcSystemFurnitureElementType(data);
            case 868: return new ::Ifc2x3::IfcTable(data);
            case 869: return new ::Ifc2x3::IfcTableRow(data);
            case 870: return new ::Ifc2x3::IfcTankType(data);
            case 871: return new ::Ifc2x3::IfcTankTypeEnum(data);
            case 872: return new ::Ifc2x3::IfcTask(data);
            case 873: return new ::Ifc2x3::IfcTelecomAddress(data);
            case 874: return new ::Ifc2x3::IfcTemperatureGradientMeasure(data);
            case 875: return new ::Ifc2x3::IfcTendon(data);
            case 876: return new ::Ifc2x3::IfcTendonAnchor(data);
            case 877: return new ::Ifc2x3::IfcTendonTypeEnum(data);
            case 878: return new ::Ifc2x3::IfcTerminatorSymbol(data);
            case 879: return new ::Ifc2x3::IfcText(data);
            case 880: return new ::Ifc2x3::IfcTextAlignment(data);
            case 881: return new ::Ifc2x3::IfcTextDecoration(data);
            case 882: return new ::Ifc2x3::IfcTextFontName(data);
            case 884: return new ::Ifc2x3::IfcTextLiteral(data);
            case 885: return new ::Ifc2x3::IfcTextLiteralWithExtent(data);
            case 886: return new ::Ifc2x3::IfcTextPath(data);
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
            case 901: return new ::Ifc2x3::IfcThermalLoadSourceEnum(data);
            case 902: return new ::Ifc2x3::IfcThermalLoadTypeEnum(data);
            case 903: return new ::Ifc2x3::IfcThermalMaterialProperties(data);
            case 904: return new ::Ifc2x3::IfcThermalResistanceMeasure(data);
            case 905: return new ::Ifc2x3::IfcThermalTransmittanceMeasure(data);
            case 906: return new ::Ifc2x3::IfcThermodynamicTemperatureMeasure(data);
            case 907: return new ::Ifc2x3::IfcTimeMeasure(data);
            case 908: return new ::Ifc2x3::IfcTimeSeries(data);
            case 909: return new ::Ifc2x3::IfcTimeSeriesDataTypeEnum(data);
            case 910: return new ::Ifc2x3::IfcTimeSeriesReferenceRelationship(data);
            case 911: return new ::Ifc2x3::IfcTimeSeriesSchedule(data);
            case 912: return new ::Ifc2x3::IfcTimeSeriesScheduleTypeEnum(data);
            case 913: return new ::Ifc2x3::IfcTimeSeriesValue(data);
            case 914: return new ::Ifc2x3::IfcTimeStamp(data);
            case 915: return new ::Ifc2x3::IfcTopologicalRepresentationItem(data);
            case 916: return new ::Ifc2x3::IfcTopologyRepresentation(data);
            case 917: return new ::Ifc2x3::IfcTorqueMeasure(data);
            case 918: return new ::Ifc2x3::IfcTransformerType(data);
            case 919: return new ::Ifc2x3::IfcTransformerTypeEnum(data);
            case 920: return new ::Ifc2x3::IfcTransitionCode(data);
            case 921: return new ::Ifc2x3::IfcTransportElement(data);
            case 922: return new ::Ifc2x3::IfcTransportElementType(data);
            case 923: return new ::Ifc2x3::IfcTransportElementTypeEnum(data);
            case 924: return new ::Ifc2x3::IfcTrapeziumProfileDef(data);
            case 925: return new ::Ifc2x3::IfcTrimmedCurve(data);
            case 926: return new ::Ifc2x3::IfcTrimmingPreference(data);
            case 928: return new ::Ifc2x3::IfcTShapeProfileDef(data);
            case 929: return new ::Ifc2x3::IfcTubeBundleType(data);
            case 930: return new ::Ifc2x3::IfcTubeBundleTypeEnum(data);
            case 931: return new ::Ifc2x3::IfcTwoDirectionRepeatFactor(data);
            case 932: return new ::Ifc2x3::IfcTypeObject(data);
            case 933: return new ::Ifc2x3::IfcTypeProduct(data);
            case 935: return new ::Ifc2x3::IfcUnitaryEquipmentType(data);
            case 936: return new ::Ifc2x3::IfcUnitaryEquipmentTypeEnum(data);
            case 937: return new ::Ifc2x3::IfcUnitAssignment(data);
            case 938: return new ::Ifc2x3::IfcUnitEnum(data);
            case 939: return new ::Ifc2x3::IfcUShapeProfileDef(data);
            case 941: return new ::Ifc2x3::IfcValveType(data);
            case 942: return new ::Ifc2x3::IfcValveTypeEnum(data);
            case 943: return new ::Ifc2x3::IfcVaporPermeabilityMeasure(data);
            case 944: return new ::Ifc2x3::IfcVector(data);
            case 946: return new ::Ifc2x3::IfcVertex(data);
            case 947: return new ::Ifc2x3::IfcVertexBasedTextureMap(data);
            case 948: return new ::Ifc2x3::IfcVertexLoop(data);
            case 949: return new ::Ifc2x3::IfcVertexPoint(data);
            case 950: return new ::Ifc2x3::IfcVibrationIsolatorType(data);
            case 951: return new ::Ifc2x3::IfcVibrationIsolatorTypeEnum(data);
            case 952: return new ::Ifc2x3::IfcVirtualElement(data);
            case 953: return new ::Ifc2x3::IfcVirtualGridIntersection(data);
            case 954: return new ::Ifc2x3::IfcVolumeMeasure(data);
            case 955: return new ::Ifc2x3::IfcVolumetricFlowRateMeasure(data);
            case 956: return new ::Ifc2x3::IfcWall(data);
            case 957: return new ::Ifc2x3::IfcWallStandardCase(data);
            case 958: return new ::Ifc2x3::IfcWallType(data);
            case 959: return new ::Ifc2x3::IfcWallTypeEnum(data);
            case 960: return new ::Ifc2x3::IfcWarpingConstantMeasure(data);
            case 961: return new ::Ifc2x3::IfcWarpingMomentMeasure(data);
            case 962: return new ::Ifc2x3::IfcWasteTerminalType(data);
            case 963: return new ::Ifc2x3::IfcWasteTerminalTypeEnum(data);
            case 964: return new ::Ifc2x3::IfcWaterProperties(data);
            case 965: return new ::Ifc2x3::IfcWindow(data);
            case 966: return new ::Ifc2x3::IfcWindowLiningProperties(data);
            case 967: return new ::Ifc2x3::IfcWindowPanelOperationEnum(data);
            case 968: return new ::Ifc2x3::IfcWindowPanelPositionEnum(data);
            case 969: return new ::Ifc2x3::IfcWindowPanelProperties(data);
            case 970: return new ::Ifc2x3::IfcWindowStyle(data);
            case 971: return new ::Ifc2x3::IfcWindowStyleConstructionEnum(data);
            case 972: return new ::Ifc2x3::IfcWindowStyleOperationEnum(data);
            case 973: return new ::Ifc2x3::IfcWorkControl(data);
            case 974: return new ::Ifc2x3::IfcWorkControlTypeEnum(data);
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
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC2X3_populate_schema() {
    IFC2X3_types[1] = new type_declaration("IfcAbsorbedDoseMeasure", 1, new simple_type(simple_type::real_type));
    IFC2X3_types[2] = new type_declaration("IfcAccelerationMeasure", 2, new simple_type(simple_type::real_type));
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
        IFC2X3_types[4] = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IFC2X3_types[5] = new enumeration_type("IfcActionTypeEnum", 5, items);
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
        IFC2X3_types[10] = new enumeration_type("IfcActuatorTypeEnum", 10, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC2X3_types[12] = new enumeration_type("IfcAddressTypeEnum", 12, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AHEAD");
        items.push_back("BEHIND");
        IFC2X3_types[13] = new enumeration_type("IfcAheadOrBehind", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IFC2X3_types[15] = new enumeration_type("IfcAirTerminalBoxTypeEnum", 15, items);
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
        IFC2X3_types[17] = new enumeration_type("IfcAirTerminalTypeEnum", 17, items);
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
        IFC2X3_types[19] = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 19, items);
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
        IFC2X3_types[21] = new enumeration_type("IfcAlarmTypeEnum", 21, items);
    }
    IFC2X3_types[22] = new type_declaration("IfcAmountOfSubstanceMeasure", 22, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IFC2X3_types[23] = new enumeration_type("IfcAnalysisModelTypeEnum", 23, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IFC2X3_types[24] = new enumeration_type("IfcAnalysisTheoryTypeEnum", 24, items);
    }
    IFC2X3_types[26] = new type_declaration("IfcAngularVelocityMeasure", 26, new simple_type(simple_type::real_type));
    IFC2X3_types[47] = new type_declaration("IfcAreaMeasure", 47, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IFC2X3_types[48] = new enumeration_type("IfcArithmeticOperatorEnum", 48, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IFC2X3_types[49] = new enumeration_type("IfcAssemblyPlaceEnum", 49, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IFC2X3_types[81] = new enumeration_type("IfcBSplineCurveForm", 81, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEAM");
        items.push_back("JOIST");
        items.push_back("LINTEL");
        items.push_back("NOTDEFINED");
        items.push_back("T_BEAM");
        items.push_back("USERDEFINED");
        IFC2X3_types[58] = new enumeration_type("IfcBeamTypeEnum", 58, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EQUALTO");
        items.push_back("GREATERTHAN");
        items.push_back("GREATERTHANOREQUALTO");
        items.push_back("LESSTHAN");
        items.push_back("LESSTHANOREQUALTO");
        items.push_back("NOTEQUALTO");
        IFC2X3_types[59] = new enumeration_type("IfcBenchmarkEnum", 59, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IFC2X3_types[64] = new enumeration_type("IfcBoilerTypeEnum", 64, items);
    }
    IFC2X3_types[65] = new type_declaration("IfcBoolean", 65, new simple_type(simple_type::boolean_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IFC2X3_types[68] = new enumeration_type("IfcBooleanOperator", 68, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[88] = new enumeration_type("IfcBuildingElementProxyTypeEnum", 88, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IFC2X3_types[92] = new enumeration_type("IfcCableCarrierFittingTypeEnum", 92, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[94] = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 94, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[96] = new enumeration_type("IfcCableSegmentTypeEnum", 96, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("MODIFIEDADDED");
        items.push_back("MODIFIEDDELETED");
        items.push_back("NOCHANGE");
        IFC2X3_types[106] = new enumeration_type("IfcChangeActionEnum", 106, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IFC2X3_types[109] = new enumeration_type("IfcChillerTypeEnum", 109, items);
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
        IFC2X3_types[122] = new enumeration_type("IfcCoilTypeEnum", 122, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[129] = new enumeration_type("IfcColumnTypeEnum", 129, items);
    }
    IFC2X3_types[130] = new type_declaration("IfcComplexNumber", 130, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IFC2X3_types[135] = new type_declaration("IfcCompoundPlaneAngleMeasure", 135, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
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
        IFC2X3_types[137] = new enumeration_type("IfcCompressorTypeEnum", 137, items);
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
        IFC2X3_types[139] = new enumeration_type("IfcCondenserTypeEnum", 139, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IFC2X3_types[151] = new enumeration_type("IfcConnectionTypeEnum", 151, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IFC2X3_types[155] = new enumeration_type("IfcConstraintEnum", 155, items);
    }
    IFC2X3_types[161] = new type_declaration("IfcContextDependentMeasure", 161, new simple_type(simple_type::real_type));
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
        IFC2X3_types[165] = new enumeration_type("IfcControllerTypeEnum", 165, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IFC2X3_types[168] = new enumeration_type("IfcCooledBeamTypeEnum", 168, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[170] = new enumeration_type("IfcCoolingTowerTypeEnum", 170, items);
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
        IFC2X3_types[174] = new enumeration_type("IfcCostScheduleTypeEnum", 174, items);
    }
    IFC2X3_types[176] = new type_declaration("IfcCountMeasure", 176, new simple_type(simple_type::number_type));
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
        IFC2X3_types[179] = new enumeration_type("IfcCoveringTypeEnum", 179, items);
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
        IFC2X3_types[187] = new enumeration_type("IfcCurrencyEnum", 187, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[191] = new enumeration_type("IfcCurtainWallTypeEnum", 191, items);
    }
    IFC2X3_types[192] = new type_declaration("IfcCurvatureMeasure", 192, new simple_type(simple_type::real_type));
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
        IFC2X3_types[203] = new enumeration_type("IfcDamperTypeEnum", 203, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IFC2X3_types[204] = new enumeration_type("IfcDataOriginEnum", 204, items);
    }
    IFC2X3_types[207] = new type_declaration("IfcDayInMonthNumber", 207, new simple_type(simple_type::integer_type));
    IFC2X3_types[208] = new type_declaration("IfcDaylightSavingHour", 208, new simple_type(simple_type::integer_type));
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
        IFC2X3_types[215] = new enumeration_type("IfcDerivedUnitEnum", 215, items);
    }
    IFC2X3_types[216] = new type_declaration("IfcDescriptiveMeasure", 216, new simple_type(simple_type::string_type));
    IFC2X3_types[220] = new type_declaration("IfcDimensionCount", 220, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("ORIGIN");
        items.push_back("TARGET");
        IFC2X3_types[224] = new enumeration_type("IfcDimensionExtentUsage", 224, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC2X3_types[227] = new enumeration_type("IfcDirectionSenseEnum", 227, items);
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
        IFC2X3_types[232] = new enumeration_type("IfcDistributionChamberElementTypeEnum", 232, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IFC2X3_types[240] = new enumeration_type("IfcDocumentConfidentialityEnum", 240, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IFC2X3_types[246] = new enumeration_type("IfcDocumentStatusEnum", 246, items);
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
        IFC2X3_types[249] = new enumeration_type("IfcDoorPanelOperationEnum", 249, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IFC2X3_types[250] = new enumeration_type("IfcDoorPanelPositionEnum", 250, items);
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
        IFC2X3_types[253] = new enumeration_type("IfcDoorStyleConstructionEnum", 253, items);
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
        IFC2X3_types[254] = new enumeration_type("IfcDoorStyleOperationEnum", 254, items);
    }
    IFC2X3_types[255] = new type_declaration("IfcDoseEquivalentMeasure", 255, new simple_type(simple_type::real_type));
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
        IFC2X3_types[263] = new enumeration_type("IfcDuctFittingTypeEnum", 263, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IFC2X3_types[265] = new enumeration_type("IfcDuctSegmentTypeEnum", 265, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IFC2X3_types[267] = new enumeration_type("IfcDuctSilencerTypeEnum", 267, items);
    }
    IFC2X3_types[268] = new type_declaration("IfcDynamicViscosityMeasure", 268, new simple_type(simple_type::real_type));
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
        IFC2X3_types[277] = new enumeration_type("IfcElectricApplianceTypeEnum", 277, items);
    }
    IFC2X3_types[278] = new type_declaration("IfcElectricCapacitanceMeasure", 278, new simple_type(simple_type::real_type));
    IFC2X3_types[279] = new type_declaration("IfcElectricChargeMeasure", 279, new simple_type(simple_type::real_type));
    IFC2X3_types[280] = new type_declaration("IfcElectricConductanceMeasure", 280, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ALTERNATING");
        items.push_back("DIRECT");
        items.push_back("NOTDEFINED");
        IFC2X3_types[281] = new enumeration_type("IfcElectricCurrentEnum", 281, items);
    }
    IFC2X3_types[282] = new type_declaration("IfcElectricCurrentMeasure", 282, new simple_type(simple_type::real_type));
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
        IFC2X3_types[284] = new enumeration_type("IfcElectricDistributionPointFunctionEnum", 284, items);
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
        IFC2X3_types[286] = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 286, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[288] = new enumeration_type("IfcElectricGeneratorTypeEnum", 288, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELECTRICCABLEHEATER");
        items.push_back("ELECTRICMATHEATER");
        items.push_back("ELECTRICPOINTHEATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[290] = new enumeration_type("IfcElectricHeaterTypeEnum", 290, items);
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
        IFC2X3_types[292] = new enumeration_type("IfcElectricMotorTypeEnum", 292, items);
    }
    IFC2X3_types[293] = new type_declaration("IfcElectricResistanceMeasure", 293, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IFC2X3_types[295] = new enumeration_type("IfcElectricTimeControlTypeEnum", 295, items);
    }
    IFC2X3_types[296] = new type_declaration("IfcElectricVoltageMeasure", 296, new simple_type(simple_type::real_type));
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
        IFC2X3_types[300] = new enumeration_type("IfcElementAssemblyTypeEnum", 300, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IFC2X3_types[303] = new enumeration_type("IfcElementCompositionEnum", 303, items);
    }
    IFC2X3_types[310] = new type_declaration("IfcEnergyMeasure", 310, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AUXILIARY");
        items.push_back("NOTDEFINED");
        items.push_back("PRIMARY");
        items.push_back("SECONDARY");
        items.push_back("TERTIARY");
        items.push_back("USERDEFINED");
        IFC2X3_types[312] = new enumeration_type("IfcEnergySequenceEnum", 312, items);
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
        IFC2X3_types[313] = new enumeration_type("IfcEnvironmentalImpactCategoryEnum", 313, items);
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
        IFC2X3_types[318] = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 318, items);
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
        IFC2X3_types[320] = new enumeration_type("IfcEvaporatorTypeEnum", 320, items);
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
        IFC2X3_types[337] = new enumeration_type("IfcFanTypeEnum", 337, items);
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
        IFC2X3_types[350] = new enumeration_type("IfcFilterTypeEnum", 350, items);
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
        IFC2X3_types[352] = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 352, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IFC2X3_types[355] = new enumeration_type("IfcFlowDirectionEnum", 355, items);
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
        IFC2X3_types[359] = new enumeration_type("IfcFlowInstrumentTypeEnum", 359, items);
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
        IFC2X3_types[361] = new enumeration_type("IfcFlowMeterTypeEnum", 361, items);
    }
    IFC2X3_types[373] = new type_declaration("IfcFontStyle", 373, new simple_type(simple_type::string_type));
    IFC2X3_types[374] = new type_declaration("IfcFontVariant", 374, new simple_type(simple_type::string_type));
    IFC2X3_types[375] = new type_declaration("IfcFontWeight", 375, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IFC2X3_types[377] = new enumeration_type("IfcFootingTypeEnum", 377, items);
    }
    IFC2X3_types[378] = new type_declaration("IfcForceMeasure", 378, new simple_type(simple_type::real_type));
    IFC2X3_types[379] = new type_declaration("IfcFrequencyMeasure", 379, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GASAPPLIANCE");
        items.push_back("GASBOOSTER");
        items.push_back("GASBURNER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[386] = new enumeration_type("IfcGasTerminalTypeEnum", 386, items);
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
        IFC2X3_types[390] = new enumeration_type("IfcGeometricProjectionEnum", 390, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IFC2X3_types[397] = new enumeration_type("IfcGlobalOrLocalEnum", 397, items);
    }
    IFC2X3_types[396] = new type_declaration("IfcGloballyUniqueId", 396, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IFC2X3_types[405] = new enumeration_type("IfcHeatExchangerTypeEnum", 405, items);
    }
    IFC2X3_types[406] = new type_declaration("IfcHeatFluxDensityMeasure", 406, new simple_type(simple_type::real_type));
    IFC2X3_types[407] = new type_declaration("IfcHeatingValueMeasure", 407, new simple_type(simple_type::real_type));
    IFC2X3_types[408] = new type_declaration("IfcHourInDay", 408, new simple_type(simple_type::integer_type));
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
        IFC2X3_types[410] = new enumeration_type("IfcHumidifierTypeEnum", 410, items);
    }
    IFC2X3_types[412] = new type_declaration("IfcIdentifier", 412, new simple_type(simple_type::string_type));
    IFC2X3_types[413] = new type_declaration("IfcIlluminanceMeasure", 413, new simple_type(simple_type::real_type));
    IFC2X3_types[415] = new type_declaration("IfcInductanceMeasure", 415, new simple_type(simple_type::real_type));
    IFC2X3_types[416] = new type_declaration("IfcInteger", 416, new simple_type(simple_type::integer_type));
    IFC2X3_types[417] = new type_declaration("IfcIntegerCountRateMeasure", 417, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("EXTERNAL");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IFC2X3_types[418] = new enumeration_type("IfcInternalOrExternalEnum", 418, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IFC2X3_types[420] = new enumeration_type("IfcInventoryTypeEnum", 420, items);
    }
    IFC2X3_types[421] = new type_declaration("IfcIonConcentrationMeasure", 421, new simple_type(simple_type::real_type));
    IFC2X3_types[425] = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 425, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[427] = new enumeration_type("IfcJunctionBoxTypeEnum", 427, items);
    }
    IFC2X3_types[428] = new type_declaration("IfcKinematicViscosityMeasure", 428, new simple_type(simple_type::real_type));
    IFC2X3_types[429] = new type_declaration("IfcLabel", 429, new simple_type(simple_type::string_type));
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
        IFC2X3_types[432] = new enumeration_type("IfcLampTypeEnum", 432, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IFC2X3_types[434] = new enumeration_type("IfcLayerSetDirectionEnum", 434, items);
    }
    IFC2X3_types[435] = new type_declaration("IfcLengthMeasure", 435, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IFC2X3_types[439] = new enumeration_type("IfcLightDistributionCurveEnum", 439, items);
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
        IFC2X3_types[442] = new enumeration_type("IfcLightEmissionSourceEnum", 442, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("USERDEFINED");
        IFC2X3_types[444] = new enumeration_type("IfcLightFixtureTypeEnum", 444, items);
    }
    IFC2X3_types[454] = new type_declaration("IfcLinearForceMeasure", 454, new simple_type(simple_type::real_type));
    IFC2X3_types[455] = new type_declaration("IfcLinearMomentMeasure", 455, new simple_type(simple_type::real_type));
    IFC2X3_types[456] = new type_declaration("IfcLinearStiffnessMeasure", 456, new simple_type(simple_type::real_type));
    IFC2X3_types[457] = new type_declaration("IfcLinearVelocityMeasure", 457, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_COMBINATION_GROUP");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[458] = new enumeration_type("IfcLoadGroupTypeEnum", 458, items);
    }
    IFC2X3_types[461] = new type_declaration("IfcLogical", 461, new simple_type(simple_type::logical_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALOR");
        IFC2X3_types[462] = new enumeration_type("IfcLogicalOperatorEnum", 462, items);
    }
    IFC2X3_types[465] = new type_declaration("IfcLuminousFluxMeasure", 465, new simple_type(simple_type::real_type));
    IFC2X3_types[466] = new type_declaration("IfcLuminousIntensityDistributionMeasure", 466, new simple_type(simple_type::real_type));
    IFC2X3_types[467] = new type_declaration("IfcLuminousIntensityMeasure", 467, new simple_type(simple_type::real_type));
    IFC2X3_types[468] = new type_declaration("IfcMagneticFluxDensityMeasure", 468, new simple_type(simple_type::real_type));
    IFC2X3_types[469] = new type_declaration("IfcMagneticFluxMeasure", 469, new simple_type(simple_type::real_type));
    IFC2X3_types[472] = new type_declaration("IfcMassDensityMeasure", 472, new simple_type(simple_type::real_type));
    IFC2X3_types[473] = new type_declaration("IfcMassFlowRateMeasure", 473, new simple_type(simple_type::real_type));
    IFC2X3_types[474] = new type_declaration("IfcMassMeasure", 474, new simple_type(simple_type::real_type));
    IFC2X3_types[475] = new type_declaration("IfcMassPerLengthMeasure", 475, new simple_type(simple_type::real_type));
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
        IFC2X3_types[494] = new enumeration_type("IfcMemberTypeEnum", 494, items);
    }
    IFC2X3_types[497] = new type_declaration("IfcMinuteInHour", 497, new simple_type(simple_type::integer_type));
    IFC2X3_types[498] = new type_declaration("IfcModulusOfElasticityMeasure", 498, new simple_type(simple_type::real_type));
    IFC2X3_types[499] = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 499, new simple_type(simple_type::real_type));
    IFC2X3_types[500] = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 500, new simple_type(simple_type::real_type));
    IFC2X3_types[501] = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 501, new simple_type(simple_type::real_type));
    IFC2X3_types[502] = new type_declaration("IfcMoistureDiffusivityMeasure", 502, new simple_type(simple_type::real_type));
    IFC2X3_types[503] = new type_declaration("IfcMolecularWeightMeasure", 503, new simple_type(simple_type::real_type));
    IFC2X3_types[504] = new type_declaration("IfcMomentOfInertiaMeasure", 504, new simple_type(simple_type::real_type));
    IFC2X3_types[505] = new type_declaration("IfcMonetaryMeasure", 505, new simple_type(simple_type::real_type));
    IFC2X3_types[507] = new type_declaration("IfcMonthInYearNumber", 507, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[509] = new enumeration_type("IfcMotorConnectionTypeEnum", 509, items);
    }
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IFC2X3_types[513] = new enumeration_type("IfcNullStyle", 513, items);
    }
    IFC2X3_types[514] = new type_declaration("IfcNumericMeasure", 514, new simple_type(simple_type::number_type));
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
        IFC2X3_types[521] = new enumeration_type("IfcObjectTypeEnum", 521, items);
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
        IFC2X3_types[518] = new enumeration_type("IfcObjectiveEnum", 518, items);
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
        IFC2X3_types[523] = new enumeration_type("IfcOccupantTypeEnum", 523, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AUDIOVISUALOUTLET");
        items.push_back("COMMUNICATIONSOUTLET");
        items.push_back("NOTDEFINED");
        items.push_back("POWEROUTLET");
        items.push_back("USERDEFINED");
        IFC2X3_types[536] = new enumeration_type("IfcOutletTypeEnum", 536, items);
    }
    IFC2X3_types[547] = new type_declaration("IfcPHMeasure", 547, new simple_type(simple_type::real_type));
    IFC2X3_types[539] = new type_declaration("IfcParameterValue", 539, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IFC2X3_types[542] = new enumeration_type("IfcPermeableCoveringOperationEnum", 542, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IFC2X3_types[549] = new enumeration_type("IfcPhysicalOrVirtualEnum", 549, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IFC2X3_types[553] = new enumeration_type("IfcPileConstructionEnum", 553, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COHESION");
        items.push_back("FRICTION");
        items.push_back("NOTDEFINED");
        items.push_back("SUPPORT");
        items.push_back("USERDEFINED");
        IFC2X3_types[554] = new enumeration_type("IfcPileTypeEnum", 554, items);
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
        IFC2X3_types[556] = new enumeration_type("IfcPipeFittingTypeEnum", 556, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("GUTTER");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("SPOOL");
        items.push_back("USERDEFINED");
        IFC2X3_types[558] = new enumeration_type("IfcPipeSegmentTypeEnum", 558, items);
    }
    IFC2X3_types[563] = new type_declaration("IfcPlanarForceMeasure", 563, new simple_type(simple_type::real_type));
    IFC2X3_types[565] = new type_declaration("IfcPlaneAngleMeasure", 565, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IFC2X3_types[568] = new enumeration_type("IfcPlateTypeEnum", 568, items);
    }
    IFC2X3_types[577] = new type_declaration("IfcPositiveLengthMeasure", 577, new named_type(IFC2X3_types[435]));
    IFC2X3_types[578] = new type_declaration("IfcPositivePlaneAngleMeasure", 578, new named_type(IFC2X3_types[565]));
    IFC2X3_types[581] = new type_declaration("IfcPowerMeasure", 581, new simple_type(simple_type::real_type));
    IFC2X3_types[590] = new type_declaration("IfcPresentableText", 590, new simple_type(simple_type::string_type));
    IFC2X3_types[596] = new type_declaration("IfcPressureMeasure", 596, new simple_type(simple_type::real_type));
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
        IFC2X3_types[598] = new enumeration_type("IfcProcedureTypeEnum", 598, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IFC2X3_types[606] = new enumeration_type("IfcProfileTypeEnum", 606, items);
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
        IFC2X3_types[613] = new enumeration_type("IfcProjectOrderRecordTypeEnum", 613, items);
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
        IFC2X3_types[614] = new enumeration_type("IfcProjectOrderTypeEnum", 614, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IFC2X3_types[608] = new enumeration_type("IfcProjectedOrTrueLengthEnum", 608, items);
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
        IFC2X3_types[627] = new enumeration_type("IfcPropertySourceEnum", 627, items);
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
        IFC2X3_types[630] = new enumeration_type("IfcProtectiveDeviceTypeEnum", 630, items);
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
        IFC2X3_types[633] = new enumeration_type("IfcPumpTypeEnum", 633, items);
    }
    IFC2X3_types[640] = new type_declaration("IfcRadioActivityMeasure", 640, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[644] = new enumeration_type("IfcRailingTypeEnum", 644, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IFC2X3_types[648] = new enumeration_type("IfcRampFlightTypeEnum", 648, items);
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
        IFC2X3_types[649] = new enumeration_type("IfcRampTypeEnum", 649, items);
    }
    IFC2X3_types[650] = new type_declaration("IfcRatioMeasure", 650, new simple_type(simple_type::real_type));
    IFC2X3_types[652] = new type_declaration("IfcReal", 652, new simple_type(simple_type::real_type));
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
        IFC2X3_types[658] = new enumeration_type("IfcReflectanceMethodEnum", 658, items);
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
        IFC2X3_types[663] = new enumeration_type("IfcReinforcingBarRoleEnum", 663, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IFC2X3_types[664] = new enumeration_type("IfcReinforcingBarSurfaceEnum", 664, items);
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
        IFC2X3_types[723] = new enumeration_type("IfcResourceConsumptionEnum", 723, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("DIRECTION_X");
        items.push_back("DIRECTION_Y");
        IFC2X3_types[725] = new enumeration_type("IfcRibPlateDirectionEnum", 725, items);
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
        IFC2X3_types[729] = new enumeration_type("IfcRoleEnum", 729, items);
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
        IFC2X3_types[731] = new enumeration_type("IfcRoofTypeEnum", 731, items);
    }
    IFC2X3_types[733] = new type_declaration("IfcRotationalFrequencyMeasure", 733, new simple_type(simple_type::real_type));
    IFC2X3_types[734] = new type_declaration("IfcRotationalMassMeasure", 734, new simple_type(simple_type::real_type));
    IFC2X3_types[735] = new type_declaration("IfcRotationalStiffnessMeasure", 735, new simple_type(simple_type::real_type));
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
        IFC2X3_types[763] = new enumeration_type("IfcSIPrefix", 763, items);
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
        IFC2X3_types[766] = new enumeration_type("IfcSIUnitName", 766, items);
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
        IFC2X3_types[739] = new enumeration_type("IfcSanitaryTerminalTypeEnum", 739, items);
    }
    IFC2X3_types[741] = new type_declaration("IfcSecondInMinute", 741, new simple_type(simple_type::real_type));
    IFC2X3_types[744] = new type_declaration("IfcSectionModulusMeasure", 744, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IFC2X3_types[747] = new enumeration_type("IfcSectionTypeEnum", 747, items);
    }
    IFC2X3_types[742] = new type_declaration("IfcSectionalAreaIntegralMeasure", 742, new simple_type(simple_type::real_type));
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
        IFC2X3_types[749] = new enumeration_type("IfcSensorTypeEnum", 749, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        IFC2X3_types[750] = new enumeration_type("IfcSequenceEnum", 750, items);
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
        IFC2X3_types[753] = new enumeration_type("IfcServiceLifeFactorTypeEnum", 753, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUALSERVICELIFE");
        items.push_back("EXPECTEDSERVICELIFE");
        items.push_back("OPTIMISTICREFERENCESERVICELIFE");
        items.push_back("PESSIMISTICREFERENCESERVICELIFE");
        items.push_back("REFERENCESERVICELIFE");
        IFC2X3_types[754] = new enumeration_type("IfcServiceLifeTypeEnum", 754, items);
    }
    IFC2X3_types[758] = new type_declaration("IfcShearModulusMeasure", 758, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IFC2X3_types[770] = new enumeration_type("IfcSlabTypeEnum", 770, items);
    }
    IFC2X3_types[772] = new type_declaration("IfcSolidAngleMeasure", 772, new simple_type(simple_type::real_type));
    IFC2X3_types[774] = new type_declaration("IfcSoundPowerMeasure", 774, new simple_type(simple_type::real_type));
    IFC2X3_types[775] = new type_declaration("IfcSoundPressureMeasure", 775, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DBA");
        items.push_back("DBB");
        items.push_back("DBC");
        items.push_back("NC");
        items.push_back("NOTDEFINED");
        items.push_back("NR");
        items.push_back("USERDEFINED");
        IFC2X3_types[777] = new enumeration_type("IfcSoundScaleEnum", 777, items);
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
        IFC2X3_types[781] = new enumeration_type("IfcSpaceHeaterTypeEnum", 781, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[785] = new enumeration_type("IfcSpaceTypeEnum", 785, items);
    }
    IFC2X3_types[788] = new type_declaration("IfcSpecificHeatCapacityMeasure", 788, new simple_type(simple_type::real_type));
    IFC2X3_types[789] = new type_declaration("IfcSpecularExponent", 789, new simple_type(simple_type::real_type));
    IFC2X3_types[791] = new type_declaration("IfcSpecularRoughness", 791, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IFC2X3_types[794] = new enumeration_type("IfcStackTerminalTypeEnum", 794, items);
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
        IFC2X3_types[798] = new enumeration_type("IfcStairFlightTypeEnum", 798, items);
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
        IFC2X3_types[799] = new enumeration_type("IfcStairTypeEnum", 799, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IFC2X3_types[800] = new enumeration_type("IfcStateEnum", 800, items);
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
        IFC2X3_types[810] = new enumeration_type("IfcStructuralCurveTypeEnum", 810, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IFC2X3_types[837] = new enumeration_type("IfcStructuralSurfaceTypeEnum", 837, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC2X3_types[849] = new enumeration_type("IfcSurfaceSide", 849, items);
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
        IFC2X3_types[858] = new enumeration_type("IfcSurfaceTextureEnum", 858, items);
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
        IFC2X3_types[863] = new enumeration_type("IfcSwitchingDeviceTypeEnum", 863, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXPANSION");
        items.push_back("NOTDEFINED");
        items.push_back("PREFORMED");
        items.push_back("PRESSUREVESSEL");
        items.push_back("SECTIONAL");
        items.push_back("USERDEFINED");
        IFC2X3_types[871] = new enumeration_type("IfcTankTypeEnum", 871, items);
    }
    IFC2X3_types[874] = new type_declaration("IfcTemperatureGradientMeasure", 874, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IFC2X3_types[877] = new enumeration_type("IfcTendonTypeEnum", 877, items);
    }
    IFC2X3_types[879] = new type_declaration("IfcText", 879, new simple_type(simple_type::string_type));
    IFC2X3_types[880] = new type_declaration("IfcTextAlignment", 880, new simple_type(simple_type::string_type));
    IFC2X3_types[881] = new type_declaration("IfcTextDecoration", 881, new simple_type(simple_type::string_type));
    IFC2X3_types[882] = new type_declaration("IfcTextFontName", 882, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IFC2X3_types[886] = new enumeration_type("IfcTextPath", 886, items);
    }
    IFC2X3_types[893] = new type_declaration("IfcTextTransformation", 893, new simple_type(simple_type::string_type));
    IFC2X3_types[898] = new type_declaration("IfcThermalAdmittanceMeasure", 898, new simple_type(simple_type::real_type));
    IFC2X3_types[899] = new type_declaration("IfcThermalConductivityMeasure", 899, new simple_type(simple_type::real_type));
    IFC2X3_types[900] = new type_declaration("IfcThermalExpansionCoefficientMeasure", 900, new simple_type(simple_type::real_type));
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
        IFC2X3_types[901] = new enumeration_type("IfcThermalLoadSourceEnum", 901, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LATENT");
        items.push_back("NOTDEFINED");
        items.push_back("RADIANT");
        items.push_back("SENSIBLE");
        IFC2X3_types[902] = new enumeration_type("IfcThermalLoadTypeEnum", 902, items);
    }
    IFC2X3_types[904] = new type_declaration("IfcThermalResistanceMeasure", 904, new simple_type(simple_type::real_type));
    IFC2X3_types[905] = new type_declaration("IfcThermalTransmittanceMeasure", 905, new simple_type(simple_type::real_type));
    IFC2X3_types[906] = new type_declaration("IfcThermodynamicTemperatureMeasure", 906, new simple_type(simple_type::real_type));
    IFC2X3_types[907] = new type_declaration("IfcTimeMeasure", 907, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONTINUOUS");
        items.push_back("DISCRETE");
        items.push_back("DISCRETEBINARY");
        items.push_back("NOTDEFINED");
        items.push_back("PIECEWISEBINARY");
        items.push_back("PIECEWISECONSTANT");
        items.push_back("PIECEWISECONTINUOUS");
        IFC2X3_types[909] = new enumeration_type("IfcTimeSeriesDataTypeEnum", 909, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ANNUAL");
        items.push_back("DAILY");
        items.push_back("MONTHLY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WEEKLY");
        IFC2X3_types[912] = new enumeration_type("IfcTimeSeriesScheduleTypeEnum", 912, items);
    }
    IFC2X3_types[914] = new type_declaration("IfcTimeStamp", 914, new simple_type(simple_type::integer_type));
    IFC2X3_types[917] = new type_declaration("IfcTorqueMeasure", 917, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IFC2X3_types[919] = new enumeration_type("IfcTransformerTypeEnum", 919, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IFC2X3_types[920] = new enumeration_type("IfcTransitionCode", 920, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELEVATOR");
        items.push_back("ESCALATOR");
        items.push_back("MOVINGWALKWAY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[923] = new enumeration_type("IfcTransportElementTypeEnum", 923, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IFC2X3_types[926] = new enumeration_type("IfcTrimmingPreference", 926, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC2X3_types[930] = new enumeration_type("IfcTubeBundleTypeEnum", 930, items);
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
        IFC2X3_types[938] = new enumeration_type("IfcUnitEnum", 938, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AIRCONDITIONINGUNIT");
        items.push_back("AIRHANDLER");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFTOPUNIT");
        items.push_back("SPLITSYSTEM");
        items.push_back("USERDEFINED");
        IFC2X3_types[936] = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 936, items);
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
        IFC2X3_types[942] = new enumeration_type("IfcValveTypeEnum", 942, items);
    }
    IFC2X3_types[943] = new type_declaration("IfcVaporPermeabilityMeasure", 943, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IFC2X3_types[951] = new enumeration_type("IfcVibrationIsolatorTypeEnum", 951, items);
    }
    IFC2X3_types[954] = new type_declaration("IfcVolumeMeasure", 954, new simple_type(simple_type::real_type));
    IFC2X3_types[955] = new type_declaration("IfcVolumetricFlowRateMeasure", 955, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("ELEMENTEDWALL");
        items.push_back("NOTDEFINED");
        items.push_back("PLUMBINGWALL");
        items.push_back("POLYGONAL");
        items.push_back("SHEAR");
        items.push_back("STANDARD");
        items.push_back("USERDEFINED");
        IFC2X3_types[959] = new enumeration_type("IfcWallTypeEnum", 959, items);
    }
    IFC2X3_types[960] = new type_declaration("IfcWarpingConstantMeasure", 960, new simple_type(simple_type::real_type));
    IFC2X3_types[961] = new type_declaration("IfcWarpingMomentMeasure", 961, new simple_type(simple_type::real_type));
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
        IFC2X3_types[963] = new enumeration_type("IfcWasteTerminalTypeEnum", 963, items);
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
        IFC2X3_types[967] = new enumeration_type("IfcWindowPanelOperationEnum", 967, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IFC2X3_types[968] = new enumeration_type("IfcWindowPanelPositionEnum", 968, items);
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
        IFC2X3_types[971] = new enumeration_type("IfcWindowStyleConstructionEnum", 971, items);
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
        IFC2X3_types[972] = new enumeration_type("IfcWindowStyleOperationEnum", 972, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC2X3_types[974] = new enumeration_type("IfcWorkControlTypeEnum", 974, items);
    }
    IFC2X3_types[977] = new type_declaration("IfcYearNumber", 977, new simple_type(simple_type::integer_type));
    IFC2X3_types[7] = new entity("IfcActorRole", false, 7, (entity*) 0);
    IFC2X3_types[11] = new entity("IfcAddress", true, 11, (entity*) 0);
    IFC2X3_types[36] = new entity("IfcApplication", false, 36, (entity*) 0);
    IFC2X3_types[37] = new entity("IfcAppliedValue", true, 37, (entity*) 0);
    IFC2X3_types[38] = new entity("IfcAppliedValueRelationship", false, 38, (entity*) 0);
    IFC2X3_types[40] = new entity("IfcApproval", false, 40, (entity*) 0);
    IFC2X3_types[41] = new entity("IfcApprovalActorRelationship", false, 41, (entity*) 0);
    IFC2X3_types[42] = new entity("IfcApprovalPropertyRelationship", false, 42, (entity*) 0);
    IFC2X3_types[43] = new entity("IfcApprovalRelationship", false, 43, (entity*) 0);
    IFC2X3_types[70] = new entity("IfcBoundaryCondition", true, 70, (entity*) 0);
    IFC2X3_types[71] = new entity("IfcBoundaryEdgeCondition", false, 71, (entity*) IFC2X3_types[70]);
    IFC2X3_types[72] = new entity("IfcBoundaryFaceCondition", false, 72, (entity*) IFC2X3_types[70]);
    IFC2X3_types[73] = new entity("IfcBoundaryNodeCondition", false, 73, (entity*) IFC2X3_types[70]);
    IFC2X3_types[74] = new entity("IfcBoundaryNodeConditionWarping", false, 74, (entity*) IFC2X3_types[73]);
    IFC2X3_types[97] = new entity("IfcCalendarDate", false, 97, (entity*) 0);
    IFC2X3_types[113] = new entity("IfcClassification", false, 113, (entity*) 0);
    IFC2X3_types[114] = new entity("IfcClassificationItem", false, 114, (entity*) 0);
    IFC2X3_types[115] = new entity("IfcClassificationItemRelationship", false, 115, (entity*) 0);
    IFC2X3_types[116] = new entity("IfcClassificationNotation", false, 116, (entity*) 0);
    IFC2X3_types[117] = new entity("IfcClassificationNotationFacet", false, 117, (entity*) 0);
    IFC2X3_types[126] = new entity("IfcColourSpecification", true, 126, (entity*) 0);
    IFC2X3_types[146] = new entity("IfcConnectionGeometry", true, 146, (entity*) 0);
    IFC2X3_types[148] = new entity("IfcConnectionPointGeometry", false, 148, (entity*) IFC2X3_types[146]);
    IFC2X3_types[149] = new entity("IfcConnectionPortGeometry", false, 149, (entity*) IFC2X3_types[146]);
    IFC2X3_types[150] = new entity("IfcConnectionSurfaceGeometry", false, 150, (entity*) IFC2X3_types[146]);
    IFC2X3_types[152] = new entity("IfcConstraint", true, 152, (entity*) 0);
    IFC2X3_types[153] = new entity("IfcConstraintAggregationRelationship", false, 153, (entity*) 0);
    IFC2X3_types[154] = new entity("IfcConstraintClassificationRelationship", false, 154, (entity*) 0);
    IFC2X3_types[156] = new entity("IfcConstraintRelationship", false, 156, (entity*) 0);
    IFC2X3_types[171] = new entity("IfcCoordinatedUniversalTimeOffset", false, 171, (entity*) 0);
    IFC2X3_types[175] = new entity("IfcCostValue", false, 175, (entity*) IFC2X3_types[37]);
    IFC2X3_types[188] = new entity("IfcCurrencyRelationship", false, 188, (entity*) 0);
    IFC2X3_types[198] = new entity("IfcCurveStyleFont", false, 198, (entity*) 0);
    IFC2X3_types[199] = new entity("IfcCurveStyleFontAndScaling", false, 199, (entity*) 0);
    IFC2X3_types[200] = new entity("IfcCurveStyleFontPattern", false, 200, (entity*) 0);
    IFC2X3_types[205] = new entity("IfcDateAndTime", false, 205, (entity*) 0);
    IFC2X3_types[213] = new entity("IfcDerivedUnit", false, 213, (entity*) 0);
    IFC2X3_types[214] = new entity("IfcDerivedUnitElement", false, 214, (entity*) 0);
    IFC2X3_types[218] = new entity("IfcDimensionalExponents", false, 218, (entity*) 0);
    IFC2X3_types[241] = new entity("IfcDocumentElectronicFormat", false, 241, (entity*) 0);
    IFC2X3_types[242] = new entity("IfcDocumentInformation", false, 242, (entity*) 0);
    IFC2X3_types[243] = new entity("IfcDocumentInformationRelationship", false, 243, (entity*) 0);
    IFC2X3_types[258] = new entity("IfcDraughtingCalloutRelationship", false, 258, (entity*) 0);
    IFC2X3_types[314] = new entity("IfcEnvironmentalImpactValue", false, 314, (entity*) IFC2X3_types[37]);
    IFC2X3_types[326] = new entity("IfcExternalReference", true, 326, (entity*) 0);
    IFC2X3_types[322] = new entity("IfcExternallyDefinedHatchStyle", false, 322, (entity*) IFC2X3_types[326]);
    IFC2X3_types[323] = new entity("IfcExternallyDefinedSurfaceStyle", false, 323, (entity*) IFC2X3_types[326]);
    IFC2X3_types[324] = new entity("IfcExternallyDefinedSymbol", false, 324, (entity*) IFC2X3_types[326]);
    IFC2X3_types[325] = new entity("IfcExternallyDefinedTextFont", false, 325, (entity*) IFC2X3_types[326]);
    IFC2X3_types[399] = new entity("IfcGridAxis", false, 399, (entity*) 0);
    IFC2X3_types[423] = new entity("IfcIrregularTimeSeriesValue", false, 423, (entity*) 0);
    IFC2X3_types[436] = new entity("IfcLibraryInformation", false, 436, (entity*) 0);
    IFC2X3_types[437] = new entity("IfcLibraryReference", false, 437, (entity*) IFC2X3_types[326]);
    IFC2X3_types[440] = new entity("IfcLightDistributionData", false, 440, (entity*) 0);
    IFC2X3_types[445] = new entity("IfcLightIntensityDistribution", false, 445, (entity*) 0);
    IFC2X3_types[460] = new entity("IfcLocalTime", false, 460, (entity*) 0);
    IFC2X3_types[476] = new entity("IfcMaterial", false, 476, (entity*) 0);
    IFC2X3_types[477] = new entity("IfcMaterialClassificationRelationship", false, 477, (entity*) 0);
    IFC2X3_types[479] = new entity("IfcMaterialLayer", false, 479, (entity*) 0);
    IFC2X3_types[480] = new entity("IfcMaterialLayerSet", false, 480, (entity*) 0);
    IFC2X3_types[481] = new entity("IfcMaterialLayerSetUsage", false, 481, (entity*) 0);
    IFC2X3_types[482] = new entity("IfcMaterialList", false, 482, (entity*) 0);
    IFC2X3_types[483] = new entity("IfcMaterialProperties", true, 483, (entity*) 0);
    IFC2X3_types[486] = new entity("IfcMeasureWithUnit", false, 486, (entity*) 0);
    IFC2X3_types[490] = new entity("IfcMechanicalMaterialProperties", false, 490, (entity*) IFC2X3_types[483]);
    IFC2X3_types[491] = new entity("IfcMechanicalSteelMaterialProperties", false, 491, (entity*) IFC2X3_types[490]);
    IFC2X3_types[495] = new entity("IfcMetric", false, 495, (entity*) IFC2X3_types[152]);
    IFC2X3_types[506] = new entity("IfcMonetaryUnit", false, 506, (entity*) 0);
    IFC2X3_types[511] = new entity("IfcNamedUnit", true, 511, (entity*) 0);
    IFC2X3_types[519] = new entity("IfcObjectPlacement", true, 519, (entity*) 0);
    IFC2X3_types[517] = new entity("IfcObjective", false, 517, (entity*) IFC2X3_types[152]);
    IFC2X3_types[529] = new entity("IfcOpticalMaterialProperties", false, 529, (entity*) IFC2X3_types[483]);
    IFC2X3_types[531] = new entity("IfcOrganization", false, 531, (entity*) 0);
    IFC2X3_types[532] = new entity("IfcOrganizationRelationship", false, 532, (entity*) 0);
    IFC2X3_types[537] = new entity("IfcOwnerHistory", false, 537, (entity*) 0);
    IFC2X3_types[545] = new entity("IfcPerson", false, 545, (entity*) 0);
    IFC2X3_types[546] = new entity("IfcPersonAndOrganization", false, 546, (entity*) 0);
    IFC2X3_types[550] = new entity("IfcPhysicalQuantity", true, 550, (entity*) 0);
    IFC2X3_types[551] = new entity("IfcPhysicalSimpleQuantity", true, 551, (entity*) IFC2X3_types[550]);
    IFC2X3_types[580] = new entity("IfcPostalAddress", false, 580, (entity*) IFC2X3_types[11]);
    IFC2X3_types[585] = new entity("IfcPreDefinedItem", true, 585, (entity*) 0);
    IFC2X3_types[587] = new entity("IfcPreDefinedSymbol", true, 587, (entity*) IFC2X3_types[585]);
    IFC2X3_types[588] = new entity("IfcPreDefinedTerminatorSymbol", false, 588, (entity*) IFC2X3_types[587]);
    IFC2X3_types[589] = new entity("IfcPreDefinedTextFont", true, 589, (entity*) IFC2X3_types[585]);
    IFC2X3_types[591] = new entity("IfcPresentationLayerAssignment", false, 591, (entity*) 0);
    IFC2X3_types[592] = new entity("IfcPresentationLayerWithStyle", false, 592, (entity*) IFC2X3_types[591]);
    IFC2X3_types[593] = new entity("IfcPresentationStyle", true, 593, (entity*) 0);
    IFC2X3_types[594] = new entity("IfcPresentationStyleAssignment", false, 594, (entity*) 0);
    IFC2X3_types[602] = new entity("IfcProductRepresentation", false, 602, (entity*) 0);
    IFC2X3_types[603] = new entity("IfcProductsOfCombustionProperties", false, 603, (entity*) IFC2X3_types[483]);
    IFC2X3_types[604] = new entity("IfcProfileDef", true, 604, (entity*) 0);
    IFC2X3_types[605] = new entity("IfcProfileProperties", true, 605, (entity*) 0);
    IFC2X3_types[615] = new entity("IfcProperty", true, 615, (entity*) 0);
    IFC2X3_types[617] = new entity("IfcPropertyConstraintRelationship", false, 617, (entity*) 0);
    IFC2X3_types[619] = new entity("IfcPropertyDependencyRelationship", false, 619, (entity*) 0);
    IFC2X3_types[621] = new entity("IfcPropertyEnumeration", false, 621, (entity*) 0);
    IFC2X3_types[634] = new entity("IfcQuantityArea", false, 634, (entity*) IFC2X3_types[551]);
    IFC2X3_types[635] = new entity("IfcQuantityCount", false, 635, (entity*) IFC2X3_types[551]);
    IFC2X3_types[636] = new entity("IfcQuantityLength", false, 636, (entity*) IFC2X3_types[551]);
    IFC2X3_types[637] = new entity("IfcQuantityTime", false, 637, (entity*) IFC2X3_types[551]);
    IFC2X3_types[638] = new entity("IfcQuantityVolume", false, 638, (entity*) IFC2X3_types[551]);
    IFC2X3_types[639] = new entity("IfcQuantityWeight", false, 639, (entity*) IFC2X3_types[551]);
    IFC2X3_types[657] = new entity("IfcReferencesValueDocument", false, 657, (entity*) 0);
    IFC2X3_types[660] = new entity("IfcReinforcementBarProperties", false, 660, (entity*) 0);
    IFC2X3_types[687] = new entity("IfcRelaxation", false, 687, (entity*) 0);
    IFC2X3_types[718] = new entity("IfcRepresentation", false, 718, (entity*) 0);
    IFC2X3_types[719] = new entity("IfcRepresentationContext", false, 719, (entity*) 0);
    IFC2X3_types[720] = new entity("IfcRepresentationItem", true, 720, (entity*) 0);
    IFC2X3_types[721] = new entity("IfcRepresentationMap", false, 721, (entity*) 0);
    IFC2X3_types[726] = new entity("IfcRibPlateProfileProperties", false, 726, (entity*) IFC2X3_types[605]);
    IFC2X3_types[732] = new entity("IfcRoot", true, 732, (entity*) 0);
    IFC2X3_types[765] = new entity("IfcSIUnit", false, 765, (entity*) IFC2X3_types[511]);
    IFC2X3_types[745] = new entity("IfcSectionProperties", false, 745, (entity*) 0);
    IFC2X3_types[746] = new entity("IfcSectionReinforcementProperties", false, 746, (entity*) 0);
    IFC2X3_types[755] = new entity("IfcShapeAspect", false, 755, (entity*) 0);
    IFC2X3_types[756] = new entity("IfcShapeModel", true, 756, (entity*) IFC2X3_types[718]);
    IFC2X3_types[757] = new entity("IfcShapeRepresentation", false, 757, (entity*) IFC2X3_types[756]);
    IFC2X3_types[761] = new entity("IfcSimpleProperty", true, 761, (entity*) IFC2X3_types[615]);
    IFC2X3_types[806] = new entity("IfcStructuralConnectionCondition", true, 806, (entity*) 0);
    IFC2X3_types[814] = new entity("IfcStructuralLoad", true, 814, (entity*) 0);
    IFC2X3_types[822] = new entity("IfcStructuralLoadStatic", true, 822, (entity*) IFC2X3_types[814]);
    IFC2X3_types[823] = new entity("IfcStructuralLoadTemperature", false, 823, (entity*) IFC2X3_types[822]);
    IFC2X3_types[841] = new entity("IfcStyleModel", true, 841, (entity*) IFC2X3_types[718]);
    IFC2X3_types[839] = new entity("IfcStyledItem", false, 839, (entity*) IFC2X3_types[720]);
    IFC2X3_types[840] = new entity("IfcStyledRepresentation", false, 840, (entity*) IFC2X3_types[841]);
    IFC2X3_types[850] = new entity("IfcSurfaceStyle", false, 850, (entity*) IFC2X3_types[593]);
    IFC2X3_types[852] = new entity("IfcSurfaceStyleLighting", false, 852, (entity*) 0);
    IFC2X3_types[853] = new entity("IfcSurfaceStyleRefraction", false, 853, (entity*) 0);
    IFC2X3_types[855] = new entity("IfcSurfaceStyleShading", false, 855, (entity*) 0);
    IFC2X3_types[856] = new entity("IfcSurfaceStyleWithTextures", false, 856, (entity*) 0);
    IFC2X3_types[857] = new entity("IfcSurfaceTexture", true, 857, (entity*) 0);
    IFC2X3_types[864] = new entity("IfcSymbolStyle", false, 864, (entity*) IFC2X3_types[593]);
    IFC2X3_types[868] = new entity("IfcTable", false, 868, (entity*) 0);
    IFC2X3_types[869] = new entity("IfcTableRow", false, 869, (entity*) 0);
    IFC2X3_types[873] = new entity("IfcTelecomAddress", false, 873, (entity*) IFC2X3_types[11]);
    IFC2X3_types[887] = new entity("IfcTextStyle", false, 887, (entity*) IFC2X3_types[593]);
    IFC2X3_types[888] = new entity("IfcTextStyleFontModel", false, 888, (entity*) IFC2X3_types[589]);
    IFC2X3_types[889] = new entity("IfcTextStyleForDefinedFont", false, 889, (entity*) 0);
    IFC2X3_types[891] = new entity("IfcTextStyleTextModel", false, 891, (entity*) 0);
    IFC2X3_types[892] = new entity("IfcTextStyleWithBoxCharacteristics", false, 892, (entity*) 0);
    IFC2X3_types[894] = new entity("IfcTextureCoordinate", true, 894, (entity*) 0);
    IFC2X3_types[895] = new entity("IfcTextureCoordinateGenerator", false, 895, (entity*) IFC2X3_types[894]);
    IFC2X3_types[896] = new entity("IfcTextureMap", false, 896, (entity*) IFC2X3_types[894]);
    IFC2X3_types[897] = new entity("IfcTextureVertex", false, 897, (entity*) 0);
    IFC2X3_types[903] = new entity("IfcThermalMaterialProperties", false, 903, (entity*) IFC2X3_types[483]);
    IFC2X3_types[908] = new entity("IfcTimeSeries", true, 908, (entity*) 0);
    IFC2X3_types[910] = new entity("IfcTimeSeriesReferenceRelationship", false, 910, (entity*) 0);
    IFC2X3_types[913] = new entity("IfcTimeSeriesValue", false, 913, (entity*) 0);
    IFC2X3_types[915] = new entity("IfcTopologicalRepresentationItem", true, 915, (entity*) IFC2X3_types[720]);
    IFC2X3_types[916] = new entity("IfcTopologyRepresentation", false, 916, (entity*) IFC2X3_types[756]);
    IFC2X3_types[937] = new entity("IfcUnitAssignment", false, 937, (entity*) 0);
    IFC2X3_types[946] = new entity("IfcVertex", false, 946, (entity*) IFC2X3_types[915]);
    IFC2X3_types[947] = new entity("IfcVertexBasedTextureMap", false, 947, (entity*) 0);
    IFC2X3_types[949] = new entity("IfcVertexPoint", false, 949, (entity*) IFC2X3_types[946]);
    IFC2X3_types[953] = new entity("IfcVirtualGridIntersection", false, 953, (entity*) 0);
    IFC2X3_types[964] = new entity("IfcWaterProperties", false, 964, (entity*) IFC2X3_types[483]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[531]);
        items.push_back(IFC2X3_types[545]);
        items.push_back(IFC2X3_types[546]);
        IFC2X3_types[8] = new select_type("IfcActorSelect", 8, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[486]);
        items.push_back(IFC2X3_types[505]);
        items.push_back(IFC2X3_types[650]);
        IFC2X3_types[39] = new select_type("IfcAppliedValueSelect", 39, items);
    }
    IFC2X3_types[78] = new type_declaration("IfcBoxAlignment", 78, new named_type(IFC2X3_types[429]));
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IFC2X3_types[889]);
        IFC2X3_types[107] = new select_type("IfcCharacterStyleSelect", 107, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[429]);
        items.push_back(IFC2X3_types[486]);
        IFC2X3_types[142] = new select_type("IfcConditionCriterionSelect", 142, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[97]);
        items.push_back(IFC2X3_types[205]);
        items.push_back(IFC2X3_types[460]);
        IFC2X3_types[206] = new select_type("IfcDateTimeSelect", 206, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[324]);
        items.push_back(IFC2X3_types[587]);
        IFC2X3_types[210] = new select_type("IfcDefinedSymbolSelect", 210, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(68);
        items.push_back(IFC2X3_types[1]);
        items.push_back(IFC2X3_types[2]);
        items.push_back(IFC2X3_types[26]);
        items.push_back(IFC2X3_types[135]);
        items.push_back(IFC2X3_types[192]);
        items.push_back(IFC2X3_types[255]);
        items.push_back(IFC2X3_types[268]);
        items.push_back(IFC2X3_types[278]);
        items.push_back(IFC2X3_types[279]);
        items.push_back(IFC2X3_types[280]);
        items.push_back(IFC2X3_types[293]);
        items.push_back(IFC2X3_types[296]);
        items.push_back(IFC2X3_types[310]);
        items.push_back(IFC2X3_types[378]);
        items.push_back(IFC2X3_types[379]);
        items.push_back(IFC2X3_types[406]);
        items.push_back(IFC2X3_types[407]);
        items.push_back(IFC2X3_types[413]);
        items.push_back(IFC2X3_types[415]);
        items.push_back(IFC2X3_types[417]);
        items.push_back(IFC2X3_types[421]);
        items.push_back(IFC2X3_types[425]);
        items.push_back(IFC2X3_types[428]);
        items.push_back(IFC2X3_types[454]);
        items.push_back(IFC2X3_types[455]);
        items.push_back(IFC2X3_types[456]);
        items.push_back(IFC2X3_types[457]);
        items.push_back(IFC2X3_types[465]);
        items.push_back(IFC2X3_types[466]);
        items.push_back(IFC2X3_types[468]);
        items.push_back(IFC2X3_types[469]);
        items.push_back(IFC2X3_types[472]);
        items.push_back(IFC2X3_types[473]);
        items.push_back(IFC2X3_types[475]);
        items.push_back(IFC2X3_types[498]);
        items.push_back(IFC2X3_types[499]);
        items.push_back(IFC2X3_types[500]);
        items.push_back(IFC2X3_types[501]);
        items.push_back(IFC2X3_types[502]);
        items.push_back(IFC2X3_types[503]);
        items.push_back(IFC2X3_types[504]);
        items.push_back(IFC2X3_types[505]);
        items.push_back(IFC2X3_types[547]);
        items.push_back(IFC2X3_types[563]);
        items.push_back(IFC2X3_types[581]);
        items.push_back(IFC2X3_types[596]);
        items.push_back(IFC2X3_types[640]);
        items.push_back(IFC2X3_types[733]);
        items.push_back(IFC2X3_types[734]);
        items.push_back(IFC2X3_types[735]);
        items.push_back(IFC2X3_types[744]);
        items.push_back(IFC2X3_types[742]);
        items.push_back(IFC2X3_types[758]);
        items.push_back(IFC2X3_types[774]);
        items.push_back(IFC2X3_types[775]);
        items.push_back(IFC2X3_types[788]);
        items.push_back(IFC2X3_types[874]);
        items.push_back(IFC2X3_types[898]);
        items.push_back(IFC2X3_types[899]);
        items.push_back(IFC2X3_types[900]);
        items.push_back(IFC2X3_types[904]);
        items.push_back(IFC2X3_types[905]);
        items.push_back(IFC2X3_types[914]);
        items.push_back(IFC2X3_types[917]);
        items.push_back(IFC2X3_types[943]);
        items.push_back(IFC2X3_types[955]);
        items.push_back(IFC2X3_types[960]);
        items.push_back(IFC2X3_types[961]);
        IFC2X3_types[211] = new select_type("IfcDerivedMeasureValue", 211, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[718]);
        items.push_back(IFC2X3_types[720]);
        IFC2X3_types[433] = new select_type("IfcLayeredItem", 433, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[436]);
        items.push_back(IFC2X3_types[437]);
        IFC2X3_types[438] = new select_type("IfcLibrarySelect", 438, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[326]);
        items.push_back(IFC2X3_types[445]);
        IFC2X3_types[441] = new select_type("IfcLightDistributionDataSourceSelect", 441, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC2X3_types[476]);
        items.push_back(IFC2X3_types[479]);
        items.push_back(IFC2X3_types[480]);
        items.push_back(IFC2X3_types[481]);
        items.push_back(IFC2X3_types[482]);
        IFC2X3_types[484] = new select_type("IfcMaterialSelect", 484, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC2X3_types[175]);
        items.push_back(IFC2X3_types[206]);
        items.push_back(IFC2X3_types[486]);
        items.push_back(IFC2X3_types[868]);
        items.push_back(IFC2X3_types[879]);
        items.push_back(IFC2X3_types[908]);
        IFC2X3_types[496] = new select_type("IfcMetricValueSelect", 496, items);
    }
    IFC2X3_types[512] = new type_declaration("IfcNormalisedRatioMeasure", 512, new named_type(IFC2X3_types[650]));
    {
        std::vector<const declaration*> items; items.reserve(13);
        items.push_back(IFC2X3_types[11]);
        items.push_back(IFC2X3_types[37]);
        items.push_back(IFC2X3_types[97]);
        items.push_back(IFC2X3_types[205]);
        items.push_back(IFC2X3_types[326]);
        items.push_back(IFC2X3_types[460]);
        items.push_back(IFC2X3_types[476]);
        items.push_back(IFC2X3_types[479]);
        items.push_back(IFC2X3_types[482]);
        items.push_back(IFC2X3_types[531]);
        items.push_back(IFC2X3_types[545]);
        items.push_back(IFC2X3_types[546]);
        items.push_back(IFC2X3_types[908]);
        IFC2X3_types[520] = new select_type("IfcObjectReferenceSelect", 520, items);
    }
    IFC2X3_types[579] = new type_declaration("IfcPositiveRatioMeasure", 579, new named_type(IFC2X3_types[650]));
    {
        std::vector<const declaration*> items; items.reserve(7);
        items.push_back(IFC2X3_types[65]);
        items.push_back(IFC2X3_types[412]);
        items.push_back(IFC2X3_types[416]);
        items.push_back(IFC2X3_types[429]);
        items.push_back(IFC2X3_types[461]);
        items.push_back(IFC2X3_types[652]);
        items.push_back(IFC2X3_types[879]);
        IFC2X3_types[762] = new select_type("IfcSimpleValue", 762, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC2X3_types[216]);
        items.push_back(IFC2X3_types[435]);
        items.push_back(IFC2X3_types[512]);
        items.push_back(IFC2X3_types[577]);
        items.push_back(IFC2X3_types[579]);
        items.push_back(IFC2X3_types[650]);
        IFC2X3_types[767] = new select_type("IfcSizeSelect", 767, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[789]);
        items.push_back(IFC2X3_types[791]);
        IFC2X3_types[790] = new select_type("IfcSpecularHighlightSelect", 790, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC2X3_types[323]);
        items.push_back(IFC2X3_types[852]);
        items.push_back(IFC2X3_types[853]);
        items.push_back(IFC2X3_types[855]);
        items.push_back(IFC2X3_types[856]);
        IFC2X3_types[851] = new select_type("IfcSurfaceStyleElementSelect", 851, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[325]);
        items.push_back(IFC2X3_types[589]);
        IFC2X3_types[883] = new select_type("IfcTextFontSelect", 883, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[891]);
        items.push_back(IFC2X3_types[892]);
        IFC2X3_types[890] = new select_type("IfcTextStyleSelect", 890, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[213]);
        items.push_back(IFC2X3_types[506]);
        items.push_back(IFC2X3_types[511]);
        IFC2X3_types[934] = new select_type("IfcUnit", 934, items);
    }
    IFC2X3_types[31] = new entity("IfcAnnotationOccurrence", true, 31, (entity*) IFC2X3_types[839]);
    IFC2X3_types[33] = new entity("IfcAnnotationSurfaceOccurrence", false, 33, (entity*) IFC2X3_types[31]);
    IFC2X3_types[34] = new entity("IfcAnnotationSymbolOccurrence", false, 34, (entity*) IFC2X3_types[31]);
    IFC2X3_types[35] = new entity("IfcAnnotationTextOccurrence", false, 35, (entity*) IFC2X3_types[31]);
    IFC2X3_types[44] = new entity("IfcArbitraryClosedProfileDef", false, 44, (entity*) IFC2X3_types[604]);
    IFC2X3_types[45] = new entity("IfcArbitraryOpenProfileDef", false, 45, (entity*) IFC2X3_types[604]);
    IFC2X3_types[46] = new entity("IfcArbitraryProfileDefWithVoids", false, 46, (entity*) IFC2X3_types[44]);
    IFC2X3_types[61] = new entity("IfcBlobTexture", false, 61, (entity*) IFC2X3_types[857]);
    IFC2X3_types[104] = new entity("IfcCenterLineProfileDef", false, 104, (entity*) IFC2X3_types[45]);
    IFC2X3_types[119] = new entity("IfcClassificationReference", false, 119, (entity*) IFC2X3_types[326]);
    IFC2X3_types[125] = new entity("IfcColourRgb", false, 125, (entity*) IFC2X3_types[126]);
    IFC2X3_types[131] = new entity("IfcComplexProperty", false, 131, (entity*) IFC2X3_types[615]);
    IFC2X3_types[134] = new entity("IfcCompositeProfileDef", false, 134, (entity*) IFC2X3_types[604]);
    IFC2X3_types[144] = new entity("IfcConnectedFaceSet", false, 144, (entity*) IFC2X3_types[915]);
    IFC2X3_types[145] = new entity("IfcConnectionCurveGeometry", false, 145, (entity*) IFC2X3_types[146]);
    IFC2X3_types[147] = new entity("IfcConnectionPointEccentricity", false, 147, (entity*) IFC2X3_types[148]);
    IFC2X3_types[162] = new entity("IfcContextDependentUnit", false, 162, (entity*) IFC2X3_types[511]);
    IFC2X3_types[166] = new entity("IfcConversionBasedUnit", false, 166, (entity*) IFC2X3_types[511]);
    IFC2X3_types[197] = new entity("IfcCurveStyle", false, 197, (entity*) IFC2X3_types[593]);
    IFC2X3_types[212] = new entity("IfcDerivedProfileDef", false, 212, (entity*) IFC2X3_types[604]);
    IFC2X3_types[219] = new entity("IfcDimensionCalloutRelationship", false, 219, (entity*) IFC2X3_types[258]);
    IFC2X3_types[225] = new entity("IfcDimensionPair", false, 225, (entity*) IFC2X3_types[258]);
    IFC2X3_types[244] = new entity("IfcDocumentReference", false, 244, (entity*) IFC2X3_types[326]);
    IFC2X3_types[261] = new entity("IfcDraughtingPreDefinedTextFont", false, 261, (entity*) IFC2X3_types[589]);
    IFC2X3_types[269] = new entity("IfcEdge", false, 269, (entity*) IFC2X3_types[915]);
    IFC2X3_types[270] = new entity("IfcEdgeCurve", false, 270, (entity*) IFC2X3_types[269]);
    IFC2X3_types[321] = new entity("IfcExtendedMaterialProperties", false, 321, (entity*) IFC2X3_types[483]);
    IFC2X3_types[328] = new entity("IfcFace", false, 328, (entity*) IFC2X3_types[915]);
    IFC2X3_types[330] = new entity("IfcFaceBound", false, 330, (entity*) IFC2X3_types[915]);
    IFC2X3_types[331] = new entity("IfcFaceOuterBound", false, 331, (entity*) IFC2X3_types[330]);
    IFC2X3_types[332] = new entity("IfcFaceSurface", false, 332, (entity*) IFC2X3_types[328]);
    IFC2X3_types[335] = new entity("IfcFailureConnectionCondition", false, 335, (entity*) IFC2X3_types[806]);
    IFC2X3_types[343] = new entity("IfcFillAreaStyle", false, 343, (entity*) IFC2X3_types[593]);
    IFC2X3_types[380] = new entity("IfcFuelProperties", false, 380, (entity*) IFC2X3_types[483]);
    IFC2X3_types[387] = new entity("IfcGeneralMaterialProperties", false, 387, (entity*) IFC2X3_types[483]);
    IFC2X3_types[388] = new entity("IfcGeneralProfileProperties", false, 388, (entity*) IFC2X3_types[605]);
    IFC2X3_types[391] = new entity("IfcGeometricRepresentationContext", false, 391, (entity*) IFC2X3_types[719]);
    IFC2X3_types[392] = new entity("IfcGeometricRepresentationItem", true, 392, (entity*) IFC2X3_types[720]);
    IFC2X3_types[393] = new entity("IfcGeometricRepresentationSubContext", false, 393, (entity*) IFC2X3_types[391]);
    IFC2X3_types[394] = new entity("IfcGeometricSet", false, 394, (entity*) IFC2X3_types[392]);
    IFC2X3_types[400] = new entity("IfcGridPlacement", false, 400, (entity*) IFC2X3_types[519]);
    IFC2X3_types[402] = new entity("IfcHalfSpaceSolid", false, 402, (entity*) IFC2X3_types[392]);
    IFC2X3_types[411] = new entity("IfcHygroscopicMaterialProperties", false, 411, (entity*) IFC2X3_types[483]);
    IFC2X3_types[414] = new entity("IfcImageTexture", false, 414, (entity*) IFC2X3_types[857]);
    IFC2X3_types[422] = new entity("IfcIrregularTimeSeries", false, 422, (entity*) IFC2X3_types[908]);
    IFC2X3_types[446] = new entity("IfcLightSource", true, 446, (entity*) IFC2X3_types[392]);
    IFC2X3_types[447] = new entity("IfcLightSourceAmbient", false, 447, (entity*) IFC2X3_types[446]);
    IFC2X3_types[448] = new entity("IfcLightSourceDirectional", false, 448, (entity*) IFC2X3_types[446]);
    IFC2X3_types[449] = new entity("IfcLightSourceGoniometric", false, 449, (entity*) IFC2X3_types[446]);
    IFC2X3_types[450] = new entity("IfcLightSourcePositional", false, 450, (entity*) IFC2X3_types[446]);
    IFC2X3_types[451] = new entity("IfcLightSourceSpot", false, 451, (entity*) IFC2X3_types[450]);
    IFC2X3_types[459] = new entity("IfcLocalPlacement", false, 459, (entity*) IFC2X3_types[519]);
    IFC2X3_types[463] = new entity("IfcLoop", false, 463, (entity*) IFC2X3_types[915]);
    IFC2X3_types[471] = new entity("IfcMappedItem", false, 471, (entity*) IFC2X3_types[720]);
    IFC2X3_types[478] = new entity("IfcMaterialDefinitionRepresentation", false, 478, (entity*) IFC2X3_types[602]);
    IFC2X3_types[487] = new entity("IfcMechanicalConcreteMaterialProperties", false, 487, (entity*) IFC2X3_types[490]);
    IFC2X3_types[516] = new entity("IfcObjectDefinition", true, 516, (entity*) IFC2X3_types[732]);
    IFC2X3_types[526] = new entity("IfcOneDirectionRepeatFactor", false, 526, (entity*) IFC2X3_types[392]);
    IFC2X3_types[528] = new entity("IfcOpenShell", false, 528, (entity*) IFC2X3_types[144]);
    IFC2X3_types[534] = new entity("IfcOrientedEdge", false, 534, (entity*) IFC2X3_types[269]);
    IFC2X3_types[538] = new entity("IfcParameterizedProfileDef", true, 538, (entity*) IFC2X3_types[604]);
    IFC2X3_types[540] = new entity("IfcPath", false, 540, (entity*) IFC2X3_types[915]);
    IFC2X3_types[548] = new entity("IfcPhysicalComplexQuantity", false, 548, (entity*) IFC2X3_types[550]);
    IFC2X3_types[559] = new entity("IfcPixelTexture", false, 559, (entity*) IFC2X3_types[857]);
    IFC2X3_types[560] = new entity("IfcPlacement", true, 560, (entity*) IFC2X3_types[392]);
    IFC2X3_types[562] = new entity("IfcPlanarExtent", false, 562, (entity*) IFC2X3_types[392]);
    IFC2X3_types[569] = new entity("IfcPoint", true, 569, (entity*) IFC2X3_types[392]);
    IFC2X3_types[570] = new entity("IfcPointOnCurve", false, 570, (entity*) IFC2X3_types[569]);
    IFC2X3_types[571] = new entity("IfcPointOnSurface", false, 571, (entity*) IFC2X3_types[569]);
    IFC2X3_types[575] = new entity("IfcPolyLoop", false, 575, (entity*) IFC2X3_types[463]);
    IFC2X3_types[573] = new entity("IfcPolygonalBoundedHalfSpace", false, 573, (entity*) IFC2X3_types[402]);
    IFC2X3_types[582] = new entity("IfcPreDefinedColour", true, 582, (entity*) IFC2X3_types[585]);
    IFC2X3_types[583] = new entity("IfcPreDefinedCurveFont", true, 583, (entity*) IFC2X3_types[585]);
    IFC2X3_types[584] = new entity("IfcPreDefinedDimensionSymbol", false, 584, (entity*) IFC2X3_types[587]);
    IFC2X3_types[586] = new entity("IfcPreDefinedPointMarkerSymbol", false, 586, (entity*) IFC2X3_types[587]);
    IFC2X3_types[601] = new entity("IfcProductDefinitionShape", false, 601, (entity*) IFC2X3_types[602]);
    IFC2X3_types[616] = new entity("IfcPropertyBoundedValue", false, 616, (entity*) IFC2X3_types[761]);
    IFC2X3_types[618] = new entity("IfcPropertyDefinition", true, 618, (entity*) IFC2X3_types[732]);
    IFC2X3_types[620] = new entity("IfcPropertyEnumeratedValue", false, 620, (entity*) IFC2X3_types[761]);
    IFC2X3_types[622] = new entity("IfcPropertyListValue", false, 622, (entity*) IFC2X3_types[761]);
    IFC2X3_types[623] = new entity("IfcPropertyReferenceValue", false, 623, (entity*) IFC2X3_types[761]);
    IFC2X3_types[625] = new entity("IfcPropertySetDefinition", true, 625, (entity*) IFC2X3_types[618]);
    IFC2X3_types[626] = new entity("IfcPropertySingleValue", false, 626, (entity*) IFC2X3_types[761]);
    IFC2X3_types[628] = new entity("IfcPropertyTableValue", false, 628, (entity*) IFC2X3_types[761]);
    IFC2X3_types[654] = new entity("IfcRectangleProfileDef", false, 654, (entity*) IFC2X3_types[538]);
    IFC2X3_types[659] = new entity("IfcRegularTimeSeries", false, 659, (entity*) IFC2X3_types[908]);
    IFC2X3_types[661] = new entity("IfcReinforcementDefinitionProperties", false, 661, (entity*) IFC2X3_types[625]);
    IFC2X3_types[686] = new entity("IfcRelationship", true, 686, (entity*) IFC2X3_types[732]);
    IFC2X3_types[737] = new entity("IfcRoundedRectangleProfileDef", false, 737, (entity*) IFC2X3_types[654]);
    IFC2X3_types[743] = new entity("IfcSectionedSpine", false, 743, (entity*) IFC2X3_types[392]);
    IFC2X3_types[752] = new entity("IfcServiceLifeFactor", false, 752, (entity*) IFC2X3_types[625]);
    IFC2X3_types[760] = new entity("IfcShellBasedSurfaceModel", false, 760, (entity*) IFC2X3_types[392]);
    IFC2X3_types[771] = new entity("IfcSlippageConnectionCondition", false, 771, (entity*) IFC2X3_types[806]);
    IFC2X3_types[773] = new entity("IfcSolidModel", true, 773, (entity*) IFC2X3_types[392]);
    IFC2X3_types[776] = new entity("IfcSoundProperties", false, 776, (entity*) IFC2X3_types[625]);
    IFC2X3_types[778] = new entity("IfcSoundValue", false, 778, (entity*) IFC2X3_types[625]);
    IFC2X3_types[783] = new entity("IfcSpaceThermalLoadProperties", false, 783, (entity*) IFC2X3_types[625]);
    IFC2X3_types[816] = new entity("IfcStructuralLoadLinearForce", false, 816, (entity*) IFC2X3_types[822]);
    IFC2X3_types[817] = new entity("IfcStructuralLoadPlanarForce", false, 817, (entity*) IFC2X3_types[822]);
    IFC2X3_types[818] = new entity("IfcStructuralLoadSingleDisplacement", false, 818, (entity*) IFC2X3_types[822]);
    IFC2X3_types[819] = new entity("IfcStructuralLoadSingleDisplacementDistortion", false, 819, (entity*) IFC2X3_types[818]);
    IFC2X3_types[820] = new entity("IfcStructuralLoadSingleForce", false, 820, (entity*) IFC2X3_types[822]);
    IFC2X3_types[821] = new entity("IfcStructuralLoadSingleForceWarping", false, 821, (entity*) IFC2X3_types[820]);
    IFC2X3_types[830] = new entity("IfcStructuralProfileProperties", false, 830, (entity*) IFC2X3_types[388]);
    IFC2X3_types[833] = new entity("IfcStructuralSteelProfileProperties", false, 833, (entity*) IFC2X3_types[830]);
    IFC2X3_types[843] = new entity("IfcSubedge", false, 843, (entity*) IFC2X3_types[269]);
    IFC2X3_types[844] = new entity("IfcSurface", true, 844, (entity*) IFC2X3_types[392]);
    IFC2X3_types[854] = new entity("IfcSurfaceStyleRendering", false, 854, (entity*) IFC2X3_types[855]);
    IFC2X3_types[859] = new entity("IfcSweptAreaSolid", true, 859, (entity*) IFC2X3_types[773]);
    IFC2X3_types[860] = new entity("IfcSweptDiskSolid", false, 860, (entity*) IFC2X3_types[773]);
    IFC2X3_types[861] = new entity("IfcSweptSurface", true, 861, (entity*) IFC2X3_types[844]);
    IFC2X3_types[928] = new entity("IfcTShapeProfileDef", false, 928, (entity*) IFC2X3_types[538]);
    IFC2X3_types[878] = new entity("IfcTerminatorSymbol", false, 878, (entity*) IFC2X3_types[34]);
    IFC2X3_types[884] = new entity("IfcTextLiteral", false, 884, (entity*) IFC2X3_types[392]);
    IFC2X3_types[885] = new entity("IfcTextLiteralWithExtent", false, 885, (entity*) IFC2X3_types[884]);
    IFC2X3_types[924] = new entity("IfcTrapeziumProfileDef", false, 924, (entity*) IFC2X3_types[538]);
    IFC2X3_types[931] = new entity("IfcTwoDirectionRepeatFactor", false, 931, (entity*) IFC2X3_types[526]);
    IFC2X3_types[932] = new entity("IfcTypeObject", false, 932, (entity*) IFC2X3_types[516]);
    IFC2X3_types[933] = new entity("IfcTypeProduct", false, 933, (entity*) IFC2X3_types[932]);
    IFC2X3_types[939] = new entity("IfcUShapeProfileDef", false, 939, (entity*) IFC2X3_types[538]);
    IFC2X3_types[944] = new entity("IfcVector", false, 944, (entity*) IFC2X3_types[392]);
    IFC2X3_types[948] = new entity("IfcVertexLoop", false, 948, (entity*) IFC2X3_types[463]);
    IFC2X3_types[966] = new entity("IfcWindowLiningProperties", false, 966, (entity*) IFC2X3_types[625]);
    IFC2X3_types[969] = new entity("IfcWindowPanelProperties", false, 969, (entity*) IFC2X3_types[625]);
    IFC2X3_types[970] = new entity("IfcWindowStyle", false, 970, (entity*) IFC2X3_types[933]);
    IFC2X3_types[979] = new entity("IfcZShapeProfileDef", false, 979, (entity*) IFC2X3_types[538]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[116]);
        items.push_back(IFC2X3_types[119]);
        IFC2X3_types[118] = new select_type("IfcClassificationNotationSelect", 118, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[126]);
        items.push_back(IFC2X3_types[582]);
        IFC2X3_types[123] = new select_type("IfcColour", 123, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[125]);
        items.push_back(IFC2X3_types[512]);
        IFC2X3_types[124] = new select_type("IfcColourOrFactor", 124, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[198]);
        items.push_back(IFC2X3_types[583]);
        IFC2X3_types[201] = new select_type("IfcCurveStyleFontSelect", 201, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[242]);
        items.push_back(IFC2X3_types[244]);
        IFC2X3_types[245] = new select_type("IfcDocumentSelect", 245, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[526]);
        items.push_back(IFC2X3_types[577]);
        IFC2X3_types[403] = new select_type("IfcHatchLineDistanceSelect", 403, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(22);
        items.push_back(IFC2X3_types[22]);
        items.push_back(IFC2X3_types[47]);
        items.push_back(IFC2X3_types[130]);
        items.push_back(IFC2X3_types[161]);
        items.push_back(IFC2X3_types[176]);
        items.push_back(IFC2X3_types[216]);
        items.push_back(IFC2X3_types[282]);
        items.push_back(IFC2X3_types[435]);
        items.push_back(IFC2X3_types[467]);
        items.push_back(IFC2X3_types[474]);
        items.push_back(IFC2X3_types[512]);
        items.push_back(IFC2X3_types[514]);
        items.push_back(IFC2X3_types[539]);
        items.push_back(IFC2X3_types[565]);
        items.push_back(IFC2X3_types[577]);
        items.push_back(IFC2X3_types[578]);
        items.push_back(IFC2X3_types[579]);
        items.push_back(IFC2X3_types[650]);
        items.push_back(IFC2X3_types[772]);
        items.push_back(IFC2X3_types[906]);
        items.push_back(IFC2X3_types[907]);
        items.push_back(IFC2X3_types[954]);
        IFC2X3_types[485] = new select_type("IfcMeasureValue", 485, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[569]);
        items.push_back(IFC2X3_types[949]);
        IFC2X3_types[572] = new select_type("IfcPointOrVertexPoint", 572, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC2X3_types[197]);
        items.push_back(IFC2X3_types[343]);
        items.push_back(IFC2X3_types[513]);
        items.push_back(IFC2X3_types[850]);
        items.push_back(IFC2X3_types[864]);
        items.push_back(IFC2X3_types[887]);
        IFC2X3_types[595] = new select_type("IfcPresentationStyleSelect", 595, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IFC2X3_types[123]);
        IFC2X3_types[865] = new select_type("IfcSymbolStyleSelect", 865, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[211]);
        items.push_back(IFC2X3_types[485]);
        items.push_back(IFC2X3_types[762]);
        IFC2X3_types[940] = new select_type("IfcValue", 940, items);
    }
    IFC2X3_types[28] = new entity("IfcAnnotationCurveOccurrence", false, 28, (entity*) IFC2X3_types[31]);
    IFC2X3_types[29] = new entity("IfcAnnotationFillArea", false, 29, (entity*) IFC2X3_types[392]);
    IFC2X3_types[30] = new entity("IfcAnnotationFillAreaOccurrence", false, 30, (entity*) IFC2X3_types[31]);
    IFC2X3_types[32] = new entity("IfcAnnotationSurface", false, 32, (entity*) IFC2X3_types[392]);
    IFC2X3_types[52] = new entity("IfcAxis1Placement", false, 52, (entity*) IFC2X3_types[560]);
    IFC2X3_types[54] = new entity("IfcAxis2Placement2D", false, 54, (entity*) IFC2X3_types[560]);
    IFC2X3_types[55] = new entity("IfcAxis2Placement3D", false, 55, (entity*) IFC2X3_types[560]);
    IFC2X3_types[69] = new entity("IfcBooleanResult", false, 69, (entity*) IFC2X3_types[392]);
    IFC2X3_types[76] = new entity("IfcBoundedSurface", false, 76, (entity*) IFC2X3_types[844]);
    IFC2X3_types[77] = new entity("IfcBoundingBox", false, 77, (entity*) IFC2X3_types[392]);
    IFC2X3_types[79] = new entity("IfcBoxedHalfSpace", false, 79, (entity*) IFC2X3_types[402]);
    IFC2X3_types[186] = new entity("IfcCShapeProfileDef", false, 186, (entity*) IFC2X3_types[538]);
    IFC2X3_types[98] = new entity("IfcCartesianPoint", false, 98, (entity*) IFC2X3_types[569]);
    IFC2X3_types[99] = new entity("IfcCartesianTransformationOperator", true, 99, (entity*) IFC2X3_types[392]);
    IFC2X3_types[100] = new entity("IfcCartesianTransformationOperator2D", false, 100, (entity*) IFC2X3_types[99]);
    IFC2X3_types[101] = new entity("IfcCartesianTransformationOperator2DnonUniform", false, 101, (entity*) IFC2X3_types[100]);
    IFC2X3_types[102] = new entity("IfcCartesianTransformationOperator3D", false, 102, (entity*) IFC2X3_types[99]);
    IFC2X3_types[103] = new entity("IfcCartesianTransformationOperator3DnonUniform", false, 103, (entity*) IFC2X3_types[102]);
    IFC2X3_types[112] = new entity("IfcCircleProfileDef", false, 112, (entity*) IFC2X3_types[538]);
    IFC2X3_types[120] = new entity("IfcClosedShell", false, 120, (entity*) IFC2X3_types[144]);
    IFC2X3_types[133] = new entity("IfcCompositeCurveSegment", false, 133, (entity*) IFC2X3_types[392]);
    IFC2X3_types[180] = new entity("IfcCraneRailAShapeProfileDef", false, 180, (entity*) IFC2X3_types[538]);
    IFC2X3_types[181] = new entity("IfcCraneRailFShapeProfileDef", false, 181, (entity*) IFC2X3_types[538]);
    IFC2X3_types[183] = new entity("IfcCsgPrimitive3D", true, 183, (entity*) IFC2X3_types[392]);
    IFC2X3_types[185] = new entity("IfcCsgSolid", false, 185, (entity*) IFC2X3_types[773]);
    IFC2X3_types[193] = new entity("IfcCurve", true, 193, (entity*) IFC2X3_types[392]);
    IFC2X3_types[194] = new entity("IfcCurveBoundedPlane", false, 194, (entity*) IFC2X3_types[76]);
    IFC2X3_types[209] = new entity("IfcDefinedSymbol", false, 209, (entity*) IFC2X3_types[392]);
    IFC2X3_types[221] = new entity("IfcDimensionCurve", false, 221, (entity*) IFC2X3_types[28]);
    IFC2X3_types[223] = new entity("IfcDimensionCurveTerminator", false, 223, (entity*) IFC2X3_types[878]);
    IFC2X3_types[226] = new entity("IfcDirection", false, 226, (entity*) IFC2X3_types[392]);
    IFC2X3_types[248] = new entity("IfcDoorLiningProperties", false, 248, (entity*) IFC2X3_types[625]);
    IFC2X3_types[251] = new entity("IfcDoorPanelProperties", false, 251, (entity*) IFC2X3_types[625]);
    IFC2X3_types[252] = new entity("IfcDoorStyle", false, 252, (entity*) IFC2X3_types[933]);
    IFC2X3_types[256] = new entity("IfcDraughtingCallout", false, 256, (entity*) IFC2X3_types[392]);
    IFC2X3_types[259] = new entity("IfcDraughtingPreDefinedColour", false, 259, (entity*) IFC2X3_types[582]);
    IFC2X3_types[260] = new entity("IfcDraughtingPreDefinedCurveFont", false, 260, (entity*) IFC2X3_types[583]);
    IFC2X3_types[272] = new entity("IfcEdgeLoop", false, 272, (entity*) IFC2X3_types[463]);
    IFC2X3_types[304] = new entity("IfcElementQuantity", false, 304, (entity*) IFC2X3_types[625]);
    IFC2X3_types[305] = new entity("IfcElementType", true, 305, (entity*) IFC2X3_types[933]);
    IFC2X3_types[298] = new entity("IfcElementarySurface", true, 298, (entity*) IFC2X3_types[844]);
    IFC2X3_types[307] = new entity("IfcEllipseProfileDef", false, 307, (entity*) IFC2X3_types[538]);
    IFC2X3_types[311] = new entity("IfcEnergyProperties", false, 311, (entity*) IFC2X3_types[625]);
    IFC2X3_types[327] = new entity("IfcExtrudedAreaSolid", false, 327, (entity*) IFC2X3_types[859]);
    IFC2X3_types[329] = new entity("IfcFaceBasedSurfaceModel", false, 329, (entity*) IFC2X3_types[392]);
    IFC2X3_types[344] = new entity("IfcFillAreaStyleHatching", false, 344, (entity*) IFC2X3_types[392]);
    IFC2X3_types[347] = new entity("IfcFillAreaStyleTileSymbolWithStyle", false, 347, (entity*) IFC2X3_types[392]);
    IFC2X3_types[345] = new entity("IfcFillAreaStyleTiles", false, 345, (entity*) IFC2X3_types[392]);
    IFC2X3_types[372] = new entity("IfcFluidFlowProperties", false, 372, (entity*) IFC2X3_types[625]);
    IFC2X3_types[382] = new entity("IfcFurnishingElementType", false, 382, (entity*) IFC2X3_types[305]);
    IFC2X3_types[384] = new entity("IfcFurnitureType", false, 384, (entity*) IFC2X3_types[382]);
    IFC2X3_types[389] = new entity("IfcGeometricCurveSet", false, 389, (entity*) IFC2X3_types[394]);
    IFC2X3_types[424] = new entity("IfcIShapeProfileDef", false, 424, (entity*) IFC2X3_types[538]);
    IFC2X3_types[464] = new entity("IfcLShapeProfileDef", false, 464, (entity*) IFC2X3_types[538]);
    IFC2X3_types[452] = new entity("IfcLine", false, 452, (entity*) IFC2X3_types[193]);
    IFC2X3_types[470] = new entity("IfcManifoldSolidBrep", true, 470, (entity*) IFC2X3_types[773]);
    IFC2X3_types[515] = new entity("IfcObject", true, 515, (entity*) IFC2X3_types[516]);
    IFC2X3_types[524] = new entity("IfcOffsetCurve2D", false, 524, (entity*) IFC2X3_types[193]);
    IFC2X3_types[525] = new entity("IfcOffsetCurve3D", false, 525, (entity*) IFC2X3_types[193]);
    IFC2X3_types[543] = new entity("IfcPermeableCoveringProperties", false, 543, (entity*) IFC2X3_types[625]);
    IFC2X3_types[561] = new entity("IfcPlanarBox", false, 561, (entity*) IFC2X3_types[562]);
    IFC2X3_types[564] = new entity("IfcPlane", false, 564, (entity*) IFC2X3_types[298]);
    IFC2X3_types[599] = new entity("IfcProcess", true, 599, (entity*) IFC2X3_types[515]);
    IFC2X3_types[600] = new entity("IfcProduct", true, 600, (entity*) IFC2X3_types[515]);
    IFC2X3_types[607] = new entity("IfcProject", false, 607, (entity*) IFC2X3_types[515]);
    IFC2X3_types[609] = new entity("IfcProjectionCurve", false, 609, (entity*) IFC2X3_types[28]);
    IFC2X3_types[624] = new entity("IfcPropertySet", false, 624, (entity*) IFC2X3_types[625]);
    IFC2X3_types[631] = new entity("IfcProxy", false, 631, (entity*) IFC2X3_types[600]);
    IFC2X3_types[653] = new entity("IfcRectangleHollowProfileDef", false, 653, (entity*) IFC2X3_types[654]);
    IFC2X3_types[655] = new entity("IfcRectangularPyramid", false, 655, (entity*) IFC2X3_types[183]);
    IFC2X3_types[656] = new entity("IfcRectangularTrimmedSurface", false, 656, (entity*) IFC2X3_types[76]);
    IFC2X3_types[668] = new entity("IfcRelAssigns", true, 668, (entity*) IFC2X3_types[686]);
    IFC2X3_types[670] = new entity("IfcRelAssignsToActor", false, 670, (entity*) IFC2X3_types[668]);
    IFC2X3_types[671] = new entity("IfcRelAssignsToControl", false, 671, (entity*) IFC2X3_types[668]);
    IFC2X3_types[672] = new entity("IfcRelAssignsToGroup", false, 672, (entity*) IFC2X3_types[668]);
    IFC2X3_types[673] = new entity("IfcRelAssignsToProcess", false, 673, (entity*) IFC2X3_types[668]);
    IFC2X3_types[674] = new entity("IfcRelAssignsToProduct", false, 674, (entity*) IFC2X3_types[668]);
    IFC2X3_types[675] = new entity("IfcRelAssignsToProjectOrder", false, 675, (entity*) IFC2X3_types[671]);
    IFC2X3_types[676] = new entity("IfcRelAssignsToResource", false, 676, (entity*) IFC2X3_types[668]);
    IFC2X3_types[677] = new entity("IfcRelAssociates", false, 677, (entity*) IFC2X3_types[686]);
    IFC2X3_types[678] = new entity("IfcRelAssociatesAppliedValue", false, 678, (entity*) IFC2X3_types[677]);
    IFC2X3_types[679] = new entity("IfcRelAssociatesApproval", false, 679, (entity*) IFC2X3_types[677]);
    IFC2X3_types[680] = new entity("IfcRelAssociatesClassification", false, 680, (entity*) IFC2X3_types[677]);
    IFC2X3_types[681] = new entity("IfcRelAssociatesConstraint", false, 681, (entity*) IFC2X3_types[677]);
    IFC2X3_types[682] = new entity("IfcRelAssociatesDocument", false, 682, (entity*) IFC2X3_types[677]);
    IFC2X3_types[683] = new entity("IfcRelAssociatesLibrary", false, 683, (entity*) IFC2X3_types[677]);
    IFC2X3_types[684] = new entity("IfcRelAssociatesMaterial", false, 684, (entity*) IFC2X3_types[677]);
    IFC2X3_types[685] = new entity("IfcRelAssociatesProfileProperties", false, 685, (entity*) IFC2X3_types[677]);
    IFC2X3_types[688] = new entity("IfcRelConnects", true, 688, (entity*) IFC2X3_types[686]);
    IFC2X3_types[689] = new entity("IfcRelConnectsElements", false, 689, (entity*) IFC2X3_types[688]);
    IFC2X3_types[690] = new entity("IfcRelConnectsPathElements", false, 690, (entity*) IFC2X3_types[689]);
    IFC2X3_types[692] = new entity("IfcRelConnectsPortToElement", false, 692, (entity*) IFC2X3_types[688]);
    IFC2X3_types[691] = new entity("IfcRelConnectsPorts", false, 691, (entity*) IFC2X3_types[688]);
    IFC2X3_types[693] = new entity("IfcRelConnectsStructuralActivity", false, 693, (entity*) IFC2X3_types[688]);
    IFC2X3_types[694] = new entity("IfcRelConnectsStructuralElement", false, 694, (entity*) IFC2X3_types[688]);
    IFC2X3_types[695] = new entity("IfcRelConnectsStructuralMember", false, 695, (entity*) IFC2X3_types[688]);
    IFC2X3_types[696] = new entity("IfcRelConnectsWithEccentricity", false, 696, (entity*) IFC2X3_types[695]);
    IFC2X3_types[697] = new entity("IfcRelConnectsWithRealizingElements", false, 697, (entity*) IFC2X3_types[689]);
    IFC2X3_types[698] = new entity("IfcRelContainedInSpatialStructure", false, 698, (entity*) IFC2X3_types[688]);
    IFC2X3_types[699] = new entity("IfcRelCoversBldgElements", false, 699, (entity*) IFC2X3_types[688]);
    IFC2X3_types[700] = new entity("IfcRelCoversSpaces", false, 700, (entity*) IFC2X3_types[688]);
    IFC2X3_types[701] = new entity("IfcRelDecomposes", true, 701, (entity*) IFC2X3_types[686]);
    IFC2X3_types[702] = new entity("IfcRelDefines", true, 702, (entity*) IFC2X3_types[686]);
    IFC2X3_types[703] = new entity("IfcRelDefinesByProperties", false, 703, (entity*) IFC2X3_types[702]);
    IFC2X3_types[704] = new entity("IfcRelDefinesByType", false, 704, (entity*) IFC2X3_types[702]);
    IFC2X3_types[705] = new entity("IfcRelFillsElement", false, 705, (entity*) IFC2X3_types[688]);
    IFC2X3_types[706] = new entity("IfcRelFlowControlElements", false, 706, (entity*) IFC2X3_types[688]);
    IFC2X3_types[707] = new entity("IfcRelInteractionRequirements", false, 707, (entity*) IFC2X3_types[688]);
    IFC2X3_types[708] = new entity("IfcRelNests", false, 708, (entity*) IFC2X3_types[701]);
    IFC2X3_types[709] = new entity("IfcRelOccupiesSpaces", false, 709, (entity*) IFC2X3_types[670]);
    IFC2X3_types[710] = new entity("IfcRelOverridesProperties", false, 710, (entity*) IFC2X3_types[703]);
    IFC2X3_types[711] = new entity("IfcRelProjectsElement", false, 711, (entity*) IFC2X3_types[688]);
    IFC2X3_types[712] = new entity("IfcRelReferencedInSpatialStructure", false, 712, (entity*) IFC2X3_types[688]);
    IFC2X3_types[713] = new entity("IfcRelSchedulesCostItems", false, 713, (entity*) IFC2X3_types[671]);
    IFC2X3_types[714] = new entity("IfcRelSequence", false, 714, (entity*) IFC2X3_types[688]);
    IFC2X3_types[715] = new entity("IfcRelServicesBuildings", false, 715, (entity*) IFC2X3_types[688]);
    IFC2X3_types[716] = new entity("IfcRelSpaceBoundary", false, 716, (entity*) IFC2X3_types[688]);
    IFC2X3_types[717] = new entity("IfcRelVoidsElement", false, 717, (entity*) IFC2X3_types[688]);
    IFC2X3_types[722] = new entity("IfcResource", true, 722, (entity*) IFC2X3_types[515]);
    IFC2X3_types[724] = new entity("IfcRevolvedAreaSolid", false, 724, (entity*) IFC2X3_types[859]);
    IFC2X3_types[727] = new entity("IfcRightCircularCone", false, 727, (entity*) IFC2X3_types[183]);
    IFC2X3_types[728] = new entity("IfcRightCircularCylinder", false, 728, (entity*) IFC2X3_types[183]);
    IFC2X3_types[786] = new entity("IfcSpatialStructureElement", true, 786, (entity*) IFC2X3_types[600]);
    IFC2X3_types[787] = new entity("IfcSpatialStructureElementType", true, 787, (entity*) IFC2X3_types[305]);
    IFC2X3_types[792] = new entity("IfcSphere", false, 792, (entity*) IFC2X3_types[183]);
    IFC2X3_types[802] = new entity("IfcStructuralActivity", true, 802, (entity*) IFC2X3_types[600]);
    IFC2X3_types[811] = new entity("IfcStructuralItem", true, 811, (entity*) IFC2X3_types[600]);
    IFC2X3_types[824] = new entity("IfcStructuralMember", true, 824, (entity*) IFC2X3_types[811]);
    IFC2X3_types[831] = new entity("IfcStructuralReaction", true, 831, (entity*) IFC2X3_types[802]);
    IFC2X3_types[835] = new entity("IfcStructuralSurfaceMember", false, 835, (entity*) IFC2X3_types[824]);
    IFC2X3_types[836] = new entity("IfcStructuralSurfaceMemberVarying", false, 836, (entity*) IFC2X3_types[835]);
    IFC2X3_types[838] = new entity("IfcStructuredDimensionCallout", false, 838, (entity*) IFC2X3_types[256]);
    IFC2X3_types[845] = new entity("IfcSurfaceCurveSweptAreaSolid", false, 845, (entity*) IFC2X3_types[859]);
    IFC2X3_types[846] = new entity("IfcSurfaceOfLinearExtrusion", false, 846, (entity*) IFC2X3_types[861]);
    IFC2X3_types[847] = new entity("IfcSurfaceOfRevolution", false, 847, (entity*) IFC2X3_types[861]);
    IFC2X3_types[867] = new entity("IfcSystemFurnitureElementType", false, 867, (entity*) IFC2X3_types[382]);
    IFC2X3_types[872] = new entity("IfcTask", false, 872, (entity*) IFC2X3_types[599]);
    IFC2X3_types[922] = new entity("IfcTransportElementType", false, 922, (entity*) IFC2X3_types[305]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[54]);
        items.push_back(IFC2X3_types[55]);
        IFC2X3_types[53] = new select_type("IfcAxis2Placement", 53, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC2X3_types[69]);
        items.push_back(IFC2X3_types[183]);
        items.push_back(IFC2X3_types[402]);
        items.push_back(IFC2X3_types[773]);
        IFC2X3_types[67] = new select_type("IfcBooleanOperand", 67, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[69]);
        items.push_back(IFC2X3_types[183]);
        IFC2X3_types[184] = new select_type("IfcCsgSelect", 184, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[199]);
        items.push_back(IFC2X3_types[201]);
        IFC2X3_types[195] = new select_type("IfcCurveFontOrScaledCurveFontSelect", 195, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[28]);
        items.push_back(IFC2X3_types[34]);
        items.push_back(IFC2X3_types[35]);
        IFC2X3_types[257] = new select_type("IfcDraughtingCalloutElement", 257, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IFC2X3_types[347]);
        IFC2X3_types[346] = new select_type("IfcFillAreaStyleTileShapeSelect", 346, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC2X3_types[123]);
        items.push_back(IFC2X3_types[322]);
        items.push_back(IFC2X3_types[344]);
        items.push_back(IFC2X3_types[345]);
        IFC2X3_types[348] = new select_type("IfcFillStyleSelect", 348, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[193]);
        items.push_back(IFC2X3_types[569]);
        items.push_back(IFC2X3_types[844]);
        IFC2X3_types[395] = new select_type("IfcGeometricSetSelect", 395, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[226]);
        items.push_back(IFC2X3_types[565]);
        IFC2X3_types[533] = new select_type("IfcOrientationSelect", 533, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[120]);
        items.push_back(IFC2X3_types[528]);
        IFC2X3_types[759] = new select_type("IfcShell", 759, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC2X3_types[329]);
        items.push_back(IFC2X3_types[332]);
        items.push_back(IFC2X3_types[844]);
        IFC2X3_types[848] = new select_type("IfcSurfaceOrFaceSurface", 848, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[98]);
        items.push_back(IFC2X3_types[539]);
        IFC2X3_types[927] = new select_type("IfcTrimmingSelect", 927, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[226]);
        items.push_back(IFC2X3_types[944]);
        IFC2X3_types[945] = new select_type("IfcVectorOrDirection", 945, items);
    }
    IFC2X3_types[6] = new entity("IfcActor", false, 6, (entity*) IFC2X3_types[515]);
    IFC2X3_types[27] = new entity("IfcAnnotation", false, 27, (entity*) IFC2X3_types[600]);
    IFC2X3_types[51] = new entity("IfcAsymmetricIShapeProfileDef", false, 51, (entity*) IFC2X3_types[424]);
    IFC2X3_types[62] = new entity("IfcBlock", false, 62, (entity*) IFC2X3_types[183]);
    IFC2X3_types[66] = new entity("IfcBooleanClippingResult", false, 66, (entity*) IFC2X3_types[69]);
    IFC2X3_types[75] = new entity("IfcBoundedCurve", true, 75, (entity*) IFC2X3_types[193]);
    IFC2X3_types[82] = new entity("IfcBuilding", false, 82, (entity*) IFC2X3_types[786]);
    IFC2X3_types[89] = new entity("IfcBuildingElementType", true, 89, (entity*) IFC2X3_types[305]);
    IFC2X3_types[90] = new entity("IfcBuildingStorey", false, 90, (entity*) IFC2X3_types[786]);
    IFC2X3_types[111] = new entity("IfcCircleHollowProfileDef", false, 111, (entity*) IFC2X3_types[112]);
    IFC2X3_types[128] = new entity("IfcColumnType", false, 128, (entity*) IFC2X3_types[89]);
    IFC2X3_types[132] = new entity("IfcCompositeCurve", false, 132, (entity*) IFC2X3_types[75]);
    IFC2X3_types[143] = new entity("IfcConic", true, 143, (entity*) IFC2X3_types[193]);
    IFC2X3_types[160] = new entity("IfcConstructionResource", true, 160, (entity*) IFC2X3_types[722]);
    IFC2X3_types[163] = new entity("IfcControl", true, 163, (entity*) IFC2X3_types[515]);
    IFC2X3_types[172] = new entity("IfcCostItem", false, 172, (entity*) IFC2X3_types[163]);
    IFC2X3_types[173] = new entity("IfcCostSchedule", false, 173, (entity*) IFC2X3_types[163]);
    IFC2X3_types[178] = new entity("IfcCoveringType", false, 178, (entity*) IFC2X3_types[89]);
    IFC2X3_types[182] = new entity("IfcCrewResource", false, 182, (entity*) IFC2X3_types[160]);
    IFC2X3_types[190] = new entity("IfcCurtainWallType", false, 190, (entity*) IFC2X3_types[89]);
    IFC2X3_types[222] = new entity("IfcDimensionCurveDirectedCallout", false, 222, (entity*) IFC2X3_types[256]);
    IFC2X3_types[236] = new entity("IfcDistributionElementType", false, 236, (entity*) IFC2X3_types[305]);
    IFC2X3_types[238] = new entity("IfcDistributionFlowElementType", true, 238, (entity*) IFC2X3_types[236]);
    IFC2X3_types[273] = new entity("IfcElectricalBaseProperties", false, 273, (entity*) IFC2X3_types[311]);
    IFC2X3_types[297] = new entity("IfcElement", true, 297, (entity*) IFC2X3_types[600]);
    IFC2X3_types[299] = new entity("IfcElementAssembly", false, 299, (entity*) IFC2X3_types[297]);
    IFC2X3_types[301] = new entity("IfcElementComponent", true, 301, (entity*) IFC2X3_types[297]);
    IFC2X3_types[302] = new entity("IfcElementComponentType", true, 302, (entity*) IFC2X3_types[305]);
    IFC2X3_types[306] = new entity("IfcEllipse", false, 306, (entity*) IFC2X3_types[143]);
    IFC2X3_types[309] = new entity("IfcEnergyConversionDeviceType", true, 309, (entity*) IFC2X3_types[238]);
    IFC2X3_types[315] = new entity("IfcEquipmentElement", false, 315, (entity*) IFC2X3_types[297]);
    IFC2X3_types[316] = new entity("IfcEquipmentStandard", false, 316, (entity*) IFC2X3_types[163]);
    IFC2X3_types[317] = new entity("IfcEvaporativeCoolerType", false, 317, (entity*) IFC2X3_types[309]);
    IFC2X3_types[319] = new entity("IfcEvaporatorType", false, 319, (entity*) IFC2X3_types[309]);
    IFC2X3_types[333] = new entity("IfcFacetedBrep", false, 333, (entity*) IFC2X3_types[470]);
    IFC2X3_types[334] = new entity("IfcFacetedBrepWithVoids", false, 334, (entity*) IFC2X3_types[470]);
    IFC2X3_types[338] = new entity("IfcFastener", false, 338, (entity*) IFC2X3_types[301]);
    IFC2X3_types[339] = new entity("IfcFastenerType", false, 339, (entity*) IFC2X3_types[302]);
    IFC2X3_types[340] = new entity("IfcFeatureElement", true, 340, (entity*) IFC2X3_types[297]);
    IFC2X3_types[341] = new entity("IfcFeatureElementAddition", true, 341, (entity*) IFC2X3_types[340]);
    IFC2X3_types[342] = new entity("IfcFeatureElementSubtraction", true, 342, (entity*) IFC2X3_types[340]);
    IFC2X3_types[354] = new entity("IfcFlowControllerType", true, 354, (entity*) IFC2X3_types[238]);
    IFC2X3_types[357] = new entity("IfcFlowFittingType", true, 357, (entity*) IFC2X3_types[238]);
    IFC2X3_types[360] = new entity("IfcFlowMeterType", false, 360, (entity*) IFC2X3_types[354]);
    IFC2X3_types[363] = new entity("IfcFlowMovingDeviceType", true, 363, (entity*) IFC2X3_types[238]);
    IFC2X3_types[365] = new entity("IfcFlowSegmentType", true, 365, (entity*) IFC2X3_types[238]);
    IFC2X3_types[367] = new entity("IfcFlowStorageDeviceType", true, 367, (entity*) IFC2X3_types[238]);
    IFC2X3_types[369] = new entity("IfcFlowTerminalType", true, 369, (entity*) IFC2X3_types[238]);
    IFC2X3_types[371] = new entity("IfcFlowTreatmentDeviceType", true, 371, (entity*) IFC2X3_types[238]);
    IFC2X3_types[381] = new entity("IfcFurnishingElement", false, 381, (entity*) IFC2X3_types[297]);
    IFC2X3_types[383] = new entity("IfcFurnitureStandard", false, 383, (entity*) IFC2X3_types[163]);
    IFC2X3_types[385] = new entity("IfcGasTerminalType", false, 385, (entity*) IFC2X3_types[369]);
    IFC2X3_types[398] = new entity("IfcGrid", false, 398, (entity*) IFC2X3_types[600]);
    IFC2X3_types[401] = new entity("IfcGroup", false, 401, (entity*) IFC2X3_types[515]);
    IFC2X3_types[404] = new entity("IfcHeatExchangerType", false, 404, (entity*) IFC2X3_types[309]);
    IFC2X3_types[409] = new entity("IfcHumidifierType", false, 409, (entity*) IFC2X3_types[309]);
    IFC2X3_types[419] = new entity("IfcInventory", false, 419, (entity*) IFC2X3_types[401]);
    IFC2X3_types[426] = new entity("IfcJunctionBoxType", false, 426, (entity*) IFC2X3_types[357]);
    IFC2X3_types[430] = new entity("IfcLaborResource", false, 430, (entity*) IFC2X3_types[160]);
    IFC2X3_types[431] = new entity("IfcLampType", false, 431, (entity*) IFC2X3_types[369]);
    IFC2X3_types[443] = new entity("IfcLightFixtureType", false, 443, (entity*) IFC2X3_types[369]);
    IFC2X3_types[453] = new entity("IfcLinearDimension", false, 453, (entity*) IFC2X3_types[222]);
    IFC2X3_types[488] = new entity("IfcMechanicalFastener", false, 488, (entity*) IFC2X3_types[338]);
    IFC2X3_types[489] = new entity("IfcMechanicalFastenerType", false, 489, (entity*) IFC2X3_types[339]);
    IFC2X3_types[493] = new entity("IfcMemberType", false, 493, (entity*) IFC2X3_types[89]);
    IFC2X3_types[508] = new entity("IfcMotorConnectionType", false, 508, (entity*) IFC2X3_types[309]);
    IFC2X3_types[510] = new entity("IfcMove", false, 510, (entity*) IFC2X3_types[872]);
    IFC2X3_types[522] = new entity("IfcOccupant", false, 522, (entity*) IFC2X3_types[6]);
    IFC2X3_types[527] = new entity("IfcOpeningElement", false, 527, (entity*) IFC2X3_types[342]);
    IFC2X3_types[530] = new entity("IfcOrderAction", false, 530, (entity*) IFC2X3_types[872]);
    IFC2X3_types[535] = new entity("IfcOutletType", false, 535, (entity*) IFC2X3_types[369]);
    IFC2X3_types[541] = new entity("IfcPerformanceHistory", false, 541, (entity*) IFC2X3_types[163]);
    IFC2X3_types[544] = new entity("IfcPermit", false, 544, (entity*) IFC2X3_types[163]);
    IFC2X3_types[555] = new entity("IfcPipeFittingType", false, 555, (entity*) IFC2X3_types[357]);
    IFC2X3_types[557] = new entity("IfcPipeSegmentType", false, 557, (entity*) IFC2X3_types[365]);
    IFC2X3_types[567] = new entity("IfcPlateType", false, 567, (entity*) IFC2X3_types[89]);
    IFC2X3_types[574] = new entity("IfcPolyline", false, 574, (entity*) IFC2X3_types[75]);
    IFC2X3_types[576] = new entity("IfcPort", true, 576, (entity*) IFC2X3_types[600]);
    IFC2X3_types[597] = new entity("IfcProcedure", false, 597, (entity*) IFC2X3_types[599]);
    IFC2X3_types[611] = new entity("IfcProjectOrder", false, 611, (entity*) IFC2X3_types[163]);
    IFC2X3_types[612] = new entity("IfcProjectOrderRecord", false, 612, (entity*) IFC2X3_types[163]);
    IFC2X3_types[610] = new entity("IfcProjectionElement", false, 610, (entity*) IFC2X3_types[341]);
    IFC2X3_types[629] = new entity("IfcProtectiveDeviceType", false, 629, (entity*) IFC2X3_types[354]);
    IFC2X3_types[632] = new entity("IfcPumpType", false, 632, (entity*) IFC2X3_types[363]);
    IFC2X3_types[641] = new entity("IfcRadiusDimension", false, 641, (entity*) IFC2X3_types[222]);
    IFC2X3_types[643] = new entity("IfcRailingType", false, 643, (entity*) IFC2X3_types[89]);
    IFC2X3_types[647] = new entity("IfcRampFlightType", false, 647, (entity*) IFC2X3_types[89]);
    IFC2X3_types[667] = new entity("IfcRelAggregates", false, 667, (entity*) IFC2X3_types[701]);
    IFC2X3_types[669] = new entity("IfcRelAssignsTasks", false, 669, (entity*) IFC2X3_types[671]);
    IFC2X3_types[738] = new entity("IfcSanitaryTerminalType", false, 738, (entity*) IFC2X3_types[369]);
    IFC2X3_types[740] = new entity("IfcScheduleTimeControl", false, 740, (entity*) IFC2X3_types[163]);
    IFC2X3_types[751] = new entity("IfcServiceLife", false, 751, (entity*) IFC2X3_types[163]);
    IFC2X3_types[764] = new entity("IfcSite", false, 764, (entity*) IFC2X3_types[786]);
    IFC2X3_types[769] = new entity("IfcSlabType", false, 769, (entity*) IFC2X3_types[89]);
    IFC2X3_types[779] = new entity("IfcSpace", false, 779, (entity*) IFC2X3_types[786]);
    IFC2X3_types[780] = new entity("IfcSpaceHeaterType", false, 780, (entity*) IFC2X3_types[309]);
    IFC2X3_types[782] = new entity("IfcSpaceProgram", false, 782, (entity*) IFC2X3_types[163]);
    IFC2X3_types[784] = new entity("IfcSpaceType", false, 784, (entity*) IFC2X3_types[787]);
    IFC2X3_types[793] = new entity("IfcStackTerminalType", false, 793, (entity*) IFC2X3_types[369]);
    IFC2X3_types[797] = new entity("IfcStairFlightType", false, 797, (entity*) IFC2X3_types[89]);
    IFC2X3_types[801] = new entity("IfcStructuralAction", true, 801, (entity*) IFC2X3_types[802]);
    IFC2X3_types[805] = new entity("IfcStructuralConnection", true, 805, (entity*) IFC2X3_types[811]);
    IFC2X3_types[807] = new entity("IfcStructuralCurveConnection", false, 807, (entity*) IFC2X3_types[805]);
    IFC2X3_types[808] = new entity("IfcStructuralCurveMember", false, 808, (entity*) IFC2X3_types[824]);
    IFC2X3_types[809] = new entity("IfcStructuralCurveMemberVarying", false, 809, (entity*) IFC2X3_types[808]);
    IFC2X3_types[812] = new entity("IfcStructuralLinearAction", false, 812, (entity*) IFC2X3_types[801]);
    IFC2X3_types[813] = new entity("IfcStructuralLinearActionVarying", false, 813, (entity*) IFC2X3_types[812]);
    IFC2X3_types[815] = new entity("IfcStructuralLoadGroup", false, 815, (entity*) IFC2X3_types[401]);
    IFC2X3_types[825] = new entity("IfcStructuralPlanarAction", false, 825, (entity*) IFC2X3_types[801]);
    IFC2X3_types[826] = new entity("IfcStructuralPlanarActionVarying", false, 826, (entity*) IFC2X3_types[825]);
    IFC2X3_types[827] = new entity("IfcStructuralPointAction", false, 827, (entity*) IFC2X3_types[801]);
    IFC2X3_types[828] = new entity("IfcStructuralPointConnection", false, 828, (entity*) IFC2X3_types[805]);
    IFC2X3_types[829] = new entity("IfcStructuralPointReaction", false, 829, (entity*) IFC2X3_types[831]);
    IFC2X3_types[832] = new entity("IfcStructuralResultGroup", false, 832, (entity*) IFC2X3_types[401]);
    IFC2X3_types[834] = new entity("IfcStructuralSurfaceConnection", false, 834, (entity*) IFC2X3_types[805]);
    IFC2X3_types[842] = new entity("IfcSubContractResource", false, 842, (entity*) IFC2X3_types[160]);
    IFC2X3_types[862] = new entity("IfcSwitchingDeviceType", false, 862, (entity*) IFC2X3_types[354]);
    IFC2X3_types[866] = new entity("IfcSystem", false, 866, (entity*) IFC2X3_types[401]);
    IFC2X3_types[870] = new entity("IfcTankType", false, 870, (entity*) IFC2X3_types[367]);
    IFC2X3_types[911] = new entity("IfcTimeSeriesSchedule", false, 911, (entity*) IFC2X3_types[163]);
    IFC2X3_types[918] = new entity("IfcTransformerType", false, 918, (entity*) IFC2X3_types[309]);
    IFC2X3_types[921] = new entity("IfcTransportElement", false, 921, (entity*) IFC2X3_types[297]);
    IFC2X3_types[925] = new entity("IfcTrimmedCurve", false, 925, (entity*) IFC2X3_types[75]);
    IFC2X3_types[929] = new entity("IfcTubeBundleType", false, 929, (entity*) IFC2X3_types[309]);
    IFC2X3_types[935] = new entity("IfcUnitaryEquipmentType", false, 935, (entity*) IFC2X3_types[309]);
    IFC2X3_types[941] = new entity("IfcValveType", false, 941, (entity*) IFC2X3_types[354]);
    IFC2X3_types[952] = new entity("IfcVirtualElement", false, 952, (entity*) IFC2X3_types[297]);
    IFC2X3_types[958] = new entity("IfcWallType", false, 958, (entity*) IFC2X3_types[89]);
    IFC2X3_types[962] = new entity("IfcWasteTerminalType", false, 962, (entity*) IFC2X3_types[369]);
    IFC2X3_types[973] = new entity("IfcWorkControl", true, 973, (entity*) IFC2X3_types[163]);
    IFC2X3_types[975] = new entity("IfcWorkPlan", false, 975, (entity*) IFC2X3_types[973]);
    IFC2X3_types[976] = new entity("IfcWorkSchedule", false, 976, (entity*) IFC2X3_types[973]);
    IFC2X3_types[978] = new entity("IfcZone", false, 978, (entity*) IFC2X3_types[401]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[75]);
        items.push_back(IFC2X3_types[270]);
        IFC2X3_types[196] = new select_type("IfcCurveOrEdgeCurve", 196, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC2X3_types[297]);
        items.push_back(IFC2X3_types[811]);
        IFC2X3_types[803] = new select_type("IfcStructuralActivityAssignmentSelect", 803, items);
    }
    IFC2X3_types[0] = new entity("Ifc2DCompositeCurve", false, 0, (entity*) IFC2X3_types[132]);
    IFC2X3_types[3] = new entity("IfcActionRequest", false, 3, (entity*) IFC2X3_types[163]);
    IFC2X3_types[14] = new entity("IfcAirTerminalBoxType", false, 14, (entity*) IFC2X3_types[354]);
    IFC2X3_types[16] = new entity("IfcAirTerminalType", false, 16, (entity*) IFC2X3_types[369]);
    IFC2X3_types[18] = new entity("IfcAirToAirHeatRecoveryType", false, 18, (entity*) IFC2X3_types[309]);
    IFC2X3_types[25] = new entity("IfcAngularDimension", false, 25, (entity*) IFC2X3_types[222]);
    IFC2X3_types[50] = new entity("IfcAsset", false, 50, (entity*) IFC2X3_types[401]);
    IFC2X3_types[80] = new entity("IfcBSplineCurve", true, 80, (entity*) IFC2X3_types[75]);
    IFC2X3_types[57] = new entity("IfcBeamType", false, 57, (entity*) IFC2X3_types[89]);
    IFC2X3_types[60] = new entity("IfcBezierCurve", false, 60, (entity*) IFC2X3_types[80]);
    IFC2X3_types[63] = new entity("IfcBoilerType", false, 63, (entity*) IFC2X3_types[309]);
    IFC2X3_types[83] = new entity("IfcBuildingElement", true, 83, (entity*) IFC2X3_types[297]);
    IFC2X3_types[84] = new entity("IfcBuildingElementComponent", true, 84, (entity*) IFC2X3_types[83]);
    IFC2X3_types[85] = new entity("IfcBuildingElementPart", false, 85, (entity*) IFC2X3_types[84]);
    IFC2X3_types[86] = new entity("IfcBuildingElementProxy", false, 86, (entity*) IFC2X3_types[83]);
    IFC2X3_types[87] = new entity("IfcBuildingElementProxyType", false, 87, (entity*) IFC2X3_types[89]);
    IFC2X3_types[91] = new entity("IfcCableCarrierFittingType", false, 91, (entity*) IFC2X3_types[357]);
    IFC2X3_types[93] = new entity("IfcCableCarrierSegmentType", false, 93, (entity*) IFC2X3_types[365]);
    IFC2X3_types[95] = new entity("IfcCableSegmentType", false, 95, (entity*) IFC2X3_types[365]);
    IFC2X3_types[108] = new entity("IfcChillerType", false, 108, (entity*) IFC2X3_types[309]);
    IFC2X3_types[110] = new entity("IfcCircle", false, 110, (entity*) IFC2X3_types[143]);
    IFC2X3_types[121] = new entity("IfcCoilType", false, 121, (entity*) IFC2X3_types[309]);
    IFC2X3_types[127] = new entity("IfcColumn", false, 127, (entity*) IFC2X3_types[83]);
    IFC2X3_types[136] = new entity("IfcCompressorType", false, 136, (entity*) IFC2X3_types[363]);
    IFC2X3_types[138] = new entity("IfcCondenserType", false, 138, (entity*) IFC2X3_types[309]);
    IFC2X3_types[140] = new entity("IfcCondition", false, 140, (entity*) IFC2X3_types[401]);
    IFC2X3_types[141] = new entity("IfcConditionCriterion", false, 141, (entity*) IFC2X3_types[163]);
    IFC2X3_types[157] = new entity("IfcConstructionEquipmentResource", false, 157, (entity*) IFC2X3_types[160]);
    IFC2X3_types[158] = new entity("IfcConstructionMaterialResource", false, 158, (entity*) IFC2X3_types[160]);
    IFC2X3_types[159] = new entity("IfcConstructionProductResource", false, 159, (entity*) IFC2X3_types[160]);
    IFC2X3_types[167] = new entity("IfcCooledBeamType", false, 167, (entity*) IFC2X3_types[309]);
    IFC2X3_types[169] = new entity("IfcCoolingTowerType", false, 169, (entity*) IFC2X3_types[309]);
    IFC2X3_types[177] = new entity("IfcCovering", false, 177, (entity*) IFC2X3_types[83]);
    IFC2X3_types[189] = new entity("IfcCurtainWall", false, 189, (entity*) IFC2X3_types[83]);
    IFC2X3_types[202] = new entity("IfcDamperType", false, 202, (entity*) IFC2X3_types[354]);
    IFC2X3_types[217] = new entity("IfcDiameterDimension", false, 217, (entity*) IFC2X3_types[222]);
    IFC2X3_types[228] = new entity("IfcDiscreteAccessory", false, 228, (entity*) IFC2X3_types[301]);
    IFC2X3_types[229] = new entity("IfcDiscreteAccessoryType", false, 229, (entity*) IFC2X3_types[302]);
    IFC2X3_types[231] = new entity("IfcDistributionChamberElementType", false, 231, (entity*) IFC2X3_types[238]);
    IFC2X3_types[234] = new entity("IfcDistributionControlElementType", true, 234, (entity*) IFC2X3_types[236]);
    IFC2X3_types[235] = new entity("IfcDistributionElement", false, 235, (entity*) IFC2X3_types[297]);
    IFC2X3_types[237] = new entity("IfcDistributionFlowElement", false, 237, (entity*) IFC2X3_types[235]);
    IFC2X3_types[239] = new entity("IfcDistributionPort", false, 239, (entity*) IFC2X3_types[576]);
    IFC2X3_types[247] = new entity("IfcDoor", false, 247, (entity*) IFC2X3_types[83]);
    IFC2X3_types[262] = new entity("IfcDuctFittingType", false, 262, (entity*) IFC2X3_types[357]);
    IFC2X3_types[264] = new entity("IfcDuctSegmentType", false, 264, (entity*) IFC2X3_types[365]);
    IFC2X3_types[266] = new entity("IfcDuctSilencerType", false, 266, (entity*) IFC2X3_types[371]);
    IFC2X3_types[271] = new entity("IfcEdgeFeature", true, 271, (entity*) IFC2X3_types[342]);
    IFC2X3_types[276] = new entity("IfcElectricApplianceType", false, 276, (entity*) IFC2X3_types[369]);
    IFC2X3_types[285] = new entity("IfcElectricFlowStorageDeviceType", false, 285, (entity*) IFC2X3_types[367]);
    IFC2X3_types[287] = new entity("IfcElectricGeneratorType", false, 287, (entity*) IFC2X3_types[309]);
    IFC2X3_types[289] = new entity("IfcElectricHeaterType", false, 289, (entity*) IFC2X3_types[369]);
    IFC2X3_types[291] = new entity("IfcElectricMotorType", false, 291, (entity*) IFC2X3_types[309]);
    IFC2X3_types[294] = new entity("IfcElectricTimeControlType", false, 294, (entity*) IFC2X3_types[354]);
    IFC2X3_types[274] = new entity("IfcElectricalCircuit", false, 274, (entity*) IFC2X3_types[866]);
    IFC2X3_types[275] = new entity("IfcElectricalElement", false, 275, (entity*) IFC2X3_types[297]);
    IFC2X3_types[308] = new entity("IfcEnergyConversionDevice", false, 308, (entity*) IFC2X3_types[237]);
    IFC2X3_types[336] = new entity("IfcFanType", false, 336, (entity*) IFC2X3_types[363]);
    IFC2X3_types[349] = new entity("IfcFilterType", false, 349, (entity*) IFC2X3_types[371]);
    IFC2X3_types[351] = new entity("IfcFireSuppressionTerminalType", false, 351, (entity*) IFC2X3_types[369]);
    IFC2X3_types[353] = new entity("IfcFlowController", false, 353, (entity*) IFC2X3_types[237]);
    IFC2X3_types[356] = new entity("IfcFlowFitting", false, 356, (entity*) IFC2X3_types[237]);
    IFC2X3_types[358] = new entity("IfcFlowInstrumentType", false, 358, (entity*) IFC2X3_types[234]);
    IFC2X3_types[362] = new entity("IfcFlowMovingDevice", false, 362, (entity*) IFC2X3_types[237]);
    IFC2X3_types[364] = new entity("IfcFlowSegment", false, 364, (entity*) IFC2X3_types[237]);
    IFC2X3_types[366] = new entity("IfcFlowStorageDevice", false, 366, (entity*) IFC2X3_types[237]);
    IFC2X3_types[368] = new entity("IfcFlowTerminal", false, 368, (entity*) IFC2X3_types[237]);
    IFC2X3_types[370] = new entity("IfcFlowTreatmentDevice", false, 370, (entity*) IFC2X3_types[237]);
    IFC2X3_types[376] = new entity("IfcFooting", false, 376, (entity*) IFC2X3_types[83]);
    IFC2X3_types[492] = new entity("IfcMember", false, 492, (entity*) IFC2X3_types[83]);
    IFC2X3_types[552] = new entity("IfcPile", false, 552, (entity*) IFC2X3_types[83]);
    IFC2X3_types[566] = new entity("IfcPlate", false, 566, (entity*) IFC2X3_types[83]);
    IFC2X3_types[642] = new entity("IfcRailing", false, 642, (entity*) IFC2X3_types[83]);
    IFC2X3_types[645] = new entity("IfcRamp", false, 645, (entity*) IFC2X3_types[83]);
    IFC2X3_types[646] = new entity("IfcRampFlight", false, 646, (entity*) IFC2X3_types[83]);
    IFC2X3_types[651] = new entity("IfcRationalBezierCurve", false, 651, (entity*) IFC2X3_types[60]);
    IFC2X3_types[665] = new entity("IfcReinforcingElement", true, 665, (entity*) IFC2X3_types[84]);
    IFC2X3_types[666] = new entity("IfcReinforcingMesh", false, 666, (entity*) IFC2X3_types[665]);
    IFC2X3_types[730] = new entity("IfcRoof", false, 730, (entity*) IFC2X3_types[83]);
    IFC2X3_types[736] = new entity("IfcRoundedEdgeFeature", false, 736, (entity*) IFC2X3_types[271]);
    IFC2X3_types[748] = new entity("IfcSensorType", false, 748, (entity*) IFC2X3_types[234]);
    IFC2X3_types[768] = new entity("IfcSlab", false, 768, (entity*) IFC2X3_types[83]);
    IFC2X3_types[795] = new entity("IfcStair", false, 795, (entity*) IFC2X3_types[83]);
    IFC2X3_types[796] = new entity("IfcStairFlight", false, 796, (entity*) IFC2X3_types[83]);
    IFC2X3_types[804] = new entity("IfcStructuralAnalysisModel", false, 804, (entity*) IFC2X3_types[866]);
    IFC2X3_types[875] = new entity("IfcTendon", false, 875, (entity*) IFC2X3_types[665]);
    IFC2X3_types[876] = new entity("IfcTendonAnchor", false, 876, (entity*) IFC2X3_types[665]);
    IFC2X3_types[950] = new entity("IfcVibrationIsolatorType", false, 950, (entity*) IFC2X3_types[229]);
    IFC2X3_types[956] = new entity("IfcWall", false, 956, (entity*) IFC2X3_types[83]);
    IFC2X3_types[957] = new entity("IfcWallStandardCase", false, 957, (entity*) IFC2X3_types[956]);
    IFC2X3_types[965] = new entity("IfcWindow", false, 965, (entity*) IFC2X3_types[83]);
    IFC2X3_types[9] = new entity("IfcActuatorType", false, 9, (entity*) IFC2X3_types[234]);
    IFC2X3_types[20] = new entity("IfcAlarmType", false, 20, (entity*) IFC2X3_types[234]);
    IFC2X3_types[56] = new entity("IfcBeam", false, 56, (entity*) IFC2X3_types[83]);
    IFC2X3_types[105] = new entity("IfcChamferEdgeFeature", false, 105, (entity*) IFC2X3_types[271]);
    IFC2X3_types[164] = new entity("IfcControllerType", false, 164, (entity*) IFC2X3_types[234]);
    IFC2X3_types[230] = new entity("IfcDistributionChamberElement", false, 230, (entity*) IFC2X3_types[237]);
    IFC2X3_types[233] = new entity("IfcDistributionControlElement", false, 233, (entity*) IFC2X3_types[235]);
    IFC2X3_types[283] = new entity("IfcElectricDistributionPoint", false, 283, (entity*) IFC2X3_types[353]);
    IFC2X3_types[662] = new entity("IfcReinforcingBar", false, 662, (entity*) IFC2X3_types[665]);
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[0])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RequestID", new named_type(IFC2X3_types[412]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[3])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TheActor", new named_type(IFC2X3_types[8]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[6])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Role", new named_type(IFC2X3_types[729]), false));
        attributes.push_back(new attribute("UserDefinedRole", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[7])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[10]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[9])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Purpose", new named_type(IFC2X3_types[12]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("UserDefinedPurpose", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[11])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[15]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[14])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[17]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[16])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[19]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[18])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[21]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[20])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[25])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[27])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[28])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[193])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[29])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FillStyleTarget", new named_type(IFC2X3_types[569]), true));
        attributes.push_back(new attribute("GlobalOrLocal", new named_type(IFC2X3_types[397]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[30])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[31])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Item", new named_type(IFC2X3_types[392]), false));
        attributes.push_back(new attribute("TextureCoordinates", new named_type(IFC2X3_types[894]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[32])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[33])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[34])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[35])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ApplicationDeveloper", new named_type(IFC2X3_types[531]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("ApplicationFullName", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("ApplicationIdentifier", new named_type(IFC2X3_types[412]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[36])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("AppliedValue", new named_type(IFC2X3_types[39]), true));
        attributes.push_back(new attribute("UnitBasis", new named_type(IFC2X3_types[486]), true));
        attributes.push_back(new attribute("ApplicableDate", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("FixedUntilDate", new named_type(IFC2X3_types[206]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[37])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ComponentOfTotal", new named_type(IFC2X3_types[37]), false));
        attributes.push_back(new attribute("Components", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[37])), false));
        attributes.push_back(new attribute("ArithmeticOperator", new named_type(IFC2X3_types[48]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[38])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("ApprovalDateTime", new named_type(IFC2X3_types[206]), false));
        attributes.push_back(new attribute("ApprovalStatus", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ApprovalLevel", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ApprovalQualifier", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Identifier", new named_type(IFC2X3_types[412]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[40])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Actor", new named_type(IFC2X3_types[8]), false));
        attributes.push_back(new attribute("Approval", new named_type(IFC2X3_types[40]), false));
        attributes.push_back(new attribute("Role", new named_type(IFC2X3_types[7]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[41])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ApprovedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[615])), false));
        attributes.push_back(new attribute("Approval", new named_type(IFC2X3_types[40]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[42])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatedApproval", new named_type(IFC2X3_types[40]), false));
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC2X3_types[40]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[43])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OuterCurve", new named_type(IFC2X3_types[193]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[44])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Curve", new named_type(IFC2X3_types[75]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[45])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[193])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[46])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("AssetID", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC2X3_types[175]), false));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC2X3_types[175]), false));
        attributes.push_back(new attribute("TotalReplacementCost", new named_type(IFC2X3_types[175]), false));
        attributes.push_back(new attribute("Owner", new named_type(IFC2X3_types[8]), false));
        attributes.push_back(new attribute("User", new named_type(IFC2X3_types[8]), false));
        attributes.push_back(new attribute("ResponsiblePerson", new named_type(IFC2X3_types[545]), false));
        attributes.push_back(new attribute("IncorporationDate", new named_type(IFC2X3_types[97]), false));
        attributes.push_back(new attribute("DepreciatedValue", new named_type(IFC2X3_types[175]), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[50])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("TopFlangeWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("TopFlangeThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("TopFlangeFilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("CentreOfGravityInY", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[51])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC2X3_types[226]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[52])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RefDirection", new named_type(IFC2X3_types[226]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[54])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC2X3_types[226]), true));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC2X3_types[226]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[55])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Degree", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_types[98])), false));
        attributes.push_back(new attribute("CurveForm", new named_type(IFC2X3_types[81]), false));
        attributes.push_back(new attribute("ClosedCurve", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[80])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[56])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[58]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[57])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[60])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RasterFormat", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("RasterCode", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[61])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("ZLength", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[62])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[64]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[63])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[66])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Operator", new named_type(IFC2X3_types[68]), false));
        attributes.push_back(new attribute("FirstOperand", new named_type(IFC2X3_types[67]), false));
        attributes.push_back(new attribute("SecondOperand", new named_type(IFC2X3_types[67]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[69])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[70])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LinearStiffnessByLengthX", new named_type(IFC2X3_types[499]), true));
        attributes.push_back(new attribute("LinearStiffnessByLengthY", new named_type(IFC2X3_types[499]), true));
        attributes.push_back(new attribute("LinearStiffnessByLengthZ", new named_type(IFC2X3_types[499]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthX", new named_type(IFC2X3_types[500]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthY", new named_type(IFC2X3_types[500]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthZ", new named_type(IFC2X3_types[500]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[71])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("LinearStiffnessByAreaX", new named_type(IFC2X3_types[501]), true));
        attributes.push_back(new attribute("LinearStiffnessByAreaY", new named_type(IFC2X3_types[501]), true));
        attributes.push_back(new attribute("LinearStiffnessByAreaZ", new named_type(IFC2X3_types[501]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[72])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LinearStiffnessX", new named_type(IFC2X3_types[456]), true));
        attributes.push_back(new attribute("LinearStiffnessY", new named_type(IFC2X3_types[456]), true));
        attributes.push_back(new attribute("LinearStiffnessZ", new named_type(IFC2X3_types[456]), true));
        attributes.push_back(new attribute("RotationalStiffnessX", new named_type(IFC2X3_types[735]), true));
        attributes.push_back(new attribute("RotationalStiffnessY", new named_type(IFC2X3_types[735]), true));
        attributes.push_back(new attribute("RotationalStiffnessZ", new named_type(IFC2X3_types[735]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[73])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingStiffness", new named_type(IFC2X3_types[961]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[74])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[75])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[76])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Corner", new named_type(IFC2X3_types[98]), false));
        attributes.push_back(new attribute("XDim", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("ZDim", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[77])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Enclosure", new named_type(IFC2X3_types[77]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[79])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ElevationOfRefHeight", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("ElevationOfTerrain", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("BuildingAddress", new named_type(IFC2X3_types[580]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[82])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[83])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[84])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[85])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CompositionType", new named_type(IFC2X3_types[303]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[86])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[88]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[87])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[89])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elevation", new named_type(IFC2X3_types[435]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[90])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WallThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Girth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("InternalFilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("CentreOfGravityInX", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[186])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[92]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[91])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[94]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[93])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[96]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[95])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DayComponent", new named_type(IFC2X3_types[207]), false));
        attributes.push_back(new attribute("MonthComponent", new named_type(IFC2X3_types[507]), false));
        attributes.push_back(new attribute("YearComponent", new named_type(IFC2X3_types[977]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[97])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC2X3_types[435])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[98])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Axis1", new named_type(IFC2X3_types[226]), true));
        attributes.push_back(new attribute("Axis2", new named_type(IFC2X3_types[226]), true));
        attributes.push_back(new attribute("LocalOrigin", new named_type(IFC2X3_types[98]), false));
        attributes.push_back(new attribute("Scale", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[99])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[100])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Scale2", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[101])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis3", new named_type(IFC2X3_types[226]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[102])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Scale2", new simple_type(simple_type::real_type), true));
        attributes.push_back(new attribute("Scale3", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[103])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Thickness", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[104])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Width", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("Height", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[105])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[109]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[108])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[110])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[111])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Source", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Edition", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("EditionDate", new named_type(IFC2X3_types[97]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[113])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Notation", new named_type(IFC2X3_types[117]), false));
        attributes.push_back(new attribute("ItemOf", new named_type(IFC2X3_types[113]), true));
        attributes.push_back(new attribute("Title", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[114])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingItem", new named_type(IFC2X3_types[114]), false));
        attributes.push_back(new attribute("RelatedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[114])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[115])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("NotationFacets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[117])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[116])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("NotationValue", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[117])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ReferencedSource", new named_type(IFC2X3_types[113]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[119])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[120])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[122]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[121])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Red", new named_type(IFC2X3_types[512]), false));
        attributes.push_back(new attribute("Green", new named_type(IFC2X3_types[512]), false));
        attributes.push_back(new attribute("Blue", new named_type(IFC2X3_types[512]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[125])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[126])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[127])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[129]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[128])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[615])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[133])), false));
        attributes.push_back(new attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[132])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Transition", new named_type(IFC2X3_types[920]), false));
        attributes.push_back(new attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("ParentCurve", new named_type(IFC2X3_types[193]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[133])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC2X3_types[604])), false));
        attributes.push_back(new attribute("Label", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[137]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[136])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[139]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[138])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[140])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Criterion", new named_type(IFC2X3_types[142]), false));
        attributes.push_back(new attribute("CriterionDateTime", new named_type(IFC2X3_types[206]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[141])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[53]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[143])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[328])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[144])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CurveOnRelatingElement", new named_type(IFC2X3_types[196]), false));
        attributes.push_back(new attribute("CurveOnRelatedElement", new named_type(IFC2X3_types[196]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[145])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[146])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("EccentricityInX", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("EccentricityInY", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("EccentricityInZ", new named_type(IFC2X3_types[435]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[147])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PointOnRelatingElement", new named_type(IFC2X3_types[572]), false));
        attributes.push_back(new attribute("PointOnRelatedElement", new named_type(IFC2X3_types[572]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[148])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("LocationAtRelatingElement", new named_type(IFC2X3_types[53]), false));
        attributes.push_back(new attribute("LocationAtRelatedElement", new named_type(IFC2X3_types[53]), true));
        attributes.push_back(new attribute("ProfileOfPort", new named_type(IFC2X3_types[604]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[149])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceOnRelatingElement", new named_type(IFC2X3_types[848]), false));
        attributes.push_back(new attribute("SurfaceOnRelatedElement", new named_type(IFC2X3_types[848]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[150])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("ConstraintGrade", new named_type(IFC2X3_types[155]), false));
        attributes.push_back(new attribute("ConstraintSource", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("CreatingActor", new named_type(IFC2X3_types[8]), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("UserDefinedGrade", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[152])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC2X3_types[152]), false));
        attributes.push_back(new attribute("RelatedConstraints", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[152])), false));
        attributes.push_back(new attribute("LogicalAggregator", new named_type(IFC2X3_types[462]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[153])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ClassifiedConstraint", new named_type(IFC2X3_types[152]), false));
        attributes.push_back(new attribute("RelatedClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[118])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[154])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC2X3_types[152]), false));
        attributes.push_back(new attribute("RelatedConstraints", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[152])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[156])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[157])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Suppliers", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[8])), true));
        attributes.push_back(new attribute("UsageRatio", new named_type(IFC2X3_types[650]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[158])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[159])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ResourceIdentifier", new named_type(IFC2X3_types[412]), true));
        attributes.push_back(new attribute("ResourceGroup", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ResourceConsumption", new named_type(IFC2X3_types[723]), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC2X3_types[486]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[160])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[162])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[163])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[165]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[164])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("ConversionFactor", new named_type(IFC2X3_types[486]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[166])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[168]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[167])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[170]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[169])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("HourOffset", new named_type(IFC2X3_types[408]), false));
        attributes.push_back(new attribute("MinuteOffset", new named_type(IFC2X3_types[497]), true));
        attributes.push_back(new attribute("Sense", new named_type(IFC2X3_types[13]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[171])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[172])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("SubmittedBy", new named_type(IFC2X3_types[8]), true));
        attributes.push_back(new attribute("PreparedBy", new named_type(IFC2X3_types[8]), true));
        attributes.push_back(new attribute("SubmittedOn", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("TargetUsers", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[8])), true));
        attributes.push_back(new attribute("UpdateDate", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("ID", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[174]), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[173])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CostType", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Condition", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[175])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[179]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[177])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[179]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[178])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseWidth2", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("HeadWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("HeadDepth2", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("HeadDepth3", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseWidth4", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseDepth1", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseDepth2", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseDepth3", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("CentreOfGravityInY", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[180])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("HeadWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("HeadDepth2", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("HeadDepth3", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseDepth1", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BaseDepth2", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("CentreOfGravityInY", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[181])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[182])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[55]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[183])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TreeRootExpression", new named_type(IFC2X3_types[184]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[185])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingMonetaryUnit", new named_type(IFC2X3_types[506]), false));
        attributes.push_back(new attribute("RelatedMonetaryUnit", new named_type(IFC2X3_types[506]), false));
        attributes.push_back(new attribute("ExchangeRate", new named_type(IFC2X3_types[579]), false));
        attributes.push_back(new attribute("RateDateTime", new named_type(IFC2X3_types[205]), false));
        attributes.push_back(new attribute("RateSource", new named_type(IFC2X3_types[436]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[188])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[189])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[191]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[190])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[193])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC2X3_types[564]), false));
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC2X3_types[193])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[194])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("CurveFont", new named_type(IFC2X3_types[195]), true));
        attributes.push_back(new attribute("CurveWidth", new named_type(IFC2X3_types[767]), true));
        attributes.push_back(new attribute("CurveColour", new named_type(IFC2X3_types[123]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[197])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[200])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[198])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("CurveFont", new named_type(IFC2X3_types[201]), false));
        attributes.push_back(new attribute("CurveFontScaling", new named_type(IFC2X3_types[579]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[199])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VisibleSegmentLength", new named_type(IFC2X3_types[435]), false));
        attributes.push_back(new attribute("InvisibleSegmentLength", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[200])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[203]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[202])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DateComponent", new named_type(IFC2X3_types[97]), false));
        attributes.push_back(new attribute("TimeComponent", new named_type(IFC2X3_types[460]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[205])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Definition", new named_type(IFC2X3_types[210]), false));
        attributes.push_back(new attribute("Target", new named_type(IFC2X3_types[100]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[209])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ParentProfile", new named_type(IFC2X3_types[604]), false));
        attributes.push_back(new attribute("Operator", new named_type(IFC2X3_types[100]), false));
        attributes.push_back(new attribute("Label", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[212])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[214])), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC2X3_types[215]), false));
        attributes.push_back(new attribute("UserDefinedType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[213])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[511]), false));
        attributes.push_back(new attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[214])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[217])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[219])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[221])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[222])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Role", new named_type(IFC2X3_types[224]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[223])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[225])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("LengthExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("MassExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("TimeExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("ElectricCurrentExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("ThermodynamicTemperatureExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("AmountOfSubstanceExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new attribute("LuminousIntensityExponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[218])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new simple_type(simple_type::real_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[226])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[228])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[229])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[230])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[232]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[231])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ControlElementId", new named_type(IFC2X3_types[412]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[233])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[234])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[235])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[236])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[237])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[238])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FlowDirection", new named_type(IFC2X3_types[355]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[239])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("FileExtension", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("MimeContentType", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("MimeSubtype", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[241])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("DocumentId", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("DocumentReferences", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[244])), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("IntendedUse", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Scope", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Revision", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("DocumentOwner", new named_type(IFC2X3_types[8]), true));
        attributes.push_back(new attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[8])), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC2X3_types[205]), true));
        attributes.push_back(new attribute("LastRevisionTime", new named_type(IFC2X3_types[205]), true));
        attributes.push_back(new attribute("ElectronicFormat", new named_type(IFC2X3_types[241]), true));
        attributes.push_back(new attribute("ValidFrom", new named_type(IFC2X3_types[97]), true));
        attributes.push_back(new attribute("ValidUntil", new named_type(IFC2X3_types[97]), true));
        attributes.push_back(new attribute("Confidentiality", new named_type(IFC2X3_types[240]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC2X3_types[246]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[242])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC2X3_types[242]), false));
        attributes.push_back(new attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[242])), false));
        attributes.push_back(new attribute("RelationshipType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[243])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[244])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[247])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("ThresholdDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("ThresholdThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("TransomOffset", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("ThresholdOffset", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("CasingThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("CasingDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC2X3_types[755]), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[248])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PanelDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("PanelOperation", new named_type(IFC2X3_types[249]), false));
        attributes.push_back(new attribute("PanelWidth", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC2X3_types[250]), false));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC2X3_types[755]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[251])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("OperationType", new named_type(IFC2X3_types[254]), false));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC2X3_types[253]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("Sizeable", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[252])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Contents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[257])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[256])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("RelatingDraughtingCallout", new named_type(IFC2X3_types[256]), false));
        attributes.push_back(new attribute("RelatedDraughtingCallout", new named_type(IFC2X3_types[256]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[258])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[259])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[260])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[261])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[263]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[262])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[265]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[264])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[267]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[266])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeStart", new named_type(IFC2X3_types[946]), false));
        attributes.push_back(new attribute("EdgeEnd", new named_type(IFC2X3_types[946]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[269])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeGeometry", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[270])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FeatureLength", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[271])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[534])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[272])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[277]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[276])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DistributionPointFunction", new named_type(IFC2X3_types[284]), false));
        attributes.push_back(new attribute("UserDefinedFunction", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[283])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[286]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[285])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[288]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[287])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[290]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[289])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[292]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[291])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[295]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[294])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("ElectricCurrentType", new named_type(IFC2X3_types[281]), true));
        attributes.push_back(new attribute("InputVoltage", new named_type(IFC2X3_types[296]), false));
        attributes.push_back(new attribute("InputFrequency", new named_type(IFC2X3_types[379]), false));
        attributes.push_back(new attribute("FullLoadCurrent", new named_type(IFC2X3_types[282]), true));
        attributes.push_back(new attribute("MinimumCircuitCurrent", new named_type(IFC2X3_types[282]), true));
        attributes.push_back(new attribute("MaximumPowerInput", new named_type(IFC2X3_types[581]), true));
        attributes.push_back(new attribute("RatedPowerInput", new named_type(IFC2X3_types[581]), true));
        attributes.push_back(new attribute("InputPhase", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[273])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[274])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[275])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Tag", new named_type(IFC2X3_types[412]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[297])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC2X3_types[49]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[300]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[299])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[301])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[302])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MethodOfMeasurement", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[550])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[304])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[305])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[55]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[298])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[306])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[307])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[308])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[309])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EnergySequence", new named_type(IFC2X3_types[312]), true));
        attributes.push_back(new attribute("UserDefinedEnergySequence", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[311])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ImpactType", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Category", new named_type(IFC2X3_types[313]), false));
        attributes.push_back(new attribute("UserDefinedCategory", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[314])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[315])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[316])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[318]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[317])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[320]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[319])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ExtendedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[615])), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[321])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Location", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ItemReference", new named_type(IFC2X3_types[412]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[326])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[322])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[323])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[324])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[325])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC2X3_types[226]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[327])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[330])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[328])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[144])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[329])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Bound", new named_type(IFC2X3_types[463]), false));
        attributes.push_back(new attribute("Orientation", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[330])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[331])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FaceSurface", new named_type(IFC2X3_types[844]), false));
        attributes.push_back(new attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[332])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[333])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[120])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[334])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TensionFailureX", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("TensionFailureY", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("TensionFailureZ", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("CompressionFailureX", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("CompressionFailureY", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("CompressionFailureZ", new named_type(IFC2X3_types[378]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[335])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[337]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[336])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[338])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[339])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[340])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[341])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[342])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[348])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[343])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("HatchLineAppearance", new named_type(IFC2X3_types[197]), false));
        attributes.push_back(new attribute("StartOfNextHatchLine", new named_type(IFC2X3_types[403]), false));
        attributes.push_back(new attribute("PointOfReferenceHatchLine", new named_type(IFC2X3_types[98]), true));
        attributes.push_back(new attribute("PatternStart", new named_type(IFC2X3_types[98]), true));
        attributes.push_back(new attribute("HatchLineAngle", new named_type(IFC2X3_types[565]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[344])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Symbol", new named_type(IFC2X3_types[34]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[347])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TilingPattern", new named_type(IFC2X3_types[526]), false));
        attributes.push_back(new attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[346])), false));
        attributes.push_back(new attribute("TilingScale", new named_type(IFC2X3_types[579]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[345])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[350]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[349])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[352]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[351])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[353])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[354])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[356])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[357])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[359]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[358])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[361]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[360])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[362])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[363])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[364])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[365])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[366])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[367])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[368])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[369])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[370])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[371])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new attribute("PropertySource", new named_type(IFC2X3_types[627]), false));
        attributes.push_back(new attribute("FlowConditionTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("VelocityTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("FlowrateTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("Fluid", new named_type(IFC2X3_types[476]), false));
        attributes.push_back(new attribute("PressureTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("UserDefinedPropertySource", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("TemperatureSingleValue", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("WetBulbTemperatureSingleValue", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("WetBulbTemperatureTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("TemperatureTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("FlowrateSingleValue", new named_type(IFC2X3_types[211]), true));
        attributes.push_back(new attribute("FlowConditionSingleValue", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("VelocitySingleValue", new named_type(IFC2X3_types[457]), true));
        attributes.push_back(new attribute("PressureSingleValue", new named_type(IFC2X3_types[596]), true));
        std::vector<bool> derived; derived.reserve(19);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[372])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[377]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[376])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CombustionTemperature", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("CarbonContent", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("LowerHeatingValue", new named_type(IFC2X3_types[407]), true));
        attributes.push_back(new attribute("HigherHeatingValue", new named_type(IFC2X3_types[407]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[380])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[381])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[382])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[383])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC2X3_types[49]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[384])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[386]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[385])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MolecularWeight", new named_type(IFC2X3_types[503]), true));
        attributes.push_back(new attribute("Porosity", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("MassDensity", new named_type(IFC2X3_types[472]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[387])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PhysicalWeight", new named_type(IFC2X3_types[475]), true));
        attributes.push_back(new attribute("Perimeter", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("MinimumPlateThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("MaximumPlateThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC2X3_types[47]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[388])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[389])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CoordinateSpaceDimension", new named_type(IFC2X3_types[220]), false));
        attributes.push_back(new attribute("Precision", new simple_type(simple_type::real_type), true));
        attributes.push_back(new attribute("WorldCoordinateSystem", new named_type(IFC2X3_types[53]), false));
        attributes.push_back(new attribute("TrueNorth", new named_type(IFC2X3_types[226]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[391])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[392])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ParentContext", new named_type(IFC2X3_types[391]), false));
        attributes.push_back(new attribute("TargetScale", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("TargetView", new named_type(IFC2X3_types[390]), false));
        attributes.push_back(new attribute("UserDefinedTargetView", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[393])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[395])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[394])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[399])), false));
        attributes.push_back(new attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[399])), false));
        attributes.push_back(new attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[399])), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[398])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("AxisTag", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("AxisCurve", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC2X3_types[65]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[399])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementLocation", new named_type(IFC2X3_types[953]), false));
        attributes.push_back(new attribute("PlacementRefDirection", new named_type(IFC2X3_types[953]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[400])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[401])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseSurface", new named_type(IFC2X3_types[844]), false));
        attributes.push_back(new attribute("AgreementFlag", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[402])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[405]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[404])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[410]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[409])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("UpperVaporResistanceFactor", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("LowerVaporResistanceFactor", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("IsothermalMoistureCapacity", new named_type(IFC2X3_types[425]), true));
        attributes.push_back(new attribute("VaporPermeability", new named_type(IFC2X3_types[943]), true));
        attributes.push_back(new attribute("MoistureDiffusivity", new named_type(IFC2X3_types[502]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[411])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[424])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("UrlReference", new named_type(IFC2X3_types[412]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[414])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("InventoryType", new named_type(IFC2X3_types[420]), false));
        attributes.push_back(new attribute("Jurisdiction", new named_type(IFC2X3_types[8]), false));
        attributes.push_back(new attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[545])), false));
        attributes.push_back(new attribute("LastUpdateDate", new named_type(IFC2X3_types[97]), false));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC2X3_types[175]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC2X3_types[175]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[419])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[423])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[422])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStamp", new named_type(IFC2X3_types[206]), false));
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[423])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[427]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[426])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("Thickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("LegSlope", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("CentreOfGravityInX", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("CentreOfGravityInY", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[464])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SkillSet", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[430])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[432]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[431])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Publisher", new named_type(IFC2X3_types[531]), true));
        attributes.push_back(new attribute("VersionDate", new named_type(IFC2X3_types[97]), true));
        attributes.push_back(new attribute("LibraryReference", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[437])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[436])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[437])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MainPlaneAngle", new named_type(IFC2X3_types[565]), false));
        attributes.push_back(new attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[565])), false));
        attributes.push_back(new attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[466])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[440])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[444]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[443])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LightDistributionCurve", new named_type(IFC2X3_types[439]), false));
        attributes.push_back(new attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[440])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[445])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("LightColour", new named_type(IFC2X3_types[125]), false));
        attributes.push_back(new attribute("AmbientIntensity", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("Intensity", new named_type(IFC2X3_types[512]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[446])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[447])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Orientation", new named_type(IFC2X3_types[226]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[448])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[55]), false));
        attributes.push_back(new attribute("ColourAppearance", new named_type(IFC2X3_types[125]), true));
        attributes.push_back(new attribute("ColourTemperature", new named_type(IFC2X3_types[906]), false));
        attributes.push_back(new attribute("LuminousFlux", new named_type(IFC2X3_types[465]), false));
        attributes.push_back(new attribute("LightEmissionSource", new named_type(IFC2X3_types[442]), false));
        attributes.push_back(new attribute("LightDistributionDataSource", new named_type(IFC2X3_types[441]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[449])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[98]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("ConstantAttenuation", new named_type(IFC2X3_types[652]), false));
        attributes.push_back(new attribute("DistanceAttenuation", new named_type(IFC2X3_types[652]), false));
        attributes.push_back(new attribute("QuadricAttenuation", new named_type(IFC2X3_types[652]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[450])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Orientation", new named_type(IFC2X3_types[226]), false));
        attributes.push_back(new attribute("ConcentrationExponent", new named_type(IFC2X3_types[652]), true));
        attributes.push_back(new attribute("SpreadAngle", new named_type(IFC2X3_types[578]), false));
        attributes.push_back(new attribute("BeamWidthAngle", new named_type(IFC2X3_types[578]), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[451])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Pnt", new named_type(IFC2X3_types[98]), false));
        attributes.push_back(new attribute("Dir", new named_type(IFC2X3_types[944]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[452])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[453])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementRelTo", new named_type(IFC2X3_types[519]), true));
        attributes.push_back(new attribute("RelativePlacement", new named_type(IFC2X3_types[53]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[459])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("HourComponent", new named_type(IFC2X3_types[408]), false));
        attributes.push_back(new attribute("MinuteComponent", new named_type(IFC2X3_types[497]), true));
        attributes.push_back(new attribute("SecondComponent", new named_type(IFC2X3_types[741]), true));
        attributes.push_back(new attribute("Zone", new named_type(IFC2X3_types[171]), true));
        attributes.push_back(new attribute("DaylightSavingOffset", new named_type(IFC2X3_types[208]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[460])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[463])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Outer", new named_type(IFC2X3_types[120]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[470])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingSource", new named_type(IFC2X3_types[721]), false));
        attributes.push_back(new attribute("MappingTarget", new named_type(IFC2X3_types[99]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[471])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[476])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[118])), false));
        attributes.push_back(new attribute("ClassifiedMaterial", new named_type(IFC2X3_types[476]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[477])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RepresentedMaterial", new named_type(IFC2X3_types[476]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[478])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Material", new named_type(IFC2X3_types[476]), true));
        attributes.push_back(new attribute("LayerThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("IsVentilated", new named_type(IFC2X3_types[461]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[479])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[479])), false));
        attributes.push_back(new attribute("LayerSetName", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[480])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ForLayerSet", new named_type(IFC2X3_types[480]), false));
        attributes.push_back(new attribute("LayerSetDirection", new named_type(IFC2X3_types[434]), false));
        attributes.push_back(new attribute("DirectionSense", new named_type(IFC2X3_types[227]), false));
        attributes.push_back(new attribute("OffsetFromReferenceLine", new named_type(IFC2X3_types[435]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[481])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[476])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[482])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Material", new named_type(IFC2X3_types[476]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[483])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ValueComponent", new named_type(IFC2X3_types[940]), false));
        attributes.push_back(new attribute("UnitComponent", new named_type(IFC2X3_types[934]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[486])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("CompressiveStrength", new named_type(IFC2X3_types[596]), true));
        attributes.push_back(new attribute("MaxAggregateSize", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("AdmixturesDescription", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Workability", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("ProtectivePoreRatio", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("WaterImpermeability", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[487])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[488])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[489])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("DynamicViscosity", new named_type(IFC2X3_types[268]), true));
        attributes.push_back(new attribute("YoungModulus", new named_type(IFC2X3_types[498]), true));
        attributes.push_back(new attribute("ShearModulus", new named_type(IFC2X3_types[498]), true));
        attributes.push_back(new attribute("PoissonRatio", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("ThermalExpansionCoefficient", new named_type(IFC2X3_types[900]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[490])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("YieldStress", new named_type(IFC2X3_types[596]), true));
        attributes.push_back(new attribute("UltimateStress", new named_type(IFC2X3_types[596]), true));
        attributes.push_back(new attribute("UltimateStrain", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("HardeningModule", new named_type(IFC2X3_types[498]), true));
        attributes.push_back(new attribute("ProportionalStress", new named_type(IFC2X3_types[596]), true));
        attributes.push_back(new attribute("PlasticStrain", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("Relaxations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[687])), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[491])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[492])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[494]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[493])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Benchmark", new named_type(IFC2X3_types[59]), false));
        attributes.push_back(new attribute("ValueSource", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("DataValue", new named_type(IFC2X3_types[496]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[495])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Currency", new named_type(IFC2X3_types[187]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[506])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[509]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[508])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MoveFrom", new named_type(IFC2X3_types[786]), false));
        attributes.push_back(new attribute("MoveTo", new named_type(IFC2X3_types[786]), false));
        attributes.push_back(new attribute("PunchList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[879])), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[510])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Dimensions", new named_type(IFC2X3_types[218]), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC2X3_types[938]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[511])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[515])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[516])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[519])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BenchmarkValues", new named_type(IFC2X3_types[495]), true));
        attributes.push_back(new attribute("ResultValues", new named_type(IFC2X3_types[495]), true));
        attributes.push_back(new attribute("ObjectiveQualifier", new named_type(IFC2X3_types[518]), false));
        attributes.push_back(new attribute("UserDefinedQualifier", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[517])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[523]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[522])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("Distance", new named_type(IFC2X3_types[435]), false));
        attributes.push_back(new attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[524])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("Distance", new named_type(IFC2X3_types[435]), false));
        attributes.push_back(new attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC2X3_types[226]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[525])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RepeatFactor", new named_type(IFC2X3_types[944]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[526])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[528])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[527])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("VisibleTransmittance", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("SolarTransmittance", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("ThermalIrTransmittance", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("ThermalIrEmissivityBack", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("ThermalIrEmissivityFront", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("VisibleReflectanceBack", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("VisibleReflectanceFront", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("SolarReflectanceFront", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("SolarReflectanceBack", new named_type(IFC2X3_types[579]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[529])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ActionID", new named_type(IFC2X3_types[412]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[530])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Id", new named_type(IFC2X3_types[412]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[11])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[531])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("RelatingOrganization", new named_type(IFC2X3_types[531]), false));
        attributes.push_back(new attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[531])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[532])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeElement", new named_type(IFC2X3_types[269]), false));
        attributes.push_back(new attribute("Orientation", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[534])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[536]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[535])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("OwningUser", new named_type(IFC2X3_types[546]), false));
        attributes.push_back(new attribute("OwningApplication", new named_type(IFC2X3_types[36]), false));
        attributes.push_back(new attribute("State", new named_type(IFC2X3_types[800]), true));
        attributes.push_back(new attribute("ChangeAction", new named_type(IFC2X3_types[106]), false));
        attributes.push_back(new attribute("LastModifiedDate", new named_type(IFC2X3_types[914]), true));
        attributes.push_back(new attribute("LastModifyingUser", new named_type(IFC2X3_types[546]), true));
        attributes.push_back(new attribute("LastModifyingApplication", new named_type(IFC2X3_types[36]), true));
        attributes.push_back(new attribute("CreationDate", new named_type(IFC2X3_types[914]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[537])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[54]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[538])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[534])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[540])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LifeCyclePhase", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[541])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC2X3_types[542]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC2X3_types[968]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC2X3_types[755]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[543])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PermitID", new named_type(IFC2X3_types[412]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[544])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Id", new named_type(IFC2X3_types[412]), true));
        attributes.push_back(new attribute("FamilyName", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("GivenName", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[11])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[545])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ThePerson", new named_type(IFC2X3_types[545]), false));
        attributes.push_back(new attribute("TheOrganization", new named_type(IFC2X3_types[531]), false));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[7])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[546])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[550])), false));
        attributes.push_back(new attribute("Discrimination", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Quality", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Usage", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[548])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[550])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[511]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[551])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[554]), false));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC2X3_types[553]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[552])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[556]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[555])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[558]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[557])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Width", new named_type(IFC2X3_types[416]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC2X3_types[416]), false));
        attributes.push_back(new attribute("ColourComponents", new named_type(IFC2X3_types[416]), false));
        attributes.push_back(new attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::binary_type)), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[559])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Location", new named_type(IFC2X3_types[98]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[560])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Placement", new named_type(IFC2X3_types[53]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[561])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SizeInX", new named_type(IFC2X3_types[435]), false));
        attributes.push_back(new attribute("SizeInY", new named_type(IFC2X3_types[435]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[562])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[564])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[566])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[568]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[567])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[569])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("PointParameter", new named_type(IFC2X3_types[539]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[570])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC2X3_types[844]), false));
        attributes.push_back(new attribute("PointParameterU", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("PointParameterV", new named_type(IFC2X3_types[539]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[571])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC2X3_types[98])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[575])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[55]), false));
        attributes.push_back(new attribute("PolygonalBoundary", new named_type(IFC2X3_types[75]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[573])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_types[98])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[574])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[576])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("InternalLocation", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("PostalBox", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Town", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Region", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("PostalCode", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Country", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[580])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[582])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[583])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[584])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[585])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[586])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[587])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[588])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[589])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[433])), false));
        attributes.push_back(new attribute("Identifier", new named_type(IFC2X3_types[412]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[591])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("LayerOn", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new attribute("LayerFrozen", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new attribute("LayerBlocked", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC2X3_types[595])), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[592])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[593])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[595])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[594])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ProcedureID", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("ProcedureType", new named_type(IFC2X3_types[598]), false));
        attributes.push_back(new attribute("UserDefinedProcedureType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[597])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[599])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ObjectPlacement", new named_type(IFC2X3_types[519]), true));
        attributes.push_back(new attribute("Representation", new named_type(IFC2X3_types[602]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[600])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[601])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[718])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[602])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("SpecificHeatCapacity", new named_type(IFC2X3_types[788]), true));
        attributes.push_back(new attribute("N20Content", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("COContent", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("CO2Content", new named_type(IFC2X3_types[579]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[603])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProfileType", new named_type(IFC2X3_types[606]), false));
        attributes.push_back(new attribute("ProfileName", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[604])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProfileName", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ProfileDefinition", new named_type(IFC2X3_types[604]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[605])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("LongName", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Phase", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[719])), false));
        attributes.push_back(new attribute("UnitsInContext", new named_type(IFC2X3_types[937]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[607])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ID", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[614]), false));
        attributes.push_back(new attribute("Status", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[611])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Records", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[675])), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[613]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[612])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[609])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[610])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[615])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("UpperBoundValue", new named_type(IFC2X3_types[940]), true));
        attributes.push_back(new attribute("LowerBoundValue", new named_type(IFC2X3_types[940]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[934]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[616])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC2X3_types[152]), false));
        attributes.push_back(new attribute("RelatedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[615])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[617])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[618])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("DependingProperty", new named_type(IFC2X3_types[615]), false));
        attributes.push_back(new attribute("DependantProperty", new named_type(IFC2X3_types[615]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[619])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        attributes.push_back(new attribute("EnumerationReference", new named_type(IFC2X3_types[621]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[620])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[934]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[621])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[934]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[622])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("PropertyReference", new named_type(IFC2X3_types[520]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[623])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[615])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[624])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[625])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("NominalValue", new named_type(IFC2X3_types[940]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[934]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[626])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        attributes.push_back(new attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("DefiningUnit", new named_type(IFC2X3_types[934]), true));
        attributes.push_back(new attribute("DefinedUnit", new named_type(IFC2X3_types[934]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[628])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[630]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[629])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProxyType", new named_type(IFC2X3_types[521]), false));
        attributes.push_back(new attribute("Tag", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[631])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[633]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[632])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AreaValue", new named_type(IFC2X3_types[47]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[634])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CountValue", new named_type(IFC2X3_types[176]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[635])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LengthValue", new named_type(IFC2X3_types[435]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[636])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TimeValue", new named_type(IFC2X3_types[907]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[637])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("VolumeValue", new named_type(IFC2X3_types[954]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[638])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightValue", new named_type(IFC2X3_types[474]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[639])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[641])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[644]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[642])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[644]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[643])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ShapeType", new named_type(IFC2X3_types[649]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[645])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[646])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[648]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[647])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new simple_type(simple_type::real_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[651])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("InnerFilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("OuterFilletRadius", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[653])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("XDim", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[654])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[655])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC2X3_types[844]), false));
        attributes.push_back(new attribute("U1", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("V1", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("U2", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("V2", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("Usense", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("Vsense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[656])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ReferencedDocument", new named_type(IFC2X3_types[245]), false));
        attributes.push_back(new attribute("ReferencingValues", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[37])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[657])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStep", new named_type(IFC2X3_types[907]), false));
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[913])), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[659])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TotalCrossSectionArea", new named_type(IFC2X3_types[47]), false));
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC2X3_types[664]), true));
        attributes.push_back(new attribute("EffectiveDepth", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("NominalBarDiameter", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("BarCount", new named_type(IFC2X3_types[176]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[660])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DefinitionType", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[746])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[661])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC2X3_types[47]), false));
        attributes.push_back(new attribute("BarLength", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("BarRole", new named_type(IFC2X3_types[663]), false));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC2X3_types[664]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[662])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[665])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("MeshLength", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC2X3_types[47]), false));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC2X3_types[47]), false));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[666])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[667])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[516])), false));
        attributes.push_back(new attribute("RelatedObjectsType", new named_type(IFC2X3_types[521]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[668])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TimeForTask", new named_type(IFC2X3_types[740]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[669])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingActor", new named_type(IFC2X3_types[6]), false));
        attributes.push_back(new attribute("ActingRole", new named_type(IFC2X3_types[7]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[670])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingControl", new named_type(IFC2X3_types[163]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[671])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingGroup", new named_type(IFC2X3_types[401]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[672])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC2X3_types[599]), false));
        attributes.push_back(new attribute("QuantityInProcess", new named_type(IFC2X3_types[486]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[673])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingProduct", new named_type(IFC2X3_types[600]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[674])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[675])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingResource", new named_type(IFC2X3_types[722]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[676])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[732])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[677])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingAppliedValue", new named_type(IFC2X3_types[37]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[678])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC2X3_types[40]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[679])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingClassification", new named_type(IFC2X3_types[118]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[680])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Intent", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC2X3_types[152]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[681])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC2X3_types[245]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[682])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingLibrary", new named_type(IFC2X3_types[438]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[683])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC2X3_types[484]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[684])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingProfileProperties", new named_type(IFC2X3_types[605]), false));
        attributes.push_back(new attribute("ProfileSectionLocation", new named_type(IFC2X3_types[755]), true));
        attributes.push_back(new attribute("ProfileOrientation", new named_type(IFC2X3_types[533]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[685])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[688])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC2X3_types[146]), true));
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC2X3_types[297]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC2X3_types[297]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[689])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new simple_type(simple_type::integer_type)), false));
        attributes.push_back(new attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new simple_type(simple_type::integer_type)), false));
        attributes.push_back(new attribute("RelatedConnectionType", new named_type(IFC2X3_types[151]), false));
        attributes.push_back(new attribute("RelatingConnectionType", new named_type(IFC2X3_types[151]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[690])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC2X3_types[576]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC2X3_types[297]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[692])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC2X3_types[576]), false));
        attributes.push_back(new attribute("RelatedPort", new named_type(IFC2X3_types[576]), false));
        attributes.push_back(new attribute("RealizingElement", new named_type(IFC2X3_types[297]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[691])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC2X3_types[803]), false));
        attributes.push_back(new attribute("RelatedStructuralActivity", new named_type(IFC2X3_types[802]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[693])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC2X3_types[297]), false));
        attributes.push_back(new attribute("RelatedStructuralMember", new named_type(IFC2X3_types[824]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[694])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("RelatingStructuralMember", new named_type(IFC2X3_types[824]), false));
        attributes.push_back(new attribute("RelatedStructuralConnection", new named_type(IFC2X3_types[805]), false));
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC2X3_types[70]), true));
        attributes.push_back(new attribute("AdditionalConditions", new named_type(IFC2X3_types[806]), true));
        attributes.push_back(new attribute("SupportedLength", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC2X3_types[55]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[695])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConnectionConstraint", new named_type(IFC2X3_types[146]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[696])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[297])), false));
        attributes.push_back(new attribute("ConnectionType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[697])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[600])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC2X3_types[786]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[698])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC2X3_types[297]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[177])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[699])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedSpace", new named_type(IFC2X3_types[779]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[177])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[700])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC2X3_types[516]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[516])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[701])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[515])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[702])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingPropertyDefinition", new named_type(IFC2X3_types[625]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[703])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingType", new named_type(IFC2X3_types[932]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[704])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOpeningElement", new named_type(IFC2X3_types[527]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC2X3_types[297]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[705])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[233])), false));
        attributes.push_back(new attribute("RelatingFlowElement", new named_type(IFC2X3_types[237]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[706])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("DailyInteraction", new named_type(IFC2X3_types[176]), true));
        attributes.push_back(new attribute("ImportanceRating", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("LocationOfInteraction", new named_type(IFC2X3_types[786]), true));
        attributes.push_back(new attribute("RelatedSpaceProgram", new named_type(IFC2X3_types[782]), false));
        attributes.push_back(new attribute("RelatingSpaceProgram", new named_type(IFC2X3_types[782]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[707])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[708])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[709])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OverridingProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[615])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[710])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC2X3_types[297]), false));
        attributes.push_back(new attribute("RelatedFeatureElement", new named_type(IFC2X3_types[341]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[711])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[600])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC2X3_types[786]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[712])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[713])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC2X3_types[599]), false));
        attributes.push_back(new attribute("RelatedProcess", new named_type(IFC2X3_types[599]), false));
        attributes.push_back(new attribute("TimeLag", new named_type(IFC2X3_types[907]), false));
        attributes.push_back(new attribute("SequenceType", new named_type(IFC2X3_types[750]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[714])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSystem", new named_type(IFC2X3_types[866]), false));
        attributes.push_back(new attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[786])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[715])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC2X3_types[779]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC2X3_types[297]), true));
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC2X3_types[146]), true));
        attributes.push_back(new attribute("PhysicalOrVirtualBoundary", new named_type(IFC2X3_types[549]), false));
        attributes.push_back(new attribute("InternalOrExternalBoundary", new named_type(IFC2X3_types[418]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[716])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC2X3_types[297]), false));
        attributes.push_back(new attribute("RelatedOpeningElement", new named_type(IFC2X3_types[342]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[717])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[686])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelaxationValue", new named_type(IFC2X3_types[512]), false));
        attributes.push_back(new attribute("InitialStress", new named_type(IFC2X3_types[512]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[687])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ContextOfItems", new named_type(IFC2X3_types[719]), false));
        attributes.push_back(new attribute("RepresentationIdentifier", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("RepresentationType", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[720])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[718])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ContextIdentifier", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ContextType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[719])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[720])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingOrigin", new named_type(IFC2X3_types[53]), false));
        attributes.push_back(new attribute("MappedRepresentation", new named_type(IFC2X3_types[718]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[721])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[722])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC2X3_types[52]), false));
        attributes.push_back(new attribute("Angle", new named_type(IFC2X3_types[565]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[724])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Thickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("RibHeight", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("RibWidth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("RibSpacing", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("Direction", new named_type(IFC2X3_types[725]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[726])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("BottomRadius", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[727])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[728])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ShapeType", new named_type(IFC2X3_types[731]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[730])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("GlobalId", new named_type(IFC2X3_types[396]), false));
        attributes.push_back(new attribute("OwnerHistory", new named_type(IFC2X3_types[537]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[732])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[736])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RoundingRadius", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[737])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Prefix", new named_type(IFC2X3_types[763]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[766]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[765])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[739]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[738])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(18);
        attributes.push_back(new attribute("ActualStart", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("EarlyStart", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("LateStart", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("EarlyFinish", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("LateFinish", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("ScheduleDuration", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("ActualDuration", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("RemainingTime", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("FreeFloat", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("IsCritical", new simple_type(simple_type::boolean_type), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("StartFloat", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("FinishFloat", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC2X3_types[579]), true));
        std::vector<bool> derived; derived.reserve(23);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[740])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SectionType", new named_type(IFC2X3_types[747]), false));
        attributes.push_back(new attribute("StartProfile", new named_type(IFC2X3_types[604]), false));
        attributes.push_back(new attribute("EndProfile", new named_type(IFC2X3_types[604]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[745])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LongitudinalStartPosition", new named_type(IFC2X3_types[435]), false));
        attributes.push_back(new attribute("LongitudinalEndPosition", new named_type(IFC2X3_types[435]), false));
        attributes.push_back(new attribute("TransversePosition", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("ReinforcementRole", new named_type(IFC2X3_types[663]), false));
        attributes.push_back(new attribute("SectionDefinition", new named_type(IFC2X3_types[745]), false));
        attributes.push_back(new attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[660])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[746])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SpineCurve", new named_type(IFC2X3_types[132]), false));
        attributes.push_back(new attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_types[604])), false));
        attributes.push_back(new attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_types[55])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[743])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[749]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[748])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ServiceLifeType", new named_type(IFC2X3_types[754]), false));
        attributes.push_back(new attribute("ServiceLifeDuration", new named_type(IFC2X3_types[907]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[751])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[753]), false));
        attributes.push_back(new attribute("UpperValue", new named_type(IFC2X3_types[485]), true));
        attributes.push_back(new attribute("MostUsedValue", new named_type(IFC2X3_types[485]), false));
        attributes.push_back(new attribute("LowerValue", new named_type(IFC2X3_types[485]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[752])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[756])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("ProductDefinitional", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new attribute("PartOfProductDefinitionShape", new named_type(IFC2X3_types[601]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[755])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[756])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[757])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[759])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[760])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[761])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RefLatitude", new named_type(IFC2X3_types[135]), true));
        attributes.push_back(new attribute("RefLongitude", new named_type(IFC2X3_types[135]), true));
        attributes.push_back(new attribute("RefElevation", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("LandTitleNumber", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("SiteAddress", new named_type(IFC2X3_types[580]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[764])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[770]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[768])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[770]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[769])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SlippageX", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("SlippageY", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("SlippageZ", new named_type(IFC2X3_types[435]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[771])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[773])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("IsAttenuating", new named_type(IFC2X3_types[65]), false));
        attributes.push_back(new attribute("SoundScale", new named_type(IFC2X3_types[777]), true));
        attributes.push_back(new attribute("SoundValues", new aggregation_type(aggregation_type::list_type, 1, 8, new named_type(IFC2X3_types[778])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[776])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SoundLevelTimeSeries", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("Frequency", new named_type(IFC2X3_types[379]), false));
        attributes.push_back(new attribute("SoundLevelSingleValue", new named_type(IFC2X3_types[211]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[778])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("InteriorOrExteriorSpace", new named_type(IFC2X3_types[418]), false));
        attributes.push_back(new attribute("ElevationWithFlooring", new named_type(IFC2X3_types[435]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[779])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[781]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[780])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("SpaceProgramIdentifier", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("MaxRequiredArea", new named_type(IFC2X3_types[47]), true));
        attributes.push_back(new attribute("MinRequiredArea", new named_type(IFC2X3_types[47]), true));
        attributes.push_back(new attribute("RequestedLocation", new named_type(IFC2X3_types[786]), true));
        attributes.push_back(new attribute("StandardRequiredArea", new named_type(IFC2X3_types[47]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[782])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new attribute("ApplicableValueRatio", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("ThermalLoadSource", new named_type(IFC2X3_types[901]), false));
        attributes.push_back(new attribute("PropertySource", new named_type(IFC2X3_types[627]), false));
        attributes.push_back(new attribute("SourceDescription", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("MaximumValue", new named_type(IFC2X3_types[581]), false));
        attributes.push_back(new attribute("MinimumValue", new named_type(IFC2X3_types[581]), true));
        attributes.push_back(new attribute("ThermalLoadTimeSeriesValues", new named_type(IFC2X3_types[908]), true));
        attributes.push_back(new attribute("UserDefinedThermalLoadSource", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("UserDefinedPropertySource", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ThermalLoadType", new named_type(IFC2X3_types[902]), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[783])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[785]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[784])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LongName", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("CompositionType", new named_type(IFC2X3_types[303]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[786])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[787])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[792])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[794]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[793])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ShapeType", new named_type(IFC2X3_types[799]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[795])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("NumberOfRiser", new simple_type(simple_type::integer_type), true));
        attributes.push_back(new attribute("NumberOfTreads", new simple_type(simple_type::integer_type), true));
        attributes.push_back(new attribute("RiserHeight", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("TreadLength", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[796])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[798]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[797])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DestabilizingLoad", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("CausedBy", new named_type(IFC2X3_types[831]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[801])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AppliedLoad", new named_type(IFC2X3_types[814]), false));
        attributes.push_back(new attribute("GlobalOrLocal", new named_type(IFC2X3_types[397]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[802])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[23]), false));
        attributes.push_back(new attribute("OrientationOf2DPlane", new named_type(IFC2X3_types[55]), true));
        attributes.push_back(new attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[815])), true));
        attributes.push_back(new attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[832])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[804])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC2X3_types[70]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[805])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[806])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[807])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[810]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[808])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[809])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[811])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC2X3_types[608]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[812])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VaryingAppliedLoadLocation", new named_type(IFC2X3_types[755]), false));
        attributes.push_back(new attribute("SubsequentAppliedLoads", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[814])), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[813])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[814])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[458]), false));
        attributes.push_back(new attribute("ActionType", new named_type(IFC2X3_types[5]), false));
        attributes.push_back(new attribute("ActionSource", new named_type(IFC2X3_types[4]), false));
        attributes.push_back(new attribute("Coefficient", new named_type(IFC2X3_types[650]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[815])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LinearForceX", new named_type(IFC2X3_types[454]), true));
        attributes.push_back(new attribute("LinearForceY", new named_type(IFC2X3_types[454]), true));
        attributes.push_back(new attribute("LinearForceZ", new named_type(IFC2X3_types[454]), true));
        attributes.push_back(new attribute("LinearMomentX", new named_type(IFC2X3_types[455]), true));
        attributes.push_back(new attribute("LinearMomentY", new named_type(IFC2X3_types[455]), true));
        attributes.push_back(new attribute("LinearMomentZ", new named_type(IFC2X3_types[455]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[816])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PlanarForceX", new named_type(IFC2X3_types[563]), true));
        attributes.push_back(new attribute("PlanarForceY", new named_type(IFC2X3_types[563]), true));
        attributes.push_back(new attribute("PlanarForceZ", new named_type(IFC2X3_types[563]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[817])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DisplacementX", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("DisplacementY", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("DisplacementZ", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("RotationalDisplacementRX", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("RotationalDisplacementRY", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("RotationalDisplacementRZ", new named_type(IFC2X3_types[565]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[818])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Distortion", new named_type(IFC2X3_types[192]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[819])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("ForceX", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("ForceY", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("ForceZ", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("MomentX", new named_type(IFC2X3_types[917]), true));
        attributes.push_back(new attribute("MomentY", new named_type(IFC2X3_types[917]), true));
        attributes.push_back(new attribute("MomentZ", new named_type(IFC2X3_types[917]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[820])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingMoment", new named_type(IFC2X3_types[961]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[821])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[822])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DeltaT_Constant", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("DeltaT_Y", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("DeltaT_Z", new named_type(IFC2X3_types[906]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[823])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[824])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC2X3_types[608]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[825])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VaryingAppliedLoadLocation", new named_type(IFC2X3_types[755]), false));
        attributes.push_back(new attribute("SubsequentAppliedLoads", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_types[814])), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[826])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[827])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[828])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[829])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(16);
        attributes.push_back(new attribute("TorsionalConstantX", new named_type(IFC2X3_types[504]), true));
        attributes.push_back(new attribute("MomentOfInertiaYZ", new named_type(IFC2X3_types[504]), true));
        attributes.push_back(new attribute("MomentOfInertiaY", new named_type(IFC2X3_types[504]), true));
        attributes.push_back(new attribute("MomentOfInertiaZ", new named_type(IFC2X3_types[504]), true));
        attributes.push_back(new attribute("WarpingConstant", new named_type(IFC2X3_types[960]), true));
        attributes.push_back(new attribute("ShearCentreZ", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("ShearCentreY", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("ShearDeformationAreaZ", new named_type(IFC2X3_types[47]), true));
        attributes.push_back(new attribute("ShearDeformationAreaY", new named_type(IFC2X3_types[47]), true));
        attributes.push_back(new attribute("MaximumSectionModulusY", new named_type(IFC2X3_types[744]), true));
        attributes.push_back(new attribute("MinimumSectionModulusY", new named_type(IFC2X3_types[744]), true));
        attributes.push_back(new attribute("MaximumSectionModulusZ", new named_type(IFC2X3_types[744]), true));
        attributes.push_back(new attribute("MinimumSectionModulusZ", new named_type(IFC2X3_types[744]), true));
        attributes.push_back(new attribute("TorsionalSectionModulus", new named_type(IFC2X3_types[744]), true));
        attributes.push_back(new attribute("CentreOfGravityInX", new named_type(IFC2X3_types[435]), true));
        attributes.push_back(new attribute("CentreOfGravityInY", new named_type(IFC2X3_types[435]), true));
        std::vector<bool> derived; derived.reserve(23);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[830])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[831])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TheoryType", new named_type(IFC2X3_types[24]), false));
        attributes.push_back(new attribute("ResultForLoadGroup", new named_type(IFC2X3_types[815]), true));
        attributes.push_back(new attribute("IsLinear", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[832])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ShearAreaZ", new named_type(IFC2X3_types[47]), true));
        attributes.push_back(new attribute("ShearAreaY", new named_type(IFC2X3_types[47]), true));
        attributes.push_back(new attribute("PlasticShapeFactorY", new named_type(IFC2X3_types[579]), true));
        attributes.push_back(new attribute("PlasticShapeFactorZ", new named_type(IFC2X3_types[579]), true));
        std::vector<bool> derived; derived.reserve(27);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[833])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[834])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[837]), false));
        attributes.push_back(new attribute("Thickness", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[835])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SubsequentThickness", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC2X3_types[577])), false));
        attributes.push_back(new attribute("VaryingThicknessLocation", new named_type(IFC2X3_types[755]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[836])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[838])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[841])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Item", new named_type(IFC2X3_types[720]), true));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[594])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[839])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[840])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SubContractor", new named_type(IFC2X3_types[8]), true));
        attributes.push_back(new attribute("JobDescription", new named_type(IFC2X3_types[879]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[842])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentEdge", new named_type(IFC2X3_types[269]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[843])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[844])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("EndParam", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("ReferenceSurface", new named_type(IFC2X3_types[844]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[845])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC2X3_types[226]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[435]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[846])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AxisPosition", new named_type(IFC2X3_types[52]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[847])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Side", new named_type(IFC2X3_types[849]), false));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC2X3_types[851])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[850])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC2X3_types[125]), false));
        attributes.push_back(new attribute("DiffuseReflectionColour", new named_type(IFC2X3_types[125]), false));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC2X3_types[125]), false));
        attributes.push_back(new attribute("ReflectanceColour", new named_type(IFC2X3_types[125]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[852])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RefractionIndex", new named_type(IFC2X3_types[652]), true));
        attributes.push_back(new attribute("DispersionFactor", new named_type(IFC2X3_types[652]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[853])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Transparency", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("DiffuseColour", new named_type(IFC2X3_types[124]), true));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC2X3_types[124]), true));
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC2X3_types[124]), true));
        attributes.push_back(new attribute("ReflectionColour", new named_type(IFC2X3_types[124]), true));
        attributes.push_back(new attribute("SpecularColour", new named_type(IFC2X3_types[124]), true));
        attributes.push_back(new attribute("SpecularHighlight", new named_type(IFC2X3_types[790]), true));
        attributes.push_back(new attribute("ReflectanceMethod", new named_type(IFC2X3_types[658]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[854])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SurfaceColour", new named_type(IFC2X3_types[125]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[855])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[857])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[856])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RepeatS", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("RepeatT", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("TextureType", new named_type(IFC2X3_types[858]), false));
        attributes.push_back(new attribute("TextureTransform", new named_type(IFC2X3_types[100]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[857])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptArea", new named_type(IFC2X3_types[604]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[55]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[859])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Directrix", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("InnerRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("StartParam", new named_type(IFC2X3_types[539]), false));
        attributes.push_back(new attribute("EndParam", new named_type(IFC2X3_types[539]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[860])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptCurve", new named_type(IFC2X3_types[604]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC2X3_types[55]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[861])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[863]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[862])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("StyleOfSymbol", new named_type(IFC2X3_types[865]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[864])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[866])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[867])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("WebEdgeRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("WebSlope", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("CentreOfGravityInY", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[928])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new simple_type(simple_type::string_type), false));
        attributes.push_back(new attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[869])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[868])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        attributes.push_back(new attribute("IsHeading", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[869])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[871]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[870])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("TaskId", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("Status", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("IsMilestone", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("Priority", new simple_type(simple_type::integer_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[872])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("PagerNumber", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[429])), true));
        attributes.push_back(new attribute("WWWHomePageURL", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[873])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[877]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC2X3_types[47]), false));
        attributes.push_back(new attribute("TensionForce", new named_type(IFC2X3_types[378]), true));
        attributes.push_back(new attribute("PreStress", new named_type(IFC2X3_types[596]), true));
        attributes.push_back(new attribute("FrictionCoefficient", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("AnchorageSlip", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("MinCurvatureRadius", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[875])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[876])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AnnotatedCurve", new named_type(IFC2X3_types[28]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[878])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Literal", new named_type(IFC2X3_types[590]), false));
        attributes.push_back(new attribute("Placement", new named_type(IFC2X3_types[53]), false));
        attributes.push_back(new attribute("Path", new named_type(IFC2X3_types[886]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[884])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Extent", new named_type(IFC2X3_types[562]), false));
        attributes.push_back(new attribute("BoxAlignment", new named_type(IFC2X3_types[78]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[885])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TextCharacterAppearance", new named_type(IFC2X3_types[107]), true));
        attributes.push_back(new attribute("TextStyle", new named_type(IFC2X3_types[890]), true));
        attributes.push_back(new attribute("TextFontStyle", new named_type(IFC2X3_types[883]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[887])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[882])), true));
        attributes.push_back(new attribute("FontStyle", new named_type(IFC2X3_types[373]), true));
        attributes.push_back(new attribute("FontVariant", new named_type(IFC2X3_types[374]), true));
        attributes.push_back(new attribute("FontWeight", new named_type(IFC2X3_types[375]), true));
        attributes.push_back(new attribute("FontSize", new named_type(IFC2X3_types[767]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[888])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Colour", new named_type(IFC2X3_types[123]), false));
        attributes.push_back(new attribute("BackgroundColour", new named_type(IFC2X3_types[123]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[889])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("TextIndent", new named_type(IFC2X3_types[767]), true));
        attributes.push_back(new attribute("TextAlign", new named_type(IFC2X3_types[880]), true));
        attributes.push_back(new attribute("TextDecoration", new named_type(IFC2X3_types[881]), true));
        attributes.push_back(new attribute("LetterSpacing", new named_type(IFC2X3_types[767]), true));
        attributes.push_back(new attribute("WordSpacing", new named_type(IFC2X3_types[767]), true));
        attributes.push_back(new attribute("TextTransform", new named_type(IFC2X3_types[893]), true));
        attributes.push_back(new attribute("LineHeight", new named_type(IFC2X3_types[767]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[891])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("BoxHeight", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("BoxWidth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("BoxSlantAngle", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("BoxRotateAngle", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("CharacterSpacing", new named_type(IFC2X3_types[767]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[892])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[894])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Mode", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[762])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[895])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TextureMaps", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[947])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[896])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC2X3_types[539])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[897])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("SpecificHeatCapacity", new named_type(IFC2X3_types[788]), true));
        attributes.push_back(new attribute("BoilingPoint", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("FreezingPoint", new named_type(IFC2X3_types[906]), true));
        attributes.push_back(new attribute("ThermalConductivity", new named_type(IFC2X3_types[899]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[903])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Name", new named_type(IFC2X3_types[429]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC2X3_types[879]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC2X3_types[206]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC2X3_types[206]), false));
        attributes.push_back(new attribute("TimeSeriesDataType", new named_type(IFC2X3_types[909]), false));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC2X3_types[204]), false));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC2X3_types[934]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[908])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ReferencedTimeSeries", new named_type(IFC2X3_types[908]), false));
        attributes.push_back(new attribute("TimeSeriesReferences", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[245])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[910])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ApplicableDates", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[206])), true));
        attributes.push_back(new attribute("TimeSeriesScheduleType", new named_type(IFC2X3_types[912]), false));
        attributes.push_back(new attribute("TimeSeries", new named_type(IFC2X3_types[908]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[911])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[940])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[913])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[915])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[916])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[919]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[918])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("OperationType", new named_type(IFC2X3_types[923]), true));
        attributes.push_back(new attribute("CapacityByWeight", new named_type(IFC2X3_types[474]), true));
        attributes.push_back(new attribute("CapacityByNumber", new named_type(IFC2X3_types[176]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[921])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[923]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[922])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BottomXDim", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("TopXDim", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("TopXOffset", new named_type(IFC2X3_types[435]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[924])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC2X3_types[193]), false));
        attributes.push_back(new attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC2X3_types[927])), false));
        attributes.push_back(new attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC2X3_types[927])), false));
        attributes.push_back(new attribute("SenseAgreement", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC2X3_types[926]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[925])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[930]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[929])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SecondRepeatFactor", new named_type(IFC2X3_types[944]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[931])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ApplicableOccurrence", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[625])), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[932])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC2X3_types[721])), true));
        attributes.push_back(new attribute("Tag", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[933])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC2X3_types[565]), true));
        attributes.push_back(new attribute("CentreOfGravityInX", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[939])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[934])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[937])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[936]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[935])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[942]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[941])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Orientation", new named_type(IFC2X3_types[226]), false));
        attributes.push_back(new attribute("Magnitude", new named_type(IFC2X3_types[435]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[944])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC2X3_types[946])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TextureVertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC2X3_types[897])), false));
        attributes.push_back(new attribute("TexturePoints", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC2X3_types[98])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[947])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LoopVertex", new named_type(IFC2X3_types[946]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[948])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("VertexGeometry", new named_type(IFC2X3_types[569]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC2X3_types[949])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[951]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[950])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[952])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC2X3_types[399])), false));
        attributes.push_back(new attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC2X3_types[435])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[953])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[956])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[957])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[959]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[958])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC2X3_types[963]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[962])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("IsPotable", new simple_type(simple_type::boolean_type), true));
        attributes.push_back(new attribute("Hardness", new named_type(IFC2X3_types[421]), true));
        attributes.push_back(new attribute("AlkalinityConcentration", new named_type(IFC2X3_types[421]), true));
        attributes.push_back(new attribute("AcidityConcentration", new named_type(IFC2X3_types[421]), true));
        attributes.push_back(new attribute("ImpuritiesContent", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("PHLevel", new named_type(IFC2X3_types[547]), true));
        attributes.push_back(new attribute("DissolvedSolidsContent", new named_type(IFC2X3_types[512]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[964])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[965])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("MullionThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("FirstTransomOffset", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("SecondTransomOffset", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("FirstMullionOffset", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("SecondMullionOffset", new named_type(IFC2X3_types[512]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC2X3_types[755]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[966])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC2X3_types[967]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC2X3_types[968]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC2X3_types[755]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[969])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC2X3_types[971]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC2X3_types[972]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new attribute("Sizeable", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[970])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new attribute("Identifier", new named_type(IFC2X3_types[412]), false));
        attributes.push_back(new attribute("CreationDate", new named_type(IFC2X3_types[206]), false));
        attributes.push_back(new attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC2X3_types[545])), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC2X3_types[429]), true));
        attributes.push_back(new attribute("Duration", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC2X3_types[907]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC2X3_types[206]), false));
        attributes.push_back(new attribute("FinishTime", new named_type(IFC2X3_types[206]), true));
        attributes.push_back(new attribute("WorkControlType", new named_type(IFC2X3_types[974]), true));
        attributes.push_back(new attribute("UserDefinedControlType", new named_type(IFC2X3_types[429]), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[973])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[975])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[976])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC2X3_types[577]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC2X3_types[577]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC2X3_types[577]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[979])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC2X3_types[978])->set_attributes(attributes, derived);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsActingUpon", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[670]), ((entity*) IFC2X3_types[670])->attributes()[0]));
        ((entity*) IFC2X3_types[6])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("OfPerson", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[545]), ((entity*) IFC2X3_types[545])->attributes()[7]));
        attributes.push_back(new inverse_attribute("OfOrganization", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[531]), ((entity*) IFC2X3_types[531])->attributes()[4]));
        ((entity*) IFC2X3_types[11])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[698]), ((entity*) IFC2X3_types[698])->attributes()[0]));
        ((entity*) IFC2X3_types[27])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ValuesReferenced", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[657]), ((entity*) IFC2X3_types[657])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ValueOfComponents", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[38]), ((entity*) IFC2X3_types[38])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsComponentIn", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[38]), ((entity*) IFC2X3_types[38])->attributes()[1]));
        ((entity*) IFC2X3_types[37])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("Actors", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[41]), ((entity*) IFC2X3_types[41])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[43]), ((entity*) IFC2X3_types[43])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[43]), ((entity*) IFC2X3_types[43])->attributes()[1]));
        ((entity*) IFC2X3_types[40])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Contains", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[114]), ((entity*) IFC2X3_types[114])->attributes()[1]));
        ((entity*) IFC2X3_types[113])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsClassifiedItemIn", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[115]), ((entity*) IFC2X3_types[115])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsClassifyingItemIn", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[115]), ((entity*) IFC2X3_types[115])->attributes()[0]));
        ((entity*) IFC2X3_types[114])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("UsingCurves", inverse_attribute::set_type, 1, -1, ((entity*) IFC2X3_types[132]), ((entity*) IFC2X3_types[132])->attributes()[0]));
        ((entity*) IFC2X3_types[133])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new inverse_attribute("ClassifiedAs", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[154]), ((entity*) IFC2X3_types[154])->attributes()[0]));
        attributes.push_back(new inverse_attribute("RelatesConstraints", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[156]), ((entity*) IFC2X3_types[156])->attributes()[2]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[156]), ((entity*) IFC2X3_types[156])->attributes()[3]));
        attributes.push_back(new inverse_attribute("PropertiesForConstraint", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[617]), ((entity*) IFC2X3_types[617])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Aggregates", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[153]), ((entity*) IFC2X3_types[153])->attributes()[2]));
        attributes.push_back(new inverse_attribute("IsAggregatedIn", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[153]), ((entity*) IFC2X3_types[153])->attributes()[3]));
        ((entity*) IFC2X3_types[152])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Controls", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[671]), ((entity*) IFC2X3_types[671])->attributes()[0]));
        ((entity*) IFC2X3_types[163])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("CoversSpaces", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[700]), ((entity*) IFC2X3_types[700])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Covers", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[699]), ((entity*) IFC2X3_types[699])->attributes()[1]));
        ((entity*) IFC2X3_types[177])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AnnotatedBySymbols", inverse_attribute::set_type, 0, 2, ((entity*) IFC2X3_types[878]), ((entity*) IFC2X3_types[878])->attributes()[0]));
        ((entity*) IFC2X3_types[221])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToFlowElement", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[706]), ((entity*) IFC2X3_types[706])->attributes()[0]));
        ((entity*) IFC2X3_types[233])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasControlElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[706]), ((entity*) IFC2X3_types[706])->attributes()[1]));
        ((entity*) IFC2X3_types[237])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsPointedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[243]), ((entity*) IFC2X3_types[243])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointer", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[243]), ((entity*) IFC2X3_types[243])->attributes()[0]));
        ((entity*) IFC2X3_types[242])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferenceToDocument", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[242]), ((entity*) IFC2X3_types[242])->attributes()[3]));
        ((entity*) IFC2X3_types[244])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsRelatedFromCallout", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[258]), ((entity*) IFC2X3_types[258])->attributes()[3]));
        attributes.push_back(new inverse_attribute("IsRelatedToCallout", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[258]), ((entity*) IFC2X3_types[258])->attributes()[2]));
        ((entity*) IFC2X3_types[256])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new inverse_attribute("HasStructuralMember", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[694]), ((entity*) IFC2X3_types[694])->attributes()[0]));
        attributes.push_back(new inverse_attribute("FillsVoids", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[705]), ((entity*) IFC2X3_types[705])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[689]), ((entity*) IFC2X3_types[689])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[699]), ((entity*) IFC2X3_types[699])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasProjections", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[711]), ((entity*) IFC2X3_types[711])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedInStructures", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[712]), ((entity*) IFC2X3_types[712])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasPorts", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[692]), ((entity*) IFC2X3_types[692])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasOpenings", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[717]), ((entity*) IFC2X3_types[717])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsConnectionRealization", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[697]), ((entity*) IFC2X3_types[697])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ProvidesBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[716]), ((entity*) IFC2X3_types[716])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[689]), ((entity*) IFC2X3_types[689])->attributes()[2]));
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[698]), ((entity*) IFC2X3_types[698])->attributes()[0]));
        ((entity*) IFC2X3_types[297])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ProjectsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[711]), ((entity*) IFC2X3_types[711])->attributes()[1]));
        ((entity*) IFC2X3_types[341])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("VoidsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[717]), ((entity*) IFC2X3_types[717])->attributes()[1]));
        ((entity*) IFC2X3_types[342])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasSubContexts", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[393]), ((entity*) IFC2X3_types[393])->attributes()[0]));
        ((entity*) IFC2X3_types[391])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[698]), ((entity*) IFC2X3_types[698])->attributes()[0]));
        ((entity*) IFC2X3_types[398])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("PartOfW", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[398]), ((entity*) IFC2X3_types[398])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfV", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[398]), ((entity*) IFC2X3_types[398])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfU", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[398]), ((entity*) IFC2X3_types[398])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasIntersections", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[953]), ((entity*) IFC2X3_types[953])->attributes()[0]));
        ((entity*) IFC2X3_types[399])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsGroupedBy", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[672]), ((entity*) IFC2X3_types[672])->attributes()[0]));
        ((entity*) IFC2X3_types[401])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferenceIntoLibrary", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[436]), ((entity*) IFC2X3_types[436])->attributes()[4]));
        ((entity*) IFC2X3_types[437])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasRepresentation", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[478]), ((entity*) IFC2X3_types[478])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ClassifiedAs", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[477]), ((entity*) IFC2X3_types[477])->attributes()[1]));
        ((entity*) IFC2X3_types[476])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialLayerSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[480]), ((entity*) IFC2X3_types[480])->attributes()[0]));
        ((entity*) IFC2X3_types[479])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[702]), ((entity*) IFC2X3_types[702])->attributes()[0]));
        ((entity*) IFC2X3_types[515])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("HasAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[668]), ((entity*) IFC2X3_types[668])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsDecomposedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[701]), ((entity*) IFC2X3_types[701])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Decomposes", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[701]), ((entity*) IFC2X3_types[701])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[677]), ((entity*) IFC2X3_types[677])->attributes()[0]));
        ((entity*) IFC2X3_types[516])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PlacesObject", inverse_attribute::set_type, 1, 1, ((entity*) IFC2X3_types[600]), ((entity*) IFC2X3_types[600])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedByPlacements", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[459]), ((entity*) IFC2X3_types[459])->attributes()[0]));
        ((entity*) IFC2X3_types[519])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasFillings", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[705]), ((entity*) IFC2X3_types[705])->attributes()[0]));
        ((entity*) IFC2X3_types[527])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsRelatedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[532]), ((entity*) IFC2X3_types[532])->attributes()[3]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[532]), ((entity*) IFC2X3_types[532])->attributes()[2]));
        attributes.push_back(new inverse_attribute("Engages", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[546]), ((entity*) IFC2X3_types[546])->attributes()[1]));
        ((entity*) IFC2X3_types[531])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("EngagedIn", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[546]), ((entity*) IFC2X3_types[546])->attributes()[0]));
        ((entity*) IFC2X3_types[545])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[548]), ((entity*) IFC2X3_types[548])->attributes()[0]));
        ((entity*) IFC2X3_types[550])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainedIn", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[692]), ((entity*) IFC2X3_types[692])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[691]), ((entity*) IFC2X3_types[691])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[691]), ((entity*) IFC2X3_types[691])->attributes()[0]));
        ((entity*) IFC2X3_types[576])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[673]), ((entity*) IFC2X3_types[673])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsSuccessorFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[714]), ((entity*) IFC2X3_types[714])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPredecessorTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[714]), ((entity*) IFC2X3_types[714])->attributes()[0]));
        ((entity*) IFC2X3_types[599])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[674]), ((entity*) IFC2X3_types[674])->attributes()[0]));
        ((entity*) IFC2X3_types[600])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ShapeOfProduct", inverse_attribute::set_type, 1, 1, ((entity*) IFC2X3_types[600]), ((entity*) IFC2X3_types[600])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[755]), ((entity*) IFC2X3_types[755])->attributes()[4]));
        ((entity*) IFC2X3_types[601])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("PropertyForDependance", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[619]), ((entity*) IFC2X3_types[619])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyDependsOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[619]), ((entity*) IFC2X3_types[619])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[131]), ((entity*) IFC2X3_types[131])->attributes()[1]));
        ((entity*) IFC2X3_types[615])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[677]), ((entity*) IFC2X3_types[677])->attributes()[0]));
        ((entity*) IFC2X3_types[618])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PropertyDefinitionOf", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[703]), ((entity*) IFC2X3_types[703])->attributes()[0]));
        attributes.push_back(new inverse_attribute("DefinesType", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[932]), ((entity*) IFC2X3_types[932])->attributes()[1]));
        ((entity*) IFC2X3_types[625])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("RepresentationMap", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[721]), ((entity*) IFC2X3_types[721])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LayerAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[591]), ((entity*) IFC2X3_types[591])->attributes()[2]));
        attributes.push_back(new inverse_attribute("OfProductRepresentation", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[602]), ((entity*) IFC2X3_types[602])->attributes()[2]));
        ((entity*) IFC2X3_types[718])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("RepresentationsInContext", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[718]), ((entity*) IFC2X3_types[718])->attributes()[0]));
        ((entity*) IFC2X3_types[719])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LayerAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[591]), ((entity*) IFC2X3_types[591])->attributes()[2]));
        attributes.push_back(new inverse_attribute("StyledByItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[839]), ((entity*) IFC2X3_types[839])->attributes()[0]));
        ((entity*) IFC2X3_types[720])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("MapUsage", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[471]), ((entity*) IFC2X3_types[471])->attributes()[0]));
        ((entity*) IFC2X3_types[721])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[676]), ((entity*) IFC2X3_types[676])->attributes()[0]));
        ((entity*) IFC2X3_types[722])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ScheduleTimeControlAssigned", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[669]), ((entity*) IFC2X3_types[669])->attributes()[0]));
        ((entity*) IFC2X3_types[740])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OfShapeAspect", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[755]), ((entity*) IFC2X3_types[755])->attributes()[0]));
        ((entity*) IFC2X3_types[756])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[700]), ((entity*) IFC2X3_types[700])->attributes()[0]));
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[716]), ((entity*) IFC2X3_types[716])->attributes()[0]));
        ((entity*) IFC2X3_types[779])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasInteractionReqsFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[707]), ((entity*) IFC2X3_types[707])->attributes()[3]));
        attributes.push_back(new inverse_attribute("HasInteractionReqsTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[707]), ((entity*) IFC2X3_types[707])->attributes()[4]));
        ((entity*) IFC2X3_types[782])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ReferencesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[712]), ((entity*) IFC2X3_types[712])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ServicedBySystems", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[715]), ((entity*) IFC2X3_types[715])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ContainsElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[698]), ((entity*) IFC2X3_types[698])->attributes()[1]));
        ((entity*) IFC2X3_types[786])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToStructuralItem", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[693]), ((entity*) IFC2X3_types[693])->attributes()[1]));
        ((entity*) IFC2X3_types[802])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectsStructuralMembers", inverse_attribute::set_type, 1, -1, ((entity*) IFC2X3_types[695]), ((entity*) IFC2X3_types[695])->attributes()[1]));
        ((entity*) IFC2X3_types[805])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedStructuralActivity", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[693]), ((entity*) IFC2X3_types[693])->attributes()[0]));
        ((entity*) IFC2X3_types[811])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("SourceOfResultGroup", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[832]), ((entity*) IFC2X3_types[832])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LoadGroupFor", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[804]), ((entity*) IFC2X3_types[804])->attributes()[2]));
        ((entity*) IFC2X3_types[815])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ReferencesElement", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[694]), ((entity*) IFC2X3_types[694])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[695]), ((entity*) IFC2X3_types[695])->attributes()[0]));
        ((entity*) IFC2X3_types[824])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Causes", inverse_attribute::set_type, 0, -1, ((entity*) IFC2X3_types[801]), ((entity*) IFC2X3_types[801])->attributes()[1]));
        ((entity*) IFC2X3_types[831])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResultGroupFor", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[804]), ((entity*) IFC2X3_types[804])->attributes()[3]));
        ((entity*) IFC2X3_types[832])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ServicesBuildings", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[715]), ((entity*) IFC2X3_types[715])->attributes()[0]));
        ((entity*) IFC2X3_types[866])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OfTable", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC2X3_types[868]), ((entity*) IFC2X3_types[868])->attributes()[1]));
        ((entity*) IFC2X3_types[869])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AnnotatedSurface", inverse_attribute::set_type, 1, 1, ((entity*) IFC2X3_types[32]), ((entity*) IFC2X3_types[32])->attributes()[1]));
        ((entity*) IFC2X3_types[894])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("DocumentedBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[910]), ((entity*) IFC2X3_types[910])->attributes()[0]));
        ((entity*) IFC2X3_types[908])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ObjectTypeOf", inverse_attribute::set_type, 0, 1, ((entity*) IFC2X3_types[704]), ((entity*) IFC2X3_types[704])->attributes()[0]));
        ((entity*) IFC2X3_types[932])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[0]));
        ((entity*) IFC2X3_types[132])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(15);
        defs.push_back(((entity*) IFC2X3_types[3]));defs.push_back(((entity*) IFC2X3_types[141]));defs.push_back(((entity*) IFC2X3_types[172]));defs.push_back(((entity*) IFC2X3_types[173]));defs.push_back(((entity*) IFC2X3_types[316]));defs.push_back(((entity*) IFC2X3_types[383]));defs.push_back(((entity*) IFC2X3_types[541]));defs.push_back(((entity*) IFC2X3_types[544]));defs.push_back(((entity*) IFC2X3_types[611]));defs.push_back(((entity*) IFC2X3_types[612]));defs.push_back(((entity*) IFC2X3_types[740]));defs.push_back(((entity*) IFC2X3_types[751]));defs.push_back(((entity*) IFC2X3_types[782]));defs.push_back(((entity*) IFC2X3_types[911]));defs.push_back(((entity*) IFC2X3_types[973]));
        ((entity*) IFC2X3_types[163])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC2X3_types[6]));defs.push_back(((entity*) IFC2X3_types[163]));defs.push_back(((entity*) IFC2X3_types[401]));defs.push_back(((entity*) IFC2X3_types[599]));defs.push_back(((entity*) IFC2X3_types[600]));defs.push_back(((entity*) IFC2X3_types[607]));defs.push_back(((entity*) IFC2X3_types[722]));
        ((entity*) IFC2X3_types[515])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[9]));defs.push_back(((entity*) IFC2X3_types[20]));defs.push_back(((entity*) IFC2X3_types[164]));defs.push_back(((entity*) IFC2X3_types[358]));defs.push_back(((entity*) IFC2X3_types[748]));
        ((entity*) IFC2X3_types[234])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC2X3_types[14]));defs.push_back(((entity*) IFC2X3_types[202]));defs.push_back(((entity*) IFC2X3_types[294]));defs.push_back(((entity*) IFC2X3_types[360]));defs.push_back(((entity*) IFC2X3_types[629]));defs.push_back(((entity*) IFC2X3_types[862]));defs.push_back(((entity*) IFC2X3_types[941]));
        ((entity*) IFC2X3_types[354])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(11);
        defs.push_back(((entity*) IFC2X3_types[16]));defs.push_back(((entity*) IFC2X3_types[276]));defs.push_back(((entity*) IFC2X3_types[289]));defs.push_back(((entity*) IFC2X3_types[351]));defs.push_back(((entity*) IFC2X3_types[385]));defs.push_back(((entity*) IFC2X3_types[431]));defs.push_back(((entity*) IFC2X3_types[443]));defs.push_back(((entity*) IFC2X3_types[535]));defs.push_back(((entity*) IFC2X3_types[738]));defs.push_back(((entity*) IFC2X3_types[793]));defs.push_back(((entity*) IFC2X3_types[962]));
        ((entity*) IFC2X3_types[369])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(18);
        defs.push_back(((entity*) IFC2X3_types[18]));defs.push_back(((entity*) IFC2X3_types[63]));defs.push_back(((entity*) IFC2X3_types[108]));defs.push_back(((entity*) IFC2X3_types[121]));defs.push_back(((entity*) IFC2X3_types[138]));defs.push_back(((entity*) IFC2X3_types[167]));defs.push_back(((entity*) IFC2X3_types[169]));defs.push_back(((entity*) IFC2X3_types[287]));defs.push_back(((entity*) IFC2X3_types[291]));defs.push_back(((entity*) IFC2X3_types[317]));defs.push_back(((entity*) IFC2X3_types[319]));defs.push_back(((entity*) IFC2X3_types[404]));defs.push_back(((entity*) IFC2X3_types[409]));defs.push_back(((entity*) IFC2X3_types[508]));defs.push_back(((entity*) IFC2X3_types[780]));defs.push_back(((entity*) IFC2X3_types[918]));defs.push_back(((entity*) IFC2X3_types[929]));defs.push_back(((entity*) IFC2X3_types[935]));
        ((entity*) IFC2X3_types[309])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[25]));defs.push_back(((entity*) IFC2X3_types[217]));defs.push_back(((entity*) IFC2X3_types[453]));defs.push_back(((entity*) IFC2X3_types[641]));
        ((entity*) IFC2X3_types[222])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC2X3_types[27]));defs.push_back(((entity*) IFC2X3_types[297]));defs.push_back(((entity*) IFC2X3_types[398]));defs.push_back(((entity*) IFC2X3_types[576]));defs.push_back(((entity*) IFC2X3_types[631]));defs.push_back(((entity*) IFC2X3_types[786]));defs.push_back(((entity*) IFC2X3_types[802]));defs.push_back(((entity*) IFC2X3_types[811]));
        ((entity*) IFC2X3_types[600])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[28]));defs.push_back(((entity*) IFC2X3_types[30]));defs.push_back(((entity*) IFC2X3_types[33]));defs.push_back(((entity*) IFC2X3_types[34]));defs.push_back(((entity*) IFC2X3_types[35]));
        ((entity*) IFC2X3_types[31])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(28);
        defs.push_back(((entity*) IFC2X3_types[29]));defs.push_back(((entity*) IFC2X3_types[32]));defs.push_back(((entity*) IFC2X3_types[69]));defs.push_back(((entity*) IFC2X3_types[77]));defs.push_back(((entity*) IFC2X3_types[99]));defs.push_back(((entity*) IFC2X3_types[133]));defs.push_back(((entity*) IFC2X3_types[183]));defs.push_back(((entity*) IFC2X3_types[193]));defs.push_back(((entity*) IFC2X3_types[209]));defs.push_back(((entity*) IFC2X3_types[226]));defs.push_back(((entity*) IFC2X3_types[256]));defs.push_back(((entity*) IFC2X3_types[329]));defs.push_back(((entity*) IFC2X3_types[344]));defs.push_back(((entity*) IFC2X3_types[347]));defs.push_back(((entity*) IFC2X3_types[345]));defs.push_back(((entity*) IFC2X3_types[394]));defs.push_back(((entity*) IFC2X3_types[402]));defs.push_back(((entity*) IFC2X3_types[446]));defs.push_back(((entity*) IFC2X3_types[526]));defs.push_back(((entity*) IFC2X3_types[560]));defs.push_back(((entity*) IFC2X3_types[562]));defs.push_back(((entity*) IFC2X3_types[569]));defs.push_back(((entity*) IFC2X3_types[743]));defs.push_back(((entity*) IFC2X3_types[760]));defs.push_back(((entity*) IFC2X3_types[773]));defs.push_back(((entity*) IFC2X3_types[844]));defs.push_back(((entity*) IFC2X3_types[884]));defs.push_back(((entity*) IFC2X3_types[944]));
        ((entity*) IFC2X3_types[392])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[31]));
        ((entity*) IFC2X3_types[839])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[44]));defs.push_back(((entity*) IFC2X3_types[45]));defs.push_back(((entity*) IFC2X3_types[134]));defs.push_back(((entity*) IFC2X3_types[212]));defs.push_back(((entity*) IFC2X3_types[538]));
        ((entity*) IFC2X3_types[604])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[46]));
        ((entity*) IFC2X3_types[44])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC2X3_types[50]));defs.push_back(((entity*) IFC2X3_types[140]));defs.push_back(((entity*) IFC2X3_types[419]));defs.push_back(((entity*) IFC2X3_types[815]));defs.push_back(((entity*) IFC2X3_types[832]));defs.push_back(((entity*) IFC2X3_types[866]));defs.push_back(((entity*) IFC2X3_types[978]));
        ((entity*) IFC2X3_types[401])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[51]));
        ((entity*) IFC2X3_types[424])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[52]));defs.push_back(((entity*) IFC2X3_types[54]));defs.push_back(((entity*) IFC2X3_types[55]));
        ((entity*) IFC2X3_types[560])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[80]));defs.push_back(((entity*) IFC2X3_types[132]));defs.push_back(((entity*) IFC2X3_types[574]));defs.push_back(((entity*) IFC2X3_types[925]));
        ((entity*) IFC2X3_types[75])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC2X3_types[56]));defs.push_back(((entity*) IFC2X3_types[84]));defs.push_back(((entity*) IFC2X3_types[86]));defs.push_back(((entity*) IFC2X3_types[127]));defs.push_back(((entity*) IFC2X3_types[177]));defs.push_back(((entity*) IFC2X3_types[189]));defs.push_back(((entity*) IFC2X3_types[247]));defs.push_back(((entity*) IFC2X3_types[376]));defs.push_back(((entity*) IFC2X3_types[492]));defs.push_back(((entity*) IFC2X3_types[552]));defs.push_back(((entity*) IFC2X3_types[566]));defs.push_back(((entity*) IFC2X3_types[642]));defs.push_back(((entity*) IFC2X3_types[645]));defs.push_back(((entity*) IFC2X3_types[646]));defs.push_back(((entity*) IFC2X3_types[730]));defs.push_back(((entity*) IFC2X3_types[768]));defs.push_back(((entity*) IFC2X3_types[795]));defs.push_back(((entity*) IFC2X3_types[796]));defs.push_back(((entity*) IFC2X3_types[956]));defs.push_back(((entity*) IFC2X3_types[965]));
        ((entity*) IFC2X3_types[83])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(12);
        defs.push_back(((entity*) IFC2X3_types[57]));defs.push_back(((entity*) IFC2X3_types[87]));defs.push_back(((entity*) IFC2X3_types[128]));defs.push_back(((entity*) IFC2X3_types[178]));defs.push_back(((entity*) IFC2X3_types[190]));defs.push_back(((entity*) IFC2X3_types[493]));defs.push_back(((entity*) IFC2X3_types[567]));defs.push_back(((entity*) IFC2X3_types[643]));defs.push_back(((entity*) IFC2X3_types[647]));defs.push_back(((entity*) IFC2X3_types[769]));defs.push_back(((entity*) IFC2X3_types[797]));defs.push_back(((entity*) IFC2X3_types[958]));
        ((entity*) IFC2X3_types[89])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[60]));
        ((entity*) IFC2X3_types[80])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[61]));defs.push_back(((entity*) IFC2X3_types[414]));defs.push_back(((entity*) IFC2X3_types[559]));
        ((entity*) IFC2X3_types[857])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[62]));defs.push_back(((entity*) IFC2X3_types[655]));defs.push_back(((entity*) IFC2X3_types[727]));defs.push_back(((entity*) IFC2X3_types[728]));defs.push_back(((entity*) IFC2X3_types[792]));
        ((entity*) IFC2X3_types[183])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[66]));
        ((entity*) IFC2X3_types[69])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[71]));defs.push_back(((entity*) IFC2X3_types[72]));defs.push_back(((entity*) IFC2X3_types[73]));
        ((entity*) IFC2X3_types[70])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[74]));
        ((entity*) IFC2X3_types[73])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[75]));defs.push_back(((entity*) IFC2X3_types[143]));defs.push_back(((entity*) IFC2X3_types[452]));defs.push_back(((entity*) IFC2X3_types[524]));defs.push_back(((entity*) IFC2X3_types[525]));
        ((entity*) IFC2X3_types[193])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[76]));defs.push_back(((entity*) IFC2X3_types[298]));defs.push_back(((entity*) IFC2X3_types[861]));
        ((entity*) IFC2X3_types[844])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[79]));defs.push_back(((entity*) IFC2X3_types[573]));
        ((entity*) IFC2X3_types[402])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[82]));defs.push_back(((entity*) IFC2X3_types[90]));defs.push_back(((entity*) IFC2X3_types[764]));defs.push_back(((entity*) IFC2X3_types[779]));
        ((entity*) IFC2X3_types[786])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(10);
        defs.push_back(((entity*) IFC2X3_types[83]));defs.push_back(((entity*) IFC2X3_types[235]));defs.push_back(((entity*) IFC2X3_types[275]));defs.push_back(((entity*) IFC2X3_types[299]));defs.push_back(((entity*) IFC2X3_types[301]));defs.push_back(((entity*) IFC2X3_types[315]));defs.push_back(((entity*) IFC2X3_types[340]));defs.push_back(((entity*) IFC2X3_types[381]));defs.push_back(((entity*) IFC2X3_types[921]));defs.push_back(((entity*) IFC2X3_types[952]));
        ((entity*) IFC2X3_types[297])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[85]));defs.push_back(((entity*) IFC2X3_types[665]));
        ((entity*) IFC2X3_types[84])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC2X3_types[89]));defs.push_back(((entity*) IFC2X3_types[236]));defs.push_back(((entity*) IFC2X3_types[302]));defs.push_back(((entity*) IFC2X3_types[382]));defs.push_back(((entity*) IFC2X3_types[787]));defs.push_back(((entity*) IFC2X3_types[922]));
        ((entity*) IFC2X3_types[305])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(12);
        defs.push_back(((entity*) IFC2X3_types[186]));defs.push_back(((entity*) IFC2X3_types[112]));defs.push_back(((entity*) IFC2X3_types[180]));defs.push_back(((entity*) IFC2X3_types[181]));defs.push_back(((entity*) IFC2X3_types[307]));defs.push_back(((entity*) IFC2X3_types[424]));defs.push_back(((entity*) IFC2X3_types[464]));defs.push_back(((entity*) IFC2X3_types[654]));defs.push_back(((entity*) IFC2X3_types[928]));defs.push_back(((entity*) IFC2X3_types[924]));defs.push_back(((entity*) IFC2X3_types[939]));defs.push_back(((entity*) IFC2X3_types[979]));
        ((entity*) IFC2X3_types[538])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[91]));defs.push_back(((entity*) IFC2X3_types[262]));defs.push_back(((entity*) IFC2X3_types[426]));defs.push_back(((entity*) IFC2X3_types[555]));
        ((entity*) IFC2X3_types[357])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[93]));defs.push_back(((entity*) IFC2X3_types[95]));defs.push_back(((entity*) IFC2X3_types[264]));defs.push_back(((entity*) IFC2X3_types[557]));
        ((entity*) IFC2X3_types[365])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[98]));defs.push_back(((entity*) IFC2X3_types[570]));defs.push_back(((entity*) IFC2X3_types[571]));
        ((entity*) IFC2X3_types[569])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[100]));defs.push_back(((entity*) IFC2X3_types[102]));
        ((entity*) IFC2X3_types[99])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[101]));
        ((entity*) IFC2X3_types[100])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[103]));
        ((entity*) IFC2X3_types[102])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[104]));
        ((entity*) IFC2X3_types[45])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[105]));defs.push_back(((entity*) IFC2X3_types[736]));
        ((entity*) IFC2X3_types[271])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[110]));defs.push_back(((entity*) IFC2X3_types[306]));
        ((entity*) IFC2X3_types[143])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[111]));
        ((entity*) IFC2X3_types[112])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC2X3_types[119]));defs.push_back(((entity*) IFC2X3_types[244]));defs.push_back(((entity*) IFC2X3_types[322]));defs.push_back(((entity*) IFC2X3_types[323]));defs.push_back(((entity*) IFC2X3_types[324]));defs.push_back(((entity*) IFC2X3_types[325]));defs.push_back(((entity*) IFC2X3_types[437]));
        ((entity*) IFC2X3_types[326])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[120]));defs.push_back(((entity*) IFC2X3_types[528]));
        ((entity*) IFC2X3_types[144])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[125]));
        ((entity*) IFC2X3_types[126])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[131]));defs.push_back(((entity*) IFC2X3_types[761]));
        ((entity*) IFC2X3_types[615])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[136]));defs.push_back(((entity*) IFC2X3_types[336]));defs.push_back(((entity*) IFC2X3_types[632]));
        ((entity*) IFC2X3_types[363])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC2X3_types[144]));defs.push_back(((entity*) IFC2X3_types[269]));defs.push_back(((entity*) IFC2X3_types[328]));defs.push_back(((entity*) IFC2X3_types[330]));defs.push_back(((entity*) IFC2X3_types[463]));defs.push_back(((entity*) IFC2X3_types[540]));defs.push_back(((entity*) IFC2X3_types[946]));
        ((entity*) IFC2X3_types[915])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[145]));defs.push_back(((entity*) IFC2X3_types[148]));defs.push_back(((entity*) IFC2X3_types[149]));defs.push_back(((entity*) IFC2X3_types[150]));
        ((entity*) IFC2X3_types[146])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[147]));
        ((entity*) IFC2X3_types[148])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC2X3_types[157]));defs.push_back(((entity*) IFC2X3_types[158]));defs.push_back(((entity*) IFC2X3_types[159]));defs.push_back(((entity*) IFC2X3_types[182]));defs.push_back(((entity*) IFC2X3_types[430]));defs.push_back(((entity*) IFC2X3_types[842]));
        ((entity*) IFC2X3_types[160])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[160]));
        ((entity*) IFC2X3_types[722])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[162]));defs.push_back(((entity*) IFC2X3_types[166]));defs.push_back(((entity*) IFC2X3_types[765]));
        ((entity*) IFC2X3_types[511])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[175]));defs.push_back(((entity*) IFC2X3_types[314]));
        ((entity*) IFC2X3_types[37])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[185]));defs.push_back(((entity*) IFC2X3_types[470]));defs.push_back(((entity*) IFC2X3_types[859]));defs.push_back(((entity*) IFC2X3_types[860]));
        ((entity*) IFC2X3_types[773])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[194]));defs.push_back(((entity*) IFC2X3_types[656]));
        ((entity*) IFC2X3_types[76])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[197]));defs.push_back(((entity*) IFC2X3_types[343]));defs.push_back(((entity*) IFC2X3_types[850]));defs.push_back(((entity*) IFC2X3_types[864]));defs.push_back(((entity*) IFC2X3_types[887]));
        ((entity*) IFC2X3_types[593])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[219]));defs.push_back(((entity*) IFC2X3_types[225]));
        ((entity*) IFC2X3_types[258])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[221]));defs.push_back(((entity*) IFC2X3_types[609]));
        ((entity*) IFC2X3_types[28])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[222]));defs.push_back(((entity*) IFC2X3_types[838]));
        ((entity*) IFC2X3_types[256])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[223]));
        ((entity*) IFC2X3_types[878])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[228]));defs.push_back(((entity*) IFC2X3_types[338]));
        ((entity*) IFC2X3_types[301])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[229]));defs.push_back(((entity*) IFC2X3_types[339]));
        ((entity*) IFC2X3_types[302])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC2X3_types[230]));defs.push_back(((entity*) IFC2X3_types[308]));defs.push_back(((entity*) IFC2X3_types[353]));defs.push_back(((entity*) IFC2X3_types[356]));defs.push_back(((entity*) IFC2X3_types[362]));defs.push_back(((entity*) IFC2X3_types[364]));defs.push_back(((entity*) IFC2X3_types[366]));defs.push_back(((entity*) IFC2X3_types[368]));defs.push_back(((entity*) IFC2X3_types[370]));
        ((entity*) IFC2X3_types[237])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC2X3_types[231]));defs.push_back(((entity*) IFC2X3_types[309]));defs.push_back(((entity*) IFC2X3_types[354]));defs.push_back(((entity*) IFC2X3_types[357]));defs.push_back(((entity*) IFC2X3_types[363]));defs.push_back(((entity*) IFC2X3_types[365]));defs.push_back(((entity*) IFC2X3_types[367]));defs.push_back(((entity*) IFC2X3_types[369]));defs.push_back(((entity*) IFC2X3_types[371]));
        ((entity*) IFC2X3_types[238])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[233]));defs.push_back(((entity*) IFC2X3_types[237]));
        ((entity*) IFC2X3_types[235])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[234]));defs.push_back(((entity*) IFC2X3_types[238]));
        ((entity*) IFC2X3_types[236])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[239]));
        ((entity*) IFC2X3_types[576])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(14);
        defs.push_back(((entity*) IFC2X3_types[248]));defs.push_back(((entity*) IFC2X3_types[251]));defs.push_back(((entity*) IFC2X3_types[304]));defs.push_back(((entity*) IFC2X3_types[311]));defs.push_back(((entity*) IFC2X3_types[372]));defs.push_back(((entity*) IFC2X3_types[543]));defs.push_back(((entity*) IFC2X3_types[624]));defs.push_back(((entity*) IFC2X3_types[661]));defs.push_back(((entity*) IFC2X3_types[752]));defs.push_back(((entity*) IFC2X3_types[776]));defs.push_back(((entity*) IFC2X3_types[778]));defs.push_back(((entity*) IFC2X3_types[783]));defs.push_back(((entity*) IFC2X3_types[966]));defs.push_back(((entity*) IFC2X3_types[969]));
        ((entity*) IFC2X3_types[625])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[252]));defs.push_back(((entity*) IFC2X3_types[305]));defs.push_back(((entity*) IFC2X3_types[970]));
        ((entity*) IFC2X3_types[933])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[259]));
        ((entity*) IFC2X3_types[582])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[260]));
        ((entity*) IFC2X3_types[583])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[261]));defs.push_back(((entity*) IFC2X3_types[888]));
        ((entity*) IFC2X3_types[589])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[266]));defs.push_back(((entity*) IFC2X3_types[349]));
        ((entity*) IFC2X3_types[371])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[270]));defs.push_back(((entity*) IFC2X3_types[534]));defs.push_back(((entity*) IFC2X3_types[843]));
        ((entity*) IFC2X3_types[269])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[271]));defs.push_back(((entity*) IFC2X3_types[527]));
        ((entity*) IFC2X3_types[342])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[272]));defs.push_back(((entity*) IFC2X3_types[575]));defs.push_back(((entity*) IFC2X3_types[948]));
        ((entity*) IFC2X3_types[463])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[283]));
        ((entity*) IFC2X3_types[353])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[285]));defs.push_back(((entity*) IFC2X3_types[870]));
        ((entity*) IFC2X3_types[367])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[273]));
        ((entity*) IFC2X3_types[311])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[274]));defs.push_back(((entity*) IFC2X3_types[804]));
        ((entity*) IFC2X3_types[866])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC2X3_types[321]));defs.push_back(((entity*) IFC2X3_types[380]));defs.push_back(((entity*) IFC2X3_types[387]));defs.push_back(((entity*) IFC2X3_types[411]));defs.push_back(((entity*) IFC2X3_types[490]));defs.push_back(((entity*) IFC2X3_types[529]));defs.push_back(((entity*) IFC2X3_types[603]));defs.push_back(((entity*) IFC2X3_types[903]));defs.push_back(((entity*) IFC2X3_types[964]));
        ((entity*) IFC2X3_types[483])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[327]));defs.push_back(((entity*) IFC2X3_types[724]));defs.push_back(((entity*) IFC2X3_types[845]));
        ((entity*) IFC2X3_types[859])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[331]));
        ((entity*) IFC2X3_types[330])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[332]));
        ((entity*) IFC2X3_types[328])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[333]));defs.push_back(((entity*) IFC2X3_types[334]));
        ((entity*) IFC2X3_types[470])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[335]));defs.push_back(((entity*) IFC2X3_types[771]));
        ((entity*) IFC2X3_types[806])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[341]));defs.push_back(((entity*) IFC2X3_types[342]));
        ((entity*) IFC2X3_types[340])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[384]));defs.push_back(((entity*) IFC2X3_types[867]));
        ((entity*) IFC2X3_types[382])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[388]));defs.push_back(((entity*) IFC2X3_types[726]));
        ((entity*) IFC2X3_types[605])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[389]));
        ((entity*) IFC2X3_types[394])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[391]));
        ((entity*) IFC2X3_types[719])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[392]));defs.push_back(((entity*) IFC2X3_types[471]));defs.push_back(((entity*) IFC2X3_types[839]));defs.push_back(((entity*) IFC2X3_types[915]));
        ((entity*) IFC2X3_types[720])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[393]));
        ((entity*) IFC2X3_types[391])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[400]));defs.push_back(((entity*) IFC2X3_types[459]));
        ((entity*) IFC2X3_types[519])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[422]));defs.push_back(((entity*) IFC2X3_types[659]));
        ((entity*) IFC2X3_types[908])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[447]));defs.push_back(((entity*) IFC2X3_types[448]));defs.push_back(((entity*) IFC2X3_types[449]));defs.push_back(((entity*) IFC2X3_types[450]));
        ((entity*) IFC2X3_types[446])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[451]));
        ((entity*) IFC2X3_types[450])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[478]));defs.push_back(((entity*) IFC2X3_types[601]));
        ((entity*) IFC2X3_types[602])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[487]));defs.push_back(((entity*) IFC2X3_types[491]));
        ((entity*) IFC2X3_types[490])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[488]));
        ((entity*) IFC2X3_types[338])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[489]));
        ((entity*) IFC2X3_types[339])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[495]));defs.push_back(((entity*) IFC2X3_types[517]));
        ((entity*) IFC2X3_types[152])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[510]));defs.push_back(((entity*) IFC2X3_types[530]));
        ((entity*) IFC2X3_types[872])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[515]));defs.push_back(((entity*) IFC2X3_types[932]));
        ((entity*) IFC2X3_types[516])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[516]));defs.push_back(((entity*) IFC2X3_types[618]));defs.push_back(((entity*) IFC2X3_types[686]));
        ((entity*) IFC2X3_types[732])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[522]));
        ((entity*) IFC2X3_types[6])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[548]));defs.push_back(((entity*) IFC2X3_types[551]));
        ((entity*) IFC2X3_types[550])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[561]));
        ((entity*) IFC2X3_types[562])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[564]));
        ((entity*) IFC2X3_types[298])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[580]));defs.push_back(((entity*) IFC2X3_types[873]));
        ((entity*) IFC2X3_types[11])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[582]));defs.push_back(((entity*) IFC2X3_types[583]));defs.push_back(((entity*) IFC2X3_types[587]));defs.push_back(((entity*) IFC2X3_types[589]));
        ((entity*) IFC2X3_types[585])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[584]));defs.push_back(((entity*) IFC2X3_types[586]));defs.push_back(((entity*) IFC2X3_types[588]));
        ((entity*) IFC2X3_types[587])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[592]));
        ((entity*) IFC2X3_types[591])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[597]));defs.push_back(((entity*) IFC2X3_types[872]));
        ((entity*) IFC2X3_types[599])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[610]));
        ((entity*) IFC2X3_types[341])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC2X3_types[616]));defs.push_back(((entity*) IFC2X3_types[620]));defs.push_back(((entity*) IFC2X3_types[622]));defs.push_back(((entity*) IFC2X3_types[623]));defs.push_back(((entity*) IFC2X3_types[626]));defs.push_back(((entity*) IFC2X3_types[628]));
        ((entity*) IFC2X3_types[761])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[625]));
        ((entity*) IFC2X3_types[618])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC2X3_types[634]));defs.push_back(((entity*) IFC2X3_types[635]));defs.push_back(((entity*) IFC2X3_types[636]));defs.push_back(((entity*) IFC2X3_types[637]));defs.push_back(((entity*) IFC2X3_types[638]));defs.push_back(((entity*) IFC2X3_types[639]));
        ((entity*) IFC2X3_types[551])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[651]));
        ((entity*) IFC2X3_types[60])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[653]));defs.push_back(((entity*) IFC2X3_types[737]));
        ((entity*) IFC2X3_types[654])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC2X3_types[662]));defs.push_back(((entity*) IFC2X3_types[666]));defs.push_back(((entity*) IFC2X3_types[875]));defs.push_back(((entity*) IFC2X3_types[876]));
        ((entity*) IFC2X3_types[665])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[667]));defs.push_back(((entity*) IFC2X3_types[708]));
        ((entity*) IFC2X3_types[701])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[668]));defs.push_back(((entity*) IFC2X3_types[677]));defs.push_back(((entity*) IFC2X3_types[688]));defs.push_back(((entity*) IFC2X3_types[701]));defs.push_back(((entity*) IFC2X3_types[702]));
        ((entity*) IFC2X3_types[686])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[669]));defs.push_back(((entity*) IFC2X3_types[675]));defs.push_back(((entity*) IFC2X3_types[713]));
        ((entity*) IFC2X3_types[671])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC2X3_types[670]));defs.push_back(((entity*) IFC2X3_types[671]));defs.push_back(((entity*) IFC2X3_types[672]));defs.push_back(((entity*) IFC2X3_types[673]));defs.push_back(((entity*) IFC2X3_types[674]));defs.push_back(((entity*) IFC2X3_types[676]));
        ((entity*) IFC2X3_types[668])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC2X3_types[678]));defs.push_back(((entity*) IFC2X3_types[679]));defs.push_back(((entity*) IFC2X3_types[680]));defs.push_back(((entity*) IFC2X3_types[681]));defs.push_back(((entity*) IFC2X3_types[682]));defs.push_back(((entity*) IFC2X3_types[683]));defs.push_back(((entity*) IFC2X3_types[684]));defs.push_back(((entity*) IFC2X3_types[685]));
        ((entity*) IFC2X3_types[677])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(18);
        defs.push_back(((entity*) IFC2X3_types[689]));defs.push_back(((entity*) IFC2X3_types[692]));defs.push_back(((entity*) IFC2X3_types[691]));defs.push_back(((entity*) IFC2X3_types[693]));defs.push_back(((entity*) IFC2X3_types[694]));defs.push_back(((entity*) IFC2X3_types[695]));defs.push_back(((entity*) IFC2X3_types[698]));defs.push_back(((entity*) IFC2X3_types[699]));defs.push_back(((entity*) IFC2X3_types[700]));defs.push_back(((entity*) IFC2X3_types[705]));defs.push_back(((entity*) IFC2X3_types[706]));defs.push_back(((entity*) IFC2X3_types[707]));defs.push_back(((entity*) IFC2X3_types[711]));defs.push_back(((entity*) IFC2X3_types[712]));defs.push_back(((entity*) IFC2X3_types[714]));defs.push_back(((entity*) IFC2X3_types[715]));defs.push_back(((entity*) IFC2X3_types[716]));defs.push_back(((entity*) IFC2X3_types[717]));
        ((entity*) IFC2X3_types[688])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[690]));defs.push_back(((entity*) IFC2X3_types[697]));
        ((entity*) IFC2X3_types[689])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[696]));
        ((entity*) IFC2X3_types[695])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[703]));defs.push_back(((entity*) IFC2X3_types[704]));
        ((entity*) IFC2X3_types[702])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[709]));
        ((entity*) IFC2X3_types[670])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[710]));
        ((entity*) IFC2X3_types[703])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[756]));defs.push_back(((entity*) IFC2X3_types[841]));
        ((entity*) IFC2X3_types[718])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[757]));defs.push_back(((entity*) IFC2X3_types[916]));
        ((entity*) IFC2X3_types[756])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[784]));
        ((entity*) IFC2X3_types[787])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[801]));defs.push_back(((entity*) IFC2X3_types[831]));
        ((entity*) IFC2X3_types[802])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[805]));defs.push_back(((entity*) IFC2X3_types[824]));
        ((entity*) IFC2X3_types[811])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[807]));defs.push_back(((entity*) IFC2X3_types[828]));defs.push_back(((entity*) IFC2X3_types[834]));
        ((entity*) IFC2X3_types[805])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[808]));defs.push_back(((entity*) IFC2X3_types[835]));
        ((entity*) IFC2X3_types[824])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[809]));
        ((entity*) IFC2X3_types[808])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC2X3_types[812]));defs.push_back(((entity*) IFC2X3_types[825]));defs.push_back(((entity*) IFC2X3_types[827]));
        ((entity*) IFC2X3_types[801])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[813]));
        ((entity*) IFC2X3_types[812])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC2X3_types[816]));defs.push_back(((entity*) IFC2X3_types[817]));defs.push_back(((entity*) IFC2X3_types[818]));defs.push_back(((entity*) IFC2X3_types[820]));defs.push_back(((entity*) IFC2X3_types[823]));
        ((entity*) IFC2X3_types[822])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[819]));
        ((entity*) IFC2X3_types[818])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[821]));
        ((entity*) IFC2X3_types[820])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[822]));
        ((entity*) IFC2X3_types[814])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[826]));
        ((entity*) IFC2X3_types[825])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[829]));
        ((entity*) IFC2X3_types[831])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[830]));
        ((entity*) IFC2X3_types[388])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[833]));
        ((entity*) IFC2X3_types[830])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[836]));
        ((entity*) IFC2X3_types[835])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[840]));
        ((entity*) IFC2X3_types[841])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[846]));defs.push_back(((entity*) IFC2X3_types[847]));
        ((entity*) IFC2X3_types[861])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[854]));
        ((entity*) IFC2X3_types[855])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[878]));
        ((entity*) IFC2X3_types[34])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[885]));
        ((entity*) IFC2X3_types[884])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[895]));defs.push_back(((entity*) IFC2X3_types[896]));
        ((entity*) IFC2X3_types[894])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[931]));
        ((entity*) IFC2X3_types[526])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[933]));
        ((entity*) IFC2X3_types[932])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[949]));
        ((entity*) IFC2X3_types[946])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[950]));
        ((entity*) IFC2X3_types[229])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC2X3_types[957]));
        ((entity*) IFC2X3_types[956])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC2X3_types[975]));defs.push_back(((entity*) IFC2X3_types[976]));
        ((entity*) IFC2X3_types[973])->set_subtypes(defs);
    }

    std::vector<const declaration*> declarations; declarations.reserve(980);
    declarations.push_back(IFC2X3_types[0]);
    declarations.push_back(IFC2X3_types[1]);
    declarations.push_back(IFC2X3_types[2]);
    declarations.push_back(IFC2X3_types[3]);
    declarations.push_back(IFC2X3_types[4]);
    declarations.push_back(IFC2X3_types[5]);
    declarations.push_back(IFC2X3_types[6]);
    declarations.push_back(IFC2X3_types[7]);
    declarations.push_back(IFC2X3_types[8]);
    declarations.push_back(IFC2X3_types[9]);
    declarations.push_back(IFC2X3_types[10]);
    declarations.push_back(IFC2X3_types[11]);
    declarations.push_back(IFC2X3_types[12]);
    declarations.push_back(IFC2X3_types[13]);
    declarations.push_back(IFC2X3_types[14]);
    declarations.push_back(IFC2X3_types[15]);
    declarations.push_back(IFC2X3_types[16]);
    declarations.push_back(IFC2X3_types[17]);
    declarations.push_back(IFC2X3_types[18]);
    declarations.push_back(IFC2X3_types[19]);
    declarations.push_back(IFC2X3_types[20]);
    declarations.push_back(IFC2X3_types[21]);
    declarations.push_back(IFC2X3_types[22]);
    declarations.push_back(IFC2X3_types[23]);
    declarations.push_back(IFC2X3_types[24]);
    declarations.push_back(IFC2X3_types[25]);
    declarations.push_back(IFC2X3_types[26]);
    declarations.push_back(IFC2X3_types[27]);
    declarations.push_back(IFC2X3_types[28]);
    declarations.push_back(IFC2X3_types[29]);
    declarations.push_back(IFC2X3_types[30]);
    declarations.push_back(IFC2X3_types[31]);
    declarations.push_back(IFC2X3_types[32]);
    declarations.push_back(IFC2X3_types[33]);
    declarations.push_back(IFC2X3_types[34]);
    declarations.push_back(IFC2X3_types[35]);
    declarations.push_back(IFC2X3_types[36]);
    declarations.push_back(IFC2X3_types[37]);
    declarations.push_back(IFC2X3_types[38]);
    declarations.push_back(IFC2X3_types[39]);
    declarations.push_back(IFC2X3_types[40]);
    declarations.push_back(IFC2X3_types[41]);
    declarations.push_back(IFC2X3_types[42]);
    declarations.push_back(IFC2X3_types[43]);
    declarations.push_back(IFC2X3_types[44]);
    declarations.push_back(IFC2X3_types[45]);
    declarations.push_back(IFC2X3_types[46]);
    declarations.push_back(IFC2X3_types[47]);
    declarations.push_back(IFC2X3_types[48]);
    declarations.push_back(IFC2X3_types[49]);
    declarations.push_back(IFC2X3_types[50]);
    declarations.push_back(IFC2X3_types[51]);
    declarations.push_back(IFC2X3_types[52]);
    declarations.push_back(IFC2X3_types[53]);
    declarations.push_back(IFC2X3_types[54]);
    declarations.push_back(IFC2X3_types[55]);
    declarations.push_back(IFC2X3_types[56]);
    declarations.push_back(IFC2X3_types[57]);
    declarations.push_back(IFC2X3_types[58]);
    declarations.push_back(IFC2X3_types[59]);
    declarations.push_back(IFC2X3_types[60]);
    declarations.push_back(IFC2X3_types[61]);
    declarations.push_back(IFC2X3_types[62]);
    declarations.push_back(IFC2X3_types[63]);
    declarations.push_back(IFC2X3_types[64]);
    declarations.push_back(IFC2X3_types[65]);
    declarations.push_back(IFC2X3_types[66]);
    declarations.push_back(IFC2X3_types[67]);
    declarations.push_back(IFC2X3_types[68]);
    declarations.push_back(IFC2X3_types[69]);
    declarations.push_back(IFC2X3_types[70]);
    declarations.push_back(IFC2X3_types[71]);
    declarations.push_back(IFC2X3_types[72]);
    declarations.push_back(IFC2X3_types[73]);
    declarations.push_back(IFC2X3_types[74]);
    declarations.push_back(IFC2X3_types[75]);
    declarations.push_back(IFC2X3_types[76]);
    declarations.push_back(IFC2X3_types[77]);
    declarations.push_back(IFC2X3_types[78]);
    declarations.push_back(IFC2X3_types[79]);
    declarations.push_back(IFC2X3_types[80]);
    declarations.push_back(IFC2X3_types[81]);
    declarations.push_back(IFC2X3_types[82]);
    declarations.push_back(IFC2X3_types[83]);
    declarations.push_back(IFC2X3_types[84]);
    declarations.push_back(IFC2X3_types[85]);
    declarations.push_back(IFC2X3_types[86]);
    declarations.push_back(IFC2X3_types[87]);
    declarations.push_back(IFC2X3_types[88]);
    declarations.push_back(IFC2X3_types[89]);
    declarations.push_back(IFC2X3_types[90]);
    declarations.push_back(IFC2X3_types[91]);
    declarations.push_back(IFC2X3_types[92]);
    declarations.push_back(IFC2X3_types[93]);
    declarations.push_back(IFC2X3_types[94]);
    declarations.push_back(IFC2X3_types[95]);
    declarations.push_back(IFC2X3_types[96]);
    declarations.push_back(IFC2X3_types[97]);
    declarations.push_back(IFC2X3_types[98]);
    declarations.push_back(IFC2X3_types[99]);
    declarations.push_back(IFC2X3_types[100]);
    declarations.push_back(IFC2X3_types[101]);
    declarations.push_back(IFC2X3_types[102]);
    declarations.push_back(IFC2X3_types[103]);
    declarations.push_back(IFC2X3_types[104]);
    declarations.push_back(IFC2X3_types[105]);
    declarations.push_back(IFC2X3_types[106]);
    declarations.push_back(IFC2X3_types[107]);
    declarations.push_back(IFC2X3_types[108]);
    declarations.push_back(IFC2X3_types[109]);
    declarations.push_back(IFC2X3_types[110]);
    declarations.push_back(IFC2X3_types[111]);
    declarations.push_back(IFC2X3_types[112]);
    declarations.push_back(IFC2X3_types[113]);
    declarations.push_back(IFC2X3_types[114]);
    declarations.push_back(IFC2X3_types[115]);
    declarations.push_back(IFC2X3_types[116]);
    declarations.push_back(IFC2X3_types[117]);
    declarations.push_back(IFC2X3_types[118]);
    declarations.push_back(IFC2X3_types[119]);
    declarations.push_back(IFC2X3_types[120]);
    declarations.push_back(IFC2X3_types[121]);
    declarations.push_back(IFC2X3_types[122]);
    declarations.push_back(IFC2X3_types[123]);
    declarations.push_back(IFC2X3_types[124]);
    declarations.push_back(IFC2X3_types[125]);
    declarations.push_back(IFC2X3_types[126]);
    declarations.push_back(IFC2X3_types[127]);
    declarations.push_back(IFC2X3_types[128]);
    declarations.push_back(IFC2X3_types[129]);
    declarations.push_back(IFC2X3_types[130]);
    declarations.push_back(IFC2X3_types[131]);
    declarations.push_back(IFC2X3_types[132]);
    declarations.push_back(IFC2X3_types[133]);
    declarations.push_back(IFC2X3_types[134]);
    declarations.push_back(IFC2X3_types[135]);
    declarations.push_back(IFC2X3_types[136]);
    declarations.push_back(IFC2X3_types[137]);
    declarations.push_back(IFC2X3_types[138]);
    declarations.push_back(IFC2X3_types[139]);
    declarations.push_back(IFC2X3_types[140]);
    declarations.push_back(IFC2X3_types[141]);
    declarations.push_back(IFC2X3_types[142]);
    declarations.push_back(IFC2X3_types[143]);
    declarations.push_back(IFC2X3_types[144]);
    declarations.push_back(IFC2X3_types[145]);
    declarations.push_back(IFC2X3_types[146]);
    declarations.push_back(IFC2X3_types[147]);
    declarations.push_back(IFC2X3_types[148]);
    declarations.push_back(IFC2X3_types[149]);
    declarations.push_back(IFC2X3_types[150]);
    declarations.push_back(IFC2X3_types[151]);
    declarations.push_back(IFC2X3_types[152]);
    declarations.push_back(IFC2X3_types[153]);
    declarations.push_back(IFC2X3_types[154]);
    declarations.push_back(IFC2X3_types[155]);
    declarations.push_back(IFC2X3_types[156]);
    declarations.push_back(IFC2X3_types[157]);
    declarations.push_back(IFC2X3_types[158]);
    declarations.push_back(IFC2X3_types[159]);
    declarations.push_back(IFC2X3_types[160]);
    declarations.push_back(IFC2X3_types[161]);
    declarations.push_back(IFC2X3_types[162]);
    declarations.push_back(IFC2X3_types[163]);
    declarations.push_back(IFC2X3_types[164]);
    declarations.push_back(IFC2X3_types[165]);
    declarations.push_back(IFC2X3_types[166]);
    declarations.push_back(IFC2X3_types[167]);
    declarations.push_back(IFC2X3_types[168]);
    declarations.push_back(IFC2X3_types[169]);
    declarations.push_back(IFC2X3_types[170]);
    declarations.push_back(IFC2X3_types[171]);
    declarations.push_back(IFC2X3_types[172]);
    declarations.push_back(IFC2X3_types[173]);
    declarations.push_back(IFC2X3_types[174]);
    declarations.push_back(IFC2X3_types[175]);
    declarations.push_back(IFC2X3_types[176]);
    declarations.push_back(IFC2X3_types[177]);
    declarations.push_back(IFC2X3_types[178]);
    declarations.push_back(IFC2X3_types[179]);
    declarations.push_back(IFC2X3_types[180]);
    declarations.push_back(IFC2X3_types[181]);
    declarations.push_back(IFC2X3_types[182]);
    declarations.push_back(IFC2X3_types[183]);
    declarations.push_back(IFC2X3_types[184]);
    declarations.push_back(IFC2X3_types[185]);
    declarations.push_back(IFC2X3_types[186]);
    declarations.push_back(IFC2X3_types[187]);
    declarations.push_back(IFC2X3_types[188]);
    declarations.push_back(IFC2X3_types[189]);
    declarations.push_back(IFC2X3_types[190]);
    declarations.push_back(IFC2X3_types[191]);
    declarations.push_back(IFC2X3_types[192]);
    declarations.push_back(IFC2X3_types[193]);
    declarations.push_back(IFC2X3_types[194]);
    declarations.push_back(IFC2X3_types[195]);
    declarations.push_back(IFC2X3_types[196]);
    declarations.push_back(IFC2X3_types[197]);
    declarations.push_back(IFC2X3_types[198]);
    declarations.push_back(IFC2X3_types[199]);
    declarations.push_back(IFC2X3_types[200]);
    declarations.push_back(IFC2X3_types[201]);
    declarations.push_back(IFC2X3_types[202]);
    declarations.push_back(IFC2X3_types[203]);
    declarations.push_back(IFC2X3_types[204]);
    declarations.push_back(IFC2X3_types[205]);
    declarations.push_back(IFC2X3_types[206]);
    declarations.push_back(IFC2X3_types[207]);
    declarations.push_back(IFC2X3_types[208]);
    declarations.push_back(IFC2X3_types[209]);
    declarations.push_back(IFC2X3_types[210]);
    declarations.push_back(IFC2X3_types[211]);
    declarations.push_back(IFC2X3_types[212]);
    declarations.push_back(IFC2X3_types[213]);
    declarations.push_back(IFC2X3_types[214]);
    declarations.push_back(IFC2X3_types[215]);
    declarations.push_back(IFC2X3_types[216]);
    declarations.push_back(IFC2X3_types[217]);
    declarations.push_back(IFC2X3_types[218]);
    declarations.push_back(IFC2X3_types[219]);
    declarations.push_back(IFC2X3_types[220]);
    declarations.push_back(IFC2X3_types[221]);
    declarations.push_back(IFC2X3_types[222]);
    declarations.push_back(IFC2X3_types[223]);
    declarations.push_back(IFC2X3_types[224]);
    declarations.push_back(IFC2X3_types[225]);
    declarations.push_back(IFC2X3_types[226]);
    declarations.push_back(IFC2X3_types[227]);
    declarations.push_back(IFC2X3_types[228]);
    declarations.push_back(IFC2X3_types[229]);
    declarations.push_back(IFC2X3_types[230]);
    declarations.push_back(IFC2X3_types[231]);
    declarations.push_back(IFC2X3_types[232]);
    declarations.push_back(IFC2X3_types[233]);
    declarations.push_back(IFC2X3_types[234]);
    declarations.push_back(IFC2X3_types[235]);
    declarations.push_back(IFC2X3_types[236]);
    declarations.push_back(IFC2X3_types[237]);
    declarations.push_back(IFC2X3_types[238]);
    declarations.push_back(IFC2X3_types[239]);
    declarations.push_back(IFC2X3_types[240]);
    declarations.push_back(IFC2X3_types[241]);
    declarations.push_back(IFC2X3_types[242]);
    declarations.push_back(IFC2X3_types[243]);
    declarations.push_back(IFC2X3_types[244]);
    declarations.push_back(IFC2X3_types[245]);
    declarations.push_back(IFC2X3_types[246]);
    declarations.push_back(IFC2X3_types[247]);
    declarations.push_back(IFC2X3_types[248]);
    declarations.push_back(IFC2X3_types[249]);
    declarations.push_back(IFC2X3_types[250]);
    declarations.push_back(IFC2X3_types[251]);
    declarations.push_back(IFC2X3_types[252]);
    declarations.push_back(IFC2X3_types[253]);
    declarations.push_back(IFC2X3_types[254]);
    declarations.push_back(IFC2X3_types[255]);
    declarations.push_back(IFC2X3_types[256]);
    declarations.push_back(IFC2X3_types[257]);
    declarations.push_back(IFC2X3_types[258]);
    declarations.push_back(IFC2X3_types[259]);
    declarations.push_back(IFC2X3_types[260]);
    declarations.push_back(IFC2X3_types[261]);
    declarations.push_back(IFC2X3_types[262]);
    declarations.push_back(IFC2X3_types[263]);
    declarations.push_back(IFC2X3_types[264]);
    declarations.push_back(IFC2X3_types[265]);
    declarations.push_back(IFC2X3_types[266]);
    declarations.push_back(IFC2X3_types[267]);
    declarations.push_back(IFC2X3_types[268]);
    declarations.push_back(IFC2X3_types[269]);
    declarations.push_back(IFC2X3_types[270]);
    declarations.push_back(IFC2X3_types[271]);
    declarations.push_back(IFC2X3_types[272]);
    declarations.push_back(IFC2X3_types[273]);
    declarations.push_back(IFC2X3_types[274]);
    declarations.push_back(IFC2X3_types[275]);
    declarations.push_back(IFC2X3_types[276]);
    declarations.push_back(IFC2X3_types[277]);
    declarations.push_back(IFC2X3_types[278]);
    declarations.push_back(IFC2X3_types[279]);
    declarations.push_back(IFC2X3_types[280]);
    declarations.push_back(IFC2X3_types[281]);
    declarations.push_back(IFC2X3_types[282]);
    declarations.push_back(IFC2X3_types[283]);
    declarations.push_back(IFC2X3_types[284]);
    declarations.push_back(IFC2X3_types[285]);
    declarations.push_back(IFC2X3_types[286]);
    declarations.push_back(IFC2X3_types[287]);
    declarations.push_back(IFC2X3_types[288]);
    declarations.push_back(IFC2X3_types[289]);
    declarations.push_back(IFC2X3_types[290]);
    declarations.push_back(IFC2X3_types[291]);
    declarations.push_back(IFC2X3_types[292]);
    declarations.push_back(IFC2X3_types[293]);
    declarations.push_back(IFC2X3_types[294]);
    declarations.push_back(IFC2X3_types[295]);
    declarations.push_back(IFC2X3_types[296]);
    declarations.push_back(IFC2X3_types[297]);
    declarations.push_back(IFC2X3_types[298]);
    declarations.push_back(IFC2X3_types[299]);
    declarations.push_back(IFC2X3_types[300]);
    declarations.push_back(IFC2X3_types[301]);
    declarations.push_back(IFC2X3_types[302]);
    declarations.push_back(IFC2X3_types[303]);
    declarations.push_back(IFC2X3_types[304]);
    declarations.push_back(IFC2X3_types[305]);
    declarations.push_back(IFC2X3_types[306]);
    declarations.push_back(IFC2X3_types[307]);
    declarations.push_back(IFC2X3_types[308]);
    declarations.push_back(IFC2X3_types[309]);
    declarations.push_back(IFC2X3_types[310]);
    declarations.push_back(IFC2X3_types[311]);
    declarations.push_back(IFC2X3_types[312]);
    declarations.push_back(IFC2X3_types[313]);
    declarations.push_back(IFC2X3_types[314]);
    declarations.push_back(IFC2X3_types[315]);
    declarations.push_back(IFC2X3_types[316]);
    declarations.push_back(IFC2X3_types[317]);
    declarations.push_back(IFC2X3_types[318]);
    declarations.push_back(IFC2X3_types[319]);
    declarations.push_back(IFC2X3_types[320]);
    declarations.push_back(IFC2X3_types[321]);
    declarations.push_back(IFC2X3_types[322]);
    declarations.push_back(IFC2X3_types[323]);
    declarations.push_back(IFC2X3_types[324]);
    declarations.push_back(IFC2X3_types[325]);
    declarations.push_back(IFC2X3_types[326]);
    declarations.push_back(IFC2X3_types[327]);
    declarations.push_back(IFC2X3_types[328]);
    declarations.push_back(IFC2X3_types[329]);
    declarations.push_back(IFC2X3_types[330]);
    declarations.push_back(IFC2X3_types[331]);
    declarations.push_back(IFC2X3_types[332]);
    declarations.push_back(IFC2X3_types[333]);
    declarations.push_back(IFC2X3_types[334]);
    declarations.push_back(IFC2X3_types[335]);
    declarations.push_back(IFC2X3_types[336]);
    declarations.push_back(IFC2X3_types[337]);
    declarations.push_back(IFC2X3_types[338]);
    declarations.push_back(IFC2X3_types[339]);
    declarations.push_back(IFC2X3_types[340]);
    declarations.push_back(IFC2X3_types[341]);
    declarations.push_back(IFC2X3_types[342]);
    declarations.push_back(IFC2X3_types[343]);
    declarations.push_back(IFC2X3_types[344]);
    declarations.push_back(IFC2X3_types[345]);
    declarations.push_back(IFC2X3_types[346]);
    declarations.push_back(IFC2X3_types[347]);
    declarations.push_back(IFC2X3_types[348]);
    declarations.push_back(IFC2X3_types[349]);
    declarations.push_back(IFC2X3_types[350]);
    declarations.push_back(IFC2X3_types[351]);
    declarations.push_back(IFC2X3_types[352]);
    declarations.push_back(IFC2X3_types[353]);
    declarations.push_back(IFC2X3_types[354]);
    declarations.push_back(IFC2X3_types[355]);
    declarations.push_back(IFC2X3_types[356]);
    declarations.push_back(IFC2X3_types[357]);
    declarations.push_back(IFC2X3_types[358]);
    declarations.push_back(IFC2X3_types[359]);
    declarations.push_back(IFC2X3_types[360]);
    declarations.push_back(IFC2X3_types[361]);
    declarations.push_back(IFC2X3_types[362]);
    declarations.push_back(IFC2X3_types[363]);
    declarations.push_back(IFC2X3_types[364]);
    declarations.push_back(IFC2X3_types[365]);
    declarations.push_back(IFC2X3_types[366]);
    declarations.push_back(IFC2X3_types[367]);
    declarations.push_back(IFC2X3_types[368]);
    declarations.push_back(IFC2X3_types[369]);
    declarations.push_back(IFC2X3_types[370]);
    declarations.push_back(IFC2X3_types[371]);
    declarations.push_back(IFC2X3_types[372]);
    declarations.push_back(IFC2X3_types[373]);
    declarations.push_back(IFC2X3_types[374]);
    declarations.push_back(IFC2X3_types[375]);
    declarations.push_back(IFC2X3_types[376]);
    declarations.push_back(IFC2X3_types[377]);
    declarations.push_back(IFC2X3_types[378]);
    declarations.push_back(IFC2X3_types[379]);
    declarations.push_back(IFC2X3_types[380]);
    declarations.push_back(IFC2X3_types[381]);
    declarations.push_back(IFC2X3_types[382]);
    declarations.push_back(IFC2X3_types[383]);
    declarations.push_back(IFC2X3_types[384]);
    declarations.push_back(IFC2X3_types[385]);
    declarations.push_back(IFC2X3_types[386]);
    declarations.push_back(IFC2X3_types[387]);
    declarations.push_back(IFC2X3_types[388]);
    declarations.push_back(IFC2X3_types[389]);
    declarations.push_back(IFC2X3_types[390]);
    declarations.push_back(IFC2X3_types[391]);
    declarations.push_back(IFC2X3_types[392]);
    declarations.push_back(IFC2X3_types[393]);
    declarations.push_back(IFC2X3_types[394]);
    declarations.push_back(IFC2X3_types[395]);
    declarations.push_back(IFC2X3_types[396]);
    declarations.push_back(IFC2X3_types[397]);
    declarations.push_back(IFC2X3_types[398]);
    declarations.push_back(IFC2X3_types[399]);
    declarations.push_back(IFC2X3_types[400]);
    declarations.push_back(IFC2X3_types[401]);
    declarations.push_back(IFC2X3_types[402]);
    declarations.push_back(IFC2X3_types[403]);
    declarations.push_back(IFC2X3_types[404]);
    declarations.push_back(IFC2X3_types[405]);
    declarations.push_back(IFC2X3_types[406]);
    declarations.push_back(IFC2X3_types[407]);
    declarations.push_back(IFC2X3_types[408]);
    declarations.push_back(IFC2X3_types[409]);
    declarations.push_back(IFC2X3_types[410]);
    declarations.push_back(IFC2X3_types[411]);
    declarations.push_back(IFC2X3_types[412]);
    declarations.push_back(IFC2X3_types[413]);
    declarations.push_back(IFC2X3_types[414]);
    declarations.push_back(IFC2X3_types[415]);
    declarations.push_back(IFC2X3_types[416]);
    declarations.push_back(IFC2X3_types[417]);
    declarations.push_back(IFC2X3_types[418]);
    declarations.push_back(IFC2X3_types[419]);
    declarations.push_back(IFC2X3_types[420]);
    declarations.push_back(IFC2X3_types[421]);
    declarations.push_back(IFC2X3_types[422]);
    declarations.push_back(IFC2X3_types[423]);
    declarations.push_back(IFC2X3_types[424]);
    declarations.push_back(IFC2X3_types[425]);
    declarations.push_back(IFC2X3_types[426]);
    declarations.push_back(IFC2X3_types[427]);
    declarations.push_back(IFC2X3_types[428]);
    declarations.push_back(IFC2X3_types[429]);
    declarations.push_back(IFC2X3_types[430]);
    declarations.push_back(IFC2X3_types[431]);
    declarations.push_back(IFC2X3_types[432]);
    declarations.push_back(IFC2X3_types[433]);
    declarations.push_back(IFC2X3_types[434]);
    declarations.push_back(IFC2X3_types[435]);
    declarations.push_back(IFC2X3_types[436]);
    declarations.push_back(IFC2X3_types[437]);
    declarations.push_back(IFC2X3_types[438]);
    declarations.push_back(IFC2X3_types[439]);
    declarations.push_back(IFC2X3_types[440]);
    declarations.push_back(IFC2X3_types[441]);
    declarations.push_back(IFC2X3_types[442]);
    declarations.push_back(IFC2X3_types[443]);
    declarations.push_back(IFC2X3_types[444]);
    declarations.push_back(IFC2X3_types[445]);
    declarations.push_back(IFC2X3_types[446]);
    declarations.push_back(IFC2X3_types[447]);
    declarations.push_back(IFC2X3_types[448]);
    declarations.push_back(IFC2X3_types[449]);
    declarations.push_back(IFC2X3_types[450]);
    declarations.push_back(IFC2X3_types[451]);
    declarations.push_back(IFC2X3_types[452]);
    declarations.push_back(IFC2X3_types[453]);
    declarations.push_back(IFC2X3_types[454]);
    declarations.push_back(IFC2X3_types[455]);
    declarations.push_back(IFC2X3_types[456]);
    declarations.push_back(IFC2X3_types[457]);
    declarations.push_back(IFC2X3_types[458]);
    declarations.push_back(IFC2X3_types[459]);
    declarations.push_back(IFC2X3_types[460]);
    declarations.push_back(IFC2X3_types[461]);
    declarations.push_back(IFC2X3_types[462]);
    declarations.push_back(IFC2X3_types[463]);
    declarations.push_back(IFC2X3_types[464]);
    declarations.push_back(IFC2X3_types[465]);
    declarations.push_back(IFC2X3_types[466]);
    declarations.push_back(IFC2X3_types[467]);
    declarations.push_back(IFC2X3_types[468]);
    declarations.push_back(IFC2X3_types[469]);
    declarations.push_back(IFC2X3_types[470]);
    declarations.push_back(IFC2X3_types[471]);
    declarations.push_back(IFC2X3_types[472]);
    declarations.push_back(IFC2X3_types[473]);
    declarations.push_back(IFC2X3_types[474]);
    declarations.push_back(IFC2X3_types[475]);
    declarations.push_back(IFC2X3_types[476]);
    declarations.push_back(IFC2X3_types[477]);
    declarations.push_back(IFC2X3_types[478]);
    declarations.push_back(IFC2X3_types[479]);
    declarations.push_back(IFC2X3_types[480]);
    declarations.push_back(IFC2X3_types[481]);
    declarations.push_back(IFC2X3_types[482]);
    declarations.push_back(IFC2X3_types[483]);
    declarations.push_back(IFC2X3_types[484]);
    declarations.push_back(IFC2X3_types[485]);
    declarations.push_back(IFC2X3_types[486]);
    declarations.push_back(IFC2X3_types[487]);
    declarations.push_back(IFC2X3_types[488]);
    declarations.push_back(IFC2X3_types[489]);
    declarations.push_back(IFC2X3_types[490]);
    declarations.push_back(IFC2X3_types[491]);
    declarations.push_back(IFC2X3_types[492]);
    declarations.push_back(IFC2X3_types[493]);
    declarations.push_back(IFC2X3_types[494]);
    declarations.push_back(IFC2X3_types[495]);
    declarations.push_back(IFC2X3_types[496]);
    declarations.push_back(IFC2X3_types[497]);
    declarations.push_back(IFC2X3_types[498]);
    declarations.push_back(IFC2X3_types[499]);
    declarations.push_back(IFC2X3_types[500]);
    declarations.push_back(IFC2X3_types[501]);
    declarations.push_back(IFC2X3_types[502]);
    declarations.push_back(IFC2X3_types[503]);
    declarations.push_back(IFC2X3_types[504]);
    declarations.push_back(IFC2X3_types[505]);
    declarations.push_back(IFC2X3_types[506]);
    declarations.push_back(IFC2X3_types[507]);
    declarations.push_back(IFC2X3_types[508]);
    declarations.push_back(IFC2X3_types[509]);
    declarations.push_back(IFC2X3_types[510]);
    declarations.push_back(IFC2X3_types[511]);
    declarations.push_back(IFC2X3_types[512]);
    declarations.push_back(IFC2X3_types[513]);
    declarations.push_back(IFC2X3_types[514]);
    declarations.push_back(IFC2X3_types[515]);
    declarations.push_back(IFC2X3_types[516]);
    declarations.push_back(IFC2X3_types[517]);
    declarations.push_back(IFC2X3_types[518]);
    declarations.push_back(IFC2X3_types[519]);
    declarations.push_back(IFC2X3_types[520]);
    declarations.push_back(IFC2X3_types[521]);
    declarations.push_back(IFC2X3_types[522]);
    declarations.push_back(IFC2X3_types[523]);
    declarations.push_back(IFC2X3_types[524]);
    declarations.push_back(IFC2X3_types[525]);
    declarations.push_back(IFC2X3_types[526]);
    declarations.push_back(IFC2X3_types[527]);
    declarations.push_back(IFC2X3_types[528]);
    declarations.push_back(IFC2X3_types[529]);
    declarations.push_back(IFC2X3_types[530]);
    declarations.push_back(IFC2X3_types[531]);
    declarations.push_back(IFC2X3_types[532]);
    declarations.push_back(IFC2X3_types[533]);
    declarations.push_back(IFC2X3_types[534]);
    declarations.push_back(IFC2X3_types[535]);
    declarations.push_back(IFC2X3_types[536]);
    declarations.push_back(IFC2X3_types[537]);
    declarations.push_back(IFC2X3_types[538]);
    declarations.push_back(IFC2X3_types[539]);
    declarations.push_back(IFC2X3_types[540]);
    declarations.push_back(IFC2X3_types[541]);
    declarations.push_back(IFC2X3_types[542]);
    declarations.push_back(IFC2X3_types[543]);
    declarations.push_back(IFC2X3_types[544]);
    declarations.push_back(IFC2X3_types[545]);
    declarations.push_back(IFC2X3_types[546]);
    declarations.push_back(IFC2X3_types[547]);
    declarations.push_back(IFC2X3_types[548]);
    declarations.push_back(IFC2X3_types[549]);
    declarations.push_back(IFC2X3_types[550]);
    declarations.push_back(IFC2X3_types[551]);
    declarations.push_back(IFC2X3_types[552]);
    declarations.push_back(IFC2X3_types[553]);
    declarations.push_back(IFC2X3_types[554]);
    declarations.push_back(IFC2X3_types[555]);
    declarations.push_back(IFC2X3_types[556]);
    declarations.push_back(IFC2X3_types[557]);
    declarations.push_back(IFC2X3_types[558]);
    declarations.push_back(IFC2X3_types[559]);
    declarations.push_back(IFC2X3_types[560]);
    declarations.push_back(IFC2X3_types[561]);
    declarations.push_back(IFC2X3_types[562]);
    declarations.push_back(IFC2X3_types[563]);
    declarations.push_back(IFC2X3_types[564]);
    declarations.push_back(IFC2X3_types[565]);
    declarations.push_back(IFC2X3_types[566]);
    declarations.push_back(IFC2X3_types[567]);
    declarations.push_back(IFC2X3_types[568]);
    declarations.push_back(IFC2X3_types[569]);
    declarations.push_back(IFC2X3_types[570]);
    declarations.push_back(IFC2X3_types[571]);
    declarations.push_back(IFC2X3_types[572]);
    declarations.push_back(IFC2X3_types[573]);
    declarations.push_back(IFC2X3_types[574]);
    declarations.push_back(IFC2X3_types[575]);
    declarations.push_back(IFC2X3_types[576]);
    declarations.push_back(IFC2X3_types[577]);
    declarations.push_back(IFC2X3_types[578]);
    declarations.push_back(IFC2X3_types[579]);
    declarations.push_back(IFC2X3_types[580]);
    declarations.push_back(IFC2X3_types[581]);
    declarations.push_back(IFC2X3_types[582]);
    declarations.push_back(IFC2X3_types[583]);
    declarations.push_back(IFC2X3_types[584]);
    declarations.push_back(IFC2X3_types[585]);
    declarations.push_back(IFC2X3_types[586]);
    declarations.push_back(IFC2X3_types[587]);
    declarations.push_back(IFC2X3_types[588]);
    declarations.push_back(IFC2X3_types[589]);
    declarations.push_back(IFC2X3_types[590]);
    declarations.push_back(IFC2X3_types[591]);
    declarations.push_back(IFC2X3_types[592]);
    declarations.push_back(IFC2X3_types[593]);
    declarations.push_back(IFC2X3_types[594]);
    declarations.push_back(IFC2X3_types[595]);
    declarations.push_back(IFC2X3_types[596]);
    declarations.push_back(IFC2X3_types[597]);
    declarations.push_back(IFC2X3_types[598]);
    declarations.push_back(IFC2X3_types[599]);
    declarations.push_back(IFC2X3_types[600]);
    declarations.push_back(IFC2X3_types[601]);
    declarations.push_back(IFC2X3_types[602]);
    declarations.push_back(IFC2X3_types[603]);
    declarations.push_back(IFC2X3_types[604]);
    declarations.push_back(IFC2X3_types[605]);
    declarations.push_back(IFC2X3_types[606]);
    declarations.push_back(IFC2X3_types[607]);
    declarations.push_back(IFC2X3_types[608]);
    declarations.push_back(IFC2X3_types[609]);
    declarations.push_back(IFC2X3_types[610]);
    declarations.push_back(IFC2X3_types[611]);
    declarations.push_back(IFC2X3_types[612]);
    declarations.push_back(IFC2X3_types[613]);
    declarations.push_back(IFC2X3_types[614]);
    declarations.push_back(IFC2X3_types[615]);
    declarations.push_back(IFC2X3_types[616]);
    declarations.push_back(IFC2X3_types[617]);
    declarations.push_back(IFC2X3_types[618]);
    declarations.push_back(IFC2X3_types[619]);
    declarations.push_back(IFC2X3_types[620]);
    declarations.push_back(IFC2X3_types[621]);
    declarations.push_back(IFC2X3_types[622]);
    declarations.push_back(IFC2X3_types[623]);
    declarations.push_back(IFC2X3_types[624]);
    declarations.push_back(IFC2X3_types[625]);
    declarations.push_back(IFC2X3_types[626]);
    declarations.push_back(IFC2X3_types[627]);
    declarations.push_back(IFC2X3_types[628]);
    declarations.push_back(IFC2X3_types[629]);
    declarations.push_back(IFC2X3_types[630]);
    declarations.push_back(IFC2X3_types[631]);
    declarations.push_back(IFC2X3_types[632]);
    declarations.push_back(IFC2X3_types[633]);
    declarations.push_back(IFC2X3_types[634]);
    declarations.push_back(IFC2X3_types[635]);
    declarations.push_back(IFC2X3_types[636]);
    declarations.push_back(IFC2X3_types[637]);
    declarations.push_back(IFC2X3_types[638]);
    declarations.push_back(IFC2X3_types[639]);
    declarations.push_back(IFC2X3_types[640]);
    declarations.push_back(IFC2X3_types[641]);
    declarations.push_back(IFC2X3_types[642]);
    declarations.push_back(IFC2X3_types[643]);
    declarations.push_back(IFC2X3_types[644]);
    declarations.push_back(IFC2X3_types[645]);
    declarations.push_back(IFC2X3_types[646]);
    declarations.push_back(IFC2X3_types[647]);
    declarations.push_back(IFC2X3_types[648]);
    declarations.push_back(IFC2X3_types[649]);
    declarations.push_back(IFC2X3_types[650]);
    declarations.push_back(IFC2X3_types[651]);
    declarations.push_back(IFC2X3_types[652]);
    declarations.push_back(IFC2X3_types[653]);
    declarations.push_back(IFC2X3_types[654]);
    declarations.push_back(IFC2X3_types[655]);
    declarations.push_back(IFC2X3_types[656]);
    declarations.push_back(IFC2X3_types[657]);
    declarations.push_back(IFC2X3_types[658]);
    declarations.push_back(IFC2X3_types[659]);
    declarations.push_back(IFC2X3_types[660]);
    declarations.push_back(IFC2X3_types[661]);
    declarations.push_back(IFC2X3_types[662]);
    declarations.push_back(IFC2X3_types[663]);
    declarations.push_back(IFC2X3_types[664]);
    declarations.push_back(IFC2X3_types[665]);
    declarations.push_back(IFC2X3_types[666]);
    declarations.push_back(IFC2X3_types[667]);
    declarations.push_back(IFC2X3_types[668]);
    declarations.push_back(IFC2X3_types[669]);
    declarations.push_back(IFC2X3_types[670]);
    declarations.push_back(IFC2X3_types[671]);
    declarations.push_back(IFC2X3_types[672]);
    declarations.push_back(IFC2X3_types[673]);
    declarations.push_back(IFC2X3_types[674]);
    declarations.push_back(IFC2X3_types[675]);
    declarations.push_back(IFC2X3_types[676]);
    declarations.push_back(IFC2X3_types[677]);
    declarations.push_back(IFC2X3_types[678]);
    declarations.push_back(IFC2X3_types[679]);
    declarations.push_back(IFC2X3_types[680]);
    declarations.push_back(IFC2X3_types[681]);
    declarations.push_back(IFC2X3_types[682]);
    declarations.push_back(IFC2X3_types[683]);
    declarations.push_back(IFC2X3_types[684]);
    declarations.push_back(IFC2X3_types[685]);
    declarations.push_back(IFC2X3_types[686]);
    declarations.push_back(IFC2X3_types[687]);
    declarations.push_back(IFC2X3_types[688]);
    declarations.push_back(IFC2X3_types[689]);
    declarations.push_back(IFC2X3_types[690]);
    declarations.push_back(IFC2X3_types[691]);
    declarations.push_back(IFC2X3_types[692]);
    declarations.push_back(IFC2X3_types[693]);
    declarations.push_back(IFC2X3_types[694]);
    declarations.push_back(IFC2X3_types[695]);
    declarations.push_back(IFC2X3_types[696]);
    declarations.push_back(IFC2X3_types[697]);
    declarations.push_back(IFC2X3_types[698]);
    declarations.push_back(IFC2X3_types[699]);
    declarations.push_back(IFC2X3_types[700]);
    declarations.push_back(IFC2X3_types[701]);
    declarations.push_back(IFC2X3_types[702]);
    declarations.push_back(IFC2X3_types[703]);
    declarations.push_back(IFC2X3_types[704]);
    declarations.push_back(IFC2X3_types[705]);
    declarations.push_back(IFC2X3_types[706]);
    declarations.push_back(IFC2X3_types[707]);
    declarations.push_back(IFC2X3_types[708]);
    declarations.push_back(IFC2X3_types[709]);
    declarations.push_back(IFC2X3_types[710]);
    declarations.push_back(IFC2X3_types[711]);
    declarations.push_back(IFC2X3_types[712]);
    declarations.push_back(IFC2X3_types[713]);
    declarations.push_back(IFC2X3_types[714]);
    declarations.push_back(IFC2X3_types[715]);
    declarations.push_back(IFC2X3_types[716]);
    declarations.push_back(IFC2X3_types[717]);
    declarations.push_back(IFC2X3_types[718]);
    declarations.push_back(IFC2X3_types[719]);
    declarations.push_back(IFC2X3_types[720]);
    declarations.push_back(IFC2X3_types[721]);
    declarations.push_back(IFC2X3_types[722]);
    declarations.push_back(IFC2X3_types[723]);
    declarations.push_back(IFC2X3_types[724]);
    declarations.push_back(IFC2X3_types[725]);
    declarations.push_back(IFC2X3_types[726]);
    declarations.push_back(IFC2X3_types[727]);
    declarations.push_back(IFC2X3_types[728]);
    declarations.push_back(IFC2X3_types[729]);
    declarations.push_back(IFC2X3_types[730]);
    declarations.push_back(IFC2X3_types[731]);
    declarations.push_back(IFC2X3_types[732]);
    declarations.push_back(IFC2X3_types[733]);
    declarations.push_back(IFC2X3_types[734]);
    declarations.push_back(IFC2X3_types[735]);
    declarations.push_back(IFC2X3_types[736]);
    declarations.push_back(IFC2X3_types[737]);
    declarations.push_back(IFC2X3_types[738]);
    declarations.push_back(IFC2X3_types[739]);
    declarations.push_back(IFC2X3_types[740]);
    declarations.push_back(IFC2X3_types[741]);
    declarations.push_back(IFC2X3_types[742]);
    declarations.push_back(IFC2X3_types[743]);
    declarations.push_back(IFC2X3_types[744]);
    declarations.push_back(IFC2X3_types[745]);
    declarations.push_back(IFC2X3_types[746]);
    declarations.push_back(IFC2X3_types[747]);
    declarations.push_back(IFC2X3_types[748]);
    declarations.push_back(IFC2X3_types[749]);
    declarations.push_back(IFC2X3_types[750]);
    declarations.push_back(IFC2X3_types[751]);
    declarations.push_back(IFC2X3_types[752]);
    declarations.push_back(IFC2X3_types[753]);
    declarations.push_back(IFC2X3_types[754]);
    declarations.push_back(IFC2X3_types[755]);
    declarations.push_back(IFC2X3_types[756]);
    declarations.push_back(IFC2X3_types[757]);
    declarations.push_back(IFC2X3_types[758]);
    declarations.push_back(IFC2X3_types[759]);
    declarations.push_back(IFC2X3_types[760]);
    declarations.push_back(IFC2X3_types[761]);
    declarations.push_back(IFC2X3_types[762]);
    declarations.push_back(IFC2X3_types[763]);
    declarations.push_back(IFC2X3_types[764]);
    declarations.push_back(IFC2X3_types[765]);
    declarations.push_back(IFC2X3_types[766]);
    declarations.push_back(IFC2X3_types[767]);
    declarations.push_back(IFC2X3_types[768]);
    declarations.push_back(IFC2X3_types[769]);
    declarations.push_back(IFC2X3_types[770]);
    declarations.push_back(IFC2X3_types[771]);
    declarations.push_back(IFC2X3_types[772]);
    declarations.push_back(IFC2X3_types[773]);
    declarations.push_back(IFC2X3_types[774]);
    declarations.push_back(IFC2X3_types[775]);
    declarations.push_back(IFC2X3_types[776]);
    declarations.push_back(IFC2X3_types[777]);
    declarations.push_back(IFC2X3_types[778]);
    declarations.push_back(IFC2X3_types[779]);
    declarations.push_back(IFC2X3_types[780]);
    declarations.push_back(IFC2X3_types[781]);
    declarations.push_back(IFC2X3_types[782]);
    declarations.push_back(IFC2X3_types[783]);
    declarations.push_back(IFC2X3_types[784]);
    declarations.push_back(IFC2X3_types[785]);
    declarations.push_back(IFC2X3_types[786]);
    declarations.push_back(IFC2X3_types[787]);
    declarations.push_back(IFC2X3_types[788]);
    declarations.push_back(IFC2X3_types[789]);
    declarations.push_back(IFC2X3_types[790]);
    declarations.push_back(IFC2X3_types[791]);
    declarations.push_back(IFC2X3_types[792]);
    declarations.push_back(IFC2X3_types[793]);
    declarations.push_back(IFC2X3_types[794]);
    declarations.push_back(IFC2X3_types[795]);
    declarations.push_back(IFC2X3_types[796]);
    declarations.push_back(IFC2X3_types[797]);
    declarations.push_back(IFC2X3_types[798]);
    declarations.push_back(IFC2X3_types[799]);
    declarations.push_back(IFC2X3_types[800]);
    declarations.push_back(IFC2X3_types[801]);
    declarations.push_back(IFC2X3_types[802]);
    declarations.push_back(IFC2X3_types[803]);
    declarations.push_back(IFC2X3_types[804]);
    declarations.push_back(IFC2X3_types[805]);
    declarations.push_back(IFC2X3_types[806]);
    declarations.push_back(IFC2X3_types[807]);
    declarations.push_back(IFC2X3_types[808]);
    declarations.push_back(IFC2X3_types[809]);
    declarations.push_back(IFC2X3_types[810]);
    declarations.push_back(IFC2X3_types[811]);
    declarations.push_back(IFC2X3_types[812]);
    declarations.push_back(IFC2X3_types[813]);
    declarations.push_back(IFC2X3_types[814]);
    declarations.push_back(IFC2X3_types[815]);
    declarations.push_back(IFC2X3_types[816]);
    declarations.push_back(IFC2X3_types[817]);
    declarations.push_back(IFC2X3_types[818]);
    declarations.push_back(IFC2X3_types[819]);
    declarations.push_back(IFC2X3_types[820]);
    declarations.push_back(IFC2X3_types[821]);
    declarations.push_back(IFC2X3_types[822]);
    declarations.push_back(IFC2X3_types[823]);
    declarations.push_back(IFC2X3_types[824]);
    declarations.push_back(IFC2X3_types[825]);
    declarations.push_back(IFC2X3_types[826]);
    declarations.push_back(IFC2X3_types[827]);
    declarations.push_back(IFC2X3_types[828]);
    declarations.push_back(IFC2X3_types[829]);
    declarations.push_back(IFC2X3_types[830]);
    declarations.push_back(IFC2X3_types[831]);
    declarations.push_back(IFC2X3_types[832]);
    declarations.push_back(IFC2X3_types[833]);
    declarations.push_back(IFC2X3_types[834]);
    declarations.push_back(IFC2X3_types[835]);
    declarations.push_back(IFC2X3_types[836]);
    declarations.push_back(IFC2X3_types[837]);
    declarations.push_back(IFC2X3_types[838]);
    declarations.push_back(IFC2X3_types[839]);
    declarations.push_back(IFC2X3_types[840]);
    declarations.push_back(IFC2X3_types[841]);
    declarations.push_back(IFC2X3_types[842]);
    declarations.push_back(IFC2X3_types[843]);
    declarations.push_back(IFC2X3_types[844]);
    declarations.push_back(IFC2X3_types[845]);
    declarations.push_back(IFC2X3_types[846]);
    declarations.push_back(IFC2X3_types[847]);
    declarations.push_back(IFC2X3_types[848]);
    declarations.push_back(IFC2X3_types[849]);
    declarations.push_back(IFC2X3_types[850]);
    declarations.push_back(IFC2X3_types[851]);
    declarations.push_back(IFC2X3_types[852]);
    declarations.push_back(IFC2X3_types[853]);
    declarations.push_back(IFC2X3_types[854]);
    declarations.push_back(IFC2X3_types[855]);
    declarations.push_back(IFC2X3_types[856]);
    declarations.push_back(IFC2X3_types[857]);
    declarations.push_back(IFC2X3_types[858]);
    declarations.push_back(IFC2X3_types[859]);
    declarations.push_back(IFC2X3_types[860]);
    declarations.push_back(IFC2X3_types[861]);
    declarations.push_back(IFC2X3_types[862]);
    declarations.push_back(IFC2X3_types[863]);
    declarations.push_back(IFC2X3_types[864]);
    declarations.push_back(IFC2X3_types[865]);
    declarations.push_back(IFC2X3_types[866]);
    declarations.push_back(IFC2X3_types[867]);
    declarations.push_back(IFC2X3_types[868]);
    declarations.push_back(IFC2X3_types[869]);
    declarations.push_back(IFC2X3_types[870]);
    declarations.push_back(IFC2X3_types[871]);
    declarations.push_back(IFC2X3_types[872]);
    declarations.push_back(IFC2X3_types[873]);
    declarations.push_back(IFC2X3_types[874]);
    declarations.push_back(IFC2X3_types[875]);
    declarations.push_back(IFC2X3_types[876]);
    declarations.push_back(IFC2X3_types[877]);
    declarations.push_back(IFC2X3_types[878]);
    declarations.push_back(IFC2X3_types[879]);
    declarations.push_back(IFC2X3_types[880]);
    declarations.push_back(IFC2X3_types[881]);
    declarations.push_back(IFC2X3_types[882]);
    declarations.push_back(IFC2X3_types[883]);
    declarations.push_back(IFC2X3_types[884]);
    declarations.push_back(IFC2X3_types[885]);
    declarations.push_back(IFC2X3_types[886]);
    declarations.push_back(IFC2X3_types[887]);
    declarations.push_back(IFC2X3_types[888]);
    declarations.push_back(IFC2X3_types[889]);
    declarations.push_back(IFC2X3_types[890]);
    declarations.push_back(IFC2X3_types[891]);
    declarations.push_back(IFC2X3_types[892]);
    declarations.push_back(IFC2X3_types[893]);
    declarations.push_back(IFC2X3_types[894]);
    declarations.push_back(IFC2X3_types[895]);
    declarations.push_back(IFC2X3_types[896]);
    declarations.push_back(IFC2X3_types[897]);
    declarations.push_back(IFC2X3_types[898]);
    declarations.push_back(IFC2X3_types[899]);
    declarations.push_back(IFC2X3_types[900]);
    declarations.push_back(IFC2X3_types[901]);
    declarations.push_back(IFC2X3_types[902]);
    declarations.push_back(IFC2X3_types[903]);
    declarations.push_back(IFC2X3_types[904]);
    declarations.push_back(IFC2X3_types[905]);
    declarations.push_back(IFC2X3_types[906]);
    declarations.push_back(IFC2X3_types[907]);
    declarations.push_back(IFC2X3_types[908]);
    declarations.push_back(IFC2X3_types[909]);
    declarations.push_back(IFC2X3_types[910]);
    declarations.push_back(IFC2X3_types[911]);
    declarations.push_back(IFC2X3_types[912]);
    declarations.push_back(IFC2X3_types[913]);
    declarations.push_back(IFC2X3_types[914]);
    declarations.push_back(IFC2X3_types[915]);
    declarations.push_back(IFC2X3_types[916]);
    declarations.push_back(IFC2X3_types[917]);
    declarations.push_back(IFC2X3_types[918]);
    declarations.push_back(IFC2X3_types[919]);
    declarations.push_back(IFC2X3_types[920]);
    declarations.push_back(IFC2X3_types[921]);
    declarations.push_back(IFC2X3_types[922]);
    declarations.push_back(IFC2X3_types[923]);
    declarations.push_back(IFC2X3_types[924]);
    declarations.push_back(IFC2X3_types[925]);
    declarations.push_back(IFC2X3_types[926]);
    declarations.push_back(IFC2X3_types[927]);
    declarations.push_back(IFC2X3_types[928]);
    declarations.push_back(IFC2X3_types[929]);
    declarations.push_back(IFC2X3_types[930]);
    declarations.push_back(IFC2X3_types[931]);
    declarations.push_back(IFC2X3_types[932]);
    declarations.push_back(IFC2X3_types[933]);
    declarations.push_back(IFC2X3_types[934]);
    declarations.push_back(IFC2X3_types[935]);
    declarations.push_back(IFC2X3_types[936]);
    declarations.push_back(IFC2X3_types[937]);
    declarations.push_back(IFC2X3_types[938]);
    declarations.push_back(IFC2X3_types[939]);
    declarations.push_back(IFC2X3_types[940]);
    declarations.push_back(IFC2X3_types[941]);
    declarations.push_back(IFC2X3_types[942]);
    declarations.push_back(IFC2X3_types[943]);
    declarations.push_back(IFC2X3_types[944]);
    declarations.push_back(IFC2X3_types[945]);
    declarations.push_back(IFC2X3_types[946]);
    declarations.push_back(IFC2X3_types[947]);
    declarations.push_back(IFC2X3_types[948]);
    declarations.push_back(IFC2X3_types[949]);
    declarations.push_back(IFC2X3_types[950]);
    declarations.push_back(IFC2X3_types[951]);
    declarations.push_back(IFC2X3_types[952]);
    declarations.push_back(IFC2X3_types[953]);
    declarations.push_back(IFC2X3_types[954]);
    declarations.push_back(IFC2X3_types[955]);
    declarations.push_back(IFC2X3_types[956]);
    declarations.push_back(IFC2X3_types[957]);
    declarations.push_back(IFC2X3_types[958]);
    declarations.push_back(IFC2X3_types[959]);
    declarations.push_back(IFC2X3_types[960]);
    declarations.push_back(IFC2X3_types[961]);
    declarations.push_back(IFC2X3_types[962]);
    declarations.push_back(IFC2X3_types[963]);
    declarations.push_back(IFC2X3_types[964]);
    declarations.push_back(IFC2X3_types[965]);
    declarations.push_back(IFC2X3_types[966]);
    declarations.push_back(IFC2X3_types[967]);
    declarations.push_back(IFC2X3_types[968]);
    declarations.push_back(IFC2X3_types[969]);
    declarations.push_back(IFC2X3_types[970]);
    declarations.push_back(IFC2X3_types[971]);
    declarations.push_back(IFC2X3_types[972]);
    declarations.push_back(IFC2X3_types[973]);
    declarations.push_back(IFC2X3_types[974]);
    declarations.push_back(IFC2X3_types[975]);
    declarations.push_back(IFC2X3_types[976]);
    declarations.push_back(IFC2X3_types[977]);
    declarations.push_back(IFC2X3_types[978]);
    declarations.push_back(IFC2X3_types[979]);
    return new schema_definition("IFC2X3", declarations, new IFC2X3_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
static std::unique_ptr<schema_definition> schema;

void Ifc2x3::clear_schema() {
    schema.reset();
}

const schema_definition& Ifc2x3::get_schema() {
    if (!schema) {
        schema.reset(IFC2X3_populate_schema());
    }
    return *schema;
}

