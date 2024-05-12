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

declaration* IFC4X1_types[1201] = {nullptr};

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


#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4X1_populate_schema() {
    IFC4X1_types[0] = new type_declaration("IfcAbsorbedDoseMeasure", 0, new simple_type(simple_type::real_type));
    IFC4X1_types[1] = new type_declaration("IfcAccelerationMeasure", 1, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("EMAIL");
        items.push_back("FAX");
        items.push_back("NOTDEFINED");
        items.push_back("PHONE");
        items.push_back("POST");
        items.push_back("USERDEFINED");
        items.push_back("VERBAL");
        IFC4X1_types[3] = new enumeration_type("IfcActionRequestTypeEnum", 3, items);
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
        IFC4X1_types[4] = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IFC4X1_types[5] = new enumeration_type("IfcActionTypeEnum", 5, items);
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
        IFC4X1_types[11] = new enumeration_type("IfcActuatorTypeEnum", 11, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4X1_types[13] = new enumeration_type("IfcAddressTypeEnum", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IFC4X1_types[20] = new enumeration_type("IfcAirTerminalBoxTypeEnum", 20, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("DIFFUSER");
        items.push_back("GRILLE");
        items.push_back("LOUVRE");
        items.push_back("NOTDEFINED");
        items.push_back("REGISTER");
        items.push_back("USERDEFINED");
        IFC4X1_types[22] = new enumeration_type("IfcAirTerminalTypeEnum", 22, items);
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
        IFC4X1_types[25] = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 25, items);
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
        IFC4X1_types[28] = new enumeration_type("IfcAlarmTypeEnum", 28, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[39] = new enumeration_type("IfcAlignmentTypeEnum", 39, items);
    }
    IFC4X1_types[40] = new type_declaration("IfcAmountOfSubstanceMeasure", 40, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IFC4X1_types[41] = new enumeration_type("IfcAnalysisModelTypeEnum", 41, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IFC4X1_types[42] = new enumeration_type("IfcAnalysisTheoryTypeEnum", 42, items);
    }
    IFC4X1_types[43] = new type_declaration("IfcAngularVelocityMeasure", 43, new simple_type(simple_type::real_type));
    IFC4X1_types[55] = new type_declaration("IfcAreaDensityMeasure", 55, new simple_type(simple_type::real_type));
    IFC4X1_types[56] = new type_declaration("IfcAreaMeasure", 56, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IFC4X1_types[57] = new enumeration_type("IfcArithmeticOperatorEnum", 57, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IFC4X1_types[58] = new enumeration_type("IfcAssemblyPlaceEnum", 58, items);
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
        IFC4X1_types[63] = new enumeration_type("IfcAudioVisualApplianceTypeEnum", 63, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IFC4X1_types[97] = new enumeration_type("IfcBSplineCurveForm", 97, items);
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
        IFC4X1_types[100] = new enumeration_type("IfcBSplineSurfaceForm", 100, items);
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
        IFC4X1_types[71] = new enumeration_type("IfcBeamTypeEnum", 71, items);
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
        IFC4X1_types[72] = new enumeration_type("IfcBenchmarkEnum", 72, items);
    }
    IFC4X1_types[74] = new type_declaration("IfcBinary", 74, new simple_type(simple_type::binary_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IFC4X1_types[79] = new enumeration_type("IfcBoilerTypeEnum", 79, items);
    }
    IFC4X1_types[80] = new type_declaration("IfcBoolean", 80, new simple_type(simple_type::boolean_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IFC4X1_types[83] = new enumeration_type("IfcBooleanOperator", 83, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("INSULATION");
        items.push_back("NOTDEFINED");
        items.push_back("PRECASTPANEL");
        items.push_back("USERDEFINED");
        IFC4X1_types[106] = new enumeration_type("IfcBuildingElementPartTypeEnum", 106, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("PARTIAL");
        items.push_back("PROVISIONFORSPACE");
        items.push_back("PROVISIONFORVOID");
        items.push_back("USERDEFINED");
        IFC4X1_types[109] = new enumeration_type("IfcBuildingElementProxyTypeEnum", 109, items);
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
        IFC4X1_types[113] = new enumeration_type("IfcBuildingSystemTypeEnum", 113, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[116] = new enumeration_type("IfcBurnerTypeEnum", 116, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IFC4X1_types[119] = new enumeration_type("IfcCableCarrierFittingTypeEnum", 119, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[122] = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 122, items);
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
        IFC4X1_types[125] = new enumeration_type("IfcCableFittingTypeEnum", 125, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BUSBARSEGMENT");
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("CORESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[128] = new enumeration_type("IfcCableSegmentTypeEnum", 128, items);
    }
    IFC4X1_types[129] = new type_declaration("IfcCardinalPointReference", 129, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("NOCHANGE");
        items.push_back("NOTDEFINED");
        IFC4X1_types[140] = new enumeration_type("IfcChangeActionEnum", 140, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IFC4X1_types[143] = new enumeration_type("IfcChillerTypeEnum", 143, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[146] = new enumeration_type("IfcChimneyTypeEnum", 146, items);
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
        IFC4X1_types[160] = new enumeration_type("IfcCoilTypeEnum", 160, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("PILASTER");
        items.push_back("USERDEFINED");
        IFC4X1_types[169] = new enumeration_type("IfcColumnTypeEnum", 169, items);
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
        IFC4X1_types[172] = new enumeration_type("IfcCommunicationsApplianceTypeEnum", 172, items);
    }
    IFC4X1_types[173] = new type_declaration("IfcComplexNumber", 173, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("P_COMPLEX");
        items.push_back("Q_COMPLEX");
        IFC4X1_types[176] = new enumeration_type("IfcComplexPropertyTemplateTypeEnum", 176, items);
    }
    IFC4X1_types[181] = new type_declaration("IfcCompoundPlaneAngleMeasure", 181, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
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
        IFC4X1_types[184] = new enumeration_type("IfcCompressorTypeEnum", 184, items);
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
        IFC4X1_types[187] = new enumeration_type("IfcCondenserTypeEnum", 187, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IFC4X1_types[195] = new enumeration_type("IfcConnectionTypeEnum", 195, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IFC4X1_types[198] = new enumeration_type("IfcConstraintEnum", 198, items);
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
        IFC4X1_types[201] = new enumeration_type("IfcConstructionEquipmentResourceTypeEnum", 201, items);
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
        IFC4X1_types[204] = new enumeration_type("IfcConstructionMaterialResourceTypeEnum", 204, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ASSEMBLY");
        items.push_back("FORMWORK");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[207] = new enumeration_type("IfcConstructionProductResourceTypeEnum", 207, items);
    }
    IFC4X1_types[211] = new type_declaration("IfcContextDependentMeasure", 211, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("FLOATING");
        items.push_back("MULTIPOSITION");
        items.push_back("NOTDEFINED");
        items.push_back("PROGRAMMABLE");
        items.push_back("PROPORTIONAL");
        items.push_back("TWOPOSITION");
        items.push_back("USERDEFINED");
        IFC4X1_types[216] = new enumeration_type("IfcControllerTypeEnum", 216, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IFC4X1_types[221] = new enumeration_type("IfcCooledBeamTypeEnum", 221, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[224] = new enumeration_type("IfcCoolingTowerTypeEnum", 224, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[229] = new enumeration_type("IfcCostItemTypeEnum", 229, items);
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
        IFC4X1_types[231] = new enumeration_type("IfcCostScheduleTypeEnum", 231, items);
    }
    IFC4X1_types[233] = new type_declaration("IfcCountMeasure", 233, new simple_type(simple_type::number_type));
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
        IFC4X1_types[236] = new enumeration_type("IfcCoveringTypeEnum", 236, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4X1_types[239] = new enumeration_type("IfcCrewResourceTypeEnum", 239, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[247] = new enumeration_type("IfcCurtainWallTypeEnum", 247, items);
    }
    IFC4X1_types[248] = new type_declaration("IfcCurvatureMeasure", 248, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LINEAR");
        items.push_back("LOG_LINEAR");
        items.push_back("LOG_LOG");
        items.push_back("NOTDEFINED");
        IFC4X1_types[253] = new enumeration_type("IfcCurveInterpolationEnum", 253, items);
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
        IFC4X1_types[265] = new enumeration_type("IfcDamperTypeEnum", 265, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IFC4X1_types[266] = new enumeration_type("IfcDataOriginEnum", 266, items);
    }
    IFC4X1_types[267] = new type_declaration("IfcDate", 267, new simple_type(simple_type::string_type));
    IFC4X1_types[268] = new type_declaration("IfcDateTime", 268, new simple_type(simple_type::string_type));
    IFC4X1_types[269] = new type_declaration("IfcDayInMonthNumber", 269, new simple_type(simple_type::integer_type));
    IFC4X1_types[270] = new type_declaration("IfcDayInWeekNumber", 270, new simple_type(simple_type::integer_type));
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
        IFC4X1_types[276] = new enumeration_type("IfcDerivedUnitEnum", 276, items);
    }
    IFC4X1_types[277] = new type_declaration("IfcDescriptiveMeasure", 277, new simple_type(simple_type::string_type));
    IFC4X1_types[279] = new type_declaration("IfcDimensionCount", 279, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4X1_types[281] = new enumeration_type("IfcDirectionSenseEnum", 281, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ANCHORPLATE");
        items.push_back("BRACKET");
        items.push_back("NOTDEFINED");
        items.push_back("SHOE");
        items.push_back("USERDEFINED");
        IFC4X1_types[284] = new enumeration_type("IfcDiscreteAccessoryTypeEnum", 284, items);
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
        IFC4X1_types[288] = new enumeration_type("IfcDistributionChamberElementTypeEnum", 288, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLE");
        items.push_back("CABLECARRIER");
        items.push_back("DUCT");
        items.push_back("NOTDEFINED");
        items.push_back("PIPE");
        items.push_back("USERDEFINED");
        IFC4X1_types[297] = new enumeration_type("IfcDistributionPortTypeEnum", 297, items);
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
        IFC4X1_types[299] = new enumeration_type("IfcDistributionSystemEnum", 299, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IFC4X1_types[300] = new enumeration_type("IfcDocumentConfidentialityEnum", 300, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IFC4X1_types[305] = new enumeration_type("IfcDocumentStatusEnum", 305, items);
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
        IFC4X1_types[308] = new enumeration_type("IfcDoorPanelOperationEnum", 308, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IFC4X1_types[309] = new enumeration_type("IfcDoorPanelPositionEnum", 309, items);
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
        IFC4X1_types[313] = new enumeration_type("IfcDoorStyleConstructionEnum", 313, items);
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
        IFC4X1_types[314] = new enumeration_type("IfcDoorStyleOperationEnum", 314, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DOOR");
        items.push_back("GATE");
        items.push_back("NOTDEFINED");
        items.push_back("TRAPDOOR");
        items.push_back("USERDEFINED");
        IFC4X1_types[316] = new enumeration_type("IfcDoorTypeEnum", 316, items);
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
        IFC4X1_types[317] = new enumeration_type("IfcDoorTypeOperationEnum", 317, items);
    }
    IFC4X1_types[318] = new type_declaration("IfcDoseEquivalentMeasure", 318, new simple_type(simple_type::real_type));
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
        IFC4X1_types[323] = new enumeration_type("IfcDuctFittingTypeEnum", 323, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IFC4X1_types[326] = new enumeration_type("IfcDuctSegmentTypeEnum", 326, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IFC4X1_types[329] = new enumeration_type("IfcDuctSilencerTypeEnum", 329, items);
    }
    IFC4X1_types[330] = new type_declaration("IfcDuration", 330, new simple_type(simple_type::string_type));
    IFC4X1_types[331] = new type_declaration("IfcDynamicViscosityMeasure", 331, new simple_type(simple_type::real_type));
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
        IFC4X1_types[337] = new enumeration_type("IfcElectricApplianceTypeEnum", 337, items);
    }
    IFC4X1_types[338] = new type_declaration("IfcElectricCapacitanceMeasure", 338, new simple_type(simple_type::real_type));
    IFC4X1_types[339] = new type_declaration("IfcElectricChargeMeasure", 339, new simple_type(simple_type::real_type));
    IFC4X1_types[340] = new type_declaration("IfcElectricConductanceMeasure", 340, new simple_type(simple_type::real_type));
    IFC4X1_types[341] = new type_declaration("IfcElectricCurrentMeasure", 341, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONSUMERUNIT");
        items.push_back("DISTRIBUTIONBOARD");
        items.push_back("MOTORCONTROLCENTRE");
        items.push_back("NOTDEFINED");
        items.push_back("SWITCHBOARD");
        items.push_back("USERDEFINED");
        IFC4X1_types[344] = new enumeration_type("IfcElectricDistributionBoardTypeEnum", 344, items);
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
        IFC4X1_types[347] = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 347, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CHP");
        items.push_back("ENGINEGENERATOR");
        items.push_back("NOTDEFINED");
        items.push_back("STANDALONE");
        items.push_back("USERDEFINED");
        IFC4X1_types[350] = new enumeration_type("IfcElectricGeneratorTypeEnum", 350, items);
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
        IFC4X1_types[353] = new enumeration_type("IfcElectricMotorTypeEnum", 353, items);
    }
    IFC4X1_types[354] = new type_declaration("IfcElectricResistanceMeasure", 354, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IFC4X1_types[357] = new enumeration_type("IfcElectricTimeControlTypeEnum", 357, items);
    }
    IFC4X1_types[358] = new type_declaration("IfcElectricVoltageMeasure", 358, new simple_type(simple_type::real_type));
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
        IFC4X1_types[363] = new enumeration_type("IfcElementAssemblyTypeEnum", 363, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IFC4X1_types[366] = new enumeration_type("IfcElementCompositionEnum", 366, items);
    }
    IFC4X1_types[373] = new type_declaration("IfcEnergyMeasure", 373, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("EXTERNALCOMBUSTION");
        items.push_back("INTERNALCOMBUSTION");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[376] = new enumeration_type("IfcEngineTypeEnum", 376, items);
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
        IFC4X1_types[379] = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 379, items);
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
        IFC4X1_types[382] = new enumeration_type("IfcEvaporatorTypeEnum", 382, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EVENTCOMPLEX");
        items.push_back("EVENTMESSAGE");
        items.push_back("EVENTRULE");
        items.push_back("EVENTTIME");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[385] = new enumeration_type("IfcEventTriggerTypeEnum", 385, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ENDEVENT");
        items.push_back("INTERMEDIATEEVENT");
        items.push_back("NOTDEFINED");
        items.push_back("STARTEVENT");
        items.push_back("USERDEFINED");
        IFC4X1_types[387] = new enumeration_type("IfcEventTypeEnum", 387, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[396] = new enumeration_type("IfcExternalSpatialElementTypeEnum", 396, items);
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
        IFC4X1_types[410] = new enumeration_type("IfcFanTypeEnum", 410, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GLUE");
        items.push_back("MORTAR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WELD");
        IFC4X1_types[413] = new enumeration_type("IfcFastenerTypeEnum", 413, items);
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
        IFC4X1_types[423] = new enumeration_type("IfcFilterTypeEnum", 423, items);
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
        IFC4X1_types[426] = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 426, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IFC4X1_types[430] = new enumeration_type("IfcFlowDirectionEnum", 430, items);
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
        IFC4X1_types[435] = new enumeration_type("IfcFlowInstrumentTypeEnum", 435, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ENERGYMETER");
        items.push_back("GASMETER");
        items.push_back("NOTDEFINED");
        items.push_back("OILMETER");
        items.push_back("USERDEFINED");
        items.push_back("WATERMETER");
        IFC4X1_types[438] = new enumeration_type("IfcFlowMeterTypeEnum", 438, items);
    }
    IFC4X1_types[449] = new type_declaration("IfcFontStyle", 449, new simple_type(simple_type::string_type));
    IFC4X1_types[450] = new type_declaration("IfcFontVariant", 450, new simple_type(simple_type::string_type));
    IFC4X1_types[451] = new type_declaration("IfcFontWeight", 451, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CAISSON_FOUNDATION");
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IFC4X1_types[454] = new enumeration_type("IfcFootingTypeEnum", 454, items);
    }
    IFC4X1_types[455] = new type_declaration("IfcForceMeasure", 455, new simple_type(simple_type::real_type));
    IFC4X1_types[456] = new type_declaration("IfcFrequencyMeasure", 456, new simple_type(simple_type::real_type));
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
        IFC4X1_types[461] = new enumeration_type("IfcFurnitureTypeEnum", 461, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("TERRAIN");
        items.push_back("USERDEFINED");
        IFC4X1_types[464] = new enumeration_type("IfcGeographicElementTypeEnum", 464, items);
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
        IFC4X1_types[466] = new enumeration_type("IfcGeometricProjectionEnum", 466, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IFC4X1_types[473] = new enumeration_type("IfcGlobalOrLocalEnum", 473, items);
    }
    IFC4X1_types[472] = new type_declaration("IfcGloballyUniqueId", 472, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("IRREGULAR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIAL");
        items.push_back("RECTANGULAR");
        items.push_back("TRIANGULAR");
        items.push_back("USERDEFINED");
        IFC4X1_types[478] = new enumeration_type("IfcGridTypeEnum", 478, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IFC4X1_types[484] = new enumeration_type("IfcHeatExchangerTypeEnum", 484, items);
    }
    IFC4X1_types[485] = new type_declaration("IfcHeatFluxDensityMeasure", 485, new simple_type(simple_type::real_type));
    IFC4X1_types[486] = new type_declaration("IfcHeatingValueMeasure", 486, new simple_type(simple_type::real_type));
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
        IFC4X1_types[489] = new enumeration_type("IfcHumidifierTypeEnum", 489, items);
    }
    IFC4X1_types[490] = new type_declaration("IfcIdentifier", 490, new simple_type(simple_type::string_type));
    IFC4X1_types[491] = new type_declaration("IfcIlluminanceMeasure", 491, new simple_type(simple_type::real_type));
    IFC4X1_types[499] = new type_declaration("IfcInductanceMeasure", 499, new simple_type(simple_type::real_type));
    IFC4X1_types[500] = new type_declaration("IfcInteger", 500, new simple_type(simple_type::integer_type));
    IFC4X1_types[501] = new type_declaration("IfcIntegerCountRateMeasure", 501, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CYCLONIC");
        items.push_back("GREASE");
        items.push_back("NOTDEFINED");
        items.push_back("OIL");
        items.push_back("PETROL");
        items.push_back("USERDEFINED");
        IFC4X1_types[504] = new enumeration_type("IfcInterceptorTypeEnum", 504, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IFC4X1_types[505] = new enumeration_type("IfcInternalOrExternalEnum", 505, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IFC4X1_types[508] = new enumeration_type("IfcInventoryTypeEnum", 508, items);
    }
    IFC4X1_types[509] = new type_declaration("IfcIonConcentrationMeasure", 509, new simple_type(simple_type::real_type));
    IFC4X1_types[513] = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 513, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DATA");
        items.push_back("NOTDEFINED");
        items.push_back("POWER");
        items.push_back("USERDEFINED");
        IFC4X1_types[516] = new enumeration_type("IfcJunctionBoxTypeEnum", 516, items);
    }
    IFC4X1_types[517] = new type_declaration("IfcKinematicViscosityMeasure", 517, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("PIECEWISE_BEZIER_KNOTS");
        items.push_back("QUASI_UNIFORM_KNOTS");
        items.push_back("UNIFORM_KNOTS");
        items.push_back("UNSPECIFIED");
        IFC4X1_types[518] = new enumeration_type("IfcKnotType", 518, items);
    }
    IFC4X1_types[519] = new type_declaration("IfcLabel", 519, new simple_type(simple_type::string_type));
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
        IFC4X1_types[522] = new enumeration_type("IfcLaborResourceTypeEnum", 522, items);
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
        IFC4X1_types[526] = new enumeration_type("IfcLampTypeEnum", 526, items);
    }
    IFC4X1_types[527] = new type_declaration("IfcLanguageId", 527, new named_type(IFC4X1_types[490]));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IFC4X1_types[529] = new enumeration_type("IfcLayerSetDirectionEnum", 529, items);
    }
    IFC4X1_types[530] = new type_declaration("IfcLengthMeasure", 530, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IFC4X1_types[534] = new enumeration_type("IfcLightDistributionCurveEnum", 534, items);
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
        IFC4X1_types[537] = new enumeration_type("IfcLightEmissionSourceEnum", 537, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("SECURITYLIGHTING");
        items.push_back("USERDEFINED");
        IFC4X1_types[540] = new enumeration_type("IfcLightFixtureTypeEnum", 540, items);
    }
    IFC4X1_types[549] = new type_declaration("IfcLinearForceMeasure", 549, new simple_type(simple_type::real_type));
    IFC4X1_types[550] = new type_declaration("IfcLinearMomentMeasure", 550, new simple_type(simple_type::real_type));
    IFC4X1_types[553] = new type_declaration("IfcLinearStiffnessMeasure", 553, new simple_type(simple_type::real_type));
    IFC4X1_types[554] = new type_declaration("IfcLinearVelocityMeasure", 554, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[557] = new enumeration_type("IfcLoadGroupTypeEnum", 557, items);
    }
    IFC4X1_types[559] = new type_declaration("IfcLogical", 559, new simple_type(simple_type::logical_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALNOTAND");
        items.push_back("LOGICALNOTOR");
        items.push_back("LOGICALOR");
        items.push_back("LOGICALXOR");
        IFC4X1_types[560] = new enumeration_type("IfcLogicalOperatorEnum", 560, items);
    }
    IFC4X1_types[563] = new type_declaration("IfcLuminousFluxMeasure", 563, new simple_type(simple_type::real_type));
    IFC4X1_types[564] = new type_declaration("IfcLuminousIntensityDistributionMeasure", 564, new simple_type(simple_type::real_type));
    IFC4X1_types[565] = new type_declaration("IfcLuminousIntensityMeasure", 565, new simple_type(simple_type::real_type));
    IFC4X1_types[566] = new type_declaration("IfcMagneticFluxDensityMeasure", 566, new simple_type(simple_type::real_type));
    IFC4X1_types[567] = new type_declaration("IfcMagneticFluxMeasure", 567, new simple_type(simple_type::real_type));
    IFC4X1_types[571] = new type_declaration("IfcMassDensityMeasure", 571, new simple_type(simple_type::real_type));
    IFC4X1_types[572] = new type_declaration("IfcMassFlowRateMeasure", 572, new simple_type(simple_type::real_type));
    IFC4X1_types[573] = new type_declaration("IfcMassMeasure", 573, new simple_type(simple_type::real_type));
    IFC4X1_types[574] = new type_declaration("IfcMassPerLengthMeasure", 574, new simple_type(simple_type::real_type));
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
        IFC4X1_types[599] = new enumeration_type("IfcMechanicalFastenerTypeEnum", 599, items);
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
        IFC4X1_types[602] = new enumeration_type("IfcMedicalDeviceTypeEnum", 602, items);
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
        IFC4X1_types[606] = new enumeration_type("IfcMemberTypeEnum", 606, items);
    }
    IFC4X1_types[610] = new type_declaration("IfcModulusOfElasticityMeasure", 610, new simple_type(simple_type::real_type));
    IFC4X1_types[611] = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 611, new simple_type(simple_type::real_type));
    IFC4X1_types[612] = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 612, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[612]);
        IFC4X1_types[613] = new select_type("IfcModulusOfRotationalSubgradeReactionSelect", 613, items);
    }
    IFC4X1_types[614] = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 614, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[614]);
        IFC4X1_types[615] = new select_type("IfcModulusOfSubgradeReactionSelect", 615, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[611]);
        IFC4X1_types[616] = new select_type("IfcModulusOfTranslationalSubgradeReactionSelect", 616, items);
    }
    IFC4X1_types[617] = new type_declaration("IfcMoistureDiffusivityMeasure", 617, new simple_type(simple_type::real_type));
    IFC4X1_types[618] = new type_declaration("IfcMolecularWeightMeasure", 618, new simple_type(simple_type::real_type));
    IFC4X1_types[619] = new type_declaration("IfcMomentOfInertiaMeasure", 619, new simple_type(simple_type::real_type));
    IFC4X1_types[620] = new type_declaration("IfcMonetaryMeasure", 620, new simple_type(simple_type::real_type));
    IFC4X1_types[622] = new type_declaration("IfcMonthInYearNumber", 622, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[625] = new enumeration_type("IfcMotorConnectionTypeEnum", 625, items);
    }
    IFC4X1_types[627] = new type_declaration("IfcNonNegativeLengthMeasure", 627, new named_type(IFC4X1_types[530]));
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IFC4X1_types[629] = new enumeration_type("IfcNullStyle", 629, items);
    }
    IFC4X1_types[630] = new type_declaration("IfcNumericMeasure", 630, new simple_type(simple_type::number_type));
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
        IFC4X1_types[637] = new enumeration_type("IfcObjectTypeEnum", 637, items);
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
        IFC4X1_types[634] = new enumeration_type("IfcObjectiveEnum", 634, items);
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
        IFC4X1_types[639] = new enumeration_type("IfcOccupantTypeEnum", 639, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OPENING");
        items.push_back("RECESS");
        items.push_back("USERDEFINED");
        IFC4X1_types[645] = new enumeration_type("IfcOpeningElementTypeEnum", 645, items);
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
        IFC4X1_types[655] = new enumeration_type("IfcOutletTypeEnum", 655, items);
    }
    IFC4X1_types[669] = new type_declaration("IfcPHMeasure", 669, new simple_type(simple_type::real_type));
    IFC4X1_types[658] = new type_declaration("IfcParameterValue", 658, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[662] = new enumeration_type("IfcPerformanceHistoryTypeEnum", 662, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IFC4X1_types[663] = new enumeration_type("IfcPermeableCoveringOperationEnum", 663, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACCESS");
        items.push_back("BUILDING");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4X1_types[666] = new enumeration_type("IfcPermitTypeEnum", 666, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IFC4X1_types[671] = new enumeration_type("IfcPhysicalOrVirtualEnum", 671, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IFC4X1_types[675] = new enumeration_type("IfcPileConstructionEnum", 675, items);
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
        IFC4X1_types[677] = new enumeration_type("IfcPileTypeEnum", 677, items);
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
        IFC4X1_types[680] = new enumeration_type("IfcPipeFittingTypeEnum", 680, items);
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
        IFC4X1_types[683] = new enumeration_type("IfcPipeSegmentTypeEnum", 683, items);
    }
    IFC4X1_types[688] = new type_declaration("IfcPlanarForceMeasure", 688, new simple_type(simple_type::real_type));
    IFC4X1_types[690] = new type_declaration("IfcPlaneAngleMeasure", 690, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IFC4X1_types[694] = new enumeration_type("IfcPlateTypeEnum", 694, items);
    }
    IFC4X1_types[705] = new type_declaration("IfcPositiveInteger", 705, new named_type(IFC4X1_types[500]));
    IFC4X1_types[706] = new type_declaration("IfcPositiveLengthMeasure", 706, new named_type(IFC4X1_types[530]));
    IFC4X1_types[707] = new type_declaration("IfcPositivePlaneAngleMeasure", 707, new named_type(IFC4X1_types[690]));
    IFC4X1_types[710] = new type_declaration("IfcPowerMeasure", 710, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CURVE3D");
        items.push_back("PCURVE_S1");
        items.push_back("PCURVE_S2");
        IFC4X1_types[717] = new enumeration_type("IfcPreferredSurfaceCurveRepresentation", 717, items);
    }
    IFC4X1_types[718] = new type_declaration("IfcPresentableText", 718, new simple_type(simple_type::string_type));
    IFC4X1_types[725] = new type_declaration("IfcPressureMeasure", 725, new simple_type(simple_type::real_type));
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
        IFC4X1_types[728] = new enumeration_type("IfcProcedureTypeEnum", 728, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IFC4X1_types[738] = new enumeration_type("IfcProfileTypeEnum", 738, items);
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
        IFC4X1_types[746] = new enumeration_type("IfcProjectOrderTypeEnum", 746, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IFC4X1_types[741] = new enumeration_type("IfcProjectedOrTrueLengthEnum", 741, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[743] = new enumeration_type("IfcProjectionElementTypeEnum", 743, items);
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
        IFC4X1_types[761] = new enumeration_type("IfcPropertySetTemplateTypeEnum", 761, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ELECTROMAGNETIC");
        items.push_back("ELECTRONIC");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENT");
        items.push_back("THERMAL");
        items.push_back("USERDEFINED");
        IFC4X1_types[769] = new enumeration_type("IfcProtectiveDeviceTrippingUnitTypeEnum", 769, items);
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
        IFC4X1_types[771] = new enumeration_type("IfcProtectiveDeviceTypeEnum", 771, items);
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
        IFC4X1_types[775] = new enumeration_type("IfcPumpTypeEnum", 775, items);
    }
    IFC4X1_types[783] = new type_declaration("IfcRadioActivityMeasure", 783, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[786] = new enumeration_type("IfcRailingTypeEnum", 786, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IFC4X1_types[790] = new enumeration_type("IfcRampFlightTypeEnum", 790, items);
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
        IFC4X1_types[792] = new enumeration_type("IfcRampTypeEnum", 792, items);
    }
    IFC4X1_types[793] = new type_declaration("IfcRatioMeasure", 793, new simple_type(simple_type::real_type));
    IFC4X1_types[796] = new type_declaration("IfcReal", 796, new simple_type(simple_type::real_type));
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
        IFC4X1_types[802] = new enumeration_type("IfcRecurrenceTypeEnum", 802, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("KILOPOINT");
        items.push_back("MILEPOINT");
        items.push_back("NOTDEFINED");
        items.push_back("STATION");
        items.push_back("USERDEFINED");
        IFC4X1_types[805] = new enumeration_type("IfcReferentTypeEnum", 805, items);
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
        IFC4X1_types[806] = new enumeration_type("IfcReflectanceMethodEnum", 806, items);
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
        IFC4X1_types[811] = new enumeration_type("IfcReinforcingBarRoleEnum", 811, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IFC4X1_types[812] = new enumeration_type("IfcReinforcingBarSurfaceEnum", 812, items);
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
        IFC4X1_types[814] = new enumeration_type("IfcReinforcingBarTypeEnum", 814, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[819] = new enumeration_type("IfcReinforcingMeshTypeEnum", 819, items);
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
        IFC4X1_types[884] = new enumeration_type("IfcRoleEnum", 884, items);
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
        IFC4X1_types[887] = new enumeration_type("IfcRoofTypeEnum", 887, items);
    }
    IFC4X1_types[889] = new type_declaration("IfcRotationalFrequencyMeasure", 889, new simple_type(simple_type::real_type));
    IFC4X1_types[890] = new type_declaration("IfcRotationalMassMeasure", 890, new simple_type(simple_type::real_type));
    IFC4X1_types[891] = new type_declaration("IfcRotationalStiffnessMeasure", 891, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[891]);
        IFC4X1_types[892] = new select_type("IfcRotationalStiffnessSelect", 892, items);
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
        IFC4X1_types[925] = new enumeration_type("IfcSIPrefix", 925, items);
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
        IFC4X1_types[928] = new enumeration_type("IfcSIUnitName", 928, items);
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
        IFC4X1_types[896] = new enumeration_type("IfcSanitaryTerminalTypeEnum", 896, items);
    }
    IFC4X1_types[903] = new type_declaration("IfcSectionModulusMeasure", 903, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IFC4X1_types[906] = new enumeration_type("IfcSectionTypeEnum", 906, items);
    }
    IFC4X1_types[899] = new type_declaration("IfcSectionalAreaIntegralMeasure", 899, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(26);
        items.push_back("CO2SENSOR");
        items.push_back("CONDUCTANCESENSOR");
        items.push_back("CONTACTSENSOR");
        items.push_back("COSENSOR");
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
        IFC4X1_types[910] = new enumeration_type("IfcSensorTypeEnum", 910, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        items.push_back("USERDEFINED");
        IFC4X1_types[911] = new enumeration_type("IfcSequenceEnum", 911, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AWNING");
        items.push_back("JALOUSIE");
        items.push_back("NOTDEFINED");
        items.push_back("SHUTTER");
        items.push_back("USERDEFINED");
        IFC4X1_types[914] = new enumeration_type("IfcShadingDeviceTypeEnum", 914, items);
    }
    IFC4X1_types[918] = new type_declaration("IfcShearModulusMeasure", 918, new simple_type(simple_type::real_type));
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
        IFC4X1_types[923] = new enumeration_type("IfcSimplePropertyTemplateTypeEnum", 923, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IFC4X1_types[934] = new enumeration_type("IfcSlabTypeEnum", 934, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SOLARCOLLECTOR");
        items.push_back("SOLARPANEL");
        items.push_back("USERDEFINED");
        IFC4X1_types[938] = new enumeration_type("IfcSolarDeviceTypeEnum", 938, items);
    }
    IFC4X1_types[939] = new type_declaration("IfcSolidAngleMeasure", 939, new simple_type(simple_type::real_type));
    IFC4X1_types[942] = new type_declaration("IfcSoundPowerLevelMeasure", 942, new simple_type(simple_type::real_type));
    IFC4X1_types[943] = new type_declaration("IfcSoundPowerMeasure", 943, new simple_type(simple_type::real_type));
    IFC4X1_types[944] = new type_declaration("IfcSoundPressureLevelMeasure", 944, new simple_type(simple_type::real_type));
    IFC4X1_types[945] = new type_declaration("IfcSoundPressureMeasure", 945, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONVECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIATOR");
        items.push_back("USERDEFINED");
        IFC4X1_types[950] = new enumeration_type("IfcSpaceHeaterTypeEnum", 950, items);
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
        IFC4X1_types[952] = new enumeration_type("IfcSpaceTypeEnum", 952, items);
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
        IFC4X1_types[959] = new enumeration_type("IfcSpatialZoneTypeEnum", 959, items);
    }
    IFC4X1_types[960] = new type_declaration("IfcSpecificHeatCapacityMeasure", 960, new simple_type(simple_type::real_type));
    IFC4X1_types[961] = new type_declaration("IfcSpecularExponent", 961, new simple_type(simple_type::real_type));
    IFC4X1_types[963] = new type_declaration("IfcSpecularRoughness", 963, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IFC4X1_types[968] = new enumeration_type("IfcStackTerminalTypeEnum", 968, items);
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
        IFC4X1_types[972] = new enumeration_type("IfcStairFlightTypeEnum", 972, items);
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
        IFC4X1_types[974] = new enumeration_type("IfcStairTypeEnum", 974, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IFC4X1_types[975] = new enumeration_type("IfcStateEnum", 975, items);
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
        IFC4X1_types[983] = new enumeration_type("IfcStructuralCurveActivityTypeEnum", 983, items);
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
        IFC4X1_types[986] = new enumeration_type("IfcStructuralCurveMemberTypeEnum", 986, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BILINEAR");
        items.push_back("CONST");
        items.push_back("DISCRETE");
        items.push_back("ISOCONTOUR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[1012] = new enumeration_type("IfcStructuralSurfaceActivityTypeEnum", 1012, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IFC4X1_types[1015] = new enumeration_type("IfcStructuralSurfaceMemberTypeEnum", 1015, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4X1_types[1024] = new enumeration_type("IfcSubContractResourceTypeEnum", 1024, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MARK");
        items.push_back("NOTDEFINED");
        items.push_back("TAG");
        items.push_back("TREATMENT");
        items.push_back("USERDEFINED");
        IFC4X1_types[1030] = new enumeration_type("IfcSurfaceFeatureTypeEnum", 1030, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4X1_types[1035] = new enumeration_type("IfcSurfaceSide", 1035, items);
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
        IFC4X1_types[1050] = new enumeration_type("IfcSwitchingDeviceTypeEnum", 1050, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PANEL");
        items.push_back("USERDEFINED");
        items.push_back("WORKSURFACE");
        IFC4X1_types[1054] = new enumeration_type("IfcSystemFurnitureElementTypeEnum", 1054, items);
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
        IFC4X1_types[1060] = new enumeration_type("IfcTankTypeEnum", 1060, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ELAPSEDTIME");
        items.push_back("NOTDEFINED");
        items.push_back("WORKTIME");
        IFC4X1_types[1062] = new enumeration_type("IfcTaskDurationEnum", 1062, items);
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
        IFC4X1_types[1066] = new enumeration_type("IfcTaskTypeEnum", 1066, items);
    }
    IFC4X1_types[1068] = new type_declaration("IfcTemperatureGradientMeasure", 1068, new simple_type(simple_type::real_type));
    IFC4X1_types[1069] = new type_declaration("IfcTemperatureRateOfChangeMeasure", 1069, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COUPLER");
        items.push_back("FIXED_END");
        items.push_back("NOTDEFINED");
        items.push_back("TENSIONING_END");
        items.push_back("USERDEFINED");
        IFC4X1_types[1073] = new enumeration_type("IfcTendonAnchorTypeEnum", 1073, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IFC4X1_types[1075] = new enumeration_type("IfcTendonTypeEnum", 1075, items);
    }
    IFC4X1_types[1078] = new type_declaration("IfcText", 1078, new simple_type(simple_type::string_type));
    IFC4X1_types[1079] = new type_declaration("IfcTextAlignment", 1079, new simple_type(simple_type::string_type));
    IFC4X1_types[1080] = new type_declaration("IfcTextDecoration", 1080, new simple_type(simple_type::string_type));
    IFC4X1_types[1081] = new type_declaration("IfcTextFontName", 1081, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IFC4X1_types[1085] = new enumeration_type("IfcTextPath", 1085, items);
    }
    IFC4X1_types[1090] = new type_declaration("IfcTextTransformation", 1090, new simple_type(simple_type::string_type));
    IFC4X1_types[1096] = new type_declaration("IfcThermalAdmittanceMeasure", 1096, new simple_type(simple_type::real_type));
    IFC4X1_types[1097] = new type_declaration("IfcThermalConductivityMeasure", 1097, new simple_type(simple_type::real_type));
    IFC4X1_types[1098] = new type_declaration("IfcThermalExpansionCoefficientMeasure", 1098, new simple_type(simple_type::real_type));
    IFC4X1_types[1099] = new type_declaration("IfcThermalResistanceMeasure", 1099, new simple_type(simple_type::real_type));
    IFC4X1_types[1100] = new type_declaration("IfcThermalTransmittanceMeasure", 1100, new simple_type(simple_type::real_type));
    IFC4X1_types[1101] = new type_declaration("IfcThermodynamicTemperatureMeasure", 1101, new simple_type(simple_type::real_type));
    IFC4X1_types[1102] = new type_declaration("IfcTime", 1102, new simple_type(simple_type::string_type));
    IFC4X1_types[1103] = new type_declaration("IfcTimeMeasure", 1103, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[330]);
        items.push_back(IFC4X1_types[793]);
        IFC4X1_types[1104] = new select_type("IfcTimeOrRatioSelect", 1104, items);
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
        IFC4X1_types[1107] = new enumeration_type("IfcTimeSeriesDataTypeEnum", 1107, items);
    }
    IFC4X1_types[1109] = new type_declaration("IfcTimeStamp", 1109, new simple_type(simple_type::integer_type));
    IFC4X1_types[1113] = new type_declaration("IfcTorqueMeasure", 1113, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("INVERTER");
        items.push_back("NOTDEFINED");
        items.push_back("RECTIFIER");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IFC4X1_types[1116] = new enumeration_type("IfcTransformerTypeEnum", 1116, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IFC4X1_types[1117] = new enumeration_type("IfcTransitionCode", 1117, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BIQUADRATICPARABOLA");
        items.push_back("BLOSSCURVE");
        items.push_back("CLOTHOIDCURVE");
        items.push_back("COSINECURVE");
        items.push_back("CUBICPARABOLA");
        items.push_back("SINECURVE");
        IFC4X1_types[1119] = new enumeration_type("IfcTransitionCurveType", 1119, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[553]);
        IFC4X1_types[1120] = new select_type("IfcTranslationalStiffnessSelect", 1120, items);
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
        IFC4X1_types[1123] = new enumeration_type("IfcTransportElementTypeEnum", 1123, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IFC4X1_types[1128] = new enumeration_type("IfcTrimmingPreference", 1128, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X1_types[1133] = new enumeration_type("IfcTubeBundleTypeEnum", 1133, items);
    }
    IFC4X1_types[1147] = new type_declaration("IfcURIReference", 1147, new simple_type(simple_type::string_type));
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
        IFC4X1_types[1146] = new enumeration_type("IfcUnitEnum", 1146, items);
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
        IFC4X1_types[1141] = new enumeration_type("IfcUnitaryControlElementTypeEnum", 1141, items);
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
        IFC4X1_types[1144] = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 1144, items);
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
        IFC4X1_types[1152] = new enumeration_type("IfcValveTypeEnum", 1152, items);
    }
    IFC4X1_types[1153] = new type_declaration("IfcVaporPermeabilityMeasure", 1153, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IFC4X1_types[1161] = new enumeration_type("IfcVibrationIsolatorTypeEnum", 1161, items);
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
        IFC4X1_types[1165] = new enumeration_type("IfcVoidingFeatureTypeEnum", 1165, items);
    }
    IFC4X1_types[1166] = new type_declaration("IfcVolumeMeasure", 1166, new simple_type(simple_type::real_type));
    IFC4X1_types[1167] = new type_declaration("IfcVolumetricFlowRateMeasure", 1167, new simple_type(simple_type::real_type));
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
        IFC4X1_types[1172] = new enumeration_type("IfcWallTypeEnum", 1172, items);
    }
    IFC4X1_types[1173] = new type_declaration("IfcWarpingConstantMeasure", 1173, new simple_type(simple_type::real_type));
    IFC4X1_types[1174] = new type_declaration("IfcWarpingMomentMeasure", 1174, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[1174]);
        IFC4X1_types[1175] = new select_type("IfcWarpingStiffnessSelect", 1175, items);
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
        IFC4X1_types[1178] = new enumeration_type("IfcWasteTerminalTypeEnum", 1178, items);
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
        IFC4X1_types[1181] = new enumeration_type("IfcWindowPanelOperationEnum", 1181, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IFC4X1_types[1182] = new enumeration_type("IfcWindowPanelPositionEnum", 1182, items);
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
        IFC4X1_types[1186] = new enumeration_type("IfcWindowStyleConstructionEnum", 1186, items);
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
        IFC4X1_types[1187] = new enumeration_type("IfcWindowStyleOperationEnum", 1187, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LIGHTDOME");
        items.push_back("NOTDEFINED");
        items.push_back("SKYLIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDOW");
        IFC4X1_types[1189] = new enumeration_type("IfcWindowTypeEnum", 1189, items);
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
        IFC4X1_types[1190] = new enumeration_type("IfcWindowTypePartitioningEnum", 1190, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FIRSTSHIFT");
        items.push_back("NOTDEFINED");
        items.push_back("SECONDSHIFT");
        items.push_back("THIRDSHIFT");
        items.push_back("USERDEFINED");
        IFC4X1_types[1192] = new enumeration_type("IfcWorkCalendarTypeEnum", 1192, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4X1_types[1195] = new enumeration_type("IfcWorkPlanTypeEnum", 1195, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4X1_types[1197] = new enumeration_type("IfcWorkScheduleTypeEnum", 1197, items);
    }
    IFC4X1_types[7] = new entity("IfcActorRole", false, 7, (entity*) 0);
    IFC4X1_types[12] = new entity("IfcAddress", true, 12, (entity*) 0);
    IFC4X1_types[46] = new entity("IfcApplication", false, 46, (entity*) 0);
    IFC4X1_types[47] = new entity("IfcAppliedValue", false, 47, (entity*) 0);
    IFC4X1_types[49] = new entity("IfcApproval", false, 49, (entity*) 0);
    IFC4X1_types[85] = new entity("IfcBoundaryCondition", true, 85, (entity*) 0);
    IFC4X1_types[87] = new entity("IfcBoundaryEdgeCondition", false, 87, (entity*) IFC4X1_types[85]);
    IFC4X1_types[88] = new entity("IfcBoundaryFaceCondition", false, 88, (entity*) IFC4X1_types[85]);
    IFC4X1_types[89] = new entity("IfcBoundaryNodeCondition", false, 89, (entity*) IFC4X1_types[85]);
    IFC4X1_types[90] = new entity("IfcBoundaryNodeConditionWarping", false, 90, (entity*) IFC4X1_types[89]);
    IFC4X1_types[191] = new entity("IfcConnectionGeometry", true, 191, (entity*) 0);
    IFC4X1_types[193] = new entity("IfcConnectionPointGeometry", false, 193, (entity*) IFC4X1_types[191]);
    IFC4X1_types[194] = new entity("IfcConnectionSurfaceGeometry", false, 194, (entity*) IFC4X1_types[191]);
    IFC4X1_types[196] = new entity("IfcConnectionVolumeGeometry", false, 196, (entity*) IFC4X1_types[191]);
    IFC4X1_types[197] = new entity("IfcConstraint", true, 197, (entity*) 0);
    IFC4X1_types[225] = new entity("IfcCoordinateOperation", true, 225, (entity*) 0);
    IFC4X1_types[226] = new entity("IfcCoordinateReferenceSystem", true, 226, (entity*) 0);
    IFC4X1_types[232] = new entity("IfcCostValue", false, 232, (entity*) IFC4X1_types[47]);
    IFC4X1_types[274] = new entity("IfcDerivedUnit", false, 274, (entity*) 0);
    IFC4X1_types[275] = new entity("IfcDerivedUnitElement", false, 275, (entity*) 0);
    IFC4X1_types[278] = new entity("IfcDimensionalExponents", false, 278, (entity*) 0);
    IFC4X1_types[389] = new entity("IfcExternalInformation", true, 389, (entity*) 0);
    IFC4X1_types[393] = new entity("IfcExternalReference", true, 393, (entity*) 0);
    IFC4X1_types[390] = new entity("IfcExternallyDefinedHatchStyle", false, 390, (entity*) IFC4X1_types[393]);
    IFC4X1_types[391] = new entity("IfcExternallyDefinedSurfaceStyle", false, 391, (entity*) IFC4X1_types[393]);
    IFC4X1_types[392] = new entity("IfcExternallyDefinedTextFont", false, 392, (entity*) IFC4X1_types[393]);
    IFC4X1_types[475] = new entity("IfcGridAxis", false, 475, (entity*) 0);
    IFC4X1_types[511] = new entity("IfcIrregularTimeSeriesValue", false, 511, (entity*) 0);
    IFC4X1_types[531] = new entity("IfcLibraryInformation", false, 531, (entity*) IFC4X1_types[389]);
    IFC4X1_types[532] = new entity("IfcLibraryReference", false, 532, (entity*) IFC4X1_types[393]);
    IFC4X1_types[535] = new entity("IfcLightDistributionData", false, 535, (entity*) 0);
    IFC4X1_types[541] = new entity("IfcLightIntensityDistribution", false, 541, (entity*) 0);
    IFC4X1_types[569] = new entity("IfcMapConversion", false, 569, (entity*) IFC4X1_types[225]);
    IFC4X1_types[576] = new entity("IfcMaterialClassificationRelationship", false, 576, (entity*) 0);
    IFC4X1_types[579] = new entity("IfcMaterialDefinition", true, 579, (entity*) 0);
    IFC4X1_types[581] = new entity("IfcMaterialLayer", false, 581, (entity*) IFC4X1_types[579]);
    IFC4X1_types[582] = new entity("IfcMaterialLayerSet", false, 582, (entity*) IFC4X1_types[579]);
    IFC4X1_types[584] = new entity("IfcMaterialLayerWithOffsets", false, 584, (entity*) IFC4X1_types[581]);
    IFC4X1_types[585] = new entity("IfcMaterialList", false, 585, (entity*) 0);
    IFC4X1_types[586] = new entity("IfcMaterialProfile", false, 586, (entity*) IFC4X1_types[579]);
    IFC4X1_types[587] = new entity("IfcMaterialProfileSet", false, 587, (entity*) IFC4X1_types[579]);
    IFC4X1_types[590] = new entity("IfcMaterialProfileWithOffsets", false, 590, (entity*) IFC4X1_types[586]);
    IFC4X1_types[594] = new entity("IfcMaterialUsageDefinition", true, 594, (entity*) 0);
    IFC4X1_types[596] = new entity("IfcMeasureWithUnit", false, 596, (entity*) 0);
    IFC4X1_types[607] = new entity("IfcMetric", false, 607, (entity*) IFC4X1_types[197]);
    IFC4X1_types[621] = new entity("IfcMonetaryUnit", false, 621, (entity*) 0);
    IFC4X1_types[626] = new entity("IfcNamedUnit", true, 626, (entity*) 0);
    IFC4X1_types[635] = new entity("IfcObjectPlacement", true, 635, (entity*) 0);
    IFC4X1_types[633] = new entity("IfcObjective", false, 633, (entity*) IFC4X1_types[197]);
    IFC4X1_types[648] = new entity("IfcOrganization", false, 648, (entity*) 0);
    IFC4X1_types[656] = new entity("IfcOwnerHistory", false, 656, (entity*) 0);
    IFC4X1_types[667] = new entity("IfcPerson", false, 667, (entity*) 0);
    IFC4X1_types[668] = new entity("IfcPersonAndOrganization", false, 668, (entity*) 0);
    IFC4X1_types[672] = new entity("IfcPhysicalQuantity", true, 672, (entity*) 0);
    IFC4X1_types[673] = new entity("IfcPhysicalSimpleQuantity", true, 673, (entity*) IFC4X1_types[672]);
    IFC4X1_types[709] = new entity("IfcPostalAddress", false, 709, (entity*) IFC4X1_types[12]);
    IFC4X1_types[719] = new entity("IfcPresentationItem", true, 719, (entity*) 0);
    IFC4X1_types[720] = new entity("IfcPresentationLayerAssignment", false, 720, (entity*) 0);
    IFC4X1_types[721] = new entity("IfcPresentationLayerWithStyle", false, 721, (entity*) IFC4X1_types[720]);
    IFC4X1_types[722] = new entity("IfcPresentationStyle", true, 722, (entity*) 0);
    IFC4X1_types[723] = new entity("IfcPresentationStyleAssignment", false, 723, (entity*) 0);
    IFC4X1_types[733] = new entity("IfcProductRepresentation", true, 733, (entity*) 0);
    IFC4X1_types[736] = new entity("IfcProfileDef", false, 736, (entity*) 0);
    IFC4X1_types[740] = new entity("IfcProjectedCRS", false, 740, (entity*) IFC4X1_types[226]);
    IFC4X1_types[748] = new entity("IfcPropertyAbstraction", true, 748, (entity*) 0);
    IFC4X1_types[753] = new entity("IfcPropertyEnumeration", false, 753, (entity*) IFC4X1_types[748]);
    IFC4X1_types[776] = new entity("IfcQuantityArea", false, 776, (entity*) IFC4X1_types[673]);
    IFC4X1_types[777] = new entity("IfcQuantityCount", false, 777, (entity*) IFC4X1_types[673]);
    IFC4X1_types[778] = new entity("IfcQuantityLength", false, 778, (entity*) IFC4X1_types[673]);
    IFC4X1_types[780] = new entity("IfcQuantityTime", false, 780, (entity*) IFC4X1_types[673]);
    IFC4X1_types[781] = new entity("IfcQuantityVolume", false, 781, (entity*) IFC4X1_types[673]);
    IFC4X1_types[782] = new entity("IfcQuantityWeight", false, 782, (entity*) IFC4X1_types[673]);
    IFC4X1_types[801] = new entity("IfcRecurrencePattern", false, 801, (entity*) 0);
    IFC4X1_types[803] = new entity("IfcReference", false, 803, (entity*) 0);
    IFC4X1_types[869] = new entity("IfcRepresentation", true, 869, (entity*) 0);
    IFC4X1_types[870] = new entity("IfcRepresentationContext", true, 870, (entity*) 0);
    IFC4X1_types[871] = new entity("IfcRepresentationItem", true, 871, (entity*) 0);
    IFC4X1_types[872] = new entity("IfcRepresentationMap", false, 872, (entity*) 0);
    IFC4X1_types[876] = new entity("IfcResourceLevelRelationship", true, 876, (entity*) 0);
    IFC4X1_types[888] = new entity("IfcRoot", true, 888, (entity*) 0);
    IFC4X1_types[927] = new entity("IfcSIUnit", false, 927, (entity*) IFC4X1_types[626]);
    IFC4X1_types[897] = new entity("IfcSchedulingTime", true, 897, (entity*) 0);
    IFC4X1_types[915] = new entity("IfcShapeAspect", false, 915, (entity*) 0);
    IFC4X1_types[916] = new entity("IfcShapeModel", true, 916, (entity*) IFC4X1_types[869]);
    IFC4X1_types[917] = new entity("IfcShapeRepresentation", false, 917, (entity*) IFC4X1_types[916]);
    IFC4X1_types[981] = new entity("IfcStructuralConnectionCondition", true, 981, (entity*) 0);
    IFC4X1_types[991] = new entity("IfcStructuralLoad", true, 991, (entity*) 0);
    IFC4X1_types[993] = new entity("IfcStructuralLoadConfiguration", false, 993, (entity*) IFC4X1_types[991]);
    IFC4X1_types[996] = new entity("IfcStructuralLoadOrResult", true, 996, (entity*) IFC4X1_types[991]);
    IFC4X1_types[1002] = new entity("IfcStructuralLoadStatic", true, 1002, (entity*) IFC4X1_types[996]);
    IFC4X1_types[1003] = new entity("IfcStructuralLoadTemperature", false, 1003, (entity*) IFC4X1_types[1002]);
    IFC4X1_types[1021] = new entity("IfcStyleModel", true, 1021, (entity*) IFC4X1_types[869]);
    IFC4X1_types[1019] = new entity("IfcStyledItem", false, 1019, (entity*) IFC4X1_types[871]);
    IFC4X1_types[1020] = new entity("IfcStyledRepresentation", false, 1020, (entity*) IFC4X1_types[1021]);
    IFC4X1_types[1034] = new entity("IfcSurfaceReinforcementArea", false, 1034, (entity*) IFC4X1_types[996]);
    IFC4X1_types[1036] = new entity("IfcSurfaceStyle", false, 1036, (entity*) IFC4X1_types[722]);
    IFC4X1_types[1038] = new entity("IfcSurfaceStyleLighting", false, 1038, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1039] = new entity("IfcSurfaceStyleRefraction", false, 1039, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1041] = new entity("IfcSurfaceStyleShading", false, 1041, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1042] = new entity("IfcSurfaceStyleWithTextures", false, 1042, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1043] = new entity("IfcSurfaceTexture", true, 1043, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1055] = new entity("IfcTable", false, 1055, (entity*) 0);
    IFC4X1_types[1056] = new entity("IfcTableColumn", false, 1056, (entity*) 0);
    IFC4X1_types[1057] = new entity("IfcTableRow", false, 1057, (entity*) 0);
    IFC4X1_types[1063] = new entity("IfcTaskTime", false, 1063, (entity*) IFC4X1_types[897]);
    IFC4X1_types[1064] = new entity("IfcTaskTimeRecurring", false, 1064, (entity*) IFC4X1_types[1063]);
    IFC4X1_types[1067] = new entity("IfcTelecomAddress", false, 1067, (entity*) IFC4X1_types[12]);
    IFC4X1_types[1086] = new entity("IfcTextStyle", false, 1086, (entity*) IFC4X1_types[722]);
    IFC4X1_types[1088] = new entity("IfcTextStyleForDefinedFont", false, 1088, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1089] = new entity("IfcTextStyleTextModel", false, 1089, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1091] = new entity("IfcTextureCoordinate", true, 1091, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1092] = new entity("IfcTextureCoordinateGenerator", false, 1092, (entity*) IFC4X1_types[1091]);
    IFC4X1_types[1093] = new entity("IfcTextureMap", false, 1093, (entity*) IFC4X1_types[1091]);
    IFC4X1_types[1094] = new entity("IfcTextureVertex", false, 1094, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1095] = new entity("IfcTextureVertexList", false, 1095, (entity*) IFC4X1_types[719]);
    IFC4X1_types[1105] = new entity("IfcTimePeriod", false, 1105, (entity*) 0);
    IFC4X1_types[1106] = new entity("IfcTimeSeries", true, 1106, (entity*) 0);
    IFC4X1_types[1108] = new entity("IfcTimeSeriesValue", false, 1108, (entity*) 0);
    IFC4X1_types[1110] = new entity("IfcTopologicalRepresentationItem", true, 1110, (entity*) IFC4X1_types[871]);
    IFC4X1_types[1111] = new entity("IfcTopologyRepresentation", false, 1111, (entity*) IFC4X1_types[916]);
    IFC4X1_types[1145] = new entity("IfcUnitAssignment", false, 1145, (entity*) 0);
    IFC4X1_types[1156] = new entity("IfcVertex", false, 1156, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[1158] = new entity("IfcVertexPoint", false, 1158, (entity*) IFC4X1_types[1156]);
    IFC4X1_types[1163] = new entity("IfcVirtualGridIntersection", false, 1163, (entity*) 0);
    IFC4X1_types[1198] = new entity("IfcWorkTime", false, 1198, (entity*) IFC4X1_types[897]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[648]);
        items.push_back(IFC4X1_types[667]);
        items.push_back(IFC4X1_types[668]);
        IFC4X1_types[8] = new select_type("IfcActorSelect", 8, items);
    }
    IFC4X1_types[54] = new type_declaration("IfcArcIndex", 54, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[705])));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[530]);
        items.push_back(IFC4X1_types[690]);
        IFC4X1_types[73] = new select_type("IfcBendingParameterSelect", 73, items);
    }
    IFC4X1_types[94] = new type_declaration("IfcBoxAlignment", 94, new named_type(IFC4X1_types[519]));
    {
        std::vector<const declaration*> items; items.reserve(71);
        items.push_back(IFC4X1_types[0]);
        items.push_back(IFC4X1_types[1]);
        items.push_back(IFC4X1_types[43]);
        items.push_back(IFC4X1_types[55]);
        items.push_back(IFC4X1_types[181]);
        items.push_back(IFC4X1_types[248]);
        items.push_back(IFC4X1_types[318]);
        items.push_back(IFC4X1_types[331]);
        items.push_back(IFC4X1_types[338]);
        items.push_back(IFC4X1_types[339]);
        items.push_back(IFC4X1_types[340]);
        items.push_back(IFC4X1_types[354]);
        items.push_back(IFC4X1_types[358]);
        items.push_back(IFC4X1_types[373]);
        items.push_back(IFC4X1_types[455]);
        items.push_back(IFC4X1_types[456]);
        items.push_back(IFC4X1_types[485]);
        items.push_back(IFC4X1_types[486]);
        items.push_back(IFC4X1_types[491]);
        items.push_back(IFC4X1_types[499]);
        items.push_back(IFC4X1_types[501]);
        items.push_back(IFC4X1_types[509]);
        items.push_back(IFC4X1_types[513]);
        items.push_back(IFC4X1_types[517]);
        items.push_back(IFC4X1_types[549]);
        items.push_back(IFC4X1_types[550]);
        items.push_back(IFC4X1_types[553]);
        items.push_back(IFC4X1_types[554]);
        items.push_back(IFC4X1_types[563]);
        items.push_back(IFC4X1_types[564]);
        items.push_back(IFC4X1_types[566]);
        items.push_back(IFC4X1_types[567]);
        items.push_back(IFC4X1_types[571]);
        items.push_back(IFC4X1_types[572]);
        items.push_back(IFC4X1_types[574]);
        items.push_back(IFC4X1_types[610]);
        items.push_back(IFC4X1_types[611]);
        items.push_back(IFC4X1_types[612]);
        items.push_back(IFC4X1_types[614]);
        items.push_back(IFC4X1_types[617]);
        items.push_back(IFC4X1_types[618]);
        items.push_back(IFC4X1_types[619]);
        items.push_back(IFC4X1_types[620]);
        items.push_back(IFC4X1_types[669]);
        items.push_back(IFC4X1_types[688]);
        items.push_back(IFC4X1_types[710]);
        items.push_back(IFC4X1_types[725]);
        items.push_back(IFC4X1_types[783]);
        items.push_back(IFC4X1_types[889]);
        items.push_back(IFC4X1_types[890]);
        items.push_back(IFC4X1_types[891]);
        items.push_back(IFC4X1_types[903]);
        items.push_back(IFC4X1_types[899]);
        items.push_back(IFC4X1_types[918]);
        items.push_back(IFC4X1_types[942]);
        items.push_back(IFC4X1_types[943]);
        items.push_back(IFC4X1_types[944]);
        items.push_back(IFC4X1_types[945]);
        items.push_back(IFC4X1_types[960]);
        items.push_back(IFC4X1_types[1068]);
        items.push_back(IFC4X1_types[1069]);
        items.push_back(IFC4X1_types[1096]);
        items.push_back(IFC4X1_types[1097]);
        items.push_back(IFC4X1_types[1098]);
        items.push_back(IFC4X1_types[1099]);
        items.push_back(IFC4X1_types[1100]);
        items.push_back(IFC4X1_types[1113]);
        items.push_back(IFC4X1_types[1153]);
        items.push_back(IFC4X1_types[1167]);
        items.push_back(IFC4X1_types[1173]);
        items.push_back(IFC4X1_types[1174]);
        IFC4X1_types[272] = new select_type("IfcDerivedMeasureValue", 272, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[869]);
        items.push_back(IFC4X1_types[871]);
        IFC4X1_types[528] = new select_type("IfcLayeredItem", 528, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[531]);
        items.push_back(IFC4X1_types[532]);
        IFC4X1_types[533] = new select_type("IfcLibrarySelect", 533, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[393]);
        items.push_back(IFC4X1_types[541]);
        IFC4X1_types[536] = new select_type("IfcLightDistributionDataSourceSelect", 536, items);
    }
    IFC4X1_types[555] = new type_declaration("IfcLineIndex", 555, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[705])));
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[579]);
        items.push_back(IFC4X1_types[585]);
        items.push_back(IFC4X1_types[594]);
        IFC4X1_types[593] = new select_type("IfcMaterialSelect", 593, items);
    }
    IFC4X1_types[628] = new type_declaration("IfcNormalisedRatioMeasure", 628, new named_type(IFC4X1_types[793]));
    {
        std::vector<const declaration*> items; items.reserve(9);
        items.push_back(IFC4X1_types[12]);
        items.push_back(IFC4X1_types[47]);
        items.push_back(IFC4X1_types[393]);
        items.push_back(IFC4X1_types[579]);
        items.push_back(IFC4X1_types[648]);
        items.push_back(IFC4X1_types[667]);
        items.push_back(IFC4X1_types[668]);
        items.push_back(IFC4X1_types[1055]);
        items.push_back(IFC4X1_types[1106]);
        IFC4X1_types[636] = new select_type("IfcObjectReferenceSelect", 636, items);
    }
    IFC4X1_types[708] = new type_declaration("IfcPositiveRatioMeasure", 708, new named_type(IFC4X1_types[793]));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[54]);
        items.push_back(IFC4X1_types[555]);
        IFC4X1_types[907] = new select_type("IfcSegmentIndexSelect", 907, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(14);
        items.push_back(IFC4X1_types[74]);
        items.push_back(IFC4X1_types[80]);
        items.push_back(IFC4X1_types[267]);
        items.push_back(IFC4X1_types[268]);
        items.push_back(IFC4X1_types[330]);
        items.push_back(IFC4X1_types[490]);
        items.push_back(IFC4X1_types[500]);
        items.push_back(IFC4X1_types[519]);
        items.push_back(IFC4X1_types[559]);
        items.push_back(IFC4X1_types[705]);
        items.push_back(IFC4X1_types[796]);
        items.push_back(IFC4X1_types[1078]);
        items.push_back(IFC4X1_types[1102]);
        items.push_back(IFC4X1_types[1109]);
        IFC4X1_types[924] = new select_type("IfcSimpleValue", 924, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4X1_types[277]);
        items.push_back(IFC4X1_types[530]);
        items.push_back(IFC4X1_types[628]);
        items.push_back(IFC4X1_types[706]);
        items.push_back(IFC4X1_types[708]);
        items.push_back(IFC4X1_types[793]);
        IFC4X1_types[929] = new select_type("IfcSizeSelect", 929, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[961]);
        items.push_back(IFC4X1_types[963]);
        IFC4X1_types[962] = new select_type("IfcSpecularHighlightSelect", 962, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[722]);
        items.push_back(IFC4X1_types[723]);
        IFC4X1_types[1018] = new select_type("IfcStyleAssignmentSelect", 1018, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4X1_types[391]);
        items.push_back(IFC4X1_types[1038]);
        items.push_back(IFC4X1_types[1039]);
        items.push_back(IFC4X1_types[1041]);
        items.push_back(IFC4X1_types[1042]);
        IFC4X1_types[1037] = new select_type("IfcSurfaceStyleElementSelect", 1037, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[274]);
        items.push_back(IFC4X1_types[621]);
        items.push_back(IFC4X1_types[626]);
        IFC4X1_types[1138] = new select_type("IfcUnit", 1138, items);
    }
    IFC4X1_types[50] = new entity("IfcApprovalRelationship", false, 50, (entity*) IFC4X1_types[876]);
    IFC4X1_types[51] = new entity("IfcArbitraryClosedProfileDef", false, 51, (entity*) IFC4X1_types[736]);
    IFC4X1_types[52] = new entity("IfcArbitraryOpenProfileDef", false, 52, (entity*) IFC4X1_types[736]);
    IFC4X1_types[53] = new entity("IfcArbitraryProfileDefWithVoids", false, 53, (entity*) IFC4X1_types[51]);
    IFC4X1_types[75] = new entity("IfcBlobTexture", false, 75, (entity*) IFC4X1_types[1043]);
    IFC4X1_types[139] = new entity("IfcCenterLineProfileDef", false, 139, (entity*) IFC4X1_types[52]);
    IFC4X1_types[153] = new entity("IfcClassification", false, 153, (entity*) IFC4X1_types[389]);
    IFC4X1_types[154] = new entity("IfcClassificationReference", false, 154, (entity*) IFC4X1_types[393]);
    IFC4X1_types[164] = new entity("IfcColourRgbList", false, 164, (entity*) IFC4X1_types[719]);
    IFC4X1_types[165] = new entity("IfcColourSpecification", true, 165, (entity*) IFC4X1_types[719]);
    IFC4X1_types[180] = new entity("IfcCompositeProfileDef", false, 180, (entity*) IFC4X1_types[736]);
    IFC4X1_types[189] = new entity("IfcConnectedFaceSet", false, 189, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[190] = new entity("IfcConnectionCurveGeometry", false, 190, (entity*) IFC4X1_types[191]);
    IFC4X1_types[192] = new entity("IfcConnectionPointEccentricity", false, 192, (entity*) IFC4X1_types[193]);
    IFC4X1_types[212] = new entity("IfcContextDependentUnit", false, 212, (entity*) IFC4X1_types[626]);
    IFC4X1_types[217] = new entity("IfcConversionBasedUnit", false, 217, (entity*) IFC4X1_types[626]);
    IFC4X1_types[218] = new entity("IfcConversionBasedUnitWithOffset", false, 218, (entity*) IFC4X1_types[217]);
    IFC4X1_types[244] = new entity("IfcCurrencyRelationship", false, 244, (entity*) IFC4X1_types[876]);
    IFC4X1_types[257] = new entity("IfcCurveStyle", false, 257, (entity*) IFC4X1_types[722]);
    IFC4X1_types[258] = new entity("IfcCurveStyleFont", false, 258, (entity*) IFC4X1_types[719]);
    IFC4X1_types[259] = new entity("IfcCurveStyleFontAndScaling", false, 259, (entity*) IFC4X1_types[719]);
    IFC4X1_types[260] = new entity("IfcCurveStyleFontPattern", false, 260, (entity*) IFC4X1_types[719]);
    IFC4X1_types[273] = new entity("IfcDerivedProfileDef", false, 273, (entity*) IFC4X1_types[736]);
    IFC4X1_types[301] = new entity("IfcDocumentInformation", false, 301, (entity*) IFC4X1_types[389]);
    IFC4X1_types[302] = new entity("IfcDocumentInformationRelationship", false, 302, (entity*) IFC4X1_types[876]);
    IFC4X1_types[303] = new entity("IfcDocumentReference", false, 303, (entity*) IFC4X1_types[393]);
    IFC4X1_types[332] = new entity("IfcEdge", false, 332, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[333] = new entity("IfcEdgeCurve", false, 333, (entity*) IFC4X1_types[332]);
    IFC4X1_types[384] = new entity("IfcEventTime", false, 384, (entity*) IFC4X1_types[897]);
    IFC4X1_types[388] = new entity("IfcExtendedProperties", true, 388, (entity*) IFC4X1_types[748]);
    IFC4X1_types[394] = new entity("IfcExternalReferenceRelationship", false, 394, (entity*) IFC4X1_types[876]);
    IFC4X1_types[400] = new entity("IfcFace", false, 400, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[402] = new entity("IfcFaceBound", false, 402, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[403] = new entity("IfcFaceOuterBound", false, 403, (entity*) IFC4X1_types[402]);
    IFC4X1_types[404] = new entity("IfcFaceSurface", false, 404, (entity*) IFC4X1_types[400]);
    IFC4X1_types[407] = new entity("IfcFailureConnectionCondition", false, 407, (entity*) IFC4X1_types[981]);
    IFC4X1_types[417] = new entity("IfcFillAreaStyle", false, 417, (entity*) IFC4X1_types[722]);
    IFC4X1_types[467] = new entity("IfcGeometricRepresentationContext", false, 467, (entity*) IFC4X1_types[870]);
    IFC4X1_types[468] = new entity("IfcGeometricRepresentationItem", true, 468, (entity*) IFC4X1_types[871]);
    IFC4X1_types[469] = new entity("IfcGeometricRepresentationSubContext", false, 469, (entity*) IFC4X1_types[467]);
    IFC4X1_types[470] = new entity("IfcGeometricSet", false, 470, (entity*) IFC4X1_types[468]);
    IFC4X1_types[476] = new entity("IfcGridPlacement", false, 476, (entity*) IFC4X1_types[635]);
    IFC4X1_types[480] = new entity("IfcHalfSpaceSolid", false, 480, (entity*) IFC4X1_types[468]);
    IFC4X1_types[492] = new entity("IfcImageTexture", false, 492, (entity*) IFC4X1_types[1043]);
    IFC4X1_types[493] = new entity("IfcIndexedColourMap", false, 493, (entity*) IFC4X1_types[719]);
    IFC4X1_types[497] = new entity("IfcIndexedTextureMap", true, 497, (entity*) IFC4X1_types[1091]);
    IFC4X1_types[498] = new entity("IfcIndexedTriangleTextureMap", false, 498, (entity*) IFC4X1_types[497]);
    IFC4X1_types[510] = new entity("IfcIrregularTimeSeries", false, 510, (entity*) IFC4X1_types[1106]);
    IFC4X1_types[523] = new entity("IfcLagTime", false, 523, (entity*) IFC4X1_types[897]);
    IFC4X1_types[542] = new entity("IfcLightSource", true, 542, (entity*) IFC4X1_types[468]);
    IFC4X1_types[543] = new entity("IfcLightSourceAmbient", false, 543, (entity*) IFC4X1_types[542]);
    IFC4X1_types[544] = new entity("IfcLightSourceDirectional", false, 544, (entity*) IFC4X1_types[542]);
    IFC4X1_types[545] = new entity("IfcLightSourceGoniometric", false, 545, (entity*) IFC4X1_types[542]);
    IFC4X1_types[546] = new entity("IfcLightSourcePositional", false, 546, (entity*) IFC4X1_types[542]);
    IFC4X1_types[547] = new entity("IfcLightSourceSpot", false, 547, (entity*) IFC4X1_types[546]);
    IFC4X1_types[551] = new entity("IfcLinearPlacement", false, 551, (entity*) IFC4X1_types[635]);
    IFC4X1_types[558] = new entity("IfcLocalPlacement", false, 558, (entity*) IFC4X1_types[635]);
    IFC4X1_types[561] = new entity("IfcLoop", false, 561, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[570] = new entity("IfcMappedItem", false, 570, (entity*) IFC4X1_types[871]);
    IFC4X1_types[575] = new entity("IfcMaterial", false, 575, (entity*) IFC4X1_types[579]);
    IFC4X1_types[577] = new entity("IfcMaterialConstituent", false, 577, (entity*) IFC4X1_types[579]);
    IFC4X1_types[578] = new entity("IfcMaterialConstituentSet", false, 578, (entity*) IFC4X1_types[579]);
    IFC4X1_types[580] = new entity("IfcMaterialDefinitionRepresentation", false, 580, (entity*) IFC4X1_types[733]);
    IFC4X1_types[583] = new entity("IfcMaterialLayerSetUsage", false, 583, (entity*) IFC4X1_types[594]);
    IFC4X1_types[588] = new entity("IfcMaterialProfileSetUsage", false, 588, (entity*) IFC4X1_types[594]);
    IFC4X1_types[589] = new entity("IfcMaterialProfileSetUsageTapering", false, 589, (entity*) IFC4X1_types[588]);
    IFC4X1_types[591] = new entity("IfcMaterialProperties", false, 591, (entity*) IFC4X1_types[388]);
    IFC4X1_types[592] = new entity("IfcMaterialRelationship", false, 592, (entity*) IFC4X1_types[876]);
    IFC4X1_types[609] = new entity("IfcMirroredProfileDef", false, 609, (entity*) IFC4X1_types[273]);
    IFC4X1_types[632] = new entity("IfcObjectDefinition", true, 632, (entity*) IFC4X1_types[888]);
    IFC4X1_types[647] = new entity("IfcOpenShell", false, 647, (entity*) IFC4X1_types[189]);
    IFC4X1_types[649] = new entity("IfcOrganizationRelationship", false, 649, (entity*) IFC4X1_types[876]);
    IFC4X1_types[650] = new entity("IfcOrientationExpression", false, 650, (entity*) IFC4X1_types[468]);
    IFC4X1_types[651] = new entity("IfcOrientedEdge", false, 651, (entity*) IFC4X1_types[332]);
    IFC4X1_types[657] = new entity("IfcParameterizedProfileDef", true, 657, (entity*) IFC4X1_types[736]);
    IFC4X1_types[659] = new entity("IfcPath", false, 659, (entity*) IFC4X1_types[1110]);
    IFC4X1_types[670] = new entity("IfcPhysicalComplexQuantity", false, 670, (entity*) IFC4X1_types[672]);
    IFC4X1_types[684] = new entity("IfcPixelTexture", false, 684, (entity*) IFC4X1_types[1043]);
    IFC4X1_types[685] = new entity("IfcPlacement", true, 685, (entity*) IFC4X1_types[468]);
    IFC4X1_types[687] = new entity("IfcPlanarExtent", false, 687, (entity*) IFC4X1_types[468]);
    IFC4X1_types[695] = new entity("IfcPoint", true, 695, (entity*) IFC4X1_types[468]);
    IFC4X1_types[696] = new entity("IfcPointOnCurve", false, 696, (entity*) IFC4X1_types[695]);
    IFC4X1_types[697] = new entity("IfcPointOnSurface", false, 697, (entity*) IFC4X1_types[695]);
    IFC4X1_types[702] = new entity("IfcPolyLoop", false, 702, (entity*) IFC4X1_types[561]);
    IFC4X1_types[699] = new entity("IfcPolygonalBoundedHalfSpace", false, 699, (entity*) IFC4X1_types[480]);
    IFC4X1_types[713] = new entity("IfcPreDefinedItem", true, 713, (entity*) IFC4X1_types[719]);
    IFC4X1_types[714] = new entity("IfcPreDefinedProperties", true, 714, (entity*) IFC4X1_types[748]);
    IFC4X1_types[716] = new entity("IfcPreDefinedTextFont", true, 716, (entity*) IFC4X1_types[713]);
    IFC4X1_types[732] = new entity("IfcProductDefinitionShape", false, 732, (entity*) IFC4X1_types[733]);
    IFC4X1_types[737] = new entity("IfcProfileProperties", false, 737, (entity*) IFC4X1_types[388]);
    IFC4X1_types[747] = new entity("IfcProperty", true, 747, (entity*) IFC4X1_types[748]);
    IFC4X1_types[750] = new entity("IfcPropertyDefinition", true, 750, (entity*) IFC4X1_types[888]);
    IFC4X1_types[751] = new entity("IfcPropertyDependencyRelationship", false, 751, (entity*) IFC4X1_types[876]);
    IFC4X1_types[757] = new entity("IfcPropertySetDefinition", true, 757, (entity*) IFC4X1_types[750]);
    IFC4X1_types[765] = new entity("IfcPropertyTemplateDefinition", true, 765, (entity*) IFC4X1_types[750]);
    IFC4X1_types[779] = new entity("IfcQuantitySet", true, 779, (entity*) IFC4X1_types[757]);
    IFC4X1_types[798] = new entity("IfcRectangleProfileDef", false, 798, (entity*) IFC4X1_types[657]);
    IFC4X1_types[807] = new entity("IfcRegularTimeSeries", false, 807, (entity*) IFC4X1_types[1106]);
    IFC4X1_types[808] = new entity("IfcReinforcementBarProperties", false, 808, (entity*) IFC4X1_types[714]);
    IFC4X1_types[836] = new entity("IfcRelationship", true, 836, (entity*) IFC4X1_types[888]);
    IFC4X1_types[874] = new entity("IfcResourceApprovalRelationship", false, 874, (entity*) IFC4X1_types[876]);
    IFC4X1_types[875] = new entity("IfcResourceConstraintRelationship", false, 875, (entity*) IFC4X1_types[876]);
    IFC4X1_types[879] = new entity("IfcResourceTime", false, 879, (entity*) IFC4X1_types[897]);
    IFC4X1_types[893] = new entity("IfcRoundedRectangleProfileDef", false, 893, (entity*) IFC4X1_types[798]);
    IFC4X1_types[904] = new entity("IfcSectionProperties", false, 904, (entity*) IFC4X1_types[714]);
    IFC4X1_types[905] = new entity("IfcSectionReinforcementProperties", false, 905, (entity*) IFC4X1_types[714]);
    IFC4X1_types[902] = new entity("IfcSectionedSpine", false, 902, (entity*) IFC4X1_types[468]);
    IFC4X1_types[920] = new entity("IfcShellBasedSurfaceModel", false, 920, (entity*) IFC4X1_types[468]);
    IFC4X1_types[921] = new entity("IfcSimpleProperty", true, 921, (entity*) IFC4X1_types[747]);
    IFC4X1_types[935] = new entity("IfcSlippageConnectionCondition", false, 935, (entity*) IFC4X1_types[981]);
    IFC4X1_types[940] = new entity("IfcSolidModel", true, 940, (entity*) IFC4X1_types[468]);
    IFC4X1_types[995] = new entity("IfcStructuralLoadLinearForce", false, 995, (entity*) IFC4X1_types[1002]);
    IFC4X1_types[997] = new entity("IfcStructuralLoadPlanarForce", false, 997, (entity*) IFC4X1_types[1002]);
    IFC4X1_types[998] = new entity("IfcStructuralLoadSingleDisplacement", false, 998, (entity*) IFC4X1_types[1002]);
    IFC4X1_types[999] = new entity("IfcStructuralLoadSingleDisplacementDistortion", false, 999, (entity*) IFC4X1_types[998]);
    IFC4X1_types[1000] = new entity("IfcStructuralLoadSingleForce", false, 1000, (entity*) IFC4X1_types[1002]);
    IFC4X1_types[1001] = new entity("IfcStructuralLoadSingleForceWarping", false, 1001, (entity*) IFC4X1_types[1000]);
    IFC4X1_types[1025] = new entity("IfcSubedge", false, 1025, (entity*) IFC4X1_types[332]);
    IFC4X1_types[1026] = new entity("IfcSurface", true, 1026, (entity*) IFC4X1_types[468]);
    IFC4X1_types[1040] = new entity("IfcSurfaceStyleRendering", false, 1040, (entity*) IFC4X1_types[1041]);
    IFC4X1_types[1044] = new entity("IfcSweptAreaSolid", true, 1044, (entity*) IFC4X1_types[940]);
    IFC4X1_types[1045] = new entity("IfcSweptDiskSolid", false, 1045, (entity*) IFC4X1_types[940]);
    IFC4X1_types[1046] = new entity("IfcSweptDiskSolidPolygonal", false, 1046, (entity*) IFC4X1_types[1045]);
    IFC4X1_types[1047] = new entity("IfcSweptSurface", true, 1047, (entity*) IFC4X1_types[1026]);
    IFC4X1_types[1130] = new entity("IfcTShapeProfileDef", false, 1130, (entity*) IFC4X1_types[657]);
    IFC4X1_types[1077] = new entity("IfcTessellatedItem", true, 1077, (entity*) IFC4X1_types[468]);
    IFC4X1_types[1083] = new entity("IfcTextLiteral", false, 1083, (entity*) IFC4X1_types[468]);
    IFC4X1_types[1084] = new entity("IfcTextLiteralWithExtent", false, 1084, (entity*) IFC4X1_types[1083]);
    IFC4X1_types[1087] = new entity("IfcTextStyleFontModel", false, 1087, (entity*) IFC4X1_types[716]);
    IFC4X1_types[1124] = new entity("IfcTrapeziumProfileDef", false, 1124, (entity*) IFC4X1_types[657]);
    IFC4X1_types[1134] = new entity("IfcTypeObject", false, 1134, (entity*) IFC4X1_types[632]);
    IFC4X1_types[1135] = new entity("IfcTypeProcess", true, 1135, (entity*) IFC4X1_types[1134]);
    IFC4X1_types[1136] = new entity("IfcTypeProduct", false, 1136, (entity*) IFC4X1_types[1134]);
    IFC4X1_types[1137] = new entity("IfcTypeResource", true, 1137, (entity*) IFC4X1_types[1134]);
    IFC4X1_types[1148] = new entity("IfcUShapeProfileDef", false, 1148, (entity*) IFC4X1_types[657]);
    IFC4X1_types[1154] = new entity("IfcVector", false, 1154, (entity*) IFC4X1_types[468]);
    IFC4X1_types[1157] = new entity("IfcVertexLoop", false, 1157, (entity*) IFC4X1_types[561]);
    IFC4X1_types[1185] = new entity("IfcWindowStyle", false, 1185, (entity*) IFC4X1_types[1136]);
    IFC4X1_types[1200] = new entity("IfcZShapeProfileDef", false, 1200, (entity*) IFC4X1_types[657]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[153]);
        items.push_back(IFC4X1_types[154]);
        IFC4X1_types[155] = new select_type("IfcClassificationReferenceSelect", 155, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[153]);
        items.push_back(IFC4X1_types[154]);
        IFC4X1_types[156] = new select_type("IfcClassificationSelect", 156, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[226]);
        items.push_back(IFC4X1_types[467]);
        IFC4X1_types[227] = new select_type("IfcCoordinateReferenceSystemSelect", 227, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[632]);
        items.push_back(IFC4X1_types[750]);
        IFC4X1_types[271] = new select_type("IfcDefinitionSelect", 271, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[301]);
        items.push_back(IFC4X1_types[303]);
        IFC4X1_types[304] = new select_type("IfcDocumentSelect", 304, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[706]);
        items.push_back(IFC4X1_types[1154]);
        IFC4X1_types[481] = new select_type("IfcHatchLineDistanceSelect", 481, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(23);
        items.push_back(IFC4X1_types[40]);
        items.push_back(IFC4X1_types[56]);
        items.push_back(IFC4X1_types[173]);
        items.push_back(IFC4X1_types[211]);
        items.push_back(IFC4X1_types[233]);
        items.push_back(IFC4X1_types[277]);
        items.push_back(IFC4X1_types[341]);
        items.push_back(IFC4X1_types[530]);
        items.push_back(IFC4X1_types[565]);
        items.push_back(IFC4X1_types[573]);
        items.push_back(IFC4X1_types[627]);
        items.push_back(IFC4X1_types[628]);
        items.push_back(IFC4X1_types[630]);
        items.push_back(IFC4X1_types[658]);
        items.push_back(IFC4X1_types[690]);
        items.push_back(IFC4X1_types[706]);
        items.push_back(IFC4X1_types[707]);
        items.push_back(IFC4X1_types[708]);
        items.push_back(IFC4X1_types[793]);
        items.push_back(IFC4X1_types[939]);
        items.push_back(IFC4X1_types[1101]);
        items.push_back(IFC4X1_types[1103]);
        items.push_back(IFC4X1_types[1166]);
        IFC4X1_types[595] = new select_type("IfcMeasureValue", 595, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[695]);
        items.push_back(IFC4X1_types[1158]);
        IFC4X1_types[698] = new select_type("IfcPointOrVertexPoint", 698, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4X1_types[257]);
        items.push_back(IFC4X1_types[417]);
        items.push_back(IFC4X1_types[629]);
        items.push_back(IFC4X1_types[1036]);
        items.push_back(IFC4X1_types[1086]);
        IFC4X1_types[724] = new select_type("IfcPresentationStyleSelect", 724, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[732]);
        items.push_back(IFC4X1_types[872]);
        IFC4X1_types[734] = new select_type("IfcProductRepresentationSelect", 734, items);
    }
    IFC4X1_types[759] = new type_declaration("IfcPropertySetDefinitionSet", 759, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[757])));
    {
        std::vector<const declaration*> items; items.reserve(17);
        items.push_back(IFC4X1_types[7]);
        items.push_back(IFC4X1_types[47]);
        items.push_back(IFC4X1_types[49]);
        items.push_back(IFC4X1_types[197]);
        items.push_back(IFC4X1_types[212]);
        items.push_back(IFC4X1_types[217]);
        items.push_back(IFC4X1_types[389]);
        items.push_back(IFC4X1_types[393]);
        items.push_back(IFC4X1_types[579]);
        items.push_back(IFC4X1_types[648]);
        items.push_back(IFC4X1_types[667]);
        items.push_back(IFC4X1_types[668]);
        items.push_back(IFC4X1_types[672]);
        items.push_back(IFC4X1_types[736]);
        items.push_back(IFC4X1_types[748]);
        items.push_back(IFC4X1_types[915]);
        items.push_back(IFC4X1_types[1106]);
        IFC4X1_types[877] = new select_type("IfcResourceObjectSelect", 877, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[392]);
        items.push_back(IFC4X1_types[716]);
        IFC4X1_types[1082] = new select_type("IfcTextFontSelect", 1082, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[272]);
        items.push_back(IFC4X1_types[595]);
        items.push_back(IFC4X1_types[924]);
        IFC4X1_types[1149] = new select_type("IfcValue", 1149, items);
    }
    IFC4X1_types[16] = new entity("IfcAdvancedFace", false, 16, (entity*) IFC4X1_types[404]);
    IFC4X1_types[30] = new entity("IfcAlignment2DHorizontal", false, 30, (entity*) IFC4X1_types[468]);
    IFC4X1_types[32] = new entity("IfcAlignment2DSegment", true, 32, (entity*) IFC4X1_types[468]);
    IFC4X1_types[36] = new entity("IfcAlignment2DVertical", false, 36, (entity*) IFC4X1_types[468]);
    IFC4X1_types[37] = new entity("IfcAlignment2DVerticalSegment", true, 37, (entity*) IFC4X1_types[32]);
    IFC4X1_types[45] = new entity("IfcAnnotationFillArea", false, 45, (entity*) IFC4X1_types[468]);
    IFC4X1_types[60] = new entity("IfcAsymmetricIShapeProfileDef", false, 60, (entity*) IFC4X1_types[657]);
    IFC4X1_types[64] = new entity("IfcAxis1Placement", false, 64, (entity*) IFC4X1_types[685]);
    IFC4X1_types[66] = new entity("IfcAxis2Placement2D", false, 66, (entity*) IFC4X1_types[685]);
    IFC4X1_types[67] = new entity("IfcAxis2Placement3D", false, 67, (entity*) IFC4X1_types[685]);
    IFC4X1_types[84] = new entity("IfcBooleanResult", false, 84, (entity*) IFC4X1_types[468]);
    IFC4X1_types[92] = new entity("IfcBoundedSurface", true, 92, (entity*) IFC4X1_types[1026]);
    IFC4X1_types[93] = new entity("IfcBoundingBox", false, 93, (entity*) IFC4X1_types[468]);
    IFC4X1_types[95] = new entity("IfcBoxedHalfSpace", false, 95, (entity*) IFC4X1_types[480]);
    IFC4X1_types[243] = new entity("IfcCShapeProfileDef", false, 243, (entity*) IFC4X1_types[657]);
    IFC4X1_types[130] = new entity("IfcCartesianPoint", false, 130, (entity*) IFC4X1_types[695]);
    IFC4X1_types[131] = new entity("IfcCartesianPointList", true, 131, (entity*) IFC4X1_types[468]);
    IFC4X1_types[132] = new entity("IfcCartesianPointList2D", false, 132, (entity*) IFC4X1_types[131]);
    IFC4X1_types[133] = new entity("IfcCartesianPointList3D", false, 133, (entity*) IFC4X1_types[131]);
    IFC4X1_types[134] = new entity("IfcCartesianTransformationOperator", true, 134, (entity*) IFC4X1_types[468]);
    IFC4X1_types[135] = new entity("IfcCartesianTransformationOperator2D", false, 135, (entity*) IFC4X1_types[134]);
    IFC4X1_types[136] = new entity("IfcCartesianTransformationOperator2DnonUniform", false, 136, (entity*) IFC4X1_types[135]);
    IFC4X1_types[137] = new entity("IfcCartesianTransformationOperator3D", false, 137, (entity*) IFC4X1_types[134]);
    IFC4X1_types[138] = new entity("IfcCartesianTransformationOperator3DnonUniform", false, 138, (entity*) IFC4X1_types[137]);
    IFC4X1_types[149] = new entity("IfcCircleProfileDef", false, 149, (entity*) IFC4X1_types[657]);
    IFC4X1_types[157] = new entity("IfcClosedShell", false, 157, (entity*) IFC4X1_types[189]);
    IFC4X1_types[163] = new entity("IfcColourRgb", false, 163, (entity*) IFC4X1_types[165]);
    IFC4X1_types[174] = new entity("IfcComplexProperty", false, 174, (entity*) IFC4X1_types[747]);
    IFC4X1_types[179] = new entity("IfcCompositeCurveSegment", false, 179, (entity*) IFC4X1_types[468]);
    IFC4X1_types[209] = new entity("IfcConstructionResourceType", true, 209, (entity*) IFC4X1_types[1137]);
    IFC4X1_types[210] = new entity("IfcContext", true, 210, (entity*) IFC4X1_types[632]);
    IFC4X1_types[238] = new entity("IfcCrewResourceType", false, 238, (entity*) IFC4X1_types[209]);
    IFC4X1_types[240] = new entity("IfcCsgPrimitive3D", true, 240, (entity*) IFC4X1_types[468]);
    IFC4X1_types[242] = new entity("IfcCsgSolid", false, 242, (entity*) IFC4X1_types[940]);
    IFC4X1_types[249] = new entity("IfcCurve", true, 249, (entity*) IFC4X1_types[468]);
    IFC4X1_types[250] = new entity("IfcCurveBoundedPlane", false, 250, (entity*) IFC4X1_types[92]);
    IFC4X1_types[251] = new entity("IfcCurveBoundedSurface", false, 251, (entity*) IFC4X1_types[92]);
    IFC4X1_types[280] = new entity("IfcDirection", false, 280, (entity*) IFC4X1_types[468]);
    IFC4X1_types[285] = new entity("IfcDistanceExpression", false, 285, (entity*) IFC4X1_types[468]);
    IFC4X1_types[312] = new entity("IfcDoorStyle", false, 312, (entity*) IFC4X1_types[1136]);
    IFC4X1_types[334] = new entity("IfcEdgeLoop", false, 334, (entity*) IFC4X1_types[561]);
    IFC4X1_types[367] = new entity("IfcElementQuantity", false, 367, (entity*) IFC4X1_types[779]);
    IFC4X1_types[368] = new entity("IfcElementType", true, 368, (entity*) IFC4X1_types[1136]);
    IFC4X1_types[360] = new entity("IfcElementarySurface", true, 360, (entity*) IFC4X1_types[1026]);
    IFC4X1_types[370] = new entity("IfcEllipseProfileDef", false, 370, (entity*) IFC4X1_types[657]);
    IFC4X1_types[386] = new entity("IfcEventType", false, 386, (entity*) IFC4X1_types[1135]);
    IFC4X1_types[398] = new entity("IfcExtrudedAreaSolid", false, 398, (entity*) IFC4X1_types[1044]);
    IFC4X1_types[399] = new entity("IfcExtrudedAreaSolidTapered", false, 399, (entity*) IFC4X1_types[398]);
    IFC4X1_types[401] = new entity("IfcFaceBasedSurfaceModel", false, 401, (entity*) IFC4X1_types[468]);
    IFC4X1_types[418] = new entity("IfcFillAreaStyleHatching", false, 418, (entity*) IFC4X1_types[468]);
    IFC4X1_types[419] = new entity("IfcFillAreaStyleTiles", false, 419, (entity*) IFC4X1_types[468]);
    IFC4X1_types[427] = new entity("IfcFixedReferenceSweptAreaSolid", false, 427, (entity*) IFC4X1_types[1044]);
    IFC4X1_types[458] = new entity("IfcFurnishingElementType", false, 458, (entity*) IFC4X1_types[368]);
    IFC4X1_types[460] = new entity("IfcFurnitureType", false, 460, (entity*) IFC4X1_types[458]);
    IFC4X1_types[463] = new entity("IfcGeographicElementType", false, 463, (entity*) IFC4X1_types[368]);
    IFC4X1_types[465] = new entity("IfcGeometricCurveSet", false, 465, (entity*) IFC4X1_types[470]);
    IFC4X1_types[512] = new entity("IfcIShapeProfileDef", false, 512, (entity*) IFC4X1_types[657]);
    IFC4X1_types[495] = new entity("IfcIndexedPolygonalFace", false, 495, (entity*) IFC4X1_types[1077]);
    IFC4X1_types[496] = new entity("IfcIndexedPolygonalFaceWithVoids", false, 496, (entity*) IFC4X1_types[495]);
    IFC4X1_types[562] = new entity("IfcLShapeProfileDef", false, 562, (entity*) IFC4X1_types[657]);
    IFC4X1_types[521] = new entity("IfcLaborResourceType", false, 521, (entity*) IFC4X1_types[209]);
    IFC4X1_types[548] = new entity("IfcLine", false, 548, (entity*) IFC4X1_types[249]);
    IFC4X1_types[568] = new entity("IfcManifoldSolidBrep", true, 568, (entity*) IFC4X1_types[940]);
    IFC4X1_types[631] = new entity("IfcObject", true, 631, (entity*) IFC4X1_types[632]);
    IFC4X1_types[640] = new entity("IfcOffsetCurve", true, 640, (entity*) IFC4X1_types[249]);
    IFC4X1_types[641] = new entity("IfcOffsetCurve2D", false, 641, (entity*) IFC4X1_types[640]);
    IFC4X1_types[642] = new entity("IfcOffsetCurve3D", false, 642, (entity*) IFC4X1_types[640]);
    IFC4X1_types[643] = new entity("IfcOffsetCurveByDistances", false, 643, (entity*) IFC4X1_types[640]);
    IFC4X1_types[660] = new entity("IfcPcurve", false, 660, (entity*) IFC4X1_types[249]);
    IFC4X1_types[686] = new entity("IfcPlanarBox", false, 686, (entity*) IFC4X1_types[687]);
    IFC4X1_types[689] = new entity("IfcPlane", false, 689, (entity*) IFC4X1_types[360]);
    IFC4X1_types[711] = new entity("IfcPreDefinedColour", true, 711, (entity*) IFC4X1_types[713]);
    IFC4X1_types[712] = new entity("IfcPreDefinedCurveFont", true, 712, (entity*) IFC4X1_types[713]);
    IFC4X1_types[715] = new entity("IfcPreDefinedPropertySet", true, 715, (entity*) IFC4X1_types[757]);
    IFC4X1_types[727] = new entity("IfcProcedureType", false, 727, (entity*) IFC4X1_types[1135]);
    IFC4X1_types[729] = new entity("IfcProcess", true, 729, (entity*) IFC4X1_types[631]);
    IFC4X1_types[731] = new entity("IfcProduct", true, 731, (entity*) IFC4X1_types[631]);
    IFC4X1_types[739] = new entity("IfcProject", false, 739, (entity*) IFC4X1_types[210]);
    IFC4X1_types[744] = new entity("IfcProjectLibrary", false, 744, (entity*) IFC4X1_types[210]);
    IFC4X1_types[749] = new entity("IfcPropertyBoundedValue", false, 749, (entity*) IFC4X1_types[921]);
    IFC4X1_types[752] = new entity("IfcPropertyEnumeratedValue", false, 752, (entity*) IFC4X1_types[921]);
    IFC4X1_types[754] = new entity("IfcPropertyListValue", false, 754, (entity*) IFC4X1_types[921]);
    IFC4X1_types[755] = new entity("IfcPropertyReferenceValue", false, 755, (entity*) IFC4X1_types[921]);
    IFC4X1_types[756] = new entity("IfcPropertySet", false, 756, (entity*) IFC4X1_types[757]);
    IFC4X1_types[760] = new entity("IfcPropertySetTemplate", false, 760, (entity*) IFC4X1_types[765]);
    IFC4X1_types[762] = new entity("IfcPropertySingleValue", false, 762, (entity*) IFC4X1_types[921]);
    IFC4X1_types[763] = new entity("IfcPropertyTableValue", false, 763, (entity*) IFC4X1_types[921]);
    IFC4X1_types[764] = new entity("IfcPropertyTemplate", true, 764, (entity*) IFC4X1_types[765]);
    IFC4X1_types[772] = new entity("IfcProxy", false, 772, (entity*) IFC4X1_types[731]);
    IFC4X1_types[797] = new entity("IfcRectangleHollowProfileDef", false, 797, (entity*) IFC4X1_types[798]);
    IFC4X1_types[799] = new entity("IfcRectangularPyramid", false, 799, (entity*) IFC4X1_types[240]);
    IFC4X1_types[800] = new entity("IfcRectangularTrimmedSurface", false, 800, (entity*) IFC4X1_types[92]);
    IFC4X1_types[809] = new entity("IfcReinforcementDefinitionProperties", false, 809, (entity*) IFC4X1_types[715]);
    IFC4X1_types[821] = new entity("IfcRelAssigns", true, 821, (entity*) IFC4X1_types[836]);
    IFC4X1_types[822] = new entity("IfcRelAssignsToActor", false, 822, (entity*) IFC4X1_types[821]);
    IFC4X1_types[823] = new entity("IfcRelAssignsToControl", false, 823, (entity*) IFC4X1_types[821]);
    IFC4X1_types[824] = new entity("IfcRelAssignsToGroup", false, 824, (entity*) IFC4X1_types[821]);
    IFC4X1_types[825] = new entity("IfcRelAssignsToGroupByFactor", false, 825, (entity*) IFC4X1_types[824]);
    IFC4X1_types[826] = new entity("IfcRelAssignsToProcess", false, 826, (entity*) IFC4X1_types[821]);
    IFC4X1_types[827] = new entity("IfcRelAssignsToProduct", false, 827, (entity*) IFC4X1_types[821]);
    IFC4X1_types[828] = new entity("IfcRelAssignsToResource", false, 828, (entity*) IFC4X1_types[821]);
    IFC4X1_types[829] = new entity("IfcRelAssociates", true, 829, (entity*) IFC4X1_types[836]);
    IFC4X1_types[830] = new entity("IfcRelAssociatesApproval", false, 830, (entity*) IFC4X1_types[829]);
    IFC4X1_types[831] = new entity("IfcRelAssociatesClassification", false, 831, (entity*) IFC4X1_types[829]);
    IFC4X1_types[832] = new entity("IfcRelAssociatesConstraint", false, 832, (entity*) IFC4X1_types[829]);
    IFC4X1_types[833] = new entity("IfcRelAssociatesDocument", false, 833, (entity*) IFC4X1_types[829]);
    IFC4X1_types[834] = new entity("IfcRelAssociatesLibrary", false, 834, (entity*) IFC4X1_types[829]);
    IFC4X1_types[835] = new entity("IfcRelAssociatesMaterial", false, 835, (entity*) IFC4X1_types[829]);
    IFC4X1_types[837] = new entity("IfcRelConnects", true, 837, (entity*) IFC4X1_types[836]);
    IFC4X1_types[838] = new entity("IfcRelConnectsElements", false, 838, (entity*) IFC4X1_types[837]);
    IFC4X1_types[839] = new entity("IfcRelConnectsPathElements", false, 839, (entity*) IFC4X1_types[838]);
    IFC4X1_types[841] = new entity("IfcRelConnectsPortToElement", false, 841, (entity*) IFC4X1_types[837]);
    IFC4X1_types[840] = new entity("IfcRelConnectsPorts", false, 840, (entity*) IFC4X1_types[837]);
    IFC4X1_types[842] = new entity("IfcRelConnectsStructuralActivity", false, 842, (entity*) IFC4X1_types[837]);
    IFC4X1_types[843] = new entity("IfcRelConnectsStructuralMember", false, 843, (entity*) IFC4X1_types[837]);
    IFC4X1_types[844] = new entity("IfcRelConnectsWithEccentricity", false, 844, (entity*) IFC4X1_types[843]);
    IFC4X1_types[845] = new entity("IfcRelConnectsWithRealizingElements", false, 845, (entity*) IFC4X1_types[838]);
    IFC4X1_types[846] = new entity("IfcRelContainedInSpatialStructure", false, 846, (entity*) IFC4X1_types[837]);
    IFC4X1_types[847] = new entity("IfcRelCoversBldgElements", false, 847, (entity*) IFC4X1_types[837]);
    IFC4X1_types[848] = new entity("IfcRelCoversSpaces", false, 848, (entity*) IFC4X1_types[837]);
    IFC4X1_types[849] = new entity("IfcRelDeclares", false, 849, (entity*) IFC4X1_types[836]);
    IFC4X1_types[850] = new entity("IfcRelDecomposes", true, 850, (entity*) IFC4X1_types[836]);
    IFC4X1_types[851] = new entity("IfcRelDefines", true, 851, (entity*) IFC4X1_types[836]);
    IFC4X1_types[852] = new entity("IfcRelDefinesByObject", false, 852, (entity*) IFC4X1_types[851]);
    IFC4X1_types[853] = new entity("IfcRelDefinesByProperties", false, 853, (entity*) IFC4X1_types[851]);
    IFC4X1_types[854] = new entity("IfcRelDefinesByTemplate", false, 854, (entity*) IFC4X1_types[851]);
    IFC4X1_types[855] = new entity("IfcRelDefinesByType", false, 855, (entity*) IFC4X1_types[851]);
    IFC4X1_types[856] = new entity("IfcRelFillsElement", false, 856, (entity*) IFC4X1_types[837]);
    IFC4X1_types[857] = new entity("IfcRelFlowControlElements", false, 857, (entity*) IFC4X1_types[837]);
    IFC4X1_types[858] = new entity("IfcRelInterferesElements", false, 858, (entity*) IFC4X1_types[837]);
    IFC4X1_types[859] = new entity("IfcRelNests", false, 859, (entity*) IFC4X1_types[850]);
    IFC4X1_types[860] = new entity("IfcRelProjectsElement", false, 860, (entity*) IFC4X1_types[850]);
    IFC4X1_types[861] = new entity("IfcRelReferencedInSpatialStructure", false, 861, (entity*) IFC4X1_types[837]);
    IFC4X1_types[862] = new entity("IfcRelSequence", false, 862, (entity*) IFC4X1_types[837]);
    IFC4X1_types[863] = new entity("IfcRelServicesBuildings", false, 863, (entity*) IFC4X1_types[837]);
    IFC4X1_types[864] = new entity("IfcRelSpaceBoundary", false, 864, (entity*) IFC4X1_types[837]);
    IFC4X1_types[865] = new entity("IfcRelSpaceBoundary1stLevel", false, 865, (entity*) IFC4X1_types[864]);
    IFC4X1_types[866] = new entity("IfcRelSpaceBoundary2ndLevel", false, 866, (entity*) IFC4X1_types[865]);
    IFC4X1_types[867] = new entity("IfcRelVoidsElement", false, 867, (entity*) IFC4X1_types[850]);
    IFC4X1_types[868] = new entity("IfcReparametrisedCompositeCurveSegment", false, 868, (entity*) IFC4X1_types[179]);
    IFC4X1_types[873] = new entity("IfcResource", true, 873, (entity*) IFC4X1_types[631]);
    IFC4X1_types[880] = new entity("IfcRevolvedAreaSolid", false, 880, (entity*) IFC4X1_types[1044]);
    IFC4X1_types[881] = new entity("IfcRevolvedAreaSolidTapered", false, 881, (entity*) IFC4X1_types[880]);
    IFC4X1_types[882] = new entity("IfcRightCircularCone", false, 882, (entity*) IFC4X1_types[240]);
    IFC4X1_types[883] = new entity("IfcRightCircularCylinder", false, 883, (entity*) IFC4X1_types[240]);
    IFC4X1_types[900] = new entity("IfcSectionedSolid", true, 900, (entity*) IFC4X1_types[940]);
    IFC4X1_types[901] = new entity("IfcSectionedSolidHorizontal", false, 901, (entity*) IFC4X1_types[900]);
    IFC4X1_types[922] = new entity("IfcSimplePropertyTemplate", false, 922, (entity*) IFC4X1_types[764]);
    IFC4X1_types[953] = new entity("IfcSpatialElement", true, 953, (entity*) IFC4X1_types[731]);
    IFC4X1_types[954] = new entity("IfcSpatialElementType", true, 954, (entity*) IFC4X1_types[1136]);
    IFC4X1_types[955] = new entity("IfcSpatialStructureElement", true, 955, (entity*) IFC4X1_types[953]);
    IFC4X1_types[956] = new entity("IfcSpatialStructureElementType", true, 956, (entity*) IFC4X1_types[954]);
    IFC4X1_types[957] = new entity("IfcSpatialZone", false, 957, (entity*) IFC4X1_types[953]);
    IFC4X1_types[958] = new entity("IfcSpatialZoneType", false, 958, (entity*) IFC4X1_types[954]);
    IFC4X1_types[964] = new entity("IfcSphere", false, 964, (entity*) IFC4X1_types[240]);
    IFC4X1_types[965] = new entity("IfcSphericalSurface", false, 965, (entity*) IFC4X1_types[360]);
    IFC4X1_types[977] = new entity("IfcStructuralActivity", true, 977, (entity*) IFC4X1_types[731]);
    IFC4X1_types[989] = new entity("IfcStructuralItem", true, 989, (entity*) IFC4X1_types[731]);
    IFC4X1_types[1004] = new entity("IfcStructuralMember", true, 1004, (entity*) IFC4X1_types[989]);
    IFC4X1_types[1009] = new entity("IfcStructuralReaction", true, 1009, (entity*) IFC4X1_types[977]);
    IFC4X1_types[1014] = new entity("IfcStructuralSurfaceMember", false, 1014, (entity*) IFC4X1_types[1004]);
    IFC4X1_types[1016] = new entity("IfcStructuralSurfaceMemberVarying", false, 1016, (entity*) IFC4X1_types[1014]);
    IFC4X1_types[1017] = new entity("IfcStructuralSurfaceReaction", false, 1017, (entity*) IFC4X1_types[1009]);
    IFC4X1_types[1023] = new entity("IfcSubContractResourceType", false, 1023, (entity*) IFC4X1_types[209]);
    IFC4X1_types[1027] = new entity("IfcSurfaceCurve", false, 1027, (entity*) IFC4X1_types[249]);
    IFC4X1_types[1028] = new entity("IfcSurfaceCurveSweptAreaSolid", false, 1028, (entity*) IFC4X1_types[1044]);
    IFC4X1_types[1031] = new entity("IfcSurfaceOfLinearExtrusion", false, 1031, (entity*) IFC4X1_types[1047]);
    IFC4X1_types[1032] = new entity("IfcSurfaceOfRevolution", false, 1032, (entity*) IFC4X1_types[1047]);
    IFC4X1_types[1053] = new entity("IfcSystemFurnitureElementType", false, 1053, (entity*) IFC4X1_types[458]);
    IFC4X1_types[1061] = new entity("IfcTask", false, 1061, (entity*) IFC4X1_types[729]);
    IFC4X1_types[1065] = new entity("IfcTaskType", false, 1065, (entity*) IFC4X1_types[1135]);
    IFC4X1_types[1076] = new entity("IfcTessellatedFaceSet", true, 1076, (entity*) IFC4X1_types[1077]);
    IFC4X1_types[1112] = new entity("IfcToroidalSurface", false, 1112, (entity*) IFC4X1_types[360]);
    IFC4X1_types[1122] = new entity("IfcTransportElementType", false, 1122, (entity*) IFC4X1_types[368]);
    IFC4X1_types[1125] = new entity("IfcTriangulatedFaceSet", false, 1125, (entity*) IFC4X1_types[1076]);
    IFC4X1_types[1126] = new entity("IfcTriangulatedIrregularNetwork", false, 1126, (entity*) IFC4X1_types[1125]);
    IFC4X1_types[1180] = new entity("IfcWindowLiningProperties", false, 1180, (entity*) IFC4X1_types[715]);
    IFC4X1_types[1183] = new entity("IfcWindowPanelProperties", false, 1183, (entity*) IFC4X1_types[715]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[596]);
        items.push_back(IFC4X1_types[803]);
        items.push_back(IFC4X1_types[1149]);
        IFC4X1_types[48] = new select_type("IfcAppliedValueSelect", 48, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[66]);
        items.push_back(IFC4X1_types[67]);
        IFC4X1_types[65] = new select_type("IfcAxis2Placement", 65, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4X1_types[84]);
        items.push_back(IFC4X1_types[240]);
        items.push_back(IFC4X1_types[480]);
        items.push_back(IFC4X1_types[940]);
        items.push_back(IFC4X1_types[1076]);
        IFC4X1_types[82] = new select_type("IfcBooleanOperand", 82, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[165]);
        items.push_back(IFC4X1_types[711]);
        IFC4X1_types[161] = new select_type("IfcColour", 161, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[163]);
        items.push_back(IFC4X1_types[628]);
        IFC4X1_types[162] = new select_type("IfcColourOrFactor", 162, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[84]);
        items.push_back(IFC4X1_types[240]);
        IFC4X1_types[241] = new select_type("IfcCsgSelect", 241, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[258]);
        items.push_back(IFC4X1_types[712]);
        IFC4X1_types[261] = new select_type("IfcCurveStyleFontSelect", 261, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC4X1_types[161]);
        items.push_back(IFC4X1_types[390]);
        items.push_back(IFC4X1_types[418]);
        items.push_back(IFC4X1_types[419]);
        IFC4X1_types[420] = new select_type("IfcFillStyleSelect", 420, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[249]);
        items.push_back(IFC4X1_types[695]);
        items.push_back(IFC4X1_types[1026]);
        IFC4X1_types[471] = new select_type("IfcGeometricSetSelect", 471, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[280]);
        items.push_back(IFC4X1_types[1163]);
        IFC4X1_types[477] = new select_type("IfcGridPlacementDirectionSelect", 477, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4X1_types[47]);
        items.push_back(IFC4X1_types[596]);
        items.push_back(IFC4X1_types[803]);
        items.push_back(IFC4X1_types[1055]);
        items.push_back(IFC4X1_types[1106]);
        items.push_back(IFC4X1_types[1149]);
        IFC4X1_types[608] = new select_type("IfcMetricValueSelect", 608, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[729]);
        items.push_back(IFC4X1_types[1135]);
        IFC4X1_types[730] = new select_type("IfcProcessSelect", 730, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[731]);
        items.push_back(IFC4X1_types[1136]);
        IFC4X1_types[735] = new select_type("IfcProductSelect", 735, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[757]);
        items.push_back(IFC4X1_types[759]);
        IFC4X1_types[758] = new select_type("IfcPropertySetDefinitionSelect", 758, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[873]);
        items.push_back(IFC4X1_types[1137]);
        IFC4X1_types[878] = new select_type("IfcResourceSelect", 878, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[157]);
        items.push_back(IFC4X1_types[647]);
        IFC4X1_types[919] = new select_type("IfcShell", 919, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[157]);
        items.push_back(IFC4X1_types[940]);
        IFC4X1_types[941] = new select_type("IfcSolidOrShell", 941, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[401]);
        items.push_back(IFC4X1_types[404]);
        items.push_back(IFC4X1_types[1026]);
        IFC4X1_types[1033] = new select_type("IfcSurfaceOrFaceSurface", 1033, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[130]);
        items.push_back(IFC4X1_types[658]);
        IFC4X1_types[1129] = new select_type("IfcTrimmingSelect", 1129, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[280]);
        items.push_back(IFC4X1_types[1154]);
        IFC4X1_types[1155] = new select_type("IfcVectorOrDirection", 1155, items);
    }
    IFC4X1_types[6] = new entity("IfcActor", false, 6, (entity*) IFC4X1_types[631]);
    IFC4X1_types[14] = new entity("IfcAdvancedBrep", false, 14, (entity*) IFC4X1_types[568]);
    IFC4X1_types[15] = new entity("IfcAdvancedBrepWithVoids", false, 15, (entity*) IFC4X1_types[14]);
    IFC4X1_types[31] = new entity("IfcAlignment2DHorizontalSegment", false, 31, (entity*) IFC4X1_types[32]);
    IFC4X1_types[33] = new entity("IfcAlignment2DVerSegCircularArc", false, 33, (entity*) IFC4X1_types[37]);
    IFC4X1_types[34] = new entity("IfcAlignment2DVerSegLine", false, 34, (entity*) IFC4X1_types[37]);
    IFC4X1_types[35] = new entity("IfcAlignment2DVerSegParabolicArc", false, 35, (entity*) IFC4X1_types[37]);
    IFC4X1_types[44] = new entity("IfcAnnotation", false, 44, (entity*) IFC4X1_types[731]);
    IFC4X1_types[99] = new entity("IfcBSplineSurface", true, 99, (entity*) IFC4X1_types[92]);
    IFC4X1_types[101] = new entity("IfcBSplineSurfaceWithKnots", false, 101, (entity*) IFC4X1_types[99]);
    IFC4X1_types[76] = new entity("IfcBlock", false, 76, (entity*) IFC4X1_types[240]);
    IFC4X1_types[81] = new entity("IfcBooleanClippingResult", false, 81, (entity*) IFC4X1_types[84]);
    IFC4X1_types[91] = new entity("IfcBoundedCurve", true, 91, (entity*) IFC4X1_types[249]);
    IFC4X1_types[102] = new entity("IfcBuilding", false, 102, (entity*) IFC4X1_types[955]);
    IFC4X1_types[110] = new entity("IfcBuildingElementType", true, 110, (entity*) IFC4X1_types[368]);
    IFC4X1_types[111] = new entity("IfcBuildingStorey", false, 111, (entity*) IFC4X1_types[955]);
    IFC4X1_types[145] = new entity("IfcChimneyType", false, 145, (entity*) IFC4X1_types[110]);
    IFC4X1_types[148] = new entity("IfcCircleHollowProfileDef", false, 148, (entity*) IFC4X1_types[149]);
    IFC4X1_types[152] = new entity("IfcCivilElementType", false, 152, (entity*) IFC4X1_types[368]);
    IFC4X1_types[168] = new entity("IfcColumnType", false, 168, (entity*) IFC4X1_types[110]);
    IFC4X1_types[175] = new entity("IfcComplexPropertyTemplate", false, 175, (entity*) IFC4X1_types[764]);
    IFC4X1_types[177] = new entity("IfcCompositeCurve", false, 177, (entity*) IFC4X1_types[91]);
    IFC4X1_types[178] = new entity("IfcCompositeCurveOnSurface", false, 178, (entity*) IFC4X1_types[177]);
    IFC4X1_types[188] = new entity("IfcConic", true, 188, (entity*) IFC4X1_types[249]);
    IFC4X1_types[200] = new entity("IfcConstructionEquipmentResourceType", false, 200, (entity*) IFC4X1_types[209]);
    IFC4X1_types[203] = new entity("IfcConstructionMaterialResourceType", false, 203, (entity*) IFC4X1_types[209]);
    IFC4X1_types[206] = new entity("IfcConstructionProductResourceType", false, 206, (entity*) IFC4X1_types[209]);
    IFC4X1_types[208] = new entity("IfcConstructionResource", true, 208, (entity*) IFC4X1_types[873]);
    IFC4X1_types[213] = new entity("IfcControl", true, 213, (entity*) IFC4X1_types[631]);
    IFC4X1_types[228] = new entity("IfcCostItem", false, 228, (entity*) IFC4X1_types[213]);
    IFC4X1_types[230] = new entity("IfcCostSchedule", false, 230, (entity*) IFC4X1_types[213]);
    IFC4X1_types[235] = new entity("IfcCoveringType", false, 235, (entity*) IFC4X1_types[110]);
    IFC4X1_types[237] = new entity("IfcCrewResource", false, 237, (entity*) IFC4X1_types[208]);
    IFC4X1_types[246] = new entity("IfcCurtainWallType", false, 246, (entity*) IFC4X1_types[110]);
    IFC4X1_types[256] = new entity("IfcCurveSegment2D", true, 256, (entity*) IFC4X1_types[91]);
    IFC4X1_types[262] = new entity("IfcCylindricalSurface", false, 262, (entity*) IFC4X1_types[360]);
    IFC4X1_types[293] = new entity("IfcDistributionElementType", false, 293, (entity*) IFC4X1_types[368]);
    IFC4X1_types[295] = new entity("IfcDistributionFlowElementType", true, 295, (entity*) IFC4X1_types[293]);
    IFC4X1_types[307] = new entity("IfcDoorLiningProperties", false, 307, (entity*) IFC4X1_types[715]);
    IFC4X1_types[310] = new entity("IfcDoorPanelProperties", false, 310, (entity*) IFC4X1_types[715]);
    IFC4X1_types[315] = new entity("IfcDoorType", false, 315, (entity*) IFC4X1_types[110]);
    IFC4X1_types[319] = new entity("IfcDraughtingPreDefinedColour", false, 319, (entity*) IFC4X1_types[711]);
    IFC4X1_types[320] = new entity("IfcDraughtingPreDefinedCurveFont", false, 320, (entity*) IFC4X1_types[712]);
    IFC4X1_types[359] = new entity("IfcElement", true, 359, (entity*) IFC4X1_types[731]);
    IFC4X1_types[361] = new entity("IfcElementAssembly", false, 361, (entity*) IFC4X1_types[359]);
    IFC4X1_types[362] = new entity("IfcElementAssemblyType", false, 362, (entity*) IFC4X1_types[368]);
    IFC4X1_types[364] = new entity("IfcElementComponent", true, 364, (entity*) IFC4X1_types[359]);
    IFC4X1_types[365] = new entity("IfcElementComponentType", true, 365, (entity*) IFC4X1_types[368]);
    IFC4X1_types[369] = new entity("IfcEllipse", false, 369, (entity*) IFC4X1_types[188]);
    IFC4X1_types[372] = new entity("IfcEnergyConversionDeviceType", true, 372, (entity*) IFC4X1_types[295]);
    IFC4X1_types[375] = new entity("IfcEngineType", false, 375, (entity*) IFC4X1_types[372]);
    IFC4X1_types[378] = new entity("IfcEvaporativeCoolerType", false, 378, (entity*) IFC4X1_types[372]);
    IFC4X1_types[381] = new entity("IfcEvaporatorType", false, 381, (entity*) IFC4X1_types[372]);
    IFC4X1_types[383] = new entity("IfcEvent", false, 383, (entity*) IFC4X1_types[729]);
    IFC4X1_types[397] = new entity("IfcExternalSpatialStructureElement", true, 397, (entity*) IFC4X1_types[953]);
    IFC4X1_types[405] = new entity("IfcFacetedBrep", false, 405, (entity*) IFC4X1_types[568]);
    IFC4X1_types[406] = new entity("IfcFacetedBrepWithVoids", false, 406, (entity*) IFC4X1_types[405]);
    IFC4X1_types[411] = new entity("IfcFastener", false, 411, (entity*) IFC4X1_types[364]);
    IFC4X1_types[412] = new entity("IfcFastenerType", false, 412, (entity*) IFC4X1_types[365]);
    IFC4X1_types[414] = new entity("IfcFeatureElement", true, 414, (entity*) IFC4X1_types[359]);
    IFC4X1_types[415] = new entity("IfcFeatureElementAddition", true, 415, (entity*) IFC4X1_types[414]);
    IFC4X1_types[416] = new entity("IfcFeatureElementSubtraction", true, 416, (entity*) IFC4X1_types[414]);
    IFC4X1_types[429] = new entity("IfcFlowControllerType", true, 429, (entity*) IFC4X1_types[295]);
    IFC4X1_types[432] = new entity("IfcFlowFittingType", true, 432, (entity*) IFC4X1_types[295]);
    IFC4X1_types[437] = new entity("IfcFlowMeterType", false, 437, (entity*) IFC4X1_types[429]);
    IFC4X1_types[440] = new entity("IfcFlowMovingDeviceType", true, 440, (entity*) IFC4X1_types[295]);
    IFC4X1_types[442] = new entity("IfcFlowSegmentType", true, 442, (entity*) IFC4X1_types[295]);
    IFC4X1_types[444] = new entity("IfcFlowStorageDeviceType", true, 444, (entity*) IFC4X1_types[295]);
    IFC4X1_types[446] = new entity("IfcFlowTerminalType", true, 446, (entity*) IFC4X1_types[295]);
    IFC4X1_types[448] = new entity("IfcFlowTreatmentDeviceType", true, 448, (entity*) IFC4X1_types[295]);
    IFC4X1_types[453] = new entity("IfcFootingType", false, 453, (entity*) IFC4X1_types[110]);
    IFC4X1_types[457] = new entity("IfcFurnishingElement", false, 457, (entity*) IFC4X1_types[359]);
    IFC4X1_types[459] = new entity("IfcFurniture", false, 459, (entity*) IFC4X1_types[457]);
    IFC4X1_types[462] = new entity("IfcGeographicElement", false, 462, (entity*) IFC4X1_types[359]);
    IFC4X1_types[479] = new entity("IfcGroup", false, 479, (entity*) IFC4X1_types[631]);
    IFC4X1_types[483] = new entity("IfcHeatExchangerType", false, 483, (entity*) IFC4X1_types[372]);
    IFC4X1_types[488] = new entity("IfcHumidifierType", false, 488, (entity*) IFC4X1_types[372]);
    IFC4X1_types[494] = new entity("IfcIndexedPolyCurve", false, 494, (entity*) IFC4X1_types[91]);
    IFC4X1_types[503] = new entity("IfcInterceptorType", false, 503, (entity*) IFC4X1_types[448]);
    IFC4X1_types[506] = new entity("IfcIntersectionCurve", false, 506, (entity*) IFC4X1_types[1027]);
    IFC4X1_types[507] = new entity("IfcInventory", false, 507, (entity*) IFC4X1_types[479]);
    IFC4X1_types[515] = new entity("IfcJunctionBoxType", false, 515, (entity*) IFC4X1_types[432]);
    IFC4X1_types[520] = new entity("IfcLaborResource", false, 520, (entity*) IFC4X1_types[208]);
    IFC4X1_types[525] = new entity("IfcLampType", false, 525, (entity*) IFC4X1_types[446]);
    IFC4X1_types[539] = new entity("IfcLightFixtureType", false, 539, (entity*) IFC4X1_types[446]);
    IFC4X1_types[556] = new entity("IfcLineSegment2D", false, 556, (entity*) IFC4X1_types[256]);
    IFC4X1_types[597] = new entity("IfcMechanicalFastener", false, 597, (entity*) IFC4X1_types[364]);
    IFC4X1_types[598] = new entity("IfcMechanicalFastenerType", false, 598, (entity*) IFC4X1_types[365]);
    IFC4X1_types[601] = new entity("IfcMedicalDeviceType", false, 601, (entity*) IFC4X1_types[446]);
    IFC4X1_types[605] = new entity("IfcMemberType", false, 605, (entity*) IFC4X1_types[110]);
    IFC4X1_types[624] = new entity("IfcMotorConnectionType", false, 624, (entity*) IFC4X1_types[372]);
    IFC4X1_types[638] = new entity("IfcOccupant", false, 638, (entity*) IFC4X1_types[6]);
    IFC4X1_types[644] = new entity("IfcOpeningElement", false, 644, (entity*) IFC4X1_types[416]);
    IFC4X1_types[646] = new entity("IfcOpeningStandardCase", false, 646, (entity*) IFC4X1_types[644]);
    IFC4X1_types[654] = new entity("IfcOutletType", false, 654, (entity*) IFC4X1_types[446]);
    IFC4X1_types[661] = new entity("IfcPerformanceHistory", false, 661, (entity*) IFC4X1_types[213]);
    IFC4X1_types[664] = new entity("IfcPermeableCoveringProperties", false, 664, (entity*) IFC4X1_types[715]);
    IFC4X1_types[665] = new entity("IfcPermit", false, 665, (entity*) IFC4X1_types[213]);
    IFC4X1_types[676] = new entity("IfcPileType", false, 676, (entity*) IFC4X1_types[110]);
    IFC4X1_types[679] = new entity("IfcPipeFittingType", false, 679, (entity*) IFC4X1_types[432]);
    IFC4X1_types[682] = new entity("IfcPipeSegmentType", false, 682, (entity*) IFC4X1_types[442]);
    IFC4X1_types[693] = new entity("IfcPlateType", false, 693, (entity*) IFC4X1_types[110]);
    IFC4X1_types[700] = new entity("IfcPolygonalFaceSet", false, 700, (entity*) IFC4X1_types[1076]);
    IFC4X1_types[701] = new entity("IfcPolyline", false, 701, (entity*) IFC4X1_types[91]);
    IFC4X1_types[703] = new entity("IfcPort", true, 703, (entity*) IFC4X1_types[731]);
    IFC4X1_types[704] = new entity("IfcPositioningElement", true, 704, (entity*) IFC4X1_types[731]);
    IFC4X1_types[726] = new entity("IfcProcedure", false, 726, (entity*) IFC4X1_types[729]);
    IFC4X1_types[745] = new entity("IfcProjectOrder", false, 745, (entity*) IFC4X1_types[213]);
    IFC4X1_types[742] = new entity("IfcProjectionElement", false, 742, (entity*) IFC4X1_types[415]);
    IFC4X1_types[770] = new entity("IfcProtectiveDeviceType", false, 770, (entity*) IFC4X1_types[429]);
    IFC4X1_types[774] = new entity("IfcPumpType", false, 774, (entity*) IFC4X1_types[440]);
    IFC4X1_types[785] = new entity("IfcRailingType", false, 785, (entity*) IFC4X1_types[110]);
    IFC4X1_types[789] = new entity("IfcRampFlightType", false, 789, (entity*) IFC4X1_types[110]);
    IFC4X1_types[791] = new entity("IfcRampType", false, 791, (entity*) IFC4X1_types[110]);
    IFC4X1_types[795] = new entity("IfcRationalBSplineSurfaceWithKnots", false, 795, (entity*) IFC4X1_types[101]);
    IFC4X1_types[804] = new entity("IfcReferent", false, 804, (entity*) IFC4X1_types[704]);
    IFC4X1_types[815] = new entity("IfcReinforcingElement", true, 815, (entity*) IFC4X1_types[364]);
    IFC4X1_types[816] = new entity("IfcReinforcingElementType", true, 816, (entity*) IFC4X1_types[365]);
    IFC4X1_types[817] = new entity("IfcReinforcingMesh", false, 817, (entity*) IFC4X1_types[815]);
    IFC4X1_types[818] = new entity("IfcReinforcingMeshType", false, 818, (entity*) IFC4X1_types[816]);
    IFC4X1_types[820] = new entity("IfcRelAggregates", false, 820, (entity*) IFC4X1_types[850]);
    IFC4X1_types[886] = new entity("IfcRoofType", false, 886, (entity*) IFC4X1_types[110]);
    IFC4X1_types[895] = new entity("IfcSanitaryTerminalType", false, 895, (entity*) IFC4X1_types[446]);
    IFC4X1_types[898] = new entity("IfcSeamCurve", false, 898, (entity*) IFC4X1_types[1027]);
    IFC4X1_types[913] = new entity("IfcShadingDeviceType", false, 913, (entity*) IFC4X1_types[110]);
    IFC4X1_types[926] = new entity("IfcSite", false, 926, (entity*) IFC4X1_types[955]);
    IFC4X1_types[933] = new entity("IfcSlabType", false, 933, (entity*) IFC4X1_types[110]);
    IFC4X1_types[937] = new entity("IfcSolarDeviceType", false, 937, (entity*) IFC4X1_types[372]);
    IFC4X1_types[946] = new entity("IfcSpace", false, 946, (entity*) IFC4X1_types[955]);
    IFC4X1_types[949] = new entity("IfcSpaceHeaterType", false, 949, (entity*) IFC4X1_types[446]);
    IFC4X1_types[951] = new entity("IfcSpaceType", false, 951, (entity*) IFC4X1_types[956]);
    IFC4X1_types[967] = new entity("IfcStackTerminalType", false, 967, (entity*) IFC4X1_types[446]);
    IFC4X1_types[971] = new entity("IfcStairFlightType", false, 971, (entity*) IFC4X1_types[110]);
    IFC4X1_types[973] = new entity("IfcStairType", false, 973, (entity*) IFC4X1_types[110]);
    IFC4X1_types[976] = new entity("IfcStructuralAction", true, 976, (entity*) IFC4X1_types[977]);
    IFC4X1_types[980] = new entity("IfcStructuralConnection", true, 980, (entity*) IFC4X1_types[989]);
    IFC4X1_types[982] = new entity("IfcStructuralCurveAction", false, 982, (entity*) IFC4X1_types[976]);
    IFC4X1_types[984] = new entity("IfcStructuralCurveConnection", false, 984, (entity*) IFC4X1_types[980]);
    IFC4X1_types[985] = new entity("IfcStructuralCurveMember", false, 985, (entity*) IFC4X1_types[1004]);
    IFC4X1_types[987] = new entity("IfcStructuralCurveMemberVarying", false, 987, (entity*) IFC4X1_types[985]);
    IFC4X1_types[988] = new entity("IfcStructuralCurveReaction", false, 988, (entity*) IFC4X1_types[1009]);
    IFC4X1_types[990] = new entity("IfcStructuralLinearAction", false, 990, (entity*) IFC4X1_types[982]);
    IFC4X1_types[994] = new entity("IfcStructuralLoadGroup", false, 994, (entity*) IFC4X1_types[479]);
    IFC4X1_types[1006] = new entity("IfcStructuralPointAction", false, 1006, (entity*) IFC4X1_types[976]);
    IFC4X1_types[1007] = new entity("IfcStructuralPointConnection", false, 1007, (entity*) IFC4X1_types[980]);
    IFC4X1_types[1008] = new entity("IfcStructuralPointReaction", false, 1008, (entity*) IFC4X1_types[1009]);
    IFC4X1_types[1010] = new entity("IfcStructuralResultGroup", false, 1010, (entity*) IFC4X1_types[479]);
    IFC4X1_types[1011] = new entity("IfcStructuralSurfaceAction", false, 1011, (entity*) IFC4X1_types[976]);
    IFC4X1_types[1013] = new entity("IfcStructuralSurfaceConnection", false, 1013, (entity*) IFC4X1_types[980]);
    IFC4X1_types[1022] = new entity("IfcSubContractResource", false, 1022, (entity*) IFC4X1_types[208]);
    IFC4X1_types[1029] = new entity("IfcSurfaceFeature", false, 1029, (entity*) IFC4X1_types[414]);
    IFC4X1_types[1049] = new entity("IfcSwitchingDeviceType", false, 1049, (entity*) IFC4X1_types[429]);
    IFC4X1_types[1051] = new entity("IfcSystem", false, 1051, (entity*) IFC4X1_types[479]);
    IFC4X1_types[1052] = new entity("IfcSystemFurnitureElement", false, 1052, (entity*) IFC4X1_types[457]);
    IFC4X1_types[1059] = new entity("IfcTankType", false, 1059, (entity*) IFC4X1_types[444]);
    IFC4X1_types[1070] = new entity("IfcTendon", false, 1070, (entity*) IFC4X1_types[815]);
    IFC4X1_types[1071] = new entity("IfcTendonAnchor", false, 1071, (entity*) IFC4X1_types[815]);
    IFC4X1_types[1072] = new entity("IfcTendonAnchorType", false, 1072, (entity*) IFC4X1_types[816]);
    IFC4X1_types[1074] = new entity("IfcTendonType", false, 1074, (entity*) IFC4X1_types[816]);
    IFC4X1_types[1115] = new entity("IfcTransformerType", false, 1115, (entity*) IFC4X1_types[372]);
    IFC4X1_types[1118] = new entity("IfcTransitionCurveSegment2D", false, 1118, (entity*) IFC4X1_types[256]);
    IFC4X1_types[1121] = new entity("IfcTransportElement", false, 1121, (entity*) IFC4X1_types[359]);
    IFC4X1_types[1127] = new entity("IfcTrimmedCurve", false, 1127, (entity*) IFC4X1_types[91]);
    IFC4X1_types[1132] = new entity("IfcTubeBundleType", false, 1132, (entity*) IFC4X1_types[372]);
    IFC4X1_types[1143] = new entity("IfcUnitaryEquipmentType", false, 1143, (entity*) IFC4X1_types[372]);
    IFC4X1_types[1151] = new entity("IfcValveType", false, 1151, (entity*) IFC4X1_types[429]);
    IFC4X1_types[1159] = new entity("IfcVibrationIsolator", false, 1159, (entity*) IFC4X1_types[364]);
    IFC4X1_types[1160] = new entity("IfcVibrationIsolatorType", false, 1160, (entity*) IFC4X1_types[365]);
    IFC4X1_types[1162] = new entity("IfcVirtualElement", false, 1162, (entity*) IFC4X1_types[359]);
    IFC4X1_types[1164] = new entity("IfcVoidingFeature", false, 1164, (entity*) IFC4X1_types[416]);
    IFC4X1_types[1171] = new entity("IfcWallType", false, 1171, (entity*) IFC4X1_types[110]);
    IFC4X1_types[1177] = new entity("IfcWasteTerminalType", false, 1177, (entity*) IFC4X1_types[446]);
    IFC4X1_types[1188] = new entity("IfcWindowType", false, 1188, (entity*) IFC4X1_types[110]);
    IFC4X1_types[1191] = new entity("IfcWorkCalendar", false, 1191, (entity*) IFC4X1_types[213]);
    IFC4X1_types[1193] = new entity("IfcWorkControl", true, 1193, (entity*) IFC4X1_types[213]);
    IFC4X1_types[1194] = new entity("IfcWorkPlan", false, 1194, (entity*) IFC4X1_types[1193]);
    IFC4X1_types[1196] = new entity("IfcWorkSchedule", false, 1196, (entity*) IFC4X1_types[1193]);
    IFC4X1_types[1199] = new entity("IfcZone", false, 1199, (entity*) IFC4X1_types[1051]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[259]);
        items.push_back(IFC4X1_types[261]);
        IFC4X1_types[252] = new select_type("IfcCurveFontOrScaledCurveFontSelect", 252, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X1_types[178]);
        items.push_back(IFC4X1_types[660]);
        items.push_back(IFC4X1_types[1027]);
        IFC4X1_types[254] = new select_type("IfcCurveOnSurface", 254, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[91]);
        items.push_back(IFC4X1_types[333]);
        IFC4X1_types[255] = new select_type("IfcCurveOrEdgeCurve", 255, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[359]);
        items.push_back(IFC4X1_types[989]);
        IFC4X1_types[978] = new select_type("IfcStructuralActivityAssignmentSelect", 978, items);
    }
    IFC4X1_types[2] = new entity("IfcActionRequest", false, 2, (entity*) IFC4X1_types[213]);
    IFC4X1_types[19] = new entity("IfcAirTerminalBoxType", false, 19, (entity*) IFC4X1_types[429]);
    IFC4X1_types[21] = new entity("IfcAirTerminalType", false, 21, (entity*) IFC4X1_types[446]);
    IFC4X1_types[24] = new entity("IfcAirToAirHeatRecoveryType", false, 24, (entity*) IFC4X1_types[372]);
    IFC4X1_types[38] = new entity("IfcAlignmentCurve", false, 38, (entity*) IFC4X1_types[91]);
    IFC4X1_types[59] = new entity("IfcAsset", false, 59, (entity*) IFC4X1_types[479]);
    IFC4X1_types[62] = new entity("IfcAudioVisualApplianceType", false, 62, (entity*) IFC4X1_types[446]);
    IFC4X1_types[96] = new entity("IfcBSplineCurve", true, 96, (entity*) IFC4X1_types[91]);
    IFC4X1_types[98] = new entity("IfcBSplineCurveWithKnots", false, 98, (entity*) IFC4X1_types[96]);
    IFC4X1_types[70] = new entity("IfcBeamType", false, 70, (entity*) IFC4X1_types[110]);
    IFC4X1_types[78] = new entity("IfcBoilerType", false, 78, (entity*) IFC4X1_types[372]);
    IFC4X1_types[86] = new entity("IfcBoundaryCurve", false, 86, (entity*) IFC4X1_types[178]);
    IFC4X1_types[103] = new entity("IfcBuildingElement", true, 103, (entity*) IFC4X1_types[359]);
    IFC4X1_types[104] = new entity("IfcBuildingElementPart", false, 104, (entity*) IFC4X1_types[364]);
    IFC4X1_types[105] = new entity("IfcBuildingElementPartType", false, 105, (entity*) IFC4X1_types[365]);
    IFC4X1_types[107] = new entity("IfcBuildingElementProxy", false, 107, (entity*) IFC4X1_types[103]);
    IFC4X1_types[108] = new entity("IfcBuildingElementProxyType", false, 108, (entity*) IFC4X1_types[110]);
    IFC4X1_types[112] = new entity("IfcBuildingSystem", false, 112, (entity*) IFC4X1_types[1051]);
    IFC4X1_types[115] = new entity("IfcBurnerType", false, 115, (entity*) IFC4X1_types[372]);
    IFC4X1_types[118] = new entity("IfcCableCarrierFittingType", false, 118, (entity*) IFC4X1_types[432]);
    IFC4X1_types[121] = new entity("IfcCableCarrierSegmentType", false, 121, (entity*) IFC4X1_types[442]);
    IFC4X1_types[124] = new entity("IfcCableFittingType", false, 124, (entity*) IFC4X1_types[432]);
    IFC4X1_types[127] = new entity("IfcCableSegmentType", false, 127, (entity*) IFC4X1_types[442]);
    IFC4X1_types[142] = new entity("IfcChillerType", false, 142, (entity*) IFC4X1_types[372]);
    IFC4X1_types[144] = new entity("IfcChimney", false, 144, (entity*) IFC4X1_types[103]);
    IFC4X1_types[147] = new entity("IfcCircle", false, 147, (entity*) IFC4X1_types[188]);
    IFC4X1_types[150] = new entity("IfcCircularArcSegment2D", false, 150, (entity*) IFC4X1_types[256]);
    IFC4X1_types[151] = new entity("IfcCivilElement", false, 151, (entity*) IFC4X1_types[359]);
    IFC4X1_types[159] = new entity("IfcCoilType", false, 159, (entity*) IFC4X1_types[372]);
    IFC4X1_types[166] = new entity("IfcColumn", false, 166, (entity*) IFC4X1_types[103]);
    IFC4X1_types[167] = new entity("IfcColumnStandardCase", false, 167, (entity*) IFC4X1_types[166]);
    IFC4X1_types[171] = new entity("IfcCommunicationsApplianceType", false, 171, (entity*) IFC4X1_types[446]);
    IFC4X1_types[183] = new entity("IfcCompressorType", false, 183, (entity*) IFC4X1_types[440]);
    IFC4X1_types[186] = new entity("IfcCondenserType", false, 186, (entity*) IFC4X1_types[372]);
    IFC4X1_types[199] = new entity("IfcConstructionEquipmentResource", false, 199, (entity*) IFC4X1_types[208]);
    IFC4X1_types[202] = new entity("IfcConstructionMaterialResource", false, 202, (entity*) IFC4X1_types[208]);
    IFC4X1_types[205] = new entity("IfcConstructionProductResource", false, 205, (entity*) IFC4X1_types[208]);
    IFC4X1_types[220] = new entity("IfcCooledBeamType", false, 220, (entity*) IFC4X1_types[372]);
    IFC4X1_types[223] = new entity("IfcCoolingTowerType", false, 223, (entity*) IFC4X1_types[372]);
    IFC4X1_types[234] = new entity("IfcCovering", false, 234, (entity*) IFC4X1_types[103]);
    IFC4X1_types[245] = new entity("IfcCurtainWall", false, 245, (entity*) IFC4X1_types[103]);
    IFC4X1_types[264] = new entity("IfcDamperType", false, 264, (entity*) IFC4X1_types[429]);
    IFC4X1_types[282] = new entity("IfcDiscreteAccessory", false, 282, (entity*) IFC4X1_types[364]);
    IFC4X1_types[283] = new entity("IfcDiscreteAccessoryType", false, 283, (entity*) IFC4X1_types[365]);
    IFC4X1_types[287] = new entity("IfcDistributionChamberElementType", false, 287, (entity*) IFC4X1_types[295]);
    IFC4X1_types[291] = new entity("IfcDistributionControlElementType", true, 291, (entity*) IFC4X1_types[293]);
    IFC4X1_types[292] = new entity("IfcDistributionElement", false, 292, (entity*) IFC4X1_types[359]);
    IFC4X1_types[294] = new entity("IfcDistributionFlowElement", false, 294, (entity*) IFC4X1_types[292]);
    IFC4X1_types[296] = new entity("IfcDistributionPort", false, 296, (entity*) IFC4X1_types[703]);
    IFC4X1_types[298] = new entity("IfcDistributionSystem", false, 298, (entity*) IFC4X1_types[1051]);
    IFC4X1_types[306] = new entity("IfcDoor", false, 306, (entity*) IFC4X1_types[103]);
    IFC4X1_types[311] = new entity("IfcDoorStandardCase", false, 311, (entity*) IFC4X1_types[306]);
    IFC4X1_types[322] = new entity("IfcDuctFittingType", false, 322, (entity*) IFC4X1_types[432]);
    IFC4X1_types[325] = new entity("IfcDuctSegmentType", false, 325, (entity*) IFC4X1_types[442]);
    IFC4X1_types[328] = new entity("IfcDuctSilencerType", false, 328, (entity*) IFC4X1_types[448]);
    IFC4X1_types[336] = new entity("IfcElectricApplianceType", false, 336, (entity*) IFC4X1_types[446]);
    IFC4X1_types[343] = new entity("IfcElectricDistributionBoardType", false, 343, (entity*) IFC4X1_types[429]);
    IFC4X1_types[346] = new entity("IfcElectricFlowStorageDeviceType", false, 346, (entity*) IFC4X1_types[444]);
    IFC4X1_types[349] = new entity("IfcElectricGeneratorType", false, 349, (entity*) IFC4X1_types[372]);
    IFC4X1_types[352] = new entity("IfcElectricMotorType", false, 352, (entity*) IFC4X1_types[372]);
    IFC4X1_types[356] = new entity("IfcElectricTimeControlType", false, 356, (entity*) IFC4X1_types[429]);
    IFC4X1_types[371] = new entity("IfcEnergyConversionDevice", false, 371, (entity*) IFC4X1_types[294]);
    IFC4X1_types[374] = new entity("IfcEngine", false, 374, (entity*) IFC4X1_types[371]);
    IFC4X1_types[377] = new entity("IfcEvaporativeCooler", false, 377, (entity*) IFC4X1_types[371]);
    IFC4X1_types[380] = new entity("IfcEvaporator", false, 380, (entity*) IFC4X1_types[371]);
    IFC4X1_types[395] = new entity("IfcExternalSpatialElement", false, 395, (entity*) IFC4X1_types[397]);
    IFC4X1_types[409] = new entity("IfcFanType", false, 409, (entity*) IFC4X1_types[440]);
    IFC4X1_types[422] = new entity("IfcFilterType", false, 422, (entity*) IFC4X1_types[448]);
    IFC4X1_types[425] = new entity("IfcFireSuppressionTerminalType", false, 425, (entity*) IFC4X1_types[446]);
    IFC4X1_types[428] = new entity("IfcFlowController", false, 428, (entity*) IFC4X1_types[294]);
    IFC4X1_types[431] = new entity("IfcFlowFitting", false, 431, (entity*) IFC4X1_types[294]);
    IFC4X1_types[434] = new entity("IfcFlowInstrumentType", false, 434, (entity*) IFC4X1_types[291]);
    IFC4X1_types[436] = new entity("IfcFlowMeter", false, 436, (entity*) IFC4X1_types[428]);
    IFC4X1_types[439] = new entity("IfcFlowMovingDevice", false, 439, (entity*) IFC4X1_types[294]);
    IFC4X1_types[441] = new entity("IfcFlowSegment", false, 441, (entity*) IFC4X1_types[294]);
    IFC4X1_types[443] = new entity("IfcFlowStorageDevice", false, 443, (entity*) IFC4X1_types[294]);
    IFC4X1_types[445] = new entity("IfcFlowTerminal", false, 445, (entity*) IFC4X1_types[294]);
    IFC4X1_types[447] = new entity("IfcFlowTreatmentDevice", false, 447, (entity*) IFC4X1_types[294]);
    IFC4X1_types[452] = new entity("IfcFooting", false, 452, (entity*) IFC4X1_types[103]);
    IFC4X1_types[474] = new entity("IfcGrid", false, 474, (entity*) IFC4X1_types[704]);
    IFC4X1_types[482] = new entity("IfcHeatExchanger", false, 482, (entity*) IFC4X1_types[371]);
    IFC4X1_types[487] = new entity("IfcHumidifier", false, 487, (entity*) IFC4X1_types[371]);
    IFC4X1_types[502] = new entity("IfcInterceptor", false, 502, (entity*) IFC4X1_types[447]);
    IFC4X1_types[514] = new entity("IfcJunctionBox", false, 514, (entity*) IFC4X1_types[431]);
    IFC4X1_types[524] = new entity("IfcLamp", false, 524, (entity*) IFC4X1_types[445]);
    IFC4X1_types[538] = new entity("IfcLightFixture", false, 538, (entity*) IFC4X1_types[445]);
    IFC4X1_types[552] = new entity("IfcLinearPositioningElement", true, 552, (entity*) IFC4X1_types[704]);
    IFC4X1_types[600] = new entity("IfcMedicalDevice", false, 600, (entity*) IFC4X1_types[445]);
    IFC4X1_types[603] = new entity("IfcMember", false, 603, (entity*) IFC4X1_types[103]);
    IFC4X1_types[604] = new entity("IfcMemberStandardCase", false, 604, (entity*) IFC4X1_types[603]);
    IFC4X1_types[623] = new entity("IfcMotorConnection", false, 623, (entity*) IFC4X1_types[371]);
    IFC4X1_types[652] = new entity("IfcOuterBoundaryCurve", false, 652, (entity*) IFC4X1_types[86]);
    IFC4X1_types[653] = new entity("IfcOutlet", false, 653, (entity*) IFC4X1_types[445]);
    IFC4X1_types[674] = new entity("IfcPile", false, 674, (entity*) IFC4X1_types[103]);
    IFC4X1_types[678] = new entity("IfcPipeFitting", false, 678, (entity*) IFC4X1_types[431]);
    IFC4X1_types[681] = new entity("IfcPipeSegment", false, 681, (entity*) IFC4X1_types[441]);
    IFC4X1_types[691] = new entity("IfcPlate", false, 691, (entity*) IFC4X1_types[103]);
    IFC4X1_types[692] = new entity("IfcPlateStandardCase", false, 692, (entity*) IFC4X1_types[691]);
    IFC4X1_types[766] = new entity("IfcProtectiveDevice", false, 766, (entity*) IFC4X1_types[428]);
    IFC4X1_types[768] = new entity("IfcProtectiveDeviceTrippingUnitType", false, 768, (entity*) IFC4X1_types[291]);
    IFC4X1_types[773] = new entity("IfcPump", false, 773, (entity*) IFC4X1_types[439]);
    IFC4X1_types[784] = new entity("IfcRailing", false, 784, (entity*) IFC4X1_types[103]);
    IFC4X1_types[787] = new entity("IfcRamp", false, 787, (entity*) IFC4X1_types[103]);
    IFC4X1_types[788] = new entity("IfcRampFlight", false, 788, (entity*) IFC4X1_types[103]);
    IFC4X1_types[794] = new entity("IfcRationalBSplineCurveWithKnots", false, 794, (entity*) IFC4X1_types[98]);
    IFC4X1_types[810] = new entity("IfcReinforcingBar", false, 810, (entity*) IFC4X1_types[815]);
    IFC4X1_types[813] = new entity("IfcReinforcingBarType", false, 813, (entity*) IFC4X1_types[816]);
    IFC4X1_types[885] = new entity("IfcRoof", false, 885, (entity*) IFC4X1_types[103]);
    IFC4X1_types[894] = new entity("IfcSanitaryTerminal", false, 894, (entity*) IFC4X1_types[445]);
    IFC4X1_types[909] = new entity("IfcSensorType", false, 909, (entity*) IFC4X1_types[291]);
    IFC4X1_types[912] = new entity("IfcShadingDevice", false, 912, (entity*) IFC4X1_types[103]);
    IFC4X1_types[930] = new entity("IfcSlab", false, 930, (entity*) IFC4X1_types[103]);
    IFC4X1_types[931] = new entity("IfcSlabElementedCase", false, 931, (entity*) IFC4X1_types[930]);
    IFC4X1_types[932] = new entity("IfcSlabStandardCase", false, 932, (entity*) IFC4X1_types[930]);
    IFC4X1_types[936] = new entity("IfcSolarDevice", false, 936, (entity*) IFC4X1_types[371]);
    IFC4X1_types[948] = new entity("IfcSpaceHeater", false, 948, (entity*) IFC4X1_types[445]);
    IFC4X1_types[966] = new entity("IfcStackTerminal", false, 966, (entity*) IFC4X1_types[445]);
    IFC4X1_types[969] = new entity("IfcStair", false, 969, (entity*) IFC4X1_types[103]);
    IFC4X1_types[970] = new entity("IfcStairFlight", false, 970, (entity*) IFC4X1_types[103]);
    IFC4X1_types[979] = new entity("IfcStructuralAnalysisModel", false, 979, (entity*) IFC4X1_types[1051]);
    IFC4X1_types[992] = new entity("IfcStructuralLoadCase", false, 992, (entity*) IFC4X1_types[994]);
    IFC4X1_types[1005] = new entity("IfcStructuralPlanarAction", false, 1005, (entity*) IFC4X1_types[1011]);
    IFC4X1_types[1048] = new entity("IfcSwitchingDevice", false, 1048, (entity*) IFC4X1_types[428]);
    IFC4X1_types[1058] = new entity("IfcTank", false, 1058, (entity*) IFC4X1_types[443]);
    IFC4X1_types[1114] = new entity("IfcTransformer", false, 1114, (entity*) IFC4X1_types[371]);
    IFC4X1_types[1131] = new entity("IfcTubeBundle", false, 1131, (entity*) IFC4X1_types[371]);
    IFC4X1_types[1140] = new entity("IfcUnitaryControlElementType", false, 1140, (entity*) IFC4X1_types[291]);
    IFC4X1_types[1142] = new entity("IfcUnitaryEquipment", false, 1142, (entity*) IFC4X1_types[371]);
    IFC4X1_types[1150] = new entity("IfcValve", false, 1150, (entity*) IFC4X1_types[428]);
    IFC4X1_types[1168] = new entity("IfcWall", false, 1168, (entity*) IFC4X1_types[103]);
    IFC4X1_types[1169] = new entity("IfcWallElementedCase", false, 1169, (entity*) IFC4X1_types[1168]);
    IFC4X1_types[1170] = new entity("IfcWallStandardCase", false, 1170, (entity*) IFC4X1_types[1168]);
    IFC4X1_types[1176] = new entity("IfcWasteTerminal", false, 1176, (entity*) IFC4X1_types[445]);
    IFC4X1_types[1179] = new entity("IfcWindow", false, 1179, (entity*) IFC4X1_types[103]);
    IFC4X1_types[1184] = new entity("IfcWindowStandardCase", false, 1184, (entity*) IFC4X1_types[1179]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X1_types[395]);
        items.push_back(IFC4X1_types[946]);
        IFC4X1_types[947] = new select_type("IfcSpaceBoundarySelect", 947, items);
    }
    IFC4X1_types[10] = new entity("IfcActuatorType", false, 10, (entity*) IFC4X1_types[291]);
    IFC4X1_types[17] = new entity("IfcAirTerminal", false, 17, (entity*) IFC4X1_types[445]);
    IFC4X1_types[18] = new entity("IfcAirTerminalBox", false, 18, (entity*) IFC4X1_types[428]);
    IFC4X1_types[23] = new entity("IfcAirToAirHeatRecovery", false, 23, (entity*) IFC4X1_types[371]);
    IFC4X1_types[27] = new entity("IfcAlarmType", false, 27, (entity*) IFC4X1_types[291]);
    IFC4X1_types[29] = new entity("IfcAlignment", false, 29, (entity*) IFC4X1_types[552]);
    IFC4X1_types[61] = new entity("IfcAudioVisualAppliance", false, 61, (entity*) IFC4X1_types[445]);
    IFC4X1_types[68] = new entity("IfcBeam", false, 68, (entity*) IFC4X1_types[103]);
    IFC4X1_types[69] = new entity("IfcBeamStandardCase", false, 69, (entity*) IFC4X1_types[68]);
    IFC4X1_types[77] = new entity("IfcBoiler", false, 77, (entity*) IFC4X1_types[371]);
    IFC4X1_types[114] = new entity("IfcBurner", false, 114, (entity*) IFC4X1_types[371]);
    IFC4X1_types[117] = new entity("IfcCableCarrierFitting", false, 117, (entity*) IFC4X1_types[431]);
    IFC4X1_types[120] = new entity("IfcCableCarrierSegment", false, 120, (entity*) IFC4X1_types[441]);
    IFC4X1_types[123] = new entity("IfcCableFitting", false, 123, (entity*) IFC4X1_types[431]);
    IFC4X1_types[126] = new entity("IfcCableSegment", false, 126, (entity*) IFC4X1_types[441]);
    IFC4X1_types[141] = new entity("IfcChiller", false, 141, (entity*) IFC4X1_types[371]);
    IFC4X1_types[158] = new entity("IfcCoil", false, 158, (entity*) IFC4X1_types[371]);
    IFC4X1_types[170] = new entity("IfcCommunicationsAppliance", false, 170, (entity*) IFC4X1_types[445]);
    IFC4X1_types[182] = new entity("IfcCompressor", false, 182, (entity*) IFC4X1_types[439]);
    IFC4X1_types[185] = new entity("IfcCondenser", false, 185, (entity*) IFC4X1_types[371]);
    IFC4X1_types[215] = new entity("IfcControllerType", false, 215, (entity*) IFC4X1_types[291]);
    IFC4X1_types[219] = new entity("IfcCooledBeam", false, 219, (entity*) IFC4X1_types[371]);
    IFC4X1_types[222] = new entity("IfcCoolingTower", false, 222, (entity*) IFC4X1_types[371]);
    IFC4X1_types[263] = new entity("IfcDamper", false, 263, (entity*) IFC4X1_types[428]);
    IFC4X1_types[286] = new entity("IfcDistributionChamberElement", false, 286, (entity*) IFC4X1_types[294]);
    IFC4X1_types[289] = new entity("IfcDistributionCircuit", false, 289, (entity*) IFC4X1_types[298]);
    IFC4X1_types[290] = new entity("IfcDistributionControlElement", false, 290, (entity*) IFC4X1_types[292]);
    IFC4X1_types[321] = new entity("IfcDuctFitting", false, 321, (entity*) IFC4X1_types[431]);
    IFC4X1_types[324] = new entity("IfcDuctSegment", false, 324, (entity*) IFC4X1_types[441]);
    IFC4X1_types[327] = new entity("IfcDuctSilencer", false, 327, (entity*) IFC4X1_types[447]);
    IFC4X1_types[335] = new entity("IfcElectricAppliance", false, 335, (entity*) IFC4X1_types[445]);
    IFC4X1_types[342] = new entity("IfcElectricDistributionBoard", false, 342, (entity*) IFC4X1_types[428]);
    IFC4X1_types[345] = new entity("IfcElectricFlowStorageDevice", false, 345, (entity*) IFC4X1_types[443]);
    IFC4X1_types[348] = new entity("IfcElectricGenerator", false, 348, (entity*) IFC4X1_types[371]);
    IFC4X1_types[351] = new entity("IfcElectricMotor", false, 351, (entity*) IFC4X1_types[371]);
    IFC4X1_types[355] = new entity("IfcElectricTimeControl", false, 355, (entity*) IFC4X1_types[428]);
    IFC4X1_types[408] = new entity("IfcFan", false, 408, (entity*) IFC4X1_types[439]);
    IFC4X1_types[421] = new entity("IfcFilter", false, 421, (entity*) IFC4X1_types[447]);
    IFC4X1_types[424] = new entity("IfcFireSuppressionTerminal", false, 424, (entity*) IFC4X1_types[445]);
    IFC4X1_types[433] = new entity("IfcFlowInstrument", false, 433, (entity*) IFC4X1_types[290]);
    IFC4X1_types[767] = new entity("IfcProtectiveDeviceTrippingUnit", false, 767, (entity*) IFC4X1_types[290]);
    IFC4X1_types[908] = new entity("IfcSensor", false, 908, (entity*) IFC4X1_types[290]);
    IFC4X1_types[1139] = new entity("IfcUnitaryControlElement", false, 1139, (entity*) IFC4X1_types[290]);
    IFC4X1_types[9] = new entity("IfcActuator", false, 9, (entity*) IFC4X1_types[290]);
    IFC4X1_types[26] = new entity("IfcAlarm", false, 26, (entity*) IFC4X1_types[290]);
    IFC4X1_types[214] = new entity("IfcController", false, 214, (entity*) IFC4X1_types[290]);
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[3]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[2])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TheActor", new named_type(IFC4X1_types[8]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[6])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Role", new named_type(IFC4X1_types[884]), false));
        attributes.push_back(new attribute("UserDefinedRole", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[7])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[11]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[9])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[11]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[10])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X1_types[13]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("UserDefinedPurpose", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[12])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[14])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[157])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[15])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[16])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[22]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[17])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[20]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[18])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[20]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[19])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[22]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[21])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[25]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[23])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[25]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[24])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[28]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[26])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[28]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[27])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[39]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[29])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("StartDistAlong", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[31])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[30])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CurveGeometry", new named_type(IFC4X1_types[256]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[31])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TangentialContinuity", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("StartTag", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("EndTag", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[32])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("IsConvex", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[33])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[34])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ParabolaConstant", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("IsConvex", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[35])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[37])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[36])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("StartDistAlong", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("HorizontalLength", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("StartHeight", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("StartGradient", new named_type(IFC4X1_types[793]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[37])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Horizontal", new named_type(IFC4X1_types[30]), false));
        attributes.push_back(new attribute("Vertical", new named_type(IFC4X1_types[36]), true));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[38])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[44])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[249])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[45])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ApplicationDeveloper", new named_type(IFC4X1_types[648]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("ApplicationFullName", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("ApplicationIdentifier", new named_type(IFC4X1_types[490]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[46])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("AppliedValue", new named_type(IFC4X1_types[48]), true));
        attributes.push_back(new attribute("UnitBasis", new named_type(IFC4X1_types[596]), true));
        attributes.push_back(new attribute("ApplicableDate", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("FixedUntilDate", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Condition", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("ArithmeticOperator", new named_type(IFC4X1_types[57]), true));
        attributes.push_back(new attribute("Components", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[47])), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[47])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Identifier", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("TimeOfApproval", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Level", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Qualifier", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("RequestingApproval", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("GivingApproval", new named_type(IFC4X1_types[8]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[49])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4X1_types[49]), false));
        attributes.push_back(new attribute("RelatedApprovals", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[49])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[50])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OuterCurve", new named_type(IFC4X1_types[249]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[51])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Curve", new named_type(IFC4X1_types[91]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[52])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[249])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[53])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC4X1_types[232]), true));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC4X1_types[232]), true));
        attributes.push_back(new attribute("TotalReplacementCost", new named_type(IFC4X1_types[232]), true));
        attributes.push_back(new attribute("Owner", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("User", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("ResponsiblePerson", new named_type(IFC4X1_types[667]), true));
        attributes.push_back(new attribute("IncorporationDate", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("DepreciatedValue", new named_type(IFC4X1_types[232]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[59])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("BottomFlangeWidth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("BottomFlangeThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("BottomFlangeFilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("TopFlangeWidth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("TopFlangeThickness", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("TopFlangeFilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("BottomFlangeEdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("BottomFlangeSlope", new named_type(IFC4X1_types[690]), true));
        attributes.push_back(new attribute("TopFlangeEdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("TopFlangeSlope", new named_type(IFC4X1_types[690]), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[60])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[63]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[61])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[63]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[62])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X1_types[280]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[64])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4X1_types[280]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[66])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X1_types[280]), true));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4X1_types[280]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[67])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Degree", new named_type(IFC4X1_types[500]), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[130])), false));
        attributes.push_back(new attribute("CurveForm", new named_type(IFC4X1_types[97]), false));
        attributes.push_back(new attribute("ClosedCurve", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X1_types[559]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[96])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("KnotMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[500])), false));
        attributes.push_back(new attribute("Knots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[658])), false));
        attributes.push_back(new attribute("KnotSpec", new named_type(IFC4X1_types[518]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[98])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("UDegree", new named_type(IFC4X1_types[500]), false));
        attributes.push_back(new attribute("VDegree", new named_type(IFC4X1_types[500]), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[130]))), false));
        attributes.push_back(new attribute("SurfaceForm", new named_type(IFC4X1_types[100]), false));
        attributes.push_back(new attribute("UClosed", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("VClosed", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X1_types[559]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[99])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("UMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[500])), false));
        attributes.push_back(new attribute("VMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[500])), false));
        attributes.push_back(new attribute("UKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[658])), false));
        attributes.push_back(new attribute("VKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[658])), false));
        attributes.push_back(new attribute("KnotSpec", new named_type(IFC4X1_types[518]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[101])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[71]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[68])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[69])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[71]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[70])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RasterFormat", new named_type(IFC4X1_types[490]), false));
        attributes.push_back(new attribute("RasterCode", new named_type(IFC4X1_types[74]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[75])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("ZLength", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[76])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[79]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[77])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[79]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[78])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[81])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Operator", new named_type(IFC4X1_types[83]), false));
        attributes.push_back(new attribute("FirstOperand", new named_type(IFC4X1_types[82]), false));
        attributes.push_back(new attribute("SecondOperand", new named_type(IFC4X1_types[82]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[84])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[85])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[86])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TranslationalStiffnessByLengthX", new named_type(IFC4X1_types[616]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByLengthY", new named_type(IFC4X1_types[616]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByLengthZ", new named_type(IFC4X1_types[616]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthX", new named_type(IFC4X1_types[613]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthY", new named_type(IFC4X1_types[613]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthZ", new named_type(IFC4X1_types[613]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[87])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TranslationalStiffnessByAreaX", new named_type(IFC4X1_types[615]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByAreaY", new named_type(IFC4X1_types[615]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByAreaZ", new named_type(IFC4X1_types[615]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[88])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TranslationalStiffnessX", new named_type(IFC4X1_types[1120]), true));
        attributes.push_back(new attribute("TranslationalStiffnessY", new named_type(IFC4X1_types[1120]), true));
        attributes.push_back(new attribute("TranslationalStiffnessZ", new named_type(IFC4X1_types[1120]), true));
        attributes.push_back(new attribute("RotationalStiffnessX", new named_type(IFC4X1_types[892]), true));
        attributes.push_back(new attribute("RotationalStiffnessY", new named_type(IFC4X1_types[892]), true));
        attributes.push_back(new attribute("RotationalStiffnessZ", new named_type(IFC4X1_types[892]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[89])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingStiffness", new named_type(IFC4X1_types[1175]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[90])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[91])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[92])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Corner", new named_type(IFC4X1_types[130]), false));
        attributes.push_back(new attribute("XDim", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("ZDim", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[93])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Enclosure", new named_type(IFC4X1_types[93]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[95])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ElevationOfRefHeight", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("ElevationOfTerrain", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("BuildingAddress", new named_type(IFC4X1_types[709]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[102])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[103])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[106]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[104])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[106]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[105])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[109]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[107])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[109]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[108])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[110])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elevation", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[111])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[113]), true));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[116]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[114])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[116]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[115])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("Girth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("InternalFilletRadius", new named_type(IFC4X1_types[627]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[243])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[119]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[117])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[119]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[118])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[122]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[120])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[122]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[121])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[125]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[123])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[125]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[124])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[128]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[126])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[128]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[127])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4X1_types[530])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[130])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_types[530]))), false));
        attributes.push_back(new attribute("TagList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[132])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[530]))), false));
        attributes.push_back(new attribute("TagList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[133])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Axis1", new named_type(IFC4X1_types[280]), true));
        attributes.push_back(new attribute("Axis2", new named_type(IFC4X1_types[280]), true));
        attributes.push_back(new attribute("LocalOrigin", new named_type(IFC4X1_types[130]), false));
        attributes.push_back(new attribute("Scale", new named_type(IFC4X1_types[796]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[135])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Scale2", new named_type(IFC4X1_types[796]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[136])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis3", new named_type(IFC4X1_types[280]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[137])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Scale2", new named_type(IFC4X1_types[796]), true));
        attributes.push_back(new attribute("Scale3", new named_type(IFC4X1_types[796]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[138])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Thickness", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[139])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[143]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[141])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[143]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[142])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[146]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[144])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[146]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[145])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[147])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[148])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[149])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("IsCCW", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[150])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[151])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[152])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Source", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Edition", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("EditionDate", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4X1_types[1147]), true));
        attributes.push_back(new attribute("ReferenceTokens", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[490])), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[153])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ReferencedSource", new named_type(IFC4X1_types[155]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Sort", new named_type(IFC4X1_types[490]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[154])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[157])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[160]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[158])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[160]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[159])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Red", new named_type(IFC4X1_types[628]), false));
        attributes.push_back(new attribute("Green", new named_type(IFC4X1_types[628]), false));
        attributes.push_back(new attribute("Blue", new named_type(IFC4X1_types[628]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[163])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ColourList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[628]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[164])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[165])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[169]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[166])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[167])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[169]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[168])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[172]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[170])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[172]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[171])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4X1_types[490]), false));
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[747])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[174])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4X1_types[176]), true));
        attributes.push_back(new attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[764])), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[175])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[179])), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X1_types[559]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[177])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[178])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Transition", new named_type(IFC4X1_types[1117]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("ParentCurve", new named_type(IFC4X1_types[249]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[179])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4X1_types[736])), false));
        attributes.push_back(new attribute("Label", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[180])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[184]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[182])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[184]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[183])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[187]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[185])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[187]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[186])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[65]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[188])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[400])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[189])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CurveOnRelatingElement", new named_type(IFC4X1_types[255]), false));
        attributes.push_back(new attribute("CurveOnRelatedElement", new named_type(IFC4X1_types[255]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[190])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[191])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("EccentricityInX", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("EccentricityInY", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("EccentricityInZ", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[192])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PointOnRelatingElement", new named_type(IFC4X1_types[698]), false));
        attributes.push_back(new attribute("PointOnRelatedElement", new named_type(IFC4X1_types[698]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[193])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceOnRelatingElement", new named_type(IFC4X1_types[1033]), false));
        attributes.push_back(new attribute("SurfaceOnRelatedElement", new named_type(IFC4X1_types[1033]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[194])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VolumeOnRelatingElement", new named_type(IFC4X1_types[941]), false));
        attributes.push_back(new attribute("VolumeOnRelatedElement", new named_type(IFC4X1_types[941]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[196])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("ConstraintGrade", new named_type(IFC4X1_types[198]), false));
        attributes.push_back(new attribute("ConstraintSource", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("CreatingActor", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("UserDefinedGrade", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[197])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[201]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[199])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[201]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[200])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[204]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[202])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[204]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[203])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[207]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[205])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[207]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[206])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Usage", new named_type(IFC4X1_types[879]), true));
        attributes.push_back(new attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[47])), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC4X1_types[672]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[208])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[47])), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC4X1_types[672]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[209])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Phase", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[870])), true));
        attributes.push_back(new attribute("UnitsInContext", new named_type(IFC4X1_types[1145]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[210])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[212])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[213])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[216]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[214])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[216]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[215])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("ConversionFactor", new named_type(IFC4X1_types[596]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[217])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConversionOffset", new named_type(IFC4X1_types[796]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[218])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[221]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[219])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[221]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[220])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[224]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[222])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[224]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[223])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SourceCRS", new named_type(IFC4X1_types[227]), false));
        attributes.push_back(new attribute("TargetCRS", new named_type(IFC4X1_types[226]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[225])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("GeodeticDatum", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("VerticalDatum", new named_type(IFC4X1_types[490]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[226])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[229]), true));
        attributes.push_back(new attribute("CostValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[232])), true));
        attributes.push_back(new attribute("CostQuantities", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[672])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[228])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[231]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("SubmittedOn", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("UpdateDate", new named_type(IFC4X1_types[268]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[230])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[232])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[236]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[234])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[236]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[235])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[239]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[237])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[239]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[238])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[67]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[240])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TreeRootExpression", new named_type(IFC4X1_types[241]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[242])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingMonetaryUnit", new named_type(IFC4X1_types[621]), false));
        attributes.push_back(new attribute("RelatedMonetaryUnit", new named_type(IFC4X1_types[621]), false));
        attributes.push_back(new attribute("ExchangeRate", new named_type(IFC4X1_types[708]), false));
        attributes.push_back(new attribute("RateDateTime", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("RateSource", new named_type(IFC4X1_types[531]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[244])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[247]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[245])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[247]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[246])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[249])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X1_types[689]), false));
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X1_types[249])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[250])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X1_types[1026]), false));
        attributes.push_back(new attribute("Boundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[86])), false));
        attributes.push_back(new attribute("ImplicitOuter", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[251])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("StartPoint", new named_type(IFC4X1_types[130]), false));
        attributes.push_back(new attribute("StartDirection", new named_type(IFC4X1_types[690]), false));
        attributes.push_back(new attribute("SegmentLength", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[256])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CurveFont", new named_type(IFC4X1_types[252]), true));
        attributes.push_back(new attribute("CurveWidth", new named_type(IFC4X1_types[929]), true));
        attributes.push_back(new attribute("CurveColour", new named_type(IFC4X1_types[161]), true));
        attributes.push_back(new attribute("ModelOrDraughting", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[257])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[260])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[258])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("CurveFont", new named_type(IFC4X1_types[261]), false));
        attributes.push_back(new attribute("CurveFontScaling", new named_type(IFC4X1_types[708]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[259])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VisibleSegmentLength", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("InvisibleSegmentLength", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[260])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[262])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[265]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[263])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[265]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[264])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ParentProfile", new named_type(IFC4X1_types[736]), false));
        attributes.push_back(new attribute("Operator", new named_type(IFC4X1_types[135]), false));
        attributes.push_back(new attribute("Label", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[273])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[275])), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC4X1_types[276]), false));
        attributes.push_back(new attribute("UserDefinedType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[274])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[626]), false));
        attributes.push_back(new attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[275])->set_attributes(attributes, derived);
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
        ((entity*)IFC4X1_types[278])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_types[796])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[280])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[284]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[282])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[284]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[283])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("DistanceAlong", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("OffsetLateral", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("OffsetVertical", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("OffsetLongitudinal", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("AlongHorizontal", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[285])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[288]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[286])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[288]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[287])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[289])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[290])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[291])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[292])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[293])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[294])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[295])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("FlowDirection", new named_type(IFC4X1_types[430]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[297]), true));
        attributes.push_back(new attribute("SystemType", new named_type(IFC4X1_types[299]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[296])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[299]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[298])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4X1_types[1147]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("IntendedUse", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Scope", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Revision", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("DocumentOwner", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[8])), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("LastRevisionTime", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ElectronicFormat", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("ValidFrom", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("ValidUntil", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("Confidentiality", new named_type(IFC4X1_types[300]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[305]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[301])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC4X1_types[301]), false));
        attributes.push_back(new attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[301])), false));
        attributes.push_back(new attribute("RelationshipType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[302])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("ReferencedDocument", new named_type(IFC4X1_types[301]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[303])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[316]), true));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X1_types[317]), true));
        attributes.push_back(new attribute("UserDefinedOperationType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[306])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(13);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("ThresholdDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("ThresholdThickness", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("TransomOffset", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("ThresholdOffset", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("CasingThickness", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("CasingDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X1_types[915]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetX", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetY", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[307])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PanelDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PanelOperation", new named_type(IFC4X1_types[308]), false));
        attributes.push_back(new attribute("PanelWidth", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4X1_types[309]), false));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X1_types[915]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[310])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[311])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X1_types[314]), false));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4X1_types[313]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("Sizeable", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[312])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[316]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X1_types[317]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("UserDefinedOperationType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[315])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[319])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[320])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[323]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[321])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[323]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[322])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[326]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[324])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[326]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[325])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[329]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[327])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[329]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[328])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeStart", new named_type(IFC4X1_types[1156]), false));
        attributes.push_back(new attribute("EdgeEnd", new named_type(IFC4X1_types[1156]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[332])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeGeometry", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[333])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[651])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[334])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[337]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[335])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[337]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[336])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[344]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[342])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[344]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[343])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[347]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[345])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[347]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[346])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[350]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[348])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[350]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[349])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[353]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[351])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[353]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[352])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[357]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[355])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[357]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[356])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Tag", new named_type(IFC4X1_types[490]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[359])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC4X1_types[58]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[363]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[361])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[363]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[362])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[364])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[365])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MethodOfMeasurement", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[672])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[367])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[368])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[67]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[360])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[369])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[370])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[371])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[372])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[376]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[374])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[376]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[375])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[379]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[377])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[379]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[378])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[382]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[380])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[382]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[381])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[387]), true));
        attributes.push_back(new attribute("EventTriggerType", new named_type(IFC4X1_types[385]), true));
        attributes.push_back(new attribute("UserDefinedEventTriggerType", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("EventOccurenceTime", new named_type(IFC4X1_types[384]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[383])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ActualDate", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("EarlyDate", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("LateDate", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ScheduleDate", new named_type(IFC4X1_types[268]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[384])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[387]), false));
        attributes.push_back(new attribute("EventTriggerType", new named_type(IFC4X1_types[385]), false));
        attributes.push_back(new attribute("UserDefinedEventTriggerType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[386])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Properties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[747])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[388])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[389])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Location", new named_type(IFC4X1_types[1147]), true));
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[393])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingReference", new named_type(IFC4X1_types[393]), false));
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[877])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[394])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[396]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[395])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[397])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[390])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[391])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[392])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC4X1_types[280]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[398])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EndSweptArea", new named_type(IFC4X1_types[736]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[399])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[402])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[400])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[189])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[401])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Bound", new named_type(IFC4X1_types[561]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[402])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[403])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FaceSurface", new named_type(IFC4X1_types[1026]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[404])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[405])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[157])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[406])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TensionFailureX", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("TensionFailureY", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("TensionFailureZ", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("CompressionFailureX", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("CompressionFailureY", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("CompressionFailureZ", new named_type(IFC4X1_types[455]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[407])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[410]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[408])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[410]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[409])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[413]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[411])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[413]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[412])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[414])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[415])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[416])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[420])), false));
        attributes.push_back(new attribute("ModelorDraughting", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[417])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("HatchLineAppearance", new named_type(IFC4X1_types[257]), false));
        attributes.push_back(new attribute("StartOfNextHatchLine", new named_type(IFC4X1_types[481]), false));
        attributes.push_back(new attribute("PointOfReferenceHatchLine", new named_type(IFC4X1_types[130]), true));
        attributes.push_back(new attribute("PatternStart", new named_type(IFC4X1_types[130]), true));
        attributes.push_back(new attribute("HatchLineAngle", new named_type(IFC4X1_types[690]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[418])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TilingPattern", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_types[1154])), false));
        attributes.push_back(new attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[1019])), false));
        attributes.push_back(new attribute("TilingScale", new named_type(IFC4X1_types[708]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[419])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[423]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[421])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[423]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[422])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[426]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[424])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[426]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[425])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4X1_types[658]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4X1_types[658]), true));
        attributes.push_back(new attribute("FixedReference", new named_type(IFC4X1_types[280]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[427])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[428])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[429])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[431])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[432])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[435]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[433])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[435]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[434])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[438]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[436])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[438]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[437])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[439])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[440])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[441])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[442])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[443])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[444])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[445])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[446])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[447])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[448])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[454]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[452])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[454]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[453])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[457])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[458])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[461]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[459])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC4X1_types[58]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[461]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[460])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[464]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[462])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[464]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[463])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[465])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CoordinateSpaceDimension", new named_type(IFC4X1_types[279]), false));
        attributes.push_back(new attribute("Precision", new named_type(IFC4X1_types[796]), true));
        attributes.push_back(new attribute("WorldCoordinateSystem", new named_type(IFC4X1_types[65]), false));
        attributes.push_back(new attribute("TrueNorth", new named_type(IFC4X1_types[280]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[467])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[468])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ParentContext", new named_type(IFC4X1_types[467]), false));
        attributes.push_back(new attribute("TargetScale", new named_type(IFC4X1_types[708]), true));
        attributes.push_back(new attribute("TargetView", new named_type(IFC4X1_types[466]), false));
        attributes.push_back(new attribute("UserDefinedTargetView", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[469])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[471])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[470])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[475])), false));
        attributes.push_back(new attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[475])), false));
        attributes.push_back(new attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[475])), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[478]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[474])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("AxisTag", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("AxisCurve", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[475])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementLocation", new named_type(IFC4X1_types[1163]), false));
        attributes.push_back(new attribute("PlacementRefDirection", new named_type(IFC4X1_types[477]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[476])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[479])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseSurface", new named_type(IFC4X1_types[1026]), false));
        attributes.push_back(new attribute("AgreementFlag", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[480])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[484]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[482])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[484]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[483])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[489]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[487])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[489]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[488])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4X1_types[690]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[512])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("URLReference", new named_type(IFC4X1_types[1147]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[492])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4X1_types[1076]), false));
        attributes.push_back(new attribute("Opacity", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("Colours", new named_type(IFC4X1_types[164]), false));
        attributes.push_back(new attribute("ColourIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[705])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[493])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Points", new named_type(IFC4X1_types[131]), false));
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[907])), true));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[494])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_types[705])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[495])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCoordIndices", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_types[705]))), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[496])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4X1_types[1076]), false));
        attributes.push_back(new attribute("TexCoords", new named_type(IFC4X1_types[1095]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[497])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TexCoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[705]))), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[498])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[504]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[502])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[504]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[503])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[506])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[508]), true));
        attributes.push_back(new attribute("Jurisdiction", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[667])), true));
        attributes.push_back(new attribute("LastUpdateDate", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC4X1_types[232]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC4X1_types[232]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[507])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[511])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[510])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStamp", new named_type(IFC4X1_types[268]), false));
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[511])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[516]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[514])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[516]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[515])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("Thickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("LegSlope", new named_type(IFC4X1_types[690]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[562])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[522]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[520])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[522]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[521])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LagValue", new named_type(IFC4X1_types[1104]), false));
        attributes.push_back(new attribute("DurationType", new named_type(IFC4X1_types[1062]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[523])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[526]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[524])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[526]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[525])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Publisher", new named_type(IFC4X1_types[8]), true));
        attributes.push_back(new attribute("VersionDate", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4X1_types[1147]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[531])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Language", new named_type(IFC4X1_types[527]), true));
        attributes.push_back(new attribute("ReferencedLibrary", new named_type(IFC4X1_types[531]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[532])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MainPlaneAngle", new named_type(IFC4X1_types[690]), false));
        attributes.push_back(new attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[690])), false));
        attributes.push_back(new attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[564])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[535])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[540]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[538])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[540]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[539])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LightDistributionCurve", new named_type(IFC4X1_types[534]), false));
        attributes.push_back(new attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[535])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[541])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("LightColour", new named_type(IFC4X1_types[163]), false));
        attributes.push_back(new attribute("AmbientIntensity", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("Intensity", new named_type(IFC4X1_types[628]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[542])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[543])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X1_types[280]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[544])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[67]), false));
        attributes.push_back(new attribute("ColourAppearance", new named_type(IFC4X1_types[163]), true));
        attributes.push_back(new attribute("ColourTemperature", new named_type(IFC4X1_types[1101]), false));
        attributes.push_back(new attribute("LuminousFlux", new named_type(IFC4X1_types[563]), false));
        attributes.push_back(new attribute("LightEmissionSource", new named_type(IFC4X1_types[537]), false));
        attributes.push_back(new attribute("LightDistributionDataSource", new named_type(IFC4X1_types[536]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[545])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[130]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("ConstantAttenuation", new named_type(IFC4X1_types[796]), false));
        attributes.push_back(new attribute("DistanceAttenuation", new named_type(IFC4X1_types[796]), false));
        attributes.push_back(new attribute("QuadricAttenuation", new named_type(IFC4X1_types[796]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[546])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X1_types[280]), false));
        attributes.push_back(new attribute("ConcentrationExponent", new named_type(IFC4X1_types[796]), true));
        attributes.push_back(new attribute("SpreadAngle", new named_type(IFC4X1_types[707]), false));
        attributes.push_back(new attribute("BeamWidthAngle", new named_type(IFC4X1_types[707]), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[547])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Pnt", new named_type(IFC4X1_types[130]), false));
        attributes.push_back(new attribute("Dir", new named_type(IFC4X1_types[1154]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[548])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[556])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PlacementRelTo", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("Distance", new named_type(IFC4X1_types[285]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X1_types[650]), true));
        attributes.push_back(new attribute("CartesianPosition", new named_type(IFC4X1_types[67]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[551])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X1_types[249]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[552])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementRelTo", new named_type(IFC4X1_types[635]), true));
        attributes.push_back(new attribute("RelativePlacement", new named_type(IFC4X1_types[65]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[558])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[561])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Outer", new named_type(IFC4X1_types[157]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[568])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Eastings", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("Northings", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("OrthogonalHeight", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("XAxisAbscissa", new named_type(IFC4X1_types[796]), true));
        attributes.push_back(new attribute("XAxisOrdinate", new named_type(IFC4X1_types[796]), true));
        attributes.push_back(new attribute("Scale", new named_type(IFC4X1_types[796]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[569])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingSource", new named_type(IFC4X1_types[872]), false));
        attributes.push_back(new attribute("MappingTarget", new named_type(IFC4X1_types[134]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[570])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[575])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[156])), false));
        attributes.push_back(new attribute("ClassifiedMaterial", new named_type(IFC4X1_types[575]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[576])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Material", new named_type(IFC4X1_types[575]), false));
        attributes.push_back(new attribute("Fraction", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[577])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("MaterialConstituents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[577])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[578])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[579])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RepresentedMaterial", new named_type(IFC4X1_types[575]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[580])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Material", new named_type(IFC4X1_types[575]), true));
        attributes.push_back(new attribute("LayerThickness", new named_type(IFC4X1_types[627]), false));
        attributes.push_back(new attribute("IsVentilated", new named_type(IFC4X1_types[559]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Priority", new named_type(IFC4X1_types[500]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[581])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[581])), false));
        attributes.push_back(new attribute("LayerSetName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[582])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ForLayerSet", new named_type(IFC4X1_types[582]), false));
        attributes.push_back(new attribute("LayerSetDirection", new named_type(IFC4X1_types[529]), false));
        attributes.push_back(new attribute("DirectionSense", new named_type(IFC4X1_types[281]), false));
        attributes.push_back(new attribute("OffsetFromReferenceLine", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("ReferenceExtent", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[583])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OffsetDirection", new named_type(IFC4X1_types[529]), false));
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X1_types[530])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[584])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[575])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[585])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Material", new named_type(IFC4X1_types[575]), true));
        attributes.push_back(new attribute("Profile", new named_type(IFC4X1_types[736]), false));
        attributes.push_back(new attribute("Priority", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[586])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("MaterialProfiles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[586])), false));
        attributes.push_back(new attribute("CompositeProfile", new named_type(IFC4X1_types[180]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[587])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ForProfileSet", new named_type(IFC4X1_types[587]), false));
        attributes.push_back(new attribute("CardinalPoint", new named_type(IFC4X1_types[129]), true));
        attributes.push_back(new attribute("ReferenceExtent", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[588])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ForProfileEndSet", new named_type(IFC4X1_types[587]), false));
        attributes.push_back(new attribute("CardinalEndPoint", new named_type(IFC4X1_types[129]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[589])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X1_types[530])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[590])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Material", new named_type(IFC4X1_types[579]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[591])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC4X1_types[575]), false));
        attributes.push_back(new attribute("RelatedMaterials", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[575])), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[592])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[594])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ValueComponent", new named_type(IFC4X1_types[1149]), false));
        attributes.push_back(new attribute("UnitComponent", new named_type(IFC4X1_types[1138]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[596])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[599]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[597])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[599]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[598])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[602]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[600])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[602]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[601])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[606]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[603])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[604])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[606]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[605])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Benchmark", new named_type(IFC4X1_types[72]), false));
        attributes.push_back(new attribute("ValueSource", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("DataValue", new named_type(IFC4X1_types[608]), true));
        attributes.push_back(new attribute("ReferencePath", new named_type(IFC4X1_types[803]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[607])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(false);
        ((entity*)IFC4X1_types[609])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Currency", new named_type(IFC4X1_types[519]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[621])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[625]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[623])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[625]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[624])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Dimensions", new named_type(IFC4X1_types[278]), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC4X1_types[1146]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[626])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[631])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[632])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[635])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BenchmarkValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[197])), true));
        attributes.push_back(new attribute("LogicalAggregator", new named_type(IFC4X1_types[560]), true));
        attributes.push_back(new attribute("ObjectiveQualifier", new named_type(IFC4X1_types[634]), false));
        attributes.push_back(new attribute("UserDefinedQualifier", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[633])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[639]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[638])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4X1_types[249]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[640])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Distance", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X1_types[559]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[641])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Distance", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4X1_types[280]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[642])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[285])), false));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[643])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[647])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[645]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[644])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[646])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[12])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[648])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOrganization", new named_type(IFC4X1_types[648]), false));
        attributes.push_back(new attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[648])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[649])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LateralAxisDirection", new named_type(IFC4X1_types[280]), false));
        attributes.push_back(new attribute("VerticalAxisDirection", new named_type(IFC4X1_types[280]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[650])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeElement", new named_type(IFC4X1_types[332]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[651])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[652])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[655]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[653])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[655]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[654])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("OwningUser", new named_type(IFC4X1_types[668]), false));
        attributes.push_back(new attribute("OwningApplication", new named_type(IFC4X1_types[46]), false));
        attributes.push_back(new attribute("State", new named_type(IFC4X1_types[975]), true));
        attributes.push_back(new attribute("ChangeAction", new named_type(IFC4X1_types[140]), true));
        attributes.push_back(new attribute("LastModifiedDate", new named_type(IFC4X1_types[1109]), true));
        attributes.push_back(new attribute("LastModifyingUser", new named_type(IFC4X1_types[668]), true));
        attributes.push_back(new attribute("LastModifyingApplication", new named_type(IFC4X1_types[46]), true));
        attributes.push_back(new attribute("CreationDate", new named_type(IFC4X1_types[1109]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[656])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[66]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[657])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[651])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[659])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X1_types[1026]), false));
        attributes.push_back(new attribute("ReferenceCurve", new named_type(IFC4X1_types[249]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[660])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LifeCyclePhase", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[662]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[661])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X1_types[663]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4X1_types[1182]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X1_types[915]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[664])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[666]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[665])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("FamilyName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("GivenName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[12])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[667])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ThePerson", new named_type(IFC4X1_types[667]), false));
        attributes.push_back(new attribute("TheOrganization", new named_type(IFC4X1_types[648]), false));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[7])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[668])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[672])), false));
        attributes.push_back(new attribute("Discrimination", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Quality", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Usage", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[670])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[672])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[626]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[673])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[677]), true));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4X1_types[675]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[674])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[677]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[676])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[680]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[678])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[680]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[679])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[683]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[681])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[683]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[682])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Width", new named_type(IFC4X1_types[500]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC4X1_types[500]), false));
        attributes.push_back(new attribute("ColourComponents", new named_type(IFC4X1_types[500]), false));
        attributes.push_back(new attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[74])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[684])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Location", new named_type(IFC4X1_types[130]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[685])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Placement", new named_type(IFC4X1_types[65]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[686])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SizeInX", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("SizeInY", new named_type(IFC4X1_types[530]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[687])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[689])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[694]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[691])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[692])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[694]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[693])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[695])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("PointParameter", new named_type(IFC4X1_types[658]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[696])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X1_types[1026]), false));
        attributes.push_back(new attribute("PointParameterU", new named_type(IFC4X1_types[658]), false));
        attributes.push_back(new attribute("PointParameterV", new named_type(IFC4X1_types[658]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[697])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_types[130])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[702])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[67]), false));
        attributes.push_back(new attribute("PolygonalBoundary", new named_type(IFC4X1_types[91]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[699])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Closed", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("Faces", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[495])), false));
        attributes.push_back(new attribute("PnIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[705])), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[700])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[130])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[701])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[703])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[704])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("InternalLocation", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("PostalBox", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Town", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Region", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("PostalCode", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Country", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[709])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[711])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[712])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[713])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[714])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[715])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[716])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[719])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[528])), false));
        attributes.push_back(new attribute("Identifier", new named_type(IFC4X1_types[490]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[720])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("LayerOn", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("LayerFrozen", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("LayerBlocked", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X1_types[722])), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[721])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[722])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[724])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[723])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[728]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[726])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[728]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[727])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[729])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ObjectPlacement", new named_type(IFC4X1_types[635]), true));
        attributes.push_back(new attribute("Representation", new named_type(IFC4X1_types[733]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[731])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[732])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[869])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[733])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProfileType", new named_type(IFC4X1_types[738]), false));
        attributes.push_back(new attribute("ProfileName", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[736])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ProfileDefinition", new named_type(IFC4X1_types[736]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[737])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[739])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[744])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[746]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[745])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MapProjection", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("MapZone", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("MapUnit", new named_type(IFC4X1_types[626]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[740])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[743]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[742])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[490]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[747])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[748])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("UpperBoundValue", new named_type(IFC4X1_types[1149]), true));
        attributes.push_back(new attribute("LowerBoundValue", new named_type(IFC4X1_types[1149]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[1138]), true));
        attributes.push_back(new attribute("SetPointValue", new named_type(IFC4X1_types[1149]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[749])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[750])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DependingProperty", new named_type(IFC4X1_types[747]), false));
        attributes.push_back(new attribute("DependantProperty", new named_type(IFC4X1_types[747]), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[751])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), true));
        attributes.push_back(new attribute("EnumerationReference", new named_type(IFC4X1_types[753]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[752])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), false));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[1138]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[753])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[1138]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[754])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("PropertyReference", new named_type(IFC4X1_types[636]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[755])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[747])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[756])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[757])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4X1_types[761]), true));
        attributes.push_back(new attribute("ApplicableEntity", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[764])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[760])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("NominalValue", new named_type(IFC4X1_types[1149]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[1138]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[762])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), true));
        attributes.push_back(new attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("DefiningUnit", new named_type(IFC4X1_types[1138]), true));
        attributes.push_back(new attribute("DefinedUnit", new named_type(IFC4X1_types[1138]), true));
        attributes.push_back(new attribute("CurveInterpolation", new named_type(IFC4X1_types[253]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[763])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[764])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[765])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[771]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[766])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[769]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[767])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[769]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[768])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[771]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[770])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProxyType", new named_type(IFC4X1_types[637]), false));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[772])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[775]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[773])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[775]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[774])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AreaValue", new named_type(IFC4X1_types[56]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[776])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CountValue", new named_type(IFC4X1_types[233]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[777])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LengthValue", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[778])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[779])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeValue", new named_type(IFC4X1_types[1103]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[780])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VolumeValue", new named_type(IFC4X1_types[1166]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[781])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("WeightValue", new named_type(IFC4X1_types[573]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[782])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[786]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[784])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[786]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[785])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[792]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[787])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[790]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[788])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[790]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[789])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[792]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[791])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[796])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[794])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[796]))), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[795])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("InnerFilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("OuterFilletRadius", new named_type(IFC4X1_types[627]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[797])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("XDim", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[798])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[799])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X1_types[1026]), false));
        attributes.push_back(new attribute("U1", new named_type(IFC4X1_types[658]), false));
        attributes.push_back(new attribute("V1", new named_type(IFC4X1_types[658]), false));
        attributes.push_back(new attribute("U2", new named_type(IFC4X1_types[658]), false));
        attributes.push_back(new attribute("V2", new named_type(IFC4X1_types[658]), false));
        attributes.push_back(new attribute("Usense", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("Vsense", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[800])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("RecurrenceType", new named_type(IFC4X1_types[802]), false));
        attributes.push_back(new attribute("DayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[269])), true));
        attributes.push_back(new attribute("WeekdayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[270])), true));
        attributes.push_back(new attribute("MonthComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[622])), true));
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("Interval", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("Occurrences", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("TimePeriods", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1105])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[801])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("TypeIdentifier", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("AttributeIdentifier", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("InstanceName", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("ListPositions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[500])), true));
        attributes.push_back(new attribute("InnerReference", new named_type(IFC4X1_types[803]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[803])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[805]), true));
        attributes.push_back(new attribute("RestartDistance", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[804])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStep", new named_type(IFC4X1_types[1103]), false));
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1108])), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[807])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TotalCrossSectionArea", new named_type(IFC4X1_types[56]), false));
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4X1_types[812]), true));
        attributes.push_back(new attribute("EffectiveDepth", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("NominalBarDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("BarCount", new named_type(IFC4X1_types[233]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[808])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DefinitionType", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[905])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[809])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("BarLength", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[814]), true));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4X1_types[812]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[810])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[814]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("BarLength", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4X1_types[812]), true));
        attributes.push_back(new attribute("BendingShapeCode", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[73])), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[813])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[815])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[816])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("MeshLength", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[819]), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[817])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[819]), false));
        attributes.push_back(new attribute("MeshLength", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("BendingShapeCode", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[73])), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[818])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4X1_types[632]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[632])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[820])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[632])), false));
        attributes.push_back(new attribute("RelatedObjectsType", new named_type(IFC4X1_types[637]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[821])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingActor", new named_type(IFC4X1_types[6]), false));
        attributes.push_back(new attribute("ActingRole", new named_type(IFC4X1_types[7]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[822])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingControl", new named_type(IFC4X1_types[213]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[823])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingGroup", new named_type(IFC4X1_types[479]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[824])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Factor", new named_type(IFC4X1_types[793]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[825])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC4X1_types[730]), false));
        attributes.push_back(new attribute("QuantityInProcess", new named_type(IFC4X1_types[596]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[826])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingProduct", new named_type(IFC4X1_types[735]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[827])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingResource", new named_type(IFC4X1_types[878]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[828])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[271])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[829])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4X1_types[49]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[830])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingClassification", new named_type(IFC4X1_types[156]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[831])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Intent", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC4X1_types[197]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[832])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC4X1_types[304]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[833])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingLibrary", new named_type(IFC4X1_types[533]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[834])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC4X1_types[593]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[835])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[837])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC4X1_types[191]), true));
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4X1_types[359]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[838])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X1_types[500])), false));
        attributes.push_back(new attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X1_types[500])), false));
        attributes.push_back(new attribute("RelatedConnectionType", new named_type(IFC4X1_types[195]), false));
        attributes.push_back(new attribute("RelatingConnectionType", new named_type(IFC4X1_types[195]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[839])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC4X1_types[703]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4X1_types[292]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[841])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC4X1_types[703]), false));
        attributes.push_back(new attribute("RelatedPort", new named_type(IFC4X1_types[703]), false));
        attributes.push_back(new attribute("RealizingElement", new named_type(IFC4X1_types[359]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[840])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X1_types[978]), false));
        attributes.push_back(new attribute("RelatedStructuralActivity", new named_type(IFC4X1_types[977]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[842])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("RelatingStructuralMember", new named_type(IFC4X1_types[1004]), false));
        attributes.push_back(new attribute("RelatedStructuralConnection", new named_type(IFC4X1_types[980]), false));
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC4X1_types[85]), true));
        attributes.push_back(new attribute("AdditionalConditions", new named_type(IFC4X1_types[981]), true));
        attributes.push_back(new attribute("SupportedLength", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC4X1_types[67]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[843])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConnectionConstraint", new named_type(IFC4X1_types[191]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[844])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[359])), false));
        attributes.push_back(new attribute("ConnectionType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[845])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[731])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC4X1_types[953]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[846])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[234])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[847])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC4X1_types[946]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[234])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[848])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingContext", new named_type(IFC4X1_types[210]), false));
        attributes.push_back(new attribute("RelatedDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[271])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[849])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[850])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[851])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[631])), false));
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4X1_types[631]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[852])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[632])), false));
        attributes.push_back(new attribute("RelatingPropertyDefinition", new named_type(IFC4X1_types[758]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[853])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[757])), false));
        attributes.push_back(new attribute("RelatingTemplate", new named_type(IFC4X1_types[760]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[854])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[631])), false));
        attributes.push_back(new attribute("RelatingType", new named_type(IFC4X1_types[1134]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[855])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOpeningElement", new named_type(IFC4X1_types[644]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC4X1_types[359]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[856])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[290])), false));
        attributes.push_back(new attribute("RelatingFlowElement", new named_type(IFC4X1_types[294]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[857])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("InterferenceGeometry", new named_type(IFC4X1_types[191]), true));
        attributes.push_back(new attribute("InterferenceType", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("ImpliedOrder", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[858])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4X1_types[632]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[632])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[859])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("RelatedFeatureElement", new named_type(IFC4X1_types[415]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[860])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[731])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC4X1_types[953]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[861])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC4X1_types[729]), false));
        attributes.push_back(new attribute("RelatedProcess", new named_type(IFC4X1_types[729]), false));
        attributes.push_back(new attribute("TimeLag", new named_type(IFC4X1_types[523]), true));
        attributes.push_back(new attribute("SequenceType", new named_type(IFC4X1_types[911]), true));
        attributes.push_back(new attribute("UserDefinedSequenceType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[862])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSystem", new named_type(IFC4X1_types[1051]), false));
        attributes.push_back(new attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[953])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[863])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC4X1_types[947]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC4X1_types[191]), true));
        attributes.push_back(new attribute("PhysicalOrVirtualBoundary", new named_type(IFC4X1_types[671]), false));
        attributes.push_back(new attribute("InternalOrExternalBoundary", new named_type(IFC4X1_types[505]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[864])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentBoundary", new named_type(IFC4X1_types[865]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[865])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CorrespondingBoundary", new named_type(IFC4X1_types[866]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[866])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC4X1_types[359]), false));
        attributes.push_back(new attribute("RelatedOpeningElement", new named_type(IFC4X1_types[416]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[867])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[836])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParamLength", new named_type(IFC4X1_types[658]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[868])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ContextOfItems", new named_type(IFC4X1_types[870]), false));
        attributes.push_back(new attribute("RepresentationIdentifier", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("RepresentationType", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[871])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[869])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ContextIdentifier", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("ContextType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[870])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[871])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingOrigin", new named_type(IFC4X1_types[65]), false));
        attributes.push_back(new attribute("MappedRepresentation", new named_type(IFC4X1_types[869]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[872])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[873])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[877])), false));
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4X1_types[49]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[874])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC4X1_types[197]), false));
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[877])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[875])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[876])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new attribute("ScheduleWork", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("ScheduleUsage", new named_type(IFC4X1_types[708]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ScheduleContour", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("LevelingDelay", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("IsOverAllocated", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ActualWork", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("ActualUsage", new named_type(IFC4X1_types[708]), true));
        attributes.push_back(new attribute("ActualStart", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("RemainingWork", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("RemainingUsage", new named_type(IFC4X1_types[708]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC4X1_types[708]), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[879])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X1_types[64]), false));
        attributes.push_back(new attribute("Angle", new named_type(IFC4X1_types[690]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[880])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EndSweptArea", new named_type(IFC4X1_types[736]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[881])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("BottomRadius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[882])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[883])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[887]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[885])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[887]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[886])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("GlobalId", new named_type(IFC4X1_types[472]), false));
        attributes.push_back(new attribute("OwnerHistory", new named_type(IFC4X1_types[656]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[888])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RoundingRadius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[893])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Prefix", new named_type(IFC4X1_types[925]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[928]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[927])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[896]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[894])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[896]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[895])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC4X1_types[266]), true));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[897])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[898])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SectionType", new named_type(IFC4X1_types[906]), false));
        attributes.push_back(new attribute("StartProfile", new named_type(IFC4X1_types[736]), false));
        attributes.push_back(new attribute("EndProfile", new named_type(IFC4X1_types[736]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[904])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LongitudinalStartPosition", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("LongitudinalEndPosition", new named_type(IFC4X1_types[530]), false));
        attributes.push_back(new attribute("TransversePosition", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("ReinforcementRole", new named_type(IFC4X1_types[811]), false));
        attributes.push_back(new attribute("SectionDefinition", new named_type(IFC4X1_types[904]), false));
        attributes.push_back(new attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[808])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[905])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[736])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[900])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[285])), false));
        attributes.push_back(new attribute("FixedAxisVertical", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[901])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SpineCurve", new named_type(IFC4X1_types[177]), false));
        attributes.push_back(new attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[736])), false));
        attributes.push_back(new attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X1_types[67])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[902])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[910]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[908])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[910]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[909])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[914]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[912])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[914]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[913])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[916])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("ProductDefinitional", new named_type(IFC4X1_types[559]), false));
        attributes.push_back(new attribute("PartOfProductDefinitionShape", new named_type(IFC4X1_types[734]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[915])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[916])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[917])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[919])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[920])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[921])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4X1_types[923]), true));
        attributes.push_back(new attribute("PrimaryMeasureType", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("SecondaryMeasureType", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Enumerators", new named_type(IFC4X1_types[753]), true));
        attributes.push_back(new attribute("PrimaryUnit", new named_type(IFC4X1_types[1138]), true));
        attributes.push_back(new attribute("SecondaryUnit", new named_type(IFC4X1_types[1138]), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("AccessState", new named_type(IFC4X1_types[975]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[922])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RefLatitude", new named_type(IFC4X1_types[181]), true));
        attributes.push_back(new attribute("RefLongitude", new named_type(IFC4X1_types[181]), true));
        attributes.push_back(new attribute("RefElevation", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("LandTitleNumber", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("SiteAddress", new named_type(IFC4X1_types[709]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[926])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[934]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[930])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[931])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[932])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[934]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[933])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SlippageX", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("SlippageY", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("SlippageZ", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[935])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[938]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[936])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[938]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[937])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[940])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[952]), true));
        attributes.push_back(new attribute("ElevationWithFlooring", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[946])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[950]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[948])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[950]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[949])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[952]), false));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[951])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[953])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[954])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CompositionType", new named_type(IFC4X1_types[366]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[955])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[956])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[959]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[957])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[959]), false));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[958])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[964])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[965])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[968]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[966])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[968]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[967])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[974]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[969])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NumberOfRisers", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("NumberOfTreads", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("RiserHeight", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("TreadLength", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[972]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[970])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[972]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[971])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[974]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[973])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DestabilizingLoad", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[976])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AppliedLoad", new named_type(IFC4X1_types[991]), false));
        attributes.push_back(new attribute("GlobalOrLocal", new named_type(IFC4X1_types[473]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[977])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[41]), false));
        attributes.push_back(new attribute("OrientationOf2DPlane", new named_type(IFC4X1_types[67]), true));
        attributes.push_back(new attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[994])), true));
        attributes.push_back(new attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[1010])), true));
        attributes.push_back(new attribute("SharedPlacement", new named_type(IFC4X1_types[635]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[979])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC4X1_types[85]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[980])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[981])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC4X1_types[741]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[983]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[982])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X1_types[280]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[984])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[986]), false));
        attributes.push_back(new attribute("Axis", new named_type(IFC4X1_types[280]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[985])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[987])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[983]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[988])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[989])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[990])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[991])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SelfWeightCoefficients", new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[793])), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[992])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[996])), false));
        attributes.push_back(new attribute("Locations", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X1_types[530]))), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[993])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[557]), false));
        attributes.push_back(new attribute("ActionType", new named_type(IFC4X1_types[5]), false));
        attributes.push_back(new attribute("ActionSource", new named_type(IFC4X1_types[4]), false));
        attributes.push_back(new attribute("Coefficient", new named_type(IFC4X1_types[793]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[994])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LinearForceX", new named_type(IFC4X1_types[549]), true));
        attributes.push_back(new attribute("LinearForceY", new named_type(IFC4X1_types[549]), true));
        attributes.push_back(new attribute("LinearForceZ", new named_type(IFC4X1_types[549]), true));
        attributes.push_back(new attribute("LinearMomentX", new named_type(IFC4X1_types[550]), true));
        attributes.push_back(new attribute("LinearMomentY", new named_type(IFC4X1_types[550]), true));
        attributes.push_back(new attribute("LinearMomentZ", new named_type(IFC4X1_types[550]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[995])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[996])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PlanarForceX", new named_type(IFC4X1_types[688]), true));
        attributes.push_back(new attribute("PlanarForceY", new named_type(IFC4X1_types[688]), true));
        attributes.push_back(new attribute("PlanarForceZ", new named_type(IFC4X1_types[688]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[997])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DisplacementX", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("DisplacementY", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("DisplacementZ", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("RotationalDisplacementRX", new named_type(IFC4X1_types[690]), true));
        attributes.push_back(new attribute("RotationalDisplacementRY", new named_type(IFC4X1_types[690]), true));
        attributes.push_back(new attribute("RotationalDisplacementRZ", new named_type(IFC4X1_types[690]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[998])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Distortion", new named_type(IFC4X1_types[248]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[999])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("ForceX", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("ForceY", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("ForceZ", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("MomentX", new named_type(IFC4X1_types[1113]), true));
        attributes.push_back(new attribute("MomentY", new named_type(IFC4X1_types[1113]), true));
        attributes.push_back(new attribute("MomentZ", new named_type(IFC4X1_types[1113]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1000])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingMoment", new named_type(IFC4X1_types[1174]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1001])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1002])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DeltaTConstant", new named_type(IFC4X1_types[1101]), true));
        attributes.push_back(new attribute("DeltaTY", new named_type(IFC4X1_types[1101]), true));
        attributes.push_back(new attribute("DeltaTZ", new named_type(IFC4X1_types[1101]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1003])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1004])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1005])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1006])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC4X1_types[67]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1007])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1008])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1009])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TheoryType", new named_type(IFC4X1_types[42]), false));
        attributes.push_back(new attribute("ResultForLoadGroup", new named_type(IFC4X1_types[994]), true));
        attributes.push_back(new attribute("IsLinear", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1010])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC4X1_types[741]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1012]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1011])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1013])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1015]), false));
        attributes.push_back(new attribute("Thickness", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1014])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1016])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1012]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1017])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1021])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Item", new named_type(IFC4X1_types[871]), true));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[1018])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1019])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1020])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1024]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1022])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1024]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1023])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentEdge", new named_type(IFC4X1_types[332]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1025])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[1026])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Curve3D", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("AssociatedGeometry", new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X1_types[660])), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC4X1_types[717]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1027])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4X1_types[658]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4X1_types[658]), true));
        attributes.push_back(new attribute("ReferenceSurface", new named_type(IFC4X1_types[1026]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1028])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1030]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1029])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC4X1_types[280]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[530]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1031])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AxisPosition", new named_type(IFC4X1_types[64]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1032])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SurfaceReinforcement1", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_types[530])), true));
        attributes.push_back(new attribute("SurfaceReinforcement2", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_types[530])), true));
        attributes.push_back(new attribute("ShearReinforcement", new named_type(IFC4X1_types[793]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1034])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Side", new named_type(IFC4X1_types[1035]), false));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4X1_types[1037])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1036])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC4X1_types[163]), false));
        attributes.push_back(new attribute("DiffuseReflectionColour", new named_type(IFC4X1_types[163]), false));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC4X1_types[163]), false));
        attributes.push_back(new attribute("ReflectanceColour", new named_type(IFC4X1_types[163]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1038])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RefractionIndex", new named_type(IFC4X1_types[796]), true));
        attributes.push_back(new attribute("DispersionFactor", new named_type(IFC4X1_types[796]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1039])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("DiffuseColour", new named_type(IFC4X1_types[162]), true));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC4X1_types[162]), true));
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC4X1_types[162]), true));
        attributes.push_back(new attribute("ReflectionColour", new named_type(IFC4X1_types[162]), true));
        attributes.push_back(new attribute("SpecularColour", new named_type(IFC4X1_types[162]), true));
        attributes.push_back(new attribute("SpecularHighlight", new named_type(IFC4X1_types[962]), true));
        attributes.push_back(new attribute("ReflectanceMethod", new named_type(IFC4X1_types[806]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1040])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceColour", new named_type(IFC4X1_types[163]), false));
        attributes.push_back(new attribute("Transparency", new named_type(IFC4X1_types[628]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1041])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1043])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1042])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RepeatS", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("RepeatT", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("Mode", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("TextureTransform", new named_type(IFC4X1_types[135]), true));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[490])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1043])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptArea", new named_type(IFC4X1_types[736]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[67]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1044])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("InnerRadius", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4X1_types[658]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4X1_types[658]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1045])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1046])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptCurve", new named_type(IFC4X1_types[736]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC4X1_types[67]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1047])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1050]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1048])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1050]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1049])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1051])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1054]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1052])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1054]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1053])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("WebEdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("WebSlope", new named_type(IFC4X1_types[690]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4X1_types[690]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1130])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1057])), true));
        attributes.push_back(new attribute("Columns", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1056])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1055])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Identifier", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[1138]), true));
        attributes.push_back(new attribute("ReferencePath", new named_type(IFC4X1_types[803]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1056])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), true));
        attributes.push_back(new attribute("IsHeading", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1057])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1060]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1058])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1060]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1059])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Status", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("IsMilestone", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("Priority", new named_type(IFC4X1_types[500]), true));
        attributes.push_back(new attribute("TaskTime", new named_type(IFC4X1_types[1063]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1066]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1061])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("DurationType", new named_type(IFC4X1_types[1062]), true));
        attributes.push_back(new attribute("ScheduleDuration", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("EarlyStart", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("EarlyFinish", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("LateStart", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("LateFinish", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("FreeFloat", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("IsCritical", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ActualDuration", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("ActualStart", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC4X1_types[268]), true));
        attributes.push_back(new attribute("RemainingTime", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC4X1_types[708]), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1063])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Recurrence", new named_type(IFC4X1_types[801]), false));
        std::vector<bool> derived; derived.reserve(21);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1064])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1066]), false));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1065])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("PagerNumber", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[519])), true));
        attributes.push_back(new attribute("WWWHomePageURL", new named_type(IFC4X1_types[1147]), true));
        attributes.push_back(new attribute("MessagingIDs", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1147])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1067])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1075]), true));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("TensionForce", new named_type(IFC4X1_types[455]), true));
        attributes.push_back(new attribute("PreStress", new named_type(IFC4X1_types[725]), true));
        attributes.push_back(new attribute("FrictionCoefficient", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("AnchorageSlip", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("MinCurvatureRadius", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1070])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1073]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1071])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1073]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1072])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1075]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X1_types[56]), true));
        attributes.push_back(new attribute("SheathDiameter", new named_type(IFC4X1_types[706]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1074])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new named_type(IFC4X1_types[133]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1076])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[1077])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Literal", new named_type(IFC4X1_types[718]), false));
        attributes.push_back(new attribute("Placement", new named_type(IFC4X1_types[65]), false));
        attributes.push_back(new attribute("Path", new named_type(IFC4X1_types[1085]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1083])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Extent", new named_type(IFC4X1_types[687]), false));
        attributes.push_back(new attribute("BoxAlignment", new named_type(IFC4X1_types[94]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1084])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("TextCharacterAppearance", new named_type(IFC4X1_types[1088]), true));
        attributes.push_back(new attribute("TextStyle", new named_type(IFC4X1_types[1089]), true));
        attributes.push_back(new attribute("TextFontStyle", new named_type(IFC4X1_types[1082]), false));
        attributes.push_back(new attribute("ModelOrDraughting", new named_type(IFC4X1_types[80]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1086])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1081])), false));
        attributes.push_back(new attribute("FontStyle", new named_type(IFC4X1_types[449]), true));
        attributes.push_back(new attribute("FontVariant", new named_type(IFC4X1_types[450]), true));
        attributes.push_back(new attribute("FontWeight", new named_type(IFC4X1_types[451]), true));
        attributes.push_back(new attribute("FontSize", new named_type(IFC4X1_types[929]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1087])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Colour", new named_type(IFC4X1_types[161]), false));
        attributes.push_back(new attribute("BackgroundColour", new named_type(IFC4X1_types[161]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1088])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("TextIndent", new named_type(IFC4X1_types[929]), true));
        attributes.push_back(new attribute("TextAlign", new named_type(IFC4X1_types[1079]), true));
        attributes.push_back(new attribute("TextDecoration", new named_type(IFC4X1_types[1080]), true));
        attributes.push_back(new attribute("LetterSpacing", new named_type(IFC4X1_types[929]), true));
        attributes.push_back(new attribute("WordSpacing", new named_type(IFC4X1_types[929]), true));
        attributes.push_back(new attribute("TextTransform", new named_type(IFC4X1_types[1090]), true));
        attributes.push_back(new attribute("LineHeight", new named_type(IFC4X1_types[929]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1089])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Maps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1043])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1091])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Mode", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[796])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1092])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Vertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X1_types[1094])), false));
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4X1_types[400]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1093])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_types[658])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1094])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TexCoordsList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_types[658]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1095])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("StartTime", new named_type(IFC4X1_types[1102]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC4X1_types[1102]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1105])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Name", new named_type(IFC4X1_types[519]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC4X1_types[268]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC4X1_types[268]), false));
        attributes.push_back(new attribute("TimeSeriesDataType", new named_type(IFC4X1_types[1107]), false));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC4X1_types[266]), false));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X1_types[1138]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1106])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[1149])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1108])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[1110])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1111])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MajorRadius", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("MinorRadius", new named_type(IFC4X1_types[706]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1116]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1114])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1116]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1115])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("StartRadius", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("EndRadius", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("IsStartRadiusCCW", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("IsEndRadiusCCW", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("TransitionCurveType", new named_type(IFC4X1_types[1119]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1118])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1123]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1121])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1123]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1122])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BottomXDim", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("TopXDim", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("TopXOffset", new named_type(IFC4X1_types[530]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1124])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Normals", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[658]))), true));
        attributes.push_back(new attribute("Closed", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X1_types[705]))), false));
        attributes.push_back(new attribute("PnIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[705])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1125])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Flags", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[500])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1126])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4X1_types[249]), false));
        attributes.push_back(new attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X1_types[1129])), false));
        attributes.push_back(new attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X1_types[1129])), false));
        attributes.push_back(new attribute("SenseAgreement", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC4X1_types[1128]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1127])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1133]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1133]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1132])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ApplicableOccurrence", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[757])), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("ProcessType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1135])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X1_types[872])), true));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1136])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X1_types[490]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X1_types[1078]), true));
        attributes.push_back(new attribute("ResourceType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1137])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4X1_types[690]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1148])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[1138])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1145])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1141]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1139])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1141]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1140])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1144]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1142])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1144]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1143])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1152]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1150])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1152]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1151])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X1_types[280]), false));
        attributes.push_back(new attribute("Magnitude", new named_type(IFC4X1_types[530]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1154])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X1_types[1156])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LoopVertex", new named_type(IFC4X1_types[1156]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1157])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("VertexGeometry", new named_type(IFC4X1_types[695]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X1_types[1158])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1161]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1159])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1161]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1160])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1162])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X1_types[475])), false));
        attributes.push_back(new attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X1_types[530])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1163])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1165]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1164])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1172]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1168])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1169])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1170])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1172]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1171])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1178]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1176])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1178]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1177])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1189]), true));
        attributes.push_back(new attribute("PartitioningType", new named_type(IFC4X1_types[1190]), true));
        attributes.push_back(new attribute("UserDefinedPartitioningType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1179])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("MullionThickness", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("FirstTransomOffset", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("SecondTransomOffset", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("FirstMullionOffset", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("SecondMullionOffset", new named_type(IFC4X1_types[628]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X1_types[915]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetX", new named_type(IFC4X1_types[530]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetY", new named_type(IFC4X1_types[530]), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1180])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X1_types[1181]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4X1_types[1182]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC4X1_types[706]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X1_types[915]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1183])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1184])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4X1_types[1186]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X1_types[1187]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X1_types[80]), false));
        attributes.push_back(new attribute("Sizeable", new named_type(IFC4X1_types[80]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1185])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1189]), false));
        attributes.push_back(new attribute("PartitioningType", new named_type(IFC4X1_types[1190]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X1_types[80]), true));
        attributes.push_back(new attribute("UserDefinedPartitioningType", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1188])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WorkingTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[1198])), true));
        attributes.push_back(new attribute("ExceptionTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[1198])), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1192]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1191])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("CreationDate", new named_type(IFC4X1_types[268]), false));
        attributes.push_back(new attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X1_types[667])), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X1_types[519]), true));
        attributes.push_back(new attribute("Duration", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC4X1_types[330]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC4X1_types[268]), false));
        attributes.push_back(new attribute("FinishTime", new named_type(IFC4X1_types[268]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1193])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1195]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1194])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X1_types[1197]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1196])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RecurrencePattern", new named_type(IFC4X1_types[801]), true));
        attributes.push_back(new attribute("Start", new named_type(IFC4X1_types[267]), true));
        attributes.push_back(new attribute("Finish", new named_type(IFC4X1_types[267]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1198])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X1_types[706]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X1_types[627]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4X1_types[627]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1200])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LongName", new named_type(IFC4X1_types[519]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X1_types[1199])->set_attributes(attributes, derived);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsActingUpon", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[822]), ((entity*) IFC4X1_types[822])->attributes()[0]));
        ((entity*) IFC4X1_types[6])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[7])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("OfPerson", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[667]), ((entity*) IFC4X1_types[667])->attributes()[7]));
        attributes.push_back(new inverse_attribute("OfOrganization", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[648]), ((entity*) IFC4X1_types[648])->attributes()[4]));
        ((entity*) IFC4X1_types[12])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToAlignmentCurve", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[38]), ((entity*) IFC4X1_types[38])->attributes()[0]));
        ((entity*) IFC4X1_types[30])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToHorizontal", inverse_attribute::set_type, 1, 1, ((entity*) IFC4X1_types[30]), ((entity*) IFC4X1_types[30])->attributes()[1]));
        ((entity*) IFC4X1_types[31])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToAlignmentCurve", inverse_attribute::set_type, 1, 1, ((entity*) IFC4X1_types[38]), ((entity*) IFC4X1_types[38])->attributes()[1]));
        ((entity*) IFC4X1_types[36])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToVertical", inverse_attribute::set_type, 1, 1, ((entity*) IFC4X1_types[36]), ((entity*) IFC4X1_types[36])->attributes()[0]));
        ((entity*) IFC4X1_types[37])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[846]), ((entity*) IFC4X1_types[846])->attributes()[0]));
        ((entity*) IFC4X1_types[44])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[47])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ApprovedObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[830]), ((entity*) IFC4X1_types[830])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ApprovedResources", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[874]), ((entity*) IFC4X1_types[874])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[50]), ((entity*) IFC4X1_types[50])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[50]), ((entity*) IFC4X1_types[50])->attributes()[0]));
        ((entity*) IFC4X1_types[49])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ClassificationForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[831]), ((entity*) IFC4X1_types[831])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[154]), ((entity*) IFC4X1_types[154])->attributes()[0]));
        ((entity*) IFC4X1_types[153])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ClassificationRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[831]), ((entity*) IFC4X1_types[831])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[154]), ((entity*) IFC4X1_types[154])->attributes()[0]));
        ((entity*) IFC4X1_types[154])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("UsingCurves", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[177]), ((entity*) IFC4X1_types[177])->attributes()[0]));
        ((entity*) IFC4X1_types[179])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PropertiesForConstraint", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[875]), ((entity*) IFC4X1_types[875])->attributes()[0]));
        ((entity*) IFC4X1_types[197])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[853]), ((entity*) IFC4X1_types[853])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Declares", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[849]), ((entity*) IFC4X1_types[849])->attributes()[0]));
        ((entity*) IFC4X1_types[210])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[212])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Controls", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[823]), ((entity*) IFC4X1_types[823])->attributes()[0]));
        ((entity*) IFC4X1_types[213])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[217])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasCoordinateOperation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[225]), ((entity*) IFC4X1_types[225])->attributes()[0]));
        ((entity*) IFC4X1_types[226])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("CoversSpaces", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[848]), ((entity*) IFC4X1_types[848])->attributes()[1]));
        attributes.push_back(new inverse_attribute("CoversElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[847]), ((entity*) IFC4X1_types[847])->attributes()[1]));
        ((entity*) IFC4X1_types[234])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToFlowElement", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[857]), ((entity*) IFC4X1_types[857])->attributes()[0]));
        ((entity*) IFC4X1_types[290])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasPorts", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[841]), ((entity*) IFC4X1_types[841])->attributes()[1]));
        ((entity*) IFC4X1_types[292])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasControlElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[857]), ((entity*) IFC4X1_types[857])->attributes()[1]));
        ((entity*) IFC4X1_types[294])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("DocumentInfoForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[833]), ((entity*) IFC4X1_types[833])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasDocumentReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[303]), ((entity*) IFC4X1_types[303])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[302]), ((entity*) IFC4X1_types[302])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointer", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[302]), ((entity*) IFC4X1_types[302])->attributes()[0]));
        ((entity*) IFC4X1_types[301])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("DocumentRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[833]), ((entity*) IFC4X1_types[833])->attributes()[0]));
        ((entity*) IFC4X1_types[303])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new inverse_attribute("FillsVoids", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[856]), ((entity*) IFC4X1_types[856])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[838]), ((entity*) IFC4X1_types[838])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsInterferedByElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[858]), ((entity*) IFC4X1_types[858])->attributes()[1]));
        attributes.push_back(new inverse_attribute("InterferesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[858]), ((entity*) IFC4X1_types[858])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasProjections", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[860]), ((entity*) IFC4X1_types[860])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedInStructures", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[861]), ((entity*) IFC4X1_types[861])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasOpenings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[867]), ((entity*) IFC4X1_types[867])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsConnectionRealization", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[845]), ((entity*) IFC4X1_types[845])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ProvidesBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[864]), ((entity*) IFC4X1_types[864])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[838]), ((entity*) IFC4X1_types[838])->attributes()[2]));
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[846]), ((entity*) IFC4X1_types[846])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[847]), ((entity*) IFC4X1_types[847])->attributes()[0]));
        ((entity*) IFC4X1_types[359])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ExternalReferenceForResources", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[0]));
        ((entity*) IFC4X1_types[393])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[864]), ((entity*) IFC4X1_types[864])->attributes()[0]));
        ((entity*) IFC4X1_types[395])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasTextureMaps", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[1093]), ((entity*) IFC4X1_types[1093])->attributes()[1]));
        ((entity*) IFC4X1_types[400])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ProjectsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X1_types[860]), ((entity*) IFC4X1_types[860])->attributes()[1]));
        ((entity*) IFC4X1_types[415])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("VoidsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X1_types[867]), ((entity*) IFC4X1_types[867])->attributes()[1]));
        ((entity*) IFC4X1_types[416])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasSubContexts", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[469]), ((entity*) IFC4X1_types[469])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasCoordinateOperation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[225]), ((entity*) IFC4X1_types[225])->attributes()[0]));
        ((entity*) IFC4X1_types[467])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("PartOfW", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[474]), ((entity*) IFC4X1_types[474])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfV", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[474]), ((entity*) IFC4X1_types[474])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfU", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[474]), ((entity*) IFC4X1_types[474])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasIntersections", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[1163]), ((entity*) IFC4X1_types[1163])->attributes()[0]));
        ((entity*) IFC4X1_types[475])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsGroupedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[824]), ((entity*) IFC4X1_types[824])->attributes()[0]));
        ((entity*) IFC4X1_types[479])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToFaceSet", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[700]), ((entity*) IFC4X1_types[700])->attributes()[1]));
        ((entity*) IFC4X1_types[495])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LibraryInfoForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[834]), ((entity*) IFC4X1_types[834])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasLibraryReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[532]), ((entity*) IFC4X1_types[532])->attributes()[2]));
        ((entity*) IFC4X1_types[531])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("LibraryRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[834]), ((entity*) IFC4X1_types[834])->attributes()[0]));
        ((entity*) IFC4X1_types[532])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("HasRepresentation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[580]), ((entity*) IFC4X1_types[580])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[592]), ((entity*) IFC4X1_types[592])->attributes()[1]));
        attributes.push_back(new inverse_attribute("RelatesTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[592]), ((entity*) IFC4X1_types[592])->attributes()[0]));
        ((entity*) IFC4X1_types[575])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialConstituentSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X1_types[578]), ((entity*) IFC4X1_types[578])->attributes()[2]));
        ((entity*) IFC4X1_types[577])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("AssociatedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[835]), ((entity*) IFC4X1_types[835])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasProperties", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[591]), ((entity*) IFC4X1_types[591])->attributes()[0]));
        ((entity*) IFC4X1_types[579])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialLayerSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X1_types[582]), ((entity*) IFC4X1_types[582])->attributes()[0]));
        ((entity*) IFC4X1_types[581])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialProfileSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X1_types[587]), ((entity*) IFC4X1_types[587])->attributes()[2]));
        ((entity*) IFC4X1_types[586])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssociatedTo", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[835]), ((entity*) IFC4X1_types[835])->attributes()[0]));
        ((entity*) IFC4X1_types[594])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("IsDeclaredBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[852]), ((entity*) IFC4X1_types[852])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Declares", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[852]), ((entity*) IFC4X1_types[852])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsTypedBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[855]), ((entity*) IFC4X1_types[855])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[853]), ((entity*) IFC4X1_types[853])->attributes()[0]));
        ((entity*) IFC4X1_types[631])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new inverse_attribute("HasAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[821]), ((entity*) IFC4X1_types[821])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Nests", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[859]), ((entity*) IFC4X1_types[859])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsNestedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[859]), ((entity*) IFC4X1_types[859])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasContext", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[849]), ((entity*) IFC4X1_types[849])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsDecomposedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[820]), ((entity*) IFC4X1_types[820])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Decomposes", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[820]), ((entity*) IFC4X1_types[820])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[829]), ((entity*) IFC4X1_types[829])->attributes()[0]));
        ((entity*) IFC4X1_types[632])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PlacesObject", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[731]), ((entity*) IFC4X1_types[731])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedByPlacements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[558]), ((entity*) IFC4X1_types[558])->attributes()[0]));
        ((entity*) IFC4X1_types[635])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasFillings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[856]), ((entity*) IFC4X1_types[856])->attributes()[0]));
        ((entity*) IFC4X1_types[644])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsRelatedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[649]), ((entity*) IFC4X1_types[649])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[649]), ((entity*) IFC4X1_types[649])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Engages", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[668]), ((entity*) IFC4X1_types[668])->attributes()[1]));
        ((entity*) IFC4X1_types[648])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("EngagedIn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[668]), ((entity*) IFC4X1_types[668])->attributes()[0]));
        ((entity*) IFC4X1_types[667])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[670]), ((entity*) IFC4X1_types[670])->attributes()[0]));
        ((entity*) IFC4X1_types[672])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainedIn", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[841]), ((entity*) IFC4X1_types[841])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[840]), ((entity*) IFC4X1_types[840])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[840]), ((entity*) IFC4X1_types[840])->attributes()[0]));
        ((entity*) IFC4X1_types[703])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[846]), ((entity*) IFC4X1_types[846])->attributes()[0]));
        ((entity*) IFC4X1_types[704])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsPredecessorTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[862]), ((entity*) IFC4X1_types[862])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsSuccessorFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[862]), ((entity*) IFC4X1_types[862])->attributes()[1]));
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[826]), ((entity*) IFC4X1_types[826])->attributes()[0]));
        ((entity*) IFC4X1_types[729])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[827]), ((entity*) IFC4X1_types[827])->attributes()[0]));
        ((entity*) IFC4X1_types[731])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ShapeOfProduct", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[731]), ((entity*) IFC4X1_types[731])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[915]), ((entity*) IFC4X1_types[915])->attributes()[4]));
        ((entity*) IFC4X1_types[732])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasProperties", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[737]), ((entity*) IFC4X1_types[737])->attributes()[0]));
        ((entity*) IFC4X1_types[736])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new inverse_attribute("PartOfPset", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[756]), ((entity*) IFC4X1_types[756])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyForDependance", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[751]), ((entity*) IFC4X1_types[751])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyDependsOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[751]), ((entity*) IFC4X1_types[751])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[174]), ((entity*) IFC4X1_types[174])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasConstraints", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[875]), ((entity*) IFC4X1_types[875])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasApprovals", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[874]), ((entity*) IFC4X1_types[874])->attributes()[0]));
        ((entity*) IFC4X1_types[747])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[748])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasContext", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[849]), ((entity*) IFC4X1_types[849])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[829]), ((entity*) IFC4X1_types[829])->attributes()[0]));
        ((entity*) IFC4X1_types[750])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("DefinesType", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[1134]), ((entity*) IFC4X1_types[1134])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[854]), ((entity*) IFC4X1_types[854])->attributes()[0]));
        attributes.push_back(new inverse_attribute("DefinesOccurrence", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[853]), ((entity*) IFC4X1_types[853])->attributes()[1]));
        ((entity*) IFC4X1_types[757])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Defines", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[854]), ((entity*) IFC4X1_types[854])->attributes()[1]));
        ((entity*) IFC4X1_types[760])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PartOfComplexTemplate", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[175]), ((entity*) IFC4X1_types[175])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfPsetTemplate", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[760]), ((entity*) IFC4X1_types[760])->attributes()[2]));
        ((entity*) IFC4X1_types[764])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("InnerBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[865]), ((entity*) IFC4X1_types[865])->attributes()[0]));
        ((entity*) IFC4X1_types[865])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Corresponds", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[866]), ((entity*) IFC4X1_types[866])->attributes()[0]));
        ((entity*) IFC4X1_types[866])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("RepresentationMap", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[872]), ((entity*) IFC4X1_types[872])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LayerAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[720]), ((entity*) IFC4X1_types[720])->attributes()[2]));
        attributes.push_back(new inverse_attribute("OfProductRepresentation", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[733]), ((entity*) IFC4X1_types[733])->attributes()[2]));
        ((entity*) IFC4X1_types[869])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("RepresentationsInContext", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[869]), ((entity*) IFC4X1_types[869])->attributes()[0]));
        ((entity*) IFC4X1_types[870])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LayerAssignment", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[720]), ((entity*) IFC4X1_types[720])->attributes()[2]));
        attributes.push_back(new inverse_attribute("StyledByItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[1019]), ((entity*) IFC4X1_types[1019])->attributes()[0]));
        ((entity*) IFC4X1_types[871])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[915]), ((entity*) IFC4X1_types[915])->attributes()[4]));
        attributes.push_back(new inverse_attribute("MapUsage", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[570]), ((entity*) IFC4X1_types[570])->attributes()[0]));
        ((entity*) IFC4X1_types[872])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[828]), ((entity*) IFC4X1_types[828])->attributes()[0]));
        ((entity*) IFC4X1_types[873])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[915])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OfShapeAspect", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[915]), ((entity*) IFC4X1_types[915])->attributes()[0]));
        ((entity*) IFC4X1_types[916])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[848]), ((entity*) IFC4X1_types[848])->attributes()[0]));
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[864]), ((entity*) IFC4X1_types[864])->attributes()[0]));
        ((entity*) IFC4X1_types[946])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainsElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[846]), ((entity*) IFC4X1_types[846])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ServicedBySystems", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[863]), ((entity*) IFC4X1_types[863])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ReferencesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[861]), ((entity*) IFC4X1_types[861])->attributes()[1]));
        ((entity*) IFC4X1_types[953])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToStructuralItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[842]), ((entity*) IFC4X1_types[842])->attributes()[1]));
        ((entity*) IFC4X1_types[977])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectsStructuralMembers", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[843]), ((entity*) IFC4X1_types[843])->attributes()[1]));
        ((entity*) IFC4X1_types[980])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedStructuralActivity", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[842]), ((entity*) IFC4X1_types[842])->attributes()[0]));
        ((entity*) IFC4X1_types[989])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("SourceOfResultGroup", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[1010]), ((entity*) IFC4X1_types[1010])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LoadGroupFor", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[979]), ((entity*) IFC4X1_types[979])->attributes()[2]));
        ((entity*) IFC4X1_types[994])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[843]), ((entity*) IFC4X1_types[843])->attributes()[0]));
        ((entity*) IFC4X1_types[1004])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResultGroupFor", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[979]), ((entity*) IFC4X1_types[979])->attributes()[3]));
        ((entity*) IFC4X1_types[1010])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsMappedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[1091]), ((entity*) IFC4X1_types[1091])->attributes()[0]));
        attributes.push_back(new inverse_attribute("UsedInStyles", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[1042]), ((entity*) IFC4X1_types[1042])->attributes()[0]));
        ((entity*) IFC4X1_types[1043])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ServicesBuildings", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[863]), ((entity*) IFC4X1_types[863])->attributes()[0]));
        ((entity*) IFC4X1_types[1051])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasColours", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[493]), ((entity*) IFC4X1_types[493])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasTextures", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[497]), ((entity*) IFC4X1_types[497])->attributes()[0]));
        ((entity*) IFC4X1_types[1076])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X1_types[394]), ((entity*) IFC4X1_types[394])->attributes()[1]));
        ((entity*) IFC4X1_types[1106])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Types", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X1_types[855]), ((entity*) IFC4X1_types[855])->attributes()[1]));
        ((entity*) IFC4X1_types[1134])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[826]), ((entity*) IFC4X1_types[826])->attributes()[0]));
        ((entity*) IFC4X1_types[1135])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[827]), ((entity*) IFC4X1_types[827])->attributes()[0]));
        ((entity*) IFC4X1_types[1136])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X1_types[828]), ((entity*) IFC4X1_types[828])->attributes()[0]));
        ((entity*) IFC4X1_types[1137])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X1_types[2]));defs.push_back(((entity*) IFC4X1_types[228]));defs.push_back(((entity*) IFC4X1_types[230]));defs.push_back(((entity*) IFC4X1_types[661]));defs.push_back(((entity*) IFC4X1_types[665]));defs.push_back(((entity*) IFC4X1_types[745]));defs.push_back(((entity*) IFC4X1_types[1191]));defs.push_back(((entity*) IFC4X1_types[1193]));
        ((entity*) IFC4X1_types[213])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[6]));defs.push_back(((entity*) IFC4X1_types[213]));defs.push_back(((entity*) IFC4X1_types[479]));defs.push_back(((entity*) IFC4X1_types[729]));defs.push_back(((entity*) IFC4X1_types[731]));defs.push_back(((entity*) IFC4X1_types[873]));
        ((entity*) IFC4X1_types[631])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X1_types[9]));defs.push_back(((entity*) IFC4X1_types[26]));defs.push_back(((entity*) IFC4X1_types[214]));defs.push_back(((entity*) IFC4X1_types[433]));defs.push_back(((entity*) IFC4X1_types[767]));defs.push_back(((entity*) IFC4X1_types[908]));defs.push_back(((entity*) IFC4X1_types[1139]));
        ((entity*) IFC4X1_types[290])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X1_types[10]));defs.push_back(((entity*) IFC4X1_types[27]));defs.push_back(((entity*) IFC4X1_types[215]));defs.push_back(((entity*) IFC4X1_types[434]));defs.push_back(((entity*) IFC4X1_types[768]));defs.push_back(((entity*) IFC4X1_types[909]));defs.push_back(((entity*) IFC4X1_types[1140]));
        ((entity*) IFC4X1_types[291])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[14]));defs.push_back(((entity*) IFC4X1_types[405]));
        ((entity*) IFC4X1_types[568])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[15]));
        ((entity*) IFC4X1_types[14])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[16]));
        ((entity*) IFC4X1_types[404])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(13);
        defs.push_back(((entity*) IFC4X1_types[17]));defs.push_back(((entity*) IFC4X1_types[61]));defs.push_back(((entity*) IFC4X1_types[170]));defs.push_back(((entity*) IFC4X1_types[335]));defs.push_back(((entity*) IFC4X1_types[424]));defs.push_back(((entity*) IFC4X1_types[524]));defs.push_back(((entity*) IFC4X1_types[538]));defs.push_back(((entity*) IFC4X1_types[600]));defs.push_back(((entity*) IFC4X1_types[653]));defs.push_back(((entity*) IFC4X1_types[894]));defs.push_back(((entity*) IFC4X1_types[948]));defs.push_back(((entity*) IFC4X1_types[966]));defs.push_back(((entity*) IFC4X1_types[1176]));
        ((entity*) IFC4X1_types[445])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X1_types[18]));defs.push_back(((entity*) IFC4X1_types[263]));defs.push_back(((entity*) IFC4X1_types[342]));defs.push_back(((entity*) IFC4X1_types[355]));defs.push_back(((entity*) IFC4X1_types[436]));defs.push_back(((entity*) IFC4X1_types[766]));defs.push_back(((entity*) IFC4X1_types[1048]));defs.push_back(((entity*) IFC4X1_types[1150]));
        ((entity*) IFC4X1_types[428])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X1_types[19]));defs.push_back(((entity*) IFC4X1_types[264]));defs.push_back(((entity*) IFC4X1_types[343]));defs.push_back(((entity*) IFC4X1_types[356]));defs.push_back(((entity*) IFC4X1_types[437]));defs.push_back(((entity*) IFC4X1_types[770]));defs.push_back(((entity*) IFC4X1_types[1049]));defs.push_back(((entity*) IFC4X1_types[1151]));
        ((entity*) IFC4X1_types[429])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(13);
        defs.push_back(((entity*) IFC4X1_types[21]));defs.push_back(((entity*) IFC4X1_types[62]));defs.push_back(((entity*) IFC4X1_types[171]));defs.push_back(((entity*) IFC4X1_types[336]));defs.push_back(((entity*) IFC4X1_types[425]));defs.push_back(((entity*) IFC4X1_types[525]));defs.push_back(((entity*) IFC4X1_types[539]));defs.push_back(((entity*) IFC4X1_types[601]));defs.push_back(((entity*) IFC4X1_types[654]));defs.push_back(((entity*) IFC4X1_types[895]));defs.push_back(((entity*) IFC4X1_types[949]));defs.push_back(((entity*) IFC4X1_types[967]));defs.push_back(((entity*) IFC4X1_types[1177]));
        ((entity*) IFC4X1_types[446])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC4X1_types[23]));defs.push_back(((entity*) IFC4X1_types[77]));defs.push_back(((entity*) IFC4X1_types[114]));defs.push_back(((entity*) IFC4X1_types[141]));defs.push_back(((entity*) IFC4X1_types[158]));defs.push_back(((entity*) IFC4X1_types[185]));defs.push_back(((entity*) IFC4X1_types[219]));defs.push_back(((entity*) IFC4X1_types[222]));defs.push_back(((entity*) IFC4X1_types[348]));defs.push_back(((entity*) IFC4X1_types[351]));defs.push_back(((entity*) IFC4X1_types[374]));defs.push_back(((entity*) IFC4X1_types[377]));defs.push_back(((entity*) IFC4X1_types[380]));defs.push_back(((entity*) IFC4X1_types[482]));defs.push_back(((entity*) IFC4X1_types[487]));defs.push_back(((entity*) IFC4X1_types[623]));defs.push_back(((entity*) IFC4X1_types[936]));defs.push_back(((entity*) IFC4X1_types[1114]));defs.push_back(((entity*) IFC4X1_types[1131]));defs.push_back(((entity*) IFC4X1_types[1142]));
        ((entity*) IFC4X1_types[371])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC4X1_types[24]));defs.push_back(((entity*) IFC4X1_types[78]));defs.push_back(((entity*) IFC4X1_types[115]));defs.push_back(((entity*) IFC4X1_types[142]));defs.push_back(((entity*) IFC4X1_types[159]));defs.push_back(((entity*) IFC4X1_types[186]));defs.push_back(((entity*) IFC4X1_types[220]));defs.push_back(((entity*) IFC4X1_types[223]));defs.push_back(((entity*) IFC4X1_types[349]));defs.push_back(((entity*) IFC4X1_types[352]));defs.push_back(((entity*) IFC4X1_types[375]));defs.push_back(((entity*) IFC4X1_types[378]));defs.push_back(((entity*) IFC4X1_types[381]));defs.push_back(((entity*) IFC4X1_types[483]));defs.push_back(((entity*) IFC4X1_types[488]));defs.push_back(((entity*) IFC4X1_types[624]));defs.push_back(((entity*) IFC4X1_types[937]));defs.push_back(((entity*) IFC4X1_types[1115]));defs.push_back(((entity*) IFC4X1_types[1132]));defs.push_back(((entity*) IFC4X1_types[1143]));
        ((entity*) IFC4X1_types[372])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[29]));
        ((entity*) IFC4X1_types[552])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(30);
        defs.push_back(((entity*) IFC4X1_types[30]));defs.push_back(((entity*) IFC4X1_types[32]));defs.push_back(((entity*) IFC4X1_types[36]));defs.push_back(((entity*) IFC4X1_types[45]));defs.push_back(((entity*) IFC4X1_types[84]));defs.push_back(((entity*) IFC4X1_types[93]));defs.push_back(((entity*) IFC4X1_types[131]));defs.push_back(((entity*) IFC4X1_types[134]));defs.push_back(((entity*) IFC4X1_types[179]));defs.push_back(((entity*) IFC4X1_types[240]));defs.push_back(((entity*) IFC4X1_types[249]));defs.push_back(((entity*) IFC4X1_types[280]));defs.push_back(((entity*) IFC4X1_types[285]));defs.push_back(((entity*) IFC4X1_types[401]));defs.push_back(((entity*) IFC4X1_types[418]));defs.push_back(((entity*) IFC4X1_types[419]));defs.push_back(((entity*) IFC4X1_types[470]));defs.push_back(((entity*) IFC4X1_types[480]));defs.push_back(((entity*) IFC4X1_types[542]));defs.push_back(((entity*) IFC4X1_types[650]));defs.push_back(((entity*) IFC4X1_types[685]));defs.push_back(((entity*) IFC4X1_types[687]));defs.push_back(((entity*) IFC4X1_types[695]));defs.push_back(((entity*) IFC4X1_types[902]));defs.push_back(((entity*) IFC4X1_types[920]));defs.push_back(((entity*) IFC4X1_types[940]));defs.push_back(((entity*) IFC4X1_types[1026]));defs.push_back(((entity*) IFC4X1_types[1077]));defs.push_back(((entity*) IFC4X1_types[1083]));defs.push_back(((entity*) IFC4X1_types[1154]));
        ((entity*) IFC4X1_types[468])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[31]));defs.push_back(((entity*) IFC4X1_types[37]));
        ((entity*) IFC4X1_types[32])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[33]));defs.push_back(((entity*) IFC4X1_types[34]));defs.push_back(((entity*) IFC4X1_types[35]));
        ((entity*) IFC4X1_types[37])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X1_types[38]));defs.push_back(((entity*) IFC4X1_types[96]));defs.push_back(((entity*) IFC4X1_types[177]));defs.push_back(((entity*) IFC4X1_types[256]));defs.push_back(((entity*) IFC4X1_types[494]));defs.push_back(((entity*) IFC4X1_types[701]));defs.push_back(((entity*) IFC4X1_types[1127]));
        ((entity*) IFC4X1_types[91])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X1_types[44]));defs.push_back(((entity*) IFC4X1_types[359]));defs.push_back(((entity*) IFC4X1_types[703]));defs.push_back(((entity*) IFC4X1_types[704]));defs.push_back(((entity*) IFC4X1_types[772]));defs.push_back(((entity*) IFC4X1_types[953]));defs.push_back(((entity*) IFC4X1_types[977]));defs.push_back(((entity*) IFC4X1_types[989]));
        ((entity*) IFC4X1_types[731])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4X1_types[50]));defs.push_back(((entity*) IFC4X1_types[244]));defs.push_back(((entity*) IFC4X1_types[302]));defs.push_back(((entity*) IFC4X1_types[394]));defs.push_back(((entity*) IFC4X1_types[592]));defs.push_back(((entity*) IFC4X1_types[649]));defs.push_back(((entity*) IFC4X1_types[751]));defs.push_back(((entity*) IFC4X1_types[874]));defs.push_back(((entity*) IFC4X1_types[875]));
        ((entity*) IFC4X1_types[876])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[51]));defs.push_back(((entity*) IFC4X1_types[52]));defs.push_back(((entity*) IFC4X1_types[180]));defs.push_back(((entity*) IFC4X1_types[273]));defs.push_back(((entity*) IFC4X1_types[657]));
        ((entity*) IFC4X1_types[736])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[53]));
        ((entity*) IFC4X1_types[51])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[59]));defs.push_back(((entity*) IFC4X1_types[507]));defs.push_back(((entity*) IFC4X1_types[994]));defs.push_back(((entity*) IFC4X1_types[1010]));defs.push_back(((entity*) IFC4X1_types[1051]));
        ((entity*) IFC4X1_types[479])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(11);
        defs.push_back(((entity*) IFC4X1_types[60]));defs.push_back(((entity*) IFC4X1_types[243]));defs.push_back(((entity*) IFC4X1_types[149]));defs.push_back(((entity*) IFC4X1_types[370]));defs.push_back(((entity*) IFC4X1_types[512]));defs.push_back(((entity*) IFC4X1_types[562]));defs.push_back(((entity*) IFC4X1_types[798]));defs.push_back(((entity*) IFC4X1_types[1130]));defs.push_back(((entity*) IFC4X1_types[1124]));defs.push_back(((entity*) IFC4X1_types[1148]));defs.push_back(((entity*) IFC4X1_types[1200]));
        ((entity*) IFC4X1_types[657])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[64]));defs.push_back(((entity*) IFC4X1_types[66]));defs.push_back(((entity*) IFC4X1_types[67]));
        ((entity*) IFC4X1_types[685])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[98]));
        ((entity*) IFC4X1_types[96])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[99]));defs.push_back(((entity*) IFC4X1_types[250]));defs.push_back(((entity*) IFC4X1_types[251]));defs.push_back(((entity*) IFC4X1_types[800]));
        ((entity*) IFC4X1_types[92])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[101]));
        ((entity*) IFC4X1_types[99])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(21);
        defs.push_back(((entity*) IFC4X1_types[68]));defs.push_back(((entity*) IFC4X1_types[107]));defs.push_back(((entity*) IFC4X1_types[144]));defs.push_back(((entity*) IFC4X1_types[166]));defs.push_back(((entity*) IFC4X1_types[234]));defs.push_back(((entity*) IFC4X1_types[245]));defs.push_back(((entity*) IFC4X1_types[306]));defs.push_back(((entity*) IFC4X1_types[452]));defs.push_back(((entity*) IFC4X1_types[603]));defs.push_back(((entity*) IFC4X1_types[674]));defs.push_back(((entity*) IFC4X1_types[691]));defs.push_back(((entity*) IFC4X1_types[784]));defs.push_back(((entity*) IFC4X1_types[787]));defs.push_back(((entity*) IFC4X1_types[788]));defs.push_back(((entity*) IFC4X1_types[885]));defs.push_back(((entity*) IFC4X1_types[912]));defs.push_back(((entity*) IFC4X1_types[930]));defs.push_back(((entity*) IFC4X1_types[969]));defs.push_back(((entity*) IFC4X1_types[970]));defs.push_back(((entity*) IFC4X1_types[1168]));defs.push_back(((entity*) IFC4X1_types[1179]));
        ((entity*) IFC4X1_types[103])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[69]));
        ((entity*) IFC4X1_types[68])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(21);
        defs.push_back(((entity*) IFC4X1_types[70]));defs.push_back(((entity*) IFC4X1_types[108]));defs.push_back(((entity*) IFC4X1_types[145]));defs.push_back(((entity*) IFC4X1_types[168]));defs.push_back(((entity*) IFC4X1_types[235]));defs.push_back(((entity*) IFC4X1_types[246]));defs.push_back(((entity*) IFC4X1_types[315]));defs.push_back(((entity*) IFC4X1_types[453]));defs.push_back(((entity*) IFC4X1_types[605]));defs.push_back(((entity*) IFC4X1_types[676]));defs.push_back(((entity*) IFC4X1_types[693]));defs.push_back(((entity*) IFC4X1_types[785]));defs.push_back(((entity*) IFC4X1_types[789]));defs.push_back(((entity*) IFC4X1_types[791]));defs.push_back(((entity*) IFC4X1_types[886]));defs.push_back(((entity*) IFC4X1_types[913]));defs.push_back(((entity*) IFC4X1_types[933]));defs.push_back(((entity*) IFC4X1_types[971]));defs.push_back(((entity*) IFC4X1_types[973]));defs.push_back(((entity*) IFC4X1_types[1171]));defs.push_back(((entity*) IFC4X1_types[1188]));
        ((entity*) IFC4X1_types[110])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[75]));defs.push_back(((entity*) IFC4X1_types[492]));defs.push_back(((entity*) IFC4X1_types[684]));
        ((entity*) IFC4X1_types[1043])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[76]));defs.push_back(((entity*) IFC4X1_types[799]));defs.push_back(((entity*) IFC4X1_types[882]));defs.push_back(((entity*) IFC4X1_types[883]));defs.push_back(((entity*) IFC4X1_types[964]));
        ((entity*) IFC4X1_types[240])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[81]));
        ((entity*) IFC4X1_types[84])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[86]));
        ((entity*) IFC4X1_types[178])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[87]));defs.push_back(((entity*) IFC4X1_types[88]));defs.push_back(((entity*) IFC4X1_types[89]));
        ((entity*) IFC4X1_types[85])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[90]));
        ((entity*) IFC4X1_types[89])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[91]));defs.push_back(((entity*) IFC4X1_types[188]));defs.push_back(((entity*) IFC4X1_types[548]));defs.push_back(((entity*) IFC4X1_types[640]));defs.push_back(((entity*) IFC4X1_types[660]));defs.push_back(((entity*) IFC4X1_types[1027]));
        ((entity*) IFC4X1_types[249])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[92]));defs.push_back(((entity*) IFC4X1_types[360]));defs.push_back(((entity*) IFC4X1_types[1047]));
        ((entity*) IFC4X1_types[1026])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[95]));defs.push_back(((entity*) IFC4X1_types[699]));
        ((entity*) IFC4X1_types[480])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[102]));defs.push_back(((entity*) IFC4X1_types[111]));defs.push_back(((entity*) IFC4X1_types[926]));defs.push_back(((entity*) IFC4X1_types[946]));
        ((entity*) IFC4X1_types[955])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(10);
        defs.push_back(((entity*) IFC4X1_types[103]));defs.push_back(((entity*) IFC4X1_types[151]));defs.push_back(((entity*) IFC4X1_types[292]));defs.push_back(((entity*) IFC4X1_types[361]));defs.push_back(((entity*) IFC4X1_types[364]));defs.push_back(((entity*) IFC4X1_types[414]));defs.push_back(((entity*) IFC4X1_types[457]));defs.push_back(((entity*) IFC4X1_types[462]));defs.push_back(((entity*) IFC4X1_types[1121]));defs.push_back(((entity*) IFC4X1_types[1162]));
        ((entity*) IFC4X1_types[359])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[104]));defs.push_back(((entity*) IFC4X1_types[282]));defs.push_back(((entity*) IFC4X1_types[411]));defs.push_back(((entity*) IFC4X1_types[597]));defs.push_back(((entity*) IFC4X1_types[815]));defs.push_back(((entity*) IFC4X1_types[1159]));
        ((entity*) IFC4X1_types[364])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[105]));defs.push_back(((entity*) IFC4X1_types[283]));defs.push_back(((entity*) IFC4X1_types[412]));defs.push_back(((entity*) IFC4X1_types[598]));defs.push_back(((entity*) IFC4X1_types[816]));defs.push_back(((entity*) IFC4X1_types[1160]));
        ((entity*) IFC4X1_types[365])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X1_types[110]));defs.push_back(((entity*) IFC4X1_types[152]));defs.push_back(((entity*) IFC4X1_types[293]));defs.push_back(((entity*) IFC4X1_types[362]));defs.push_back(((entity*) IFC4X1_types[365]));defs.push_back(((entity*) IFC4X1_types[458]));defs.push_back(((entity*) IFC4X1_types[463]));defs.push_back(((entity*) IFC4X1_types[1122]));
        ((entity*) IFC4X1_types[368])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[112]));defs.push_back(((entity*) IFC4X1_types[298]));defs.push_back(((entity*) IFC4X1_types[979]));defs.push_back(((entity*) IFC4X1_types[1199]));
        ((entity*) IFC4X1_types[1051])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[117]));defs.push_back(((entity*) IFC4X1_types[123]));defs.push_back(((entity*) IFC4X1_types[321]));defs.push_back(((entity*) IFC4X1_types[514]));defs.push_back(((entity*) IFC4X1_types[678]));
        ((entity*) IFC4X1_types[431])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[118]));defs.push_back(((entity*) IFC4X1_types[124]));defs.push_back(((entity*) IFC4X1_types[322]));defs.push_back(((entity*) IFC4X1_types[515]));defs.push_back(((entity*) IFC4X1_types[679]));
        ((entity*) IFC4X1_types[432])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[120]));defs.push_back(((entity*) IFC4X1_types[126]));defs.push_back(((entity*) IFC4X1_types[324]));defs.push_back(((entity*) IFC4X1_types[681]));
        ((entity*) IFC4X1_types[441])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[121]));defs.push_back(((entity*) IFC4X1_types[127]));defs.push_back(((entity*) IFC4X1_types[325]));defs.push_back(((entity*) IFC4X1_types[682]));
        ((entity*) IFC4X1_types[442])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[130]));defs.push_back(((entity*) IFC4X1_types[696]));defs.push_back(((entity*) IFC4X1_types[697]));
        ((entity*) IFC4X1_types[695])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[132]));defs.push_back(((entity*) IFC4X1_types[133]));
        ((entity*) IFC4X1_types[131])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[135]));defs.push_back(((entity*) IFC4X1_types[137]));
        ((entity*) IFC4X1_types[134])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[136]));
        ((entity*) IFC4X1_types[135])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[138]));
        ((entity*) IFC4X1_types[137])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[139]));
        ((entity*) IFC4X1_types[52])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[147]));defs.push_back(((entity*) IFC4X1_types[369]));
        ((entity*) IFC4X1_types[188])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[148]));
        ((entity*) IFC4X1_types[149])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[150]));defs.push_back(((entity*) IFC4X1_types[556]));defs.push_back(((entity*) IFC4X1_types[1118]));
        ((entity*) IFC4X1_types[256])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[153]));defs.push_back(((entity*) IFC4X1_types[301]));defs.push_back(((entity*) IFC4X1_types[531]));
        ((entity*) IFC4X1_types[389])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[154]));defs.push_back(((entity*) IFC4X1_types[303]));defs.push_back(((entity*) IFC4X1_types[390]));defs.push_back(((entity*) IFC4X1_types[391]));defs.push_back(((entity*) IFC4X1_types[392]));defs.push_back(((entity*) IFC4X1_types[532]));
        ((entity*) IFC4X1_types[393])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[157]));defs.push_back(((entity*) IFC4X1_types[647]));
        ((entity*) IFC4X1_types[189])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[163]));
        ((entity*) IFC4X1_types[165])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(17);
        defs.push_back(((entity*) IFC4X1_types[164]));defs.push_back(((entity*) IFC4X1_types[165]));defs.push_back(((entity*) IFC4X1_types[258]));defs.push_back(((entity*) IFC4X1_types[259]));defs.push_back(((entity*) IFC4X1_types[260]));defs.push_back(((entity*) IFC4X1_types[493]));defs.push_back(((entity*) IFC4X1_types[713]));defs.push_back(((entity*) IFC4X1_types[1038]));defs.push_back(((entity*) IFC4X1_types[1039]));defs.push_back(((entity*) IFC4X1_types[1041]));defs.push_back(((entity*) IFC4X1_types[1042]));defs.push_back(((entity*) IFC4X1_types[1043]));defs.push_back(((entity*) IFC4X1_types[1088]));defs.push_back(((entity*) IFC4X1_types[1089]));defs.push_back(((entity*) IFC4X1_types[1091]));defs.push_back(((entity*) IFC4X1_types[1094]));defs.push_back(((entity*) IFC4X1_types[1095]));
        ((entity*) IFC4X1_types[719])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[167]));
        ((entity*) IFC4X1_types[166])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[174]));defs.push_back(((entity*) IFC4X1_types[921]));
        ((entity*) IFC4X1_types[747])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[175]));defs.push_back(((entity*) IFC4X1_types[922]));
        ((entity*) IFC4X1_types[764])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[178]));
        ((entity*) IFC4X1_types[177])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[182]));defs.push_back(((entity*) IFC4X1_types[408]));defs.push_back(((entity*) IFC4X1_types[773]));
        ((entity*) IFC4X1_types[439])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[183]));defs.push_back(((entity*) IFC4X1_types[409]));defs.push_back(((entity*) IFC4X1_types[774]));
        ((entity*) IFC4X1_types[440])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X1_types[189]));defs.push_back(((entity*) IFC4X1_types[332]));defs.push_back(((entity*) IFC4X1_types[400]));defs.push_back(((entity*) IFC4X1_types[402]));defs.push_back(((entity*) IFC4X1_types[561]));defs.push_back(((entity*) IFC4X1_types[659]));defs.push_back(((entity*) IFC4X1_types[1156]));
        ((entity*) IFC4X1_types[1110])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[190]));defs.push_back(((entity*) IFC4X1_types[193]));defs.push_back(((entity*) IFC4X1_types[194]));defs.push_back(((entity*) IFC4X1_types[196]));
        ((entity*) IFC4X1_types[191])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[192]));
        ((entity*) IFC4X1_types[193])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[199]));defs.push_back(((entity*) IFC4X1_types[202]));defs.push_back(((entity*) IFC4X1_types[205]));defs.push_back(((entity*) IFC4X1_types[237]));defs.push_back(((entity*) IFC4X1_types[520]));defs.push_back(((entity*) IFC4X1_types[1022]));
        ((entity*) IFC4X1_types[208])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[200]));defs.push_back(((entity*) IFC4X1_types[203]));defs.push_back(((entity*) IFC4X1_types[206]));defs.push_back(((entity*) IFC4X1_types[238]));defs.push_back(((entity*) IFC4X1_types[521]));defs.push_back(((entity*) IFC4X1_types[1023]));
        ((entity*) IFC4X1_types[209])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[208]));
        ((entity*) IFC4X1_types[873])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[209]));
        ((entity*) IFC4X1_types[1137])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[210]));defs.push_back(((entity*) IFC4X1_types[631]));defs.push_back(((entity*) IFC4X1_types[1134]));
        ((entity*) IFC4X1_types[632])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[212]));defs.push_back(((entity*) IFC4X1_types[217]));defs.push_back(((entity*) IFC4X1_types[927]));
        ((entity*) IFC4X1_types[626])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[218]));
        ((entity*) IFC4X1_types[217])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[232]));
        ((entity*) IFC4X1_types[47])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[242]));defs.push_back(((entity*) IFC4X1_types[568]));defs.push_back(((entity*) IFC4X1_types[900]));defs.push_back(((entity*) IFC4X1_types[1044]));defs.push_back(((entity*) IFC4X1_types[1045]));
        ((entity*) IFC4X1_types[940])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[257]));defs.push_back(((entity*) IFC4X1_types[417]));defs.push_back(((entity*) IFC4X1_types[1036]));defs.push_back(((entity*) IFC4X1_types[1086]));
        ((entity*) IFC4X1_types[722])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[262]));defs.push_back(((entity*) IFC4X1_types[689]));defs.push_back(((entity*) IFC4X1_types[965]));defs.push_back(((entity*) IFC4X1_types[1112]));
        ((entity*) IFC4X1_types[360])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4X1_types[286]));defs.push_back(((entity*) IFC4X1_types[371]));defs.push_back(((entity*) IFC4X1_types[428]));defs.push_back(((entity*) IFC4X1_types[431]));defs.push_back(((entity*) IFC4X1_types[439]));defs.push_back(((entity*) IFC4X1_types[441]));defs.push_back(((entity*) IFC4X1_types[443]));defs.push_back(((entity*) IFC4X1_types[445]));defs.push_back(((entity*) IFC4X1_types[447]));
        ((entity*) IFC4X1_types[294])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4X1_types[287]));defs.push_back(((entity*) IFC4X1_types[372]));defs.push_back(((entity*) IFC4X1_types[429]));defs.push_back(((entity*) IFC4X1_types[432]));defs.push_back(((entity*) IFC4X1_types[440]));defs.push_back(((entity*) IFC4X1_types[442]));defs.push_back(((entity*) IFC4X1_types[444]));defs.push_back(((entity*) IFC4X1_types[446]));defs.push_back(((entity*) IFC4X1_types[448]));
        ((entity*) IFC4X1_types[295])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[289]));
        ((entity*) IFC4X1_types[298])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[290]));defs.push_back(((entity*) IFC4X1_types[294]));
        ((entity*) IFC4X1_types[292])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[291]));defs.push_back(((entity*) IFC4X1_types[295]));
        ((entity*) IFC4X1_types[293])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[296]));
        ((entity*) IFC4X1_types[703])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[307]));defs.push_back(((entity*) IFC4X1_types[310]));defs.push_back(((entity*) IFC4X1_types[664]));defs.push_back(((entity*) IFC4X1_types[809]));defs.push_back(((entity*) IFC4X1_types[1180]));defs.push_back(((entity*) IFC4X1_types[1183]));
        ((entity*) IFC4X1_types[715])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[311]));
        ((entity*) IFC4X1_types[306])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[312]));defs.push_back(((entity*) IFC4X1_types[368]));defs.push_back(((entity*) IFC4X1_types[954]));defs.push_back(((entity*) IFC4X1_types[1185]));
        ((entity*) IFC4X1_types[1136])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[319]));
        ((entity*) IFC4X1_types[711])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[320]));
        ((entity*) IFC4X1_types[712])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[327]));defs.push_back(((entity*) IFC4X1_types[421]));defs.push_back(((entity*) IFC4X1_types[502]));
        ((entity*) IFC4X1_types[447])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[328]));defs.push_back(((entity*) IFC4X1_types[422]));defs.push_back(((entity*) IFC4X1_types[503]));
        ((entity*) IFC4X1_types[448])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[333]));defs.push_back(((entity*) IFC4X1_types[651]));defs.push_back(((entity*) IFC4X1_types[1025]));
        ((entity*) IFC4X1_types[332])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[334]));defs.push_back(((entity*) IFC4X1_types[702]));defs.push_back(((entity*) IFC4X1_types[1157]));
        ((entity*) IFC4X1_types[561])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[345]));defs.push_back(((entity*) IFC4X1_types[1058]));
        ((entity*) IFC4X1_types[443])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[346]));defs.push_back(((entity*) IFC4X1_types[1059]));
        ((entity*) IFC4X1_types[444])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[367]));
        ((entity*) IFC4X1_types[779])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[383]));defs.push_back(((entity*) IFC4X1_types[726]));defs.push_back(((entity*) IFC4X1_types[1061]));
        ((entity*) IFC4X1_types[729])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[384]));defs.push_back(((entity*) IFC4X1_types[523]));defs.push_back(((entity*) IFC4X1_types[879]));defs.push_back(((entity*) IFC4X1_types[1063]));defs.push_back(((entity*) IFC4X1_types[1198]));
        ((entity*) IFC4X1_types[897])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[386]));defs.push_back(((entity*) IFC4X1_types[727]));defs.push_back(((entity*) IFC4X1_types[1065]));
        ((entity*) IFC4X1_types[1135])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[388]));defs.push_back(((entity*) IFC4X1_types[714]));defs.push_back(((entity*) IFC4X1_types[747]));defs.push_back(((entity*) IFC4X1_types[753]));
        ((entity*) IFC4X1_types[748])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[395]));
        ((entity*) IFC4X1_types[397])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[397]));defs.push_back(((entity*) IFC4X1_types[955]));defs.push_back(((entity*) IFC4X1_types[957]));
        ((entity*) IFC4X1_types[953])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[398]));defs.push_back(((entity*) IFC4X1_types[427]));defs.push_back(((entity*) IFC4X1_types[880]));defs.push_back(((entity*) IFC4X1_types[1028]));
        ((entity*) IFC4X1_types[1044])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[399]));
        ((entity*) IFC4X1_types[398])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[403]));
        ((entity*) IFC4X1_types[402])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[404]));
        ((entity*) IFC4X1_types[400])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[406]));
        ((entity*) IFC4X1_types[405])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[407]));defs.push_back(((entity*) IFC4X1_types[935]));
        ((entity*) IFC4X1_types[981])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[415]));defs.push_back(((entity*) IFC4X1_types[416]));defs.push_back(((entity*) IFC4X1_types[1029]));
        ((entity*) IFC4X1_types[414])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[459]));defs.push_back(((entity*) IFC4X1_types[1052]));
        ((entity*) IFC4X1_types[457])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[460]));defs.push_back(((entity*) IFC4X1_types[1053]));
        ((entity*) IFC4X1_types[458])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[465]));
        ((entity*) IFC4X1_types[470])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[467]));
        ((entity*) IFC4X1_types[870])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[468]));defs.push_back(((entity*) IFC4X1_types[570]));defs.push_back(((entity*) IFC4X1_types[1019]));defs.push_back(((entity*) IFC4X1_types[1110]));
        ((entity*) IFC4X1_types[871])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[469]));
        ((entity*) IFC4X1_types[467])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[474]));defs.push_back(((entity*) IFC4X1_types[552]));defs.push_back(((entity*) IFC4X1_types[804]));
        ((entity*) IFC4X1_types[704])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[476]));defs.push_back(((entity*) IFC4X1_types[551]));defs.push_back(((entity*) IFC4X1_types[558]));
        ((entity*) IFC4X1_types[635])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[495]));defs.push_back(((entity*) IFC4X1_types[1076]));
        ((entity*) IFC4X1_types[1077])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[496]));
        ((entity*) IFC4X1_types[495])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[497]));defs.push_back(((entity*) IFC4X1_types[1092]));defs.push_back(((entity*) IFC4X1_types[1093]));
        ((entity*) IFC4X1_types[1091])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[498]));
        ((entity*) IFC4X1_types[497])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[506]));defs.push_back(((entity*) IFC4X1_types[898]));
        ((entity*) IFC4X1_types[1027])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[510]));defs.push_back(((entity*) IFC4X1_types[807]));
        ((entity*) IFC4X1_types[1106])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[543]));defs.push_back(((entity*) IFC4X1_types[544]));defs.push_back(((entity*) IFC4X1_types[545]));defs.push_back(((entity*) IFC4X1_types[546]));
        ((entity*) IFC4X1_types[542])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[547]));
        ((entity*) IFC4X1_types[546])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[569]));
        ((entity*) IFC4X1_types[225])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X1_types[575]));defs.push_back(((entity*) IFC4X1_types[577]));defs.push_back(((entity*) IFC4X1_types[578]));defs.push_back(((entity*) IFC4X1_types[581]));defs.push_back(((entity*) IFC4X1_types[582]));defs.push_back(((entity*) IFC4X1_types[586]));defs.push_back(((entity*) IFC4X1_types[587]));
        ((entity*) IFC4X1_types[579])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[580]));defs.push_back(((entity*) IFC4X1_types[732]));
        ((entity*) IFC4X1_types[733])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[583]));defs.push_back(((entity*) IFC4X1_types[588]));
        ((entity*) IFC4X1_types[594])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[584]));
        ((entity*) IFC4X1_types[581])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[589]));
        ((entity*) IFC4X1_types[588])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[590]));
        ((entity*) IFC4X1_types[586])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[591]));defs.push_back(((entity*) IFC4X1_types[737]));
        ((entity*) IFC4X1_types[388])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[604]));
        ((entity*) IFC4X1_types[603])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[607]));defs.push_back(((entity*) IFC4X1_types[633]));
        ((entity*) IFC4X1_types[197])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[609]));
        ((entity*) IFC4X1_types[273])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[632]));defs.push_back(((entity*) IFC4X1_types[750]));defs.push_back(((entity*) IFC4X1_types[836]));
        ((entity*) IFC4X1_types[888])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[638]));
        ((entity*) IFC4X1_types[6])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[641]));defs.push_back(((entity*) IFC4X1_types[642]));defs.push_back(((entity*) IFC4X1_types[643]));
        ((entity*) IFC4X1_types[640])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[644]));defs.push_back(((entity*) IFC4X1_types[1164]));
        ((entity*) IFC4X1_types[416])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[646]));
        ((entity*) IFC4X1_types[644])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[652]));
        ((entity*) IFC4X1_types[86])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[670]));defs.push_back(((entity*) IFC4X1_types[673]));
        ((entity*) IFC4X1_types[672])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[686]));
        ((entity*) IFC4X1_types[687])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[692]));
        ((entity*) IFC4X1_types[691])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[700]));defs.push_back(((entity*) IFC4X1_types[1125]));
        ((entity*) IFC4X1_types[1076])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[709]));defs.push_back(((entity*) IFC4X1_types[1067]));
        ((entity*) IFC4X1_types[12])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[711]));defs.push_back(((entity*) IFC4X1_types[712]));defs.push_back(((entity*) IFC4X1_types[716]));
        ((entity*) IFC4X1_types[713])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[715]));defs.push_back(((entity*) IFC4X1_types[756]));defs.push_back(((entity*) IFC4X1_types[779]));
        ((entity*) IFC4X1_types[757])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[721]));
        ((entity*) IFC4X1_types[720])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[739]));defs.push_back(((entity*) IFC4X1_types[744]));
        ((entity*) IFC4X1_types[210])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[740]));
        ((entity*) IFC4X1_types[226])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[742]));
        ((entity*) IFC4X1_types[415])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[749]));defs.push_back(((entity*) IFC4X1_types[752]));defs.push_back(((entity*) IFC4X1_types[754]));defs.push_back(((entity*) IFC4X1_types[755]));defs.push_back(((entity*) IFC4X1_types[762]));defs.push_back(((entity*) IFC4X1_types[763]));
        ((entity*) IFC4X1_types[921])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[757]));defs.push_back(((entity*) IFC4X1_types[765]));
        ((entity*) IFC4X1_types[750])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[760]));defs.push_back(((entity*) IFC4X1_types[764]));
        ((entity*) IFC4X1_types[765])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[776]));defs.push_back(((entity*) IFC4X1_types[777]));defs.push_back(((entity*) IFC4X1_types[778]));defs.push_back(((entity*) IFC4X1_types[780]));defs.push_back(((entity*) IFC4X1_types[781]));defs.push_back(((entity*) IFC4X1_types[782]));
        ((entity*) IFC4X1_types[673])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[794]));
        ((entity*) IFC4X1_types[98])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[795]));
        ((entity*) IFC4X1_types[101])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[797]));defs.push_back(((entity*) IFC4X1_types[893]));
        ((entity*) IFC4X1_types[798])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[808]));defs.push_back(((entity*) IFC4X1_types[904]));defs.push_back(((entity*) IFC4X1_types[905]));
        ((entity*) IFC4X1_types[714])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[810]));defs.push_back(((entity*) IFC4X1_types[817]));defs.push_back(((entity*) IFC4X1_types[1070]));defs.push_back(((entity*) IFC4X1_types[1071]));
        ((entity*) IFC4X1_types[815])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[813]));defs.push_back(((entity*) IFC4X1_types[818]));defs.push_back(((entity*) IFC4X1_types[1072]));defs.push_back(((entity*) IFC4X1_types[1074]));
        ((entity*) IFC4X1_types[816])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[820]));defs.push_back(((entity*) IFC4X1_types[859]));defs.push_back(((entity*) IFC4X1_types[860]));defs.push_back(((entity*) IFC4X1_types[867]));
        ((entity*) IFC4X1_types[850])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[821]));defs.push_back(((entity*) IFC4X1_types[829]));defs.push_back(((entity*) IFC4X1_types[837]));defs.push_back(((entity*) IFC4X1_types[849]));defs.push_back(((entity*) IFC4X1_types[850]));defs.push_back(((entity*) IFC4X1_types[851]));
        ((entity*) IFC4X1_types[836])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[822]));defs.push_back(((entity*) IFC4X1_types[823]));defs.push_back(((entity*) IFC4X1_types[824]));defs.push_back(((entity*) IFC4X1_types[826]));defs.push_back(((entity*) IFC4X1_types[827]));defs.push_back(((entity*) IFC4X1_types[828]));
        ((entity*) IFC4X1_types[821])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[825]));
        ((entity*) IFC4X1_types[824])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X1_types[830]));defs.push_back(((entity*) IFC4X1_types[831]));defs.push_back(((entity*) IFC4X1_types[832]));defs.push_back(((entity*) IFC4X1_types[833]));defs.push_back(((entity*) IFC4X1_types[834]));defs.push_back(((entity*) IFC4X1_types[835]));
        ((entity*) IFC4X1_types[829])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(15);
        defs.push_back(((entity*) IFC4X1_types[838]));defs.push_back(((entity*) IFC4X1_types[841]));defs.push_back(((entity*) IFC4X1_types[840]));defs.push_back(((entity*) IFC4X1_types[842]));defs.push_back(((entity*) IFC4X1_types[843]));defs.push_back(((entity*) IFC4X1_types[846]));defs.push_back(((entity*) IFC4X1_types[847]));defs.push_back(((entity*) IFC4X1_types[848]));defs.push_back(((entity*) IFC4X1_types[856]));defs.push_back(((entity*) IFC4X1_types[857]));defs.push_back(((entity*) IFC4X1_types[858]));defs.push_back(((entity*) IFC4X1_types[861]));defs.push_back(((entity*) IFC4X1_types[862]));defs.push_back(((entity*) IFC4X1_types[863]));defs.push_back(((entity*) IFC4X1_types[864]));
        ((entity*) IFC4X1_types[837])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[839]));defs.push_back(((entity*) IFC4X1_types[845]));
        ((entity*) IFC4X1_types[838])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[844]));
        ((entity*) IFC4X1_types[843])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X1_types[852]));defs.push_back(((entity*) IFC4X1_types[853]));defs.push_back(((entity*) IFC4X1_types[854]));defs.push_back(((entity*) IFC4X1_types[855]));
        ((entity*) IFC4X1_types[851])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[865]));
        ((entity*) IFC4X1_types[864])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[866]));
        ((entity*) IFC4X1_types[865])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[868]));
        ((entity*) IFC4X1_types[179])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[881]));
        ((entity*) IFC4X1_types[880])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[901]));
        ((entity*) IFC4X1_types[900])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[916]));defs.push_back(((entity*) IFC4X1_types[1021]));
        ((entity*) IFC4X1_types[869])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[917]));defs.push_back(((entity*) IFC4X1_types[1111]));
        ((entity*) IFC4X1_types[916])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[931]));defs.push_back(((entity*) IFC4X1_types[932]));
        ((entity*) IFC4X1_types[930])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[951]));
        ((entity*) IFC4X1_types[956])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[956]));defs.push_back(((entity*) IFC4X1_types[958]));
        ((entity*) IFC4X1_types[954])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[976]));defs.push_back(((entity*) IFC4X1_types[1009]));
        ((entity*) IFC4X1_types[977])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[980]));defs.push_back(((entity*) IFC4X1_types[1004]));
        ((entity*) IFC4X1_types[989])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[982]));defs.push_back(((entity*) IFC4X1_types[1006]));defs.push_back(((entity*) IFC4X1_types[1011]));
        ((entity*) IFC4X1_types[976])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[984]));defs.push_back(((entity*) IFC4X1_types[1007]));defs.push_back(((entity*) IFC4X1_types[1013]));
        ((entity*) IFC4X1_types[980])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[985]));defs.push_back(((entity*) IFC4X1_types[1014]));
        ((entity*) IFC4X1_types[1004])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[987]));
        ((entity*) IFC4X1_types[985])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[988]));defs.push_back(((entity*) IFC4X1_types[1008]));defs.push_back(((entity*) IFC4X1_types[1017]));
        ((entity*) IFC4X1_types[1009])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[990]));
        ((entity*) IFC4X1_types[982])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[992]));
        ((entity*) IFC4X1_types[994])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[993]));defs.push_back(((entity*) IFC4X1_types[996]));
        ((entity*) IFC4X1_types[991])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X1_types[995]));defs.push_back(((entity*) IFC4X1_types[997]));defs.push_back(((entity*) IFC4X1_types[998]));defs.push_back(((entity*) IFC4X1_types[1000]));defs.push_back(((entity*) IFC4X1_types[1003]));
        ((entity*) IFC4X1_types[1002])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[999]));
        ((entity*) IFC4X1_types[998])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1001]));
        ((entity*) IFC4X1_types[1000])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[1002]));defs.push_back(((entity*) IFC4X1_types[1034]));
        ((entity*) IFC4X1_types[996])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1005]));
        ((entity*) IFC4X1_types[1011])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1016]));
        ((entity*) IFC4X1_types[1014])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1020]));
        ((entity*) IFC4X1_types[1021])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[1031]));defs.push_back(((entity*) IFC4X1_types[1032]));
        ((entity*) IFC4X1_types[1047])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1040]));
        ((entity*) IFC4X1_types[1041])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1046]));
        ((entity*) IFC4X1_types[1045])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1064]));
        ((entity*) IFC4X1_types[1063])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1084]));
        ((entity*) IFC4X1_types[1083])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1087]));
        ((entity*) IFC4X1_types[716])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1126]));
        ((entity*) IFC4X1_types[1125])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X1_types[1135]));defs.push_back(((entity*) IFC4X1_types[1136]));defs.push_back(((entity*) IFC4X1_types[1137]));
        ((entity*) IFC4X1_types[1134])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1158]));
        ((entity*) IFC4X1_types[1156])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[1169]));defs.push_back(((entity*) IFC4X1_types[1170]));
        ((entity*) IFC4X1_types[1168])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X1_types[1184]));
        ((entity*) IFC4X1_types[1179])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X1_types[1194]));defs.push_back(((entity*) IFC4X1_types[1196]));
        ((entity*) IFC4X1_types[1193])->set_subtypes(defs);
    }

    std::vector<const declaration*> declarations; declarations.reserve(1201);
    declarations.push_back(IFC4X1_types[0]);
    declarations.push_back(IFC4X1_types[1]);
    declarations.push_back(IFC4X1_types[2]);
    declarations.push_back(IFC4X1_types[3]);
    declarations.push_back(IFC4X1_types[4]);
    declarations.push_back(IFC4X1_types[5]);
    declarations.push_back(IFC4X1_types[6]);
    declarations.push_back(IFC4X1_types[7]);
    declarations.push_back(IFC4X1_types[8]);
    declarations.push_back(IFC4X1_types[9]);
    declarations.push_back(IFC4X1_types[10]);
    declarations.push_back(IFC4X1_types[11]);
    declarations.push_back(IFC4X1_types[12]);
    declarations.push_back(IFC4X1_types[13]);
    declarations.push_back(IFC4X1_types[14]);
    declarations.push_back(IFC4X1_types[15]);
    declarations.push_back(IFC4X1_types[16]);
    declarations.push_back(IFC4X1_types[17]);
    declarations.push_back(IFC4X1_types[18]);
    declarations.push_back(IFC4X1_types[19]);
    declarations.push_back(IFC4X1_types[20]);
    declarations.push_back(IFC4X1_types[21]);
    declarations.push_back(IFC4X1_types[22]);
    declarations.push_back(IFC4X1_types[23]);
    declarations.push_back(IFC4X1_types[24]);
    declarations.push_back(IFC4X1_types[25]);
    declarations.push_back(IFC4X1_types[26]);
    declarations.push_back(IFC4X1_types[27]);
    declarations.push_back(IFC4X1_types[28]);
    declarations.push_back(IFC4X1_types[29]);
    declarations.push_back(IFC4X1_types[30]);
    declarations.push_back(IFC4X1_types[31]);
    declarations.push_back(IFC4X1_types[32]);
    declarations.push_back(IFC4X1_types[33]);
    declarations.push_back(IFC4X1_types[34]);
    declarations.push_back(IFC4X1_types[35]);
    declarations.push_back(IFC4X1_types[36]);
    declarations.push_back(IFC4X1_types[37]);
    declarations.push_back(IFC4X1_types[38]);
    declarations.push_back(IFC4X1_types[39]);
    declarations.push_back(IFC4X1_types[40]);
    declarations.push_back(IFC4X1_types[41]);
    declarations.push_back(IFC4X1_types[42]);
    declarations.push_back(IFC4X1_types[43]);
    declarations.push_back(IFC4X1_types[44]);
    declarations.push_back(IFC4X1_types[45]);
    declarations.push_back(IFC4X1_types[46]);
    declarations.push_back(IFC4X1_types[47]);
    declarations.push_back(IFC4X1_types[48]);
    declarations.push_back(IFC4X1_types[49]);
    declarations.push_back(IFC4X1_types[50]);
    declarations.push_back(IFC4X1_types[51]);
    declarations.push_back(IFC4X1_types[52]);
    declarations.push_back(IFC4X1_types[53]);
    declarations.push_back(IFC4X1_types[54]);
    declarations.push_back(IFC4X1_types[55]);
    declarations.push_back(IFC4X1_types[56]);
    declarations.push_back(IFC4X1_types[57]);
    declarations.push_back(IFC4X1_types[58]);
    declarations.push_back(IFC4X1_types[59]);
    declarations.push_back(IFC4X1_types[60]);
    declarations.push_back(IFC4X1_types[61]);
    declarations.push_back(IFC4X1_types[62]);
    declarations.push_back(IFC4X1_types[63]);
    declarations.push_back(IFC4X1_types[64]);
    declarations.push_back(IFC4X1_types[65]);
    declarations.push_back(IFC4X1_types[66]);
    declarations.push_back(IFC4X1_types[67]);
    declarations.push_back(IFC4X1_types[68]);
    declarations.push_back(IFC4X1_types[69]);
    declarations.push_back(IFC4X1_types[70]);
    declarations.push_back(IFC4X1_types[71]);
    declarations.push_back(IFC4X1_types[72]);
    declarations.push_back(IFC4X1_types[73]);
    declarations.push_back(IFC4X1_types[74]);
    declarations.push_back(IFC4X1_types[75]);
    declarations.push_back(IFC4X1_types[76]);
    declarations.push_back(IFC4X1_types[77]);
    declarations.push_back(IFC4X1_types[78]);
    declarations.push_back(IFC4X1_types[79]);
    declarations.push_back(IFC4X1_types[80]);
    declarations.push_back(IFC4X1_types[81]);
    declarations.push_back(IFC4X1_types[82]);
    declarations.push_back(IFC4X1_types[83]);
    declarations.push_back(IFC4X1_types[84]);
    declarations.push_back(IFC4X1_types[85]);
    declarations.push_back(IFC4X1_types[86]);
    declarations.push_back(IFC4X1_types[87]);
    declarations.push_back(IFC4X1_types[88]);
    declarations.push_back(IFC4X1_types[89]);
    declarations.push_back(IFC4X1_types[90]);
    declarations.push_back(IFC4X1_types[91]);
    declarations.push_back(IFC4X1_types[92]);
    declarations.push_back(IFC4X1_types[93]);
    declarations.push_back(IFC4X1_types[94]);
    declarations.push_back(IFC4X1_types[95]);
    declarations.push_back(IFC4X1_types[96]);
    declarations.push_back(IFC4X1_types[97]);
    declarations.push_back(IFC4X1_types[98]);
    declarations.push_back(IFC4X1_types[99]);
    declarations.push_back(IFC4X1_types[100]);
    declarations.push_back(IFC4X1_types[101]);
    declarations.push_back(IFC4X1_types[102]);
    declarations.push_back(IFC4X1_types[103]);
    declarations.push_back(IFC4X1_types[104]);
    declarations.push_back(IFC4X1_types[105]);
    declarations.push_back(IFC4X1_types[106]);
    declarations.push_back(IFC4X1_types[107]);
    declarations.push_back(IFC4X1_types[108]);
    declarations.push_back(IFC4X1_types[109]);
    declarations.push_back(IFC4X1_types[110]);
    declarations.push_back(IFC4X1_types[111]);
    declarations.push_back(IFC4X1_types[112]);
    declarations.push_back(IFC4X1_types[113]);
    declarations.push_back(IFC4X1_types[114]);
    declarations.push_back(IFC4X1_types[115]);
    declarations.push_back(IFC4X1_types[116]);
    declarations.push_back(IFC4X1_types[117]);
    declarations.push_back(IFC4X1_types[118]);
    declarations.push_back(IFC4X1_types[119]);
    declarations.push_back(IFC4X1_types[120]);
    declarations.push_back(IFC4X1_types[121]);
    declarations.push_back(IFC4X1_types[122]);
    declarations.push_back(IFC4X1_types[123]);
    declarations.push_back(IFC4X1_types[124]);
    declarations.push_back(IFC4X1_types[125]);
    declarations.push_back(IFC4X1_types[126]);
    declarations.push_back(IFC4X1_types[127]);
    declarations.push_back(IFC4X1_types[128]);
    declarations.push_back(IFC4X1_types[129]);
    declarations.push_back(IFC4X1_types[130]);
    declarations.push_back(IFC4X1_types[131]);
    declarations.push_back(IFC4X1_types[132]);
    declarations.push_back(IFC4X1_types[133]);
    declarations.push_back(IFC4X1_types[134]);
    declarations.push_back(IFC4X1_types[135]);
    declarations.push_back(IFC4X1_types[136]);
    declarations.push_back(IFC4X1_types[137]);
    declarations.push_back(IFC4X1_types[138]);
    declarations.push_back(IFC4X1_types[139]);
    declarations.push_back(IFC4X1_types[140]);
    declarations.push_back(IFC4X1_types[141]);
    declarations.push_back(IFC4X1_types[142]);
    declarations.push_back(IFC4X1_types[143]);
    declarations.push_back(IFC4X1_types[144]);
    declarations.push_back(IFC4X1_types[145]);
    declarations.push_back(IFC4X1_types[146]);
    declarations.push_back(IFC4X1_types[147]);
    declarations.push_back(IFC4X1_types[148]);
    declarations.push_back(IFC4X1_types[149]);
    declarations.push_back(IFC4X1_types[150]);
    declarations.push_back(IFC4X1_types[151]);
    declarations.push_back(IFC4X1_types[152]);
    declarations.push_back(IFC4X1_types[153]);
    declarations.push_back(IFC4X1_types[154]);
    declarations.push_back(IFC4X1_types[155]);
    declarations.push_back(IFC4X1_types[156]);
    declarations.push_back(IFC4X1_types[157]);
    declarations.push_back(IFC4X1_types[158]);
    declarations.push_back(IFC4X1_types[159]);
    declarations.push_back(IFC4X1_types[160]);
    declarations.push_back(IFC4X1_types[161]);
    declarations.push_back(IFC4X1_types[162]);
    declarations.push_back(IFC4X1_types[163]);
    declarations.push_back(IFC4X1_types[164]);
    declarations.push_back(IFC4X1_types[165]);
    declarations.push_back(IFC4X1_types[166]);
    declarations.push_back(IFC4X1_types[167]);
    declarations.push_back(IFC4X1_types[168]);
    declarations.push_back(IFC4X1_types[169]);
    declarations.push_back(IFC4X1_types[170]);
    declarations.push_back(IFC4X1_types[171]);
    declarations.push_back(IFC4X1_types[172]);
    declarations.push_back(IFC4X1_types[173]);
    declarations.push_back(IFC4X1_types[174]);
    declarations.push_back(IFC4X1_types[175]);
    declarations.push_back(IFC4X1_types[176]);
    declarations.push_back(IFC4X1_types[177]);
    declarations.push_back(IFC4X1_types[178]);
    declarations.push_back(IFC4X1_types[179]);
    declarations.push_back(IFC4X1_types[180]);
    declarations.push_back(IFC4X1_types[181]);
    declarations.push_back(IFC4X1_types[182]);
    declarations.push_back(IFC4X1_types[183]);
    declarations.push_back(IFC4X1_types[184]);
    declarations.push_back(IFC4X1_types[185]);
    declarations.push_back(IFC4X1_types[186]);
    declarations.push_back(IFC4X1_types[187]);
    declarations.push_back(IFC4X1_types[188]);
    declarations.push_back(IFC4X1_types[189]);
    declarations.push_back(IFC4X1_types[190]);
    declarations.push_back(IFC4X1_types[191]);
    declarations.push_back(IFC4X1_types[192]);
    declarations.push_back(IFC4X1_types[193]);
    declarations.push_back(IFC4X1_types[194]);
    declarations.push_back(IFC4X1_types[195]);
    declarations.push_back(IFC4X1_types[196]);
    declarations.push_back(IFC4X1_types[197]);
    declarations.push_back(IFC4X1_types[198]);
    declarations.push_back(IFC4X1_types[199]);
    declarations.push_back(IFC4X1_types[200]);
    declarations.push_back(IFC4X1_types[201]);
    declarations.push_back(IFC4X1_types[202]);
    declarations.push_back(IFC4X1_types[203]);
    declarations.push_back(IFC4X1_types[204]);
    declarations.push_back(IFC4X1_types[205]);
    declarations.push_back(IFC4X1_types[206]);
    declarations.push_back(IFC4X1_types[207]);
    declarations.push_back(IFC4X1_types[208]);
    declarations.push_back(IFC4X1_types[209]);
    declarations.push_back(IFC4X1_types[210]);
    declarations.push_back(IFC4X1_types[211]);
    declarations.push_back(IFC4X1_types[212]);
    declarations.push_back(IFC4X1_types[213]);
    declarations.push_back(IFC4X1_types[214]);
    declarations.push_back(IFC4X1_types[215]);
    declarations.push_back(IFC4X1_types[216]);
    declarations.push_back(IFC4X1_types[217]);
    declarations.push_back(IFC4X1_types[218]);
    declarations.push_back(IFC4X1_types[219]);
    declarations.push_back(IFC4X1_types[220]);
    declarations.push_back(IFC4X1_types[221]);
    declarations.push_back(IFC4X1_types[222]);
    declarations.push_back(IFC4X1_types[223]);
    declarations.push_back(IFC4X1_types[224]);
    declarations.push_back(IFC4X1_types[225]);
    declarations.push_back(IFC4X1_types[226]);
    declarations.push_back(IFC4X1_types[227]);
    declarations.push_back(IFC4X1_types[228]);
    declarations.push_back(IFC4X1_types[229]);
    declarations.push_back(IFC4X1_types[230]);
    declarations.push_back(IFC4X1_types[231]);
    declarations.push_back(IFC4X1_types[232]);
    declarations.push_back(IFC4X1_types[233]);
    declarations.push_back(IFC4X1_types[234]);
    declarations.push_back(IFC4X1_types[235]);
    declarations.push_back(IFC4X1_types[236]);
    declarations.push_back(IFC4X1_types[237]);
    declarations.push_back(IFC4X1_types[238]);
    declarations.push_back(IFC4X1_types[239]);
    declarations.push_back(IFC4X1_types[240]);
    declarations.push_back(IFC4X1_types[241]);
    declarations.push_back(IFC4X1_types[242]);
    declarations.push_back(IFC4X1_types[243]);
    declarations.push_back(IFC4X1_types[244]);
    declarations.push_back(IFC4X1_types[245]);
    declarations.push_back(IFC4X1_types[246]);
    declarations.push_back(IFC4X1_types[247]);
    declarations.push_back(IFC4X1_types[248]);
    declarations.push_back(IFC4X1_types[249]);
    declarations.push_back(IFC4X1_types[250]);
    declarations.push_back(IFC4X1_types[251]);
    declarations.push_back(IFC4X1_types[252]);
    declarations.push_back(IFC4X1_types[253]);
    declarations.push_back(IFC4X1_types[254]);
    declarations.push_back(IFC4X1_types[255]);
    declarations.push_back(IFC4X1_types[256]);
    declarations.push_back(IFC4X1_types[257]);
    declarations.push_back(IFC4X1_types[258]);
    declarations.push_back(IFC4X1_types[259]);
    declarations.push_back(IFC4X1_types[260]);
    declarations.push_back(IFC4X1_types[261]);
    declarations.push_back(IFC4X1_types[262]);
    declarations.push_back(IFC4X1_types[263]);
    declarations.push_back(IFC4X1_types[264]);
    declarations.push_back(IFC4X1_types[265]);
    declarations.push_back(IFC4X1_types[266]);
    declarations.push_back(IFC4X1_types[267]);
    declarations.push_back(IFC4X1_types[268]);
    declarations.push_back(IFC4X1_types[269]);
    declarations.push_back(IFC4X1_types[270]);
    declarations.push_back(IFC4X1_types[271]);
    declarations.push_back(IFC4X1_types[272]);
    declarations.push_back(IFC4X1_types[273]);
    declarations.push_back(IFC4X1_types[274]);
    declarations.push_back(IFC4X1_types[275]);
    declarations.push_back(IFC4X1_types[276]);
    declarations.push_back(IFC4X1_types[277]);
    declarations.push_back(IFC4X1_types[278]);
    declarations.push_back(IFC4X1_types[279]);
    declarations.push_back(IFC4X1_types[280]);
    declarations.push_back(IFC4X1_types[281]);
    declarations.push_back(IFC4X1_types[282]);
    declarations.push_back(IFC4X1_types[283]);
    declarations.push_back(IFC4X1_types[284]);
    declarations.push_back(IFC4X1_types[285]);
    declarations.push_back(IFC4X1_types[286]);
    declarations.push_back(IFC4X1_types[287]);
    declarations.push_back(IFC4X1_types[288]);
    declarations.push_back(IFC4X1_types[289]);
    declarations.push_back(IFC4X1_types[290]);
    declarations.push_back(IFC4X1_types[291]);
    declarations.push_back(IFC4X1_types[292]);
    declarations.push_back(IFC4X1_types[293]);
    declarations.push_back(IFC4X1_types[294]);
    declarations.push_back(IFC4X1_types[295]);
    declarations.push_back(IFC4X1_types[296]);
    declarations.push_back(IFC4X1_types[297]);
    declarations.push_back(IFC4X1_types[298]);
    declarations.push_back(IFC4X1_types[299]);
    declarations.push_back(IFC4X1_types[300]);
    declarations.push_back(IFC4X1_types[301]);
    declarations.push_back(IFC4X1_types[302]);
    declarations.push_back(IFC4X1_types[303]);
    declarations.push_back(IFC4X1_types[304]);
    declarations.push_back(IFC4X1_types[305]);
    declarations.push_back(IFC4X1_types[306]);
    declarations.push_back(IFC4X1_types[307]);
    declarations.push_back(IFC4X1_types[308]);
    declarations.push_back(IFC4X1_types[309]);
    declarations.push_back(IFC4X1_types[310]);
    declarations.push_back(IFC4X1_types[311]);
    declarations.push_back(IFC4X1_types[312]);
    declarations.push_back(IFC4X1_types[313]);
    declarations.push_back(IFC4X1_types[314]);
    declarations.push_back(IFC4X1_types[315]);
    declarations.push_back(IFC4X1_types[316]);
    declarations.push_back(IFC4X1_types[317]);
    declarations.push_back(IFC4X1_types[318]);
    declarations.push_back(IFC4X1_types[319]);
    declarations.push_back(IFC4X1_types[320]);
    declarations.push_back(IFC4X1_types[321]);
    declarations.push_back(IFC4X1_types[322]);
    declarations.push_back(IFC4X1_types[323]);
    declarations.push_back(IFC4X1_types[324]);
    declarations.push_back(IFC4X1_types[325]);
    declarations.push_back(IFC4X1_types[326]);
    declarations.push_back(IFC4X1_types[327]);
    declarations.push_back(IFC4X1_types[328]);
    declarations.push_back(IFC4X1_types[329]);
    declarations.push_back(IFC4X1_types[330]);
    declarations.push_back(IFC4X1_types[331]);
    declarations.push_back(IFC4X1_types[332]);
    declarations.push_back(IFC4X1_types[333]);
    declarations.push_back(IFC4X1_types[334]);
    declarations.push_back(IFC4X1_types[335]);
    declarations.push_back(IFC4X1_types[336]);
    declarations.push_back(IFC4X1_types[337]);
    declarations.push_back(IFC4X1_types[338]);
    declarations.push_back(IFC4X1_types[339]);
    declarations.push_back(IFC4X1_types[340]);
    declarations.push_back(IFC4X1_types[341]);
    declarations.push_back(IFC4X1_types[342]);
    declarations.push_back(IFC4X1_types[343]);
    declarations.push_back(IFC4X1_types[344]);
    declarations.push_back(IFC4X1_types[345]);
    declarations.push_back(IFC4X1_types[346]);
    declarations.push_back(IFC4X1_types[347]);
    declarations.push_back(IFC4X1_types[348]);
    declarations.push_back(IFC4X1_types[349]);
    declarations.push_back(IFC4X1_types[350]);
    declarations.push_back(IFC4X1_types[351]);
    declarations.push_back(IFC4X1_types[352]);
    declarations.push_back(IFC4X1_types[353]);
    declarations.push_back(IFC4X1_types[354]);
    declarations.push_back(IFC4X1_types[355]);
    declarations.push_back(IFC4X1_types[356]);
    declarations.push_back(IFC4X1_types[357]);
    declarations.push_back(IFC4X1_types[358]);
    declarations.push_back(IFC4X1_types[359]);
    declarations.push_back(IFC4X1_types[360]);
    declarations.push_back(IFC4X1_types[361]);
    declarations.push_back(IFC4X1_types[362]);
    declarations.push_back(IFC4X1_types[363]);
    declarations.push_back(IFC4X1_types[364]);
    declarations.push_back(IFC4X1_types[365]);
    declarations.push_back(IFC4X1_types[366]);
    declarations.push_back(IFC4X1_types[367]);
    declarations.push_back(IFC4X1_types[368]);
    declarations.push_back(IFC4X1_types[369]);
    declarations.push_back(IFC4X1_types[370]);
    declarations.push_back(IFC4X1_types[371]);
    declarations.push_back(IFC4X1_types[372]);
    declarations.push_back(IFC4X1_types[373]);
    declarations.push_back(IFC4X1_types[374]);
    declarations.push_back(IFC4X1_types[375]);
    declarations.push_back(IFC4X1_types[376]);
    declarations.push_back(IFC4X1_types[377]);
    declarations.push_back(IFC4X1_types[378]);
    declarations.push_back(IFC4X1_types[379]);
    declarations.push_back(IFC4X1_types[380]);
    declarations.push_back(IFC4X1_types[381]);
    declarations.push_back(IFC4X1_types[382]);
    declarations.push_back(IFC4X1_types[383]);
    declarations.push_back(IFC4X1_types[384]);
    declarations.push_back(IFC4X1_types[385]);
    declarations.push_back(IFC4X1_types[386]);
    declarations.push_back(IFC4X1_types[387]);
    declarations.push_back(IFC4X1_types[388]);
    declarations.push_back(IFC4X1_types[389]);
    declarations.push_back(IFC4X1_types[390]);
    declarations.push_back(IFC4X1_types[391]);
    declarations.push_back(IFC4X1_types[392]);
    declarations.push_back(IFC4X1_types[393]);
    declarations.push_back(IFC4X1_types[394]);
    declarations.push_back(IFC4X1_types[395]);
    declarations.push_back(IFC4X1_types[396]);
    declarations.push_back(IFC4X1_types[397]);
    declarations.push_back(IFC4X1_types[398]);
    declarations.push_back(IFC4X1_types[399]);
    declarations.push_back(IFC4X1_types[400]);
    declarations.push_back(IFC4X1_types[401]);
    declarations.push_back(IFC4X1_types[402]);
    declarations.push_back(IFC4X1_types[403]);
    declarations.push_back(IFC4X1_types[404]);
    declarations.push_back(IFC4X1_types[405]);
    declarations.push_back(IFC4X1_types[406]);
    declarations.push_back(IFC4X1_types[407]);
    declarations.push_back(IFC4X1_types[408]);
    declarations.push_back(IFC4X1_types[409]);
    declarations.push_back(IFC4X1_types[410]);
    declarations.push_back(IFC4X1_types[411]);
    declarations.push_back(IFC4X1_types[412]);
    declarations.push_back(IFC4X1_types[413]);
    declarations.push_back(IFC4X1_types[414]);
    declarations.push_back(IFC4X1_types[415]);
    declarations.push_back(IFC4X1_types[416]);
    declarations.push_back(IFC4X1_types[417]);
    declarations.push_back(IFC4X1_types[418]);
    declarations.push_back(IFC4X1_types[419]);
    declarations.push_back(IFC4X1_types[420]);
    declarations.push_back(IFC4X1_types[421]);
    declarations.push_back(IFC4X1_types[422]);
    declarations.push_back(IFC4X1_types[423]);
    declarations.push_back(IFC4X1_types[424]);
    declarations.push_back(IFC4X1_types[425]);
    declarations.push_back(IFC4X1_types[426]);
    declarations.push_back(IFC4X1_types[427]);
    declarations.push_back(IFC4X1_types[428]);
    declarations.push_back(IFC4X1_types[429]);
    declarations.push_back(IFC4X1_types[430]);
    declarations.push_back(IFC4X1_types[431]);
    declarations.push_back(IFC4X1_types[432]);
    declarations.push_back(IFC4X1_types[433]);
    declarations.push_back(IFC4X1_types[434]);
    declarations.push_back(IFC4X1_types[435]);
    declarations.push_back(IFC4X1_types[436]);
    declarations.push_back(IFC4X1_types[437]);
    declarations.push_back(IFC4X1_types[438]);
    declarations.push_back(IFC4X1_types[439]);
    declarations.push_back(IFC4X1_types[440]);
    declarations.push_back(IFC4X1_types[441]);
    declarations.push_back(IFC4X1_types[442]);
    declarations.push_back(IFC4X1_types[443]);
    declarations.push_back(IFC4X1_types[444]);
    declarations.push_back(IFC4X1_types[445]);
    declarations.push_back(IFC4X1_types[446]);
    declarations.push_back(IFC4X1_types[447]);
    declarations.push_back(IFC4X1_types[448]);
    declarations.push_back(IFC4X1_types[449]);
    declarations.push_back(IFC4X1_types[450]);
    declarations.push_back(IFC4X1_types[451]);
    declarations.push_back(IFC4X1_types[452]);
    declarations.push_back(IFC4X1_types[453]);
    declarations.push_back(IFC4X1_types[454]);
    declarations.push_back(IFC4X1_types[455]);
    declarations.push_back(IFC4X1_types[456]);
    declarations.push_back(IFC4X1_types[457]);
    declarations.push_back(IFC4X1_types[458]);
    declarations.push_back(IFC4X1_types[459]);
    declarations.push_back(IFC4X1_types[460]);
    declarations.push_back(IFC4X1_types[461]);
    declarations.push_back(IFC4X1_types[462]);
    declarations.push_back(IFC4X1_types[463]);
    declarations.push_back(IFC4X1_types[464]);
    declarations.push_back(IFC4X1_types[465]);
    declarations.push_back(IFC4X1_types[466]);
    declarations.push_back(IFC4X1_types[467]);
    declarations.push_back(IFC4X1_types[468]);
    declarations.push_back(IFC4X1_types[469]);
    declarations.push_back(IFC4X1_types[470]);
    declarations.push_back(IFC4X1_types[471]);
    declarations.push_back(IFC4X1_types[472]);
    declarations.push_back(IFC4X1_types[473]);
    declarations.push_back(IFC4X1_types[474]);
    declarations.push_back(IFC4X1_types[475]);
    declarations.push_back(IFC4X1_types[476]);
    declarations.push_back(IFC4X1_types[477]);
    declarations.push_back(IFC4X1_types[478]);
    declarations.push_back(IFC4X1_types[479]);
    declarations.push_back(IFC4X1_types[480]);
    declarations.push_back(IFC4X1_types[481]);
    declarations.push_back(IFC4X1_types[482]);
    declarations.push_back(IFC4X1_types[483]);
    declarations.push_back(IFC4X1_types[484]);
    declarations.push_back(IFC4X1_types[485]);
    declarations.push_back(IFC4X1_types[486]);
    declarations.push_back(IFC4X1_types[487]);
    declarations.push_back(IFC4X1_types[488]);
    declarations.push_back(IFC4X1_types[489]);
    declarations.push_back(IFC4X1_types[490]);
    declarations.push_back(IFC4X1_types[491]);
    declarations.push_back(IFC4X1_types[492]);
    declarations.push_back(IFC4X1_types[493]);
    declarations.push_back(IFC4X1_types[494]);
    declarations.push_back(IFC4X1_types[495]);
    declarations.push_back(IFC4X1_types[496]);
    declarations.push_back(IFC4X1_types[497]);
    declarations.push_back(IFC4X1_types[498]);
    declarations.push_back(IFC4X1_types[499]);
    declarations.push_back(IFC4X1_types[500]);
    declarations.push_back(IFC4X1_types[501]);
    declarations.push_back(IFC4X1_types[502]);
    declarations.push_back(IFC4X1_types[503]);
    declarations.push_back(IFC4X1_types[504]);
    declarations.push_back(IFC4X1_types[505]);
    declarations.push_back(IFC4X1_types[506]);
    declarations.push_back(IFC4X1_types[507]);
    declarations.push_back(IFC4X1_types[508]);
    declarations.push_back(IFC4X1_types[509]);
    declarations.push_back(IFC4X1_types[510]);
    declarations.push_back(IFC4X1_types[511]);
    declarations.push_back(IFC4X1_types[512]);
    declarations.push_back(IFC4X1_types[513]);
    declarations.push_back(IFC4X1_types[514]);
    declarations.push_back(IFC4X1_types[515]);
    declarations.push_back(IFC4X1_types[516]);
    declarations.push_back(IFC4X1_types[517]);
    declarations.push_back(IFC4X1_types[518]);
    declarations.push_back(IFC4X1_types[519]);
    declarations.push_back(IFC4X1_types[520]);
    declarations.push_back(IFC4X1_types[521]);
    declarations.push_back(IFC4X1_types[522]);
    declarations.push_back(IFC4X1_types[523]);
    declarations.push_back(IFC4X1_types[524]);
    declarations.push_back(IFC4X1_types[525]);
    declarations.push_back(IFC4X1_types[526]);
    declarations.push_back(IFC4X1_types[527]);
    declarations.push_back(IFC4X1_types[528]);
    declarations.push_back(IFC4X1_types[529]);
    declarations.push_back(IFC4X1_types[530]);
    declarations.push_back(IFC4X1_types[531]);
    declarations.push_back(IFC4X1_types[532]);
    declarations.push_back(IFC4X1_types[533]);
    declarations.push_back(IFC4X1_types[534]);
    declarations.push_back(IFC4X1_types[535]);
    declarations.push_back(IFC4X1_types[536]);
    declarations.push_back(IFC4X1_types[537]);
    declarations.push_back(IFC4X1_types[538]);
    declarations.push_back(IFC4X1_types[539]);
    declarations.push_back(IFC4X1_types[540]);
    declarations.push_back(IFC4X1_types[541]);
    declarations.push_back(IFC4X1_types[542]);
    declarations.push_back(IFC4X1_types[543]);
    declarations.push_back(IFC4X1_types[544]);
    declarations.push_back(IFC4X1_types[545]);
    declarations.push_back(IFC4X1_types[546]);
    declarations.push_back(IFC4X1_types[547]);
    declarations.push_back(IFC4X1_types[548]);
    declarations.push_back(IFC4X1_types[549]);
    declarations.push_back(IFC4X1_types[550]);
    declarations.push_back(IFC4X1_types[551]);
    declarations.push_back(IFC4X1_types[552]);
    declarations.push_back(IFC4X1_types[553]);
    declarations.push_back(IFC4X1_types[554]);
    declarations.push_back(IFC4X1_types[555]);
    declarations.push_back(IFC4X1_types[556]);
    declarations.push_back(IFC4X1_types[557]);
    declarations.push_back(IFC4X1_types[558]);
    declarations.push_back(IFC4X1_types[559]);
    declarations.push_back(IFC4X1_types[560]);
    declarations.push_back(IFC4X1_types[561]);
    declarations.push_back(IFC4X1_types[562]);
    declarations.push_back(IFC4X1_types[563]);
    declarations.push_back(IFC4X1_types[564]);
    declarations.push_back(IFC4X1_types[565]);
    declarations.push_back(IFC4X1_types[566]);
    declarations.push_back(IFC4X1_types[567]);
    declarations.push_back(IFC4X1_types[568]);
    declarations.push_back(IFC4X1_types[569]);
    declarations.push_back(IFC4X1_types[570]);
    declarations.push_back(IFC4X1_types[571]);
    declarations.push_back(IFC4X1_types[572]);
    declarations.push_back(IFC4X1_types[573]);
    declarations.push_back(IFC4X1_types[574]);
    declarations.push_back(IFC4X1_types[575]);
    declarations.push_back(IFC4X1_types[576]);
    declarations.push_back(IFC4X1_types[577]);
    declarations.push_back(IFC4X1_types[578]);
    declarations.push_back(IFC4X1_types[579]);
    declarations.push_back(IFC4X1_types[580]);
    declarations.push_back(IFC4X1_types[581]);
    declarations.push_back(IFC4X1_types[582]);
    declarations.push_back(IFC4X1_types[583]);
    declarations.push_back(IFC4X1_types[584]);
    declarations.push_back(IFC4X1_types[585]);
    declarations.push_back(IFC4X1_types[586]);
    declarations.push_back(IFC4X1_types[587]);
    declarations.push_back(IFC4X1_types[588]);
    declarations.push_back(IFC4X1_types[589]);
    declarations.push_back(IFC4X1_types[590]);
    declarations.push_back(IFC4X1_types[591]);
    declarations.push_back(IFC4X1_types[592]);
    declarations.push_back(IFC4X1_types[593]);
    declarations.push_back(IFC4X1_types[594]);
    declarations.push_back(IFC4X1_types[595]);
    declarations.push_back(IFC4X1_types[596]);
    declarations.push_back(IFC4X1_types[597]);
    declarations.push_back(IFC4X1_types[598]);
    declarations.push_back(IFC4X1_types[599]);
    declarations.push_back(IFC4X1_types[600]);
    declarations.push_back(IFC4X1_types[601]);
    declarations.push_back(IFC4X1_types[602]);
    declarations.push_back(IFC4X1_types[603]);
    declarations.push_back(IFC4X1_types[604]);
    declarations.push_back(IFC4X1_types[605]);
    declarations.push_back(IFC4X1_types[606]);
    declarations.push_back(IFC4X1_types[607]);
    declarations.push_back(IFC4X1_types[608]);
    declarations.push_back(IFC4X1_types[609]);
    declarations.push_back(IFC4X1_types[610]);
    declarations.push_back(IFC4X1_types[611]);
    declarations.push_back(IFC4X1_types[612]);
    declarations.push_back(IFC4X1_types[613]);
    declarations.push_back(IFC4X1_types[614]);
    declarations.push_back(IFC4X1_types[615]);
    declarations.push_back(IFC4X1_types[616]);
    declarations.push_back(IFC4X1_types[617]);
    declarations.push_back(IFC4X1_types[618]);
    declarations.push_back(IFC4X1_types[619]);
    declarations.push_back(IFC4X1_types[620]);
    declarations.push_back(IFC4X1_types[621]);
    declarations.push_back(IFC4X1_types[622]);
    declarations.push_back(IFC4X1_types[623]);
    declarations.push_back(IFC4X1_types[624]);
    declarations.push_back(IFC4X1_types[625]);
    declarations.push_back(IFC4X1_types[626]);
    declarations.push_back(IFC4X1_types[627]);
    declarations.push_back(IFC4X1_types[628]);
    declarations.push_back(IFC4X1_types[629]);
    declarations.push_back(IFC4X1_types[630]);
    declarations.push_back(IFC4X1_types[631]);
    declarations.push_back(IFC4X1_types[632]);
    declarations.push_back(IFC4X1_types[633]);
    declarations.push_back(IFC4X1_types[634]);
    declarations.push_back(IFC4X1_types[635]);
    declarations.push_back(IFC4X1_types[636]);
    declarations.push_back(IFC4X1_types[637]);
    declarations.push_back(IFC4X1_types[638]);
    declarations.push_back(IFC4X1_types[639]);
    declarations.push_back(IFC4X1_types[640]);
    declarations.push_back(IFC4X1_types[641]);
    declarations.push_back(IFC4X1_types[642]);
    declarations.push_back(IFC4X1_types[643]);
    declarations.push_back(IFC4X1_types[644]);
    declarations.push_back(IFC4X1_types[645]);
    declarations.push_back(IFC4X1_types[646]);
    declarations.push_back(IFC4X1_types[647]);
    declarations.push_back(IFC4X1_types[648]);
    declarations.push_back(IFC4X1_types[649]);
    declarations.push_back(IFC4X1_types[650]);
    declarations.push_back(IFC4X1_types[651]);
    declarations.push_back(IFC4X1_types[652]);
    declarations.push_back(IFC4X1_types[653]);
    declarations.push_back(IFC4X1_types[654]);
    declarations.push_back(IFC4X1_types[655]);
    declarations.push_back(IFC4X1_types[656]);
    declarations.push_back(IFC4X1_types[657]);
    declarations.push_back(IFC4X1_types[658]);
    declarations.push_back(IFC4X1_types[659]);
    declarations.push_back(IFC4X1_types[660]);
    declarations.push_back(IFC4X1_types[661]);
    declarations.push_back(IFC4X1_types[662]);
    declarations.push_back(IFC4X1_types[663]);
    declarations.push_back(IFC4X1_types[664]);
    declarations.push_back(IFC4X1_types[665]);
    declarations.push_back(IFC4X1_types[666]);
    declarations.push_back(IFC4X1_types[667]);
    declarations.push_back(IFC4X1_types[668]);
    declarations.push_back(IFC4X1_types[669]);
    declarations.push_back(IFC4X1_types[670]);
    declarations.push_back(IFC4X1_types[671]);
    declarations.push_back(IFC4X1_types[672]);
    declarations.push_back(IFC4X1_types[673]);
    declarations.push_back(IFC4X1_types[674]);
    declarations.push_back(IFC4X1_types[675]);
    declarations.push_back(IFC4X1_types[676]);
    declarations.push_back(IFC4X1_types[677]);
    declarations.push_back(IFC4X1_types[678]);
    declarations.push_back(IFC4X1_types[679]);
    declarations.push_back(IFC4X1_types[680]);
    declarations.push_back(IFC4X1_types[681]);
    declarations.push_back(IFC4X1_types[682]);
    declarations.push_back(IFC4X1_types[683]);
    declarations.push_back(IFC4X1_types[684]);
    declarations.push_back(IFC4X1_types[685]);
    declarations.push_back(IFC4X1_types[686]);
    declarations.push_back(IFC4X1_types[687]);
    declarations.push_back(IFC4X1_types[688]);
    declarations.push_back(IFC4X1_types[689]);
    declarations.push_back(IFC4X1_types[690]);
    declarations.push_back(IFC4X1_types[691]);
    declarations.push_back(IFC4X1_types[692]);
    declarations.push_back(IFC4X1_types[693]);
    declarations.push_back(IFC4X1_types[694]);
    declarations.push_back(IFC4X1_types[695]);
    declarations.push_back(IFC4X1_types[696]);
    declarations.push_back(IFC4X1_types[697]);
    declarations.push_back(IFC4X1_types[698]);
    declarations.push_back(IFC4X1_types[699]);
    declarations.push_back(IFC4X1_types[700]);
    declarations.push_back(IFC4X1_types[701]);
    declarations.push_back(IFC4X1_types[702]);
    declarations.push_back(IFC4X1_types[703]);
    declarations.push_back(IFC4X1_types[704]);
    declarations.push_back(IFC4X1_types[705]);
    declarations.push_back(IFC4X1_types[706]);
    declarations.push_back(IFC4X1_types[707]);
    declarations.push_back(IFC4X1_types[708]);
    declarations.push_back(IFC4X1_types[709]);
    declarations.push_back(IFC4X1_types[710]);
    declarations.push_back(IFC4X1_types[711]);
    declarations.push_back(IFC4X1_types[712]);
    declarations.push_back(IFC4X1_types[713]);
    declarations.push_back(IFC4X1_types[714]);
    declarations.push_back(IFC4X1_types[715]);
    declarations.push_back(IFC4X1_types[716]);
    declarations.push_back(IFC4X1_types[717]);
    declarations.push_back(IFC4X1_types[718]);
    declarations.push_back(IFC4X1_types[719]);
    declarations.push_back(IFC4X1_types[720]);
    declarations.push_back(IFC4X1_types[721]);
    declarations.push_back(IFC4X1_types[722]);
    declarations.push_back(IFC4X1_types[723]);
    declarations.push_back(IFC4X1_types[724]);
    declarations.push_back(IFC4X1_types[725]);
    declarations.push_back(IFC4X1_types[726]);
    declarations.push_back(IFC4X1_types[727]);
    declarations.push_back(IFC4X1_types[728]);
    declarations.push_back(IFC4X1_types[729]);
    declarations.push_back(IFC4X1_types[730]);
    declarations.push_back(IFC4X1_types[731]);
    declarations.push_back(IFC4X1_types[732]);
    declarations.push_back(IFC4X1_types[733]);
    declarations.push_back(IFC4X1_types[734]);
    declarations.push_back(IFC4X1_types[735]);
    declarations.push_back(IFC4X1_types[736]);
    declarations.push_back(IFC4X1_types[737]);
    declarations.push_back(IFC4X1_types[738]);
    declarations.push_back(IFC4X1_types[739]);
    declarations.push_back(IFC4X1_types[740]);
    declarations.push_back(IFC4X1_types[741]);
    declarations.push_back(IFC4X1_types[742]);
    declarations.push_back(IFC4X1_types[743]);
    declarations.push_back(IFC4X1_types[744]);
    declarations.push_back(IFC4X1_types[745]);
    declarations.push_back(IFC4X1_types[746]);
    declarations.push_back(IFC4X1_types[747]);
    declarations.push_back(IFC4X1_types[748]);
    declarations.push_back(IFC4X1_types[749]);
    declarations.push_back(IFC4X1_types[750]);
    declarations.push_back(IFC4X1_types[751]);
    declarations.push_back(IFC4X1_types[752]);
    declarations.push_back(IFC4X1_types[753]);
    declarations.push_back(IFC4X1_types[754]);
    declarations.push_back(IFC4X1_types[755]);
    declarations.push_back(IFC4X1_types[756]);
    declarations.push_back(IFC4X1_types[757]);
    declarations.push_back(IFC4X1_types[758]);
    declarations.push_back(IFC4X1_types[759]);
    declarations.push_back(IFC4X1_types[760]);
    declarations.push_back(IFC4X1_types[761]);
    declarations.push_back(IFC4X1_types[762]);
    declarations.push_back(IFC4X1_types[763]);
    declarations.push_back(IFC4X1_types[764]);
    declarations.push_back(IFC4X1_types[765]);
    declarations.push_back(IFC4X1_types[766]);
    declarations.push_back(IFC4X1_types[767]);
    declarations.push_back(IFC4X1_types[768]);
    declarations.push_back(IFC4X1_types[769]);
    declarations.push_back(IFC4X1_types[770]);
    declarations.push_back(IFC4X1_types[771]);
    declarations.push_back(IFC4X1_types[772]);
    declarations.push_back(IFC4X1_types[773]);
    declarations.push_back(IFC4X1_types[774]);
    declarations.push_back(IFC4X1_types[775]);
    declarations.push_back(IFC4X1_types[776]);
    declarations.push_back(IFC4X1_types[777]);
    declarations.push_back(IFC4X1_types[778]);
    declarations.push_back(IFC4X1_types[779]);
    declarations.push_back(IFC4X1_types[780]);
    declarations.push_back(IFC4X1_types[781]);
    declarations.push_back(IFC4X1_types[782]);
    declarations.push_back(IFC4X1_types[783]);
    declarations.push_back(IFC4X1_types[784]);
    declarations.push_back(IFC4X1_types[785]);
    declarations.push_back(IFC4X1_types[786]);
    declarations.push_back(IFC4X1_types[787]);
    declarations.push_back(IFC4X1_types[788]);
    declarations.push_back(IFC4X1_types[789]);
    declarations.push_back(IFC4X1_types[790]);
    declarations.push_back(IFC4X1_types[791]);
    declarations.push_back(IFC4X1_types[792]);
    declarations.push_back(IFC4X1_types[793]);
    declarations.push_back(IFC4X1_types[794]);
    declarations.push_back(IFC4X1_types[795]);
    declarations.push_back(IFC4X1_types[796]);
    declarations.push_back(IFC4X1_types[797]);
    declarations.push_back(IFC4X1_types[798]);
    declarations.push_back(IFC4X1_types[799]);
    declarations.push_back(IFC4X1_types[800]);
    declarations.push_back(IFC4X1_types[801]);
    declarations.push_back(IFC4X1_types[802]);
    declarations.push_back(IFC4X1_types[803]);
    declarations.push_back(IFC4X1_types[804]);
    declarations.push_back(IFC4X1_types[805]);
    declarations.push_back(IFC4X1_types[806]);
    declarations.push_back(IFC4X1_types[807]);
    declarations.push_back(IFC4X1_types[808]);
    declarations.push_back(IFC4X1_types[809]);
    declarations.push_back(IFC4X1_types[810]);
    declarations.push_back(IFC4X1_types[811]);
    declarations.push_back(IFC4X1_types[812]);
    declarations.push_back(IFC4X1_types[813]);
    declarations.push_back(IFC4X1_types[814]);
    declarations.push_back(IFC4X1_types[815]);
    declarations.push_back(IFC4X1_types[816]);
    declarations.push_back(IFC4X1_types[817]);
    declarations.push_back(IFC4X1_types[818]);
    declarations.push_back(IFC4X1_types[819]);
    declarations.push_back(IFC4X1_types[820]);
    declarations.push_back(IFC4X1_types[821]);
    declarations.push_back(IFC4X1_types[822]);
    declarations.push_back(IFC4X1_types[823]);
    declarations.push_back(IFC4X1_types[824]);
    declarations.push_back(IFC4X1_types[825]);
    declarations.push_back(IFC4X1_types[826]);
    declarations.push_back(IFC4X1_types[827]);
    declarations.push_back(IFC4X1_types[828]);
    declarations.push_back(IFC4X1_types[829]);
    declarations.push_back(IFC4X1_types[830]);
    declarations.push_back(IFC4X1_types[831]);
    declarations.push_back(IFC4X1_types[832]);
    declarations.push_back(IFC4X1_types[833]);
    declarations.push_back(IFC4X1_types[834]);
    declarations.push_back(IFC4X1_types[835]);
    declarations.push_back(IFC4X1_types[836]);
    declarations.push_back(IFC4X1_types[837]);
    declarations.push_back(IFC4X1_types[838]);
    declarations.push_back(IFC4X1_types[839]);
    declarations.push_back(IFC4X1_types[840]);
    declarations.push_back(IFC4X1_types[841]);
    declarations.push_back(IFC4X1_types[842]);
    declarations.push_back(IFC4X1_types[843]);
    declarations.push_back(IFC4X1_types[844]);
    declarations.push_back(IFC4X1_types[845]);
    declarations.push_back(IFC4X1_types[846]);
    declarations.push_back(IFC4X1_types[847]);
    declarations.push_back(IFC4X1_types[848]);
    declarations.push_back(IFC4X1_types[849]);
    declarations.push_back(IFC4X1_types[850]);
    declarations.push_back(IFC4X1_types[851]);
    declarations.push_back(IFC4X1_types[852]);
    declarations.push_back(IFC4X1_types[853]);
    declarations.push_back(IFC4X1_types[854]);
    declarations.push_back(IFC4X1_types[855]);
    declarations.push_back(IFC4X1_types[856]);
    declarations.push_back(IFC4X1_types[857]);
    declarations.push_back(IFC4X1_types[858]);
    declarations.push_back(IFC4X1_types[859]);
    declarations.push_back(IFC4X1_types[860]);
    declarations.push_back(IFC4X1_types[861]);
    declarations.push_back(IFC4X1_types[862]);
    declarations.push_back(IFC4X1_types[863]);
    declarations.push_back(IFC4X1_types[864]);
    declarations.push_back(IFC4X1_types[865]);
    declarations.push_back(IFC4X1_types[866]);
    declarations.push_back(IFC4X1_types[867]);
    declarations.push_back(IFC4X1_types[868]);
    declarations.push_back(IFC4X1_types[869]);
    declarations.push_back(IFC4X1_types[870]);
    declarations.push_back(IFC4X1_types[871]);
    declarations.push_back(IFC4X1_types[872]);
    declarations.push_back(IFC4X1_types[873]);
    declarations.push_back(IFC4X1_types[874]);
    declarations.push_back(IFC4X1_types[875]);
    declarations.push_back(IFC4X1_types[876]);
    declarations.push_back(IFC4X1_types[877]);
    declarations.push_back(IFC4X1_types[878]);
    declarations.push_back(IFC4X1_types[879]);
    declarations.push_back(IFC4X1_types[880]);
    declarations.push_back(IFC4X1_types[881]);
    declarations.push_back(IFC4X1_types[882]);
    declarations.push_back(IFC4X1_types[883]);
    declarations.push_back(IFC4X1_types[884]);
    declarations.push_back(IFC4X1_types[885]);
    declarations.push_back(IFC4X1_types[886]);
    declarations.push_back(IFC4X1_types[887]);
    declarations.push_back(IFC4X1_types[888]);
    declarations.push_back(IFC4X1_types[889]);
    declarations.push_back(IFC4X1_types[890]);
    declarations.push_back(IFC4X1_types[891]);
    declarations.push_back(IFC4X1_types[892]);
    declarations.push_back(IFC4X1_types[893]);
    declarations.push_back(IFC4X1_types[894]);
    declarations.push_back(IFC4X1_types[895]);
    declarations.push_back(IFC4X1_types[896]);
    declarations.push_back(IFC4X1_types[897]);
    declarations.push_back(IFC4X1_types[898]);
    declarations.push_back(IFC4X1_types[899]);
    declarations.push_back(IFC4X1_types[900]);
    declarations.push_back(IFC4X1_types[901]);
    declarations.push_back(IFC4X1_types[902]);
    declarations.push_back(IFC4X1_types[903]);
    declarations.push_back(IFC4X1_types[904]);
    declarations.push_back(IFC4X1_types[905]);
    declarations.push_back(IFC4X1_types[906]);
    declarations.push_back(IFC4X1_types[907]);
    declarations.push_back(IFC4X1_types[908]);
    declarations.push_back(IFC4X1_types[909]);
    declarations.push_back(IFC4X1_types[910]);
    declarations.push_back(IFC4X1_types[911]);
    declarations.push_back(IFC4X1_types[912]);
    declarations.push_back(IFC4X1_types[913]);
    declarations.push_back(IFC4X1_types[914]);
    declarations.push_back(IFC4X1_types[915]);
    declarations.push_back(IFC4X1_types[916]);
    declarations.push_back(IFC4X1_types[917]);
    declarations.push_back(IFC4X1_types[918]);
    declarations.push_back(IFC4X1_types[919]);
    declarations.push_back(IFC4X1_types[920]);
    declarations.push_back(IFC4X1_types[921]);
    declarations.push_back(IFC4X1_types[922]);
    declarations.push_back(IFC4X1_types[923]);
    declarations.push_back(IFC4X1_types[924]);
    declarations.push_back(IFC4X1_types[925]);
    declarations.push_back(IFC4X1_types[926]);
    declarations.push_back(IFC4X1_types[927]);
    declarations.push_back(IFC4X1_types[928]);
    declarations.push_back(IFC4X1_types[929]);
    declarations.push_back(IFC4X1_types[930]);
    declarations.push_back(IFC4X1_types[931]);
    declarations.push_back(IFC4X1_types[932]);
    declarations.push_back(IFC4X1_types[933]);
    declarations.push_back(IFC4X1_types[934]);
    declarations.push_back(IFC4X1_types[935]);
    declarations.push_back(IFC4X1_types[936]);
    declarations.push_back(IFC4X1_types[937]);
    declarations.push_back(IFC4X1_types[938]);
    declarations.push_back(IFC4X1_types[939]);
    declarations.push_back(IFC4X1_types[940]);
    declarations.push_back(IFC4X1_types[941]);
    declarations.push_back(IFC4X1_types[942]);
    declarations.push_back(IFC4X1_types[943]);
    declarations.push_back(IFC4X1_types[944]);
    declarations.push_back(IFC4X1_types[945]);
    declarations.push_back(IFC4X1_types[946]);
    declarations.push_back(IFC4X1_types[947]);
    declarations.push_back(IFC4X1_types[948]);
    declarations.push_back(IFC4X1_types[949]);
    declarations.push_back(IFC4X1_types[950]);
    declarations.push_back(IFC4X1_types[951]);
    declarations.push_back(IFC4X1_types[952]);
    declarations.push_back(IFC4X1_types[953]);
    declarations.push_back(IFC4X1_types[954]);
    declarations.push_back(IFC4X1_types[955]);
    declarations.push_back(IFC4X1_types[956]);
    declarations.push_back(IFC4X1_types[957]);
    declarations.push_back(IFC4X1_types[958]);
    declarations.push_back(IFC4X1_types[959]);
    declarations.push_back(IFC4X1_types[960]);
    declarations.push_back(IFC4X1_types[961]);
    declarations.push_back(IFC4X1_types[962]);
    declarations.push_back(IFC4X1_types[963]);
    declarations.push_back(IFC4X1_types[964]);
    declarations.push_back(IFC4X1_types[965]);
    declarations.push_back(IFC4X1_types[966]);
    declarations.push_back(IFC4X1_types[967]);
    declarations.push_back(IFC4X1_types[968]);
    declarations.push_back(IFC4X1_types[969]);
    declarations.push_back(IFC4X1_types[970]);
    declarations.push_back(IFC4X1_types[971]);
    declarations.push_back(IFC4X1_types[972]);
    declarations.push_back(IFC4X1_types[973]);
    declarations.push_back(IFC4X1_types[974]);
    declarations.push_back(IFC4X1_types[975]);
    declarations.push_back(IFC4X1_types[976]);
    declarations.push_back(IFC4X1_types[977]);
    declarations.push_back(IFC4X1_types[978]);
    declarations.push_back(IFC4X1_types[979]);
    declarations.push_back(IFC4X1_types[980]);
    declarations.push_back(IFC4X1_types[981]);
    declarations.push_back(IFC4X1_types[982]);
    declarations.push_back(IFC4X1_types[983]);
    declarations.push_back(IFC4X1_types[984]);
    declarations.push_back(IFC4X1_types[985]);
    declarations.push_back(IFC4X1_types[986]);
    declarations.push_back(IFC4X1_types[987]);
    declarations.push_back(IFC4X1_types[988]);
    declarations.push_back(IFC4X1_types[989]);
    declarations.push_back(IFC4X1_types[990]);
    declarations.push_back(IFC4X1_types[991]);
    declarations.push_back(IFC4X1_types[992]);
    declarations.push_back(IFC4X1_types[993]);
    declarations.push_back(IFC4X1_types[994]);
    declarations.push_back(IFC4X1_types[995]);
    declarations.push_back(IFC4X1_types[996]);
    declarations.push_back(IFC4X1_types[997]);
    declarations.push_back(IFC4X1_types[998]);
    declarations.push_back(IFC4X1_types[999]);
    declarations.push_back(IFC4X1_types[1000]);
    declarations.push_back(IFC4X1_types[1001]);
    declarations.push_back(IFC4X1_types[1002]);
    declarations.push_back(IFC4X1_types[1003]);
    declarations.push_back(IFC4X1_types[1004]);
    declarations.push_back(IFC4X1_types[1005]);
    declarations.push_back(IFC4X1_types[1006]);
    declarations.push_back(IFC4X1_types[1007]);
    declarations.push_back(IFC4X1_types[1008]);
    declarations.push_back(IFC4X1_types[1009]);
    declarations.push_back(IFC4X1_types[1010]);
    declarations.push_back(IFC4X1_types[1011]);
    declarations.push_back(IFC4X1_types[1012]);
    declarations.push_back(IFC4X1_types[1013]);
    declarations.push_back(IFC4X1_types[1014]);
    declarations.push_back(IFC4X1_types[1015]);
    declarations.push_back(IFC4X1_types[1016]);
    declarations.push_back(IFC4X1_types[1017]);
    declarations.push_back(IFC4X1_types[1018]);
    declarations.push_back(IFC4X1_types[1019]);
    declarations.push_back(IFC4X1_types[1020]);
    declarations.push_back(IFC4X1_types[1021]);
    declarations.push_back(IFC4X1_types[1022]);
    declarations.push_back(IFC4X1_types[1023]);
    declarations.push_back(IFC4X1_types[1024]);
    declarations.push_back(IFC4X1_types[1025]);
    declarations.push_back(IFC4X1_types[1026]);
    declarations.push_back(IFC4X1_types[1027]);
    declarations.push_back(IFC4X1_types[1028]);
    declarations.push_back(IFC4X1_types[1029]);
    declarations.push_back(IFC4X1_types[1030]);
    declarations.push_back(IFC4X1_types[1031]);
    declarations.push_back(IFC4X1_types[1032]);
    declarations.push_back(IFC4X1_types[1033]);
    declarations.push_back(IFC4X1_types[1034]);
    declarations.push_back(IFC4X1_types[1035]);
    declarations.push_back(IFC4X1_types[1036]);
    declarations.push_back(IFC4X1_types[1037]);
    declarations.push_back(IFC4X1_types[1038]);
    declarations.push_back(IFC4X1_types[1039]);
    declarations.push_back(IFC4X1_types[1040]);
    declarations.push_back(IFC4X1_types[1041]);
    declarations.push_back(IFC4X1_types[1042]);
    declarations.push_back(IFC4X1_types[1043]);
    declarations.push_back(IFC4X1_types[1044]);
    declarations.push_back(IFC4X1_types[1045]);
    declarations.push_back(IFC4X1_types[1046]);
    declarations.push_back(IFC4X1_types[1047]);
    declarations.push_back(IFC4X1_types[1048]);
    declarations.push_back(IFC4X1_types[1049]);
    declarations.push_back(IFC4X1_types[1050]);
    declarations.push_back(IFC4X1_types[1051]);
    declarations.push_back(IFC4X1_types[1052]);
    declarations.push_back(IFC4X1_types[1053]);
    declarations.push_back(IFC4X1_types[1054]);
    declarations.push_back(IFC4X1_types[1055]);
    declarations.push_back(IFC4X1_types[1056]);
    declarations.push_back(IFC4X1_types[1057]);
    declarations.push_back(IFC4X1_types[1058]);
    declarations.push_back(IFC4X1_types[1059]);
    declarations.push_back(IFC4X1_types[1060]);
    declarations.push_back(IFC4X1_types[1061]);
    declarations.push_back(IFC4X1_types[1062]);
    declarations.push_back(IFC4X1_types[1063]);
    declarations.push_back(IFC4X1_types[1064]);
    declarations.push_back(IFC4X1_types[1065]);
    declarations.push_back(IFC4X1_types[1066]);
    declarations.push_back(IFC4X1_types[1067]);
    declarations.push_back(IFC4X1_types[1068]);
    declarations.push_back(IFC4X1_types[1069]);
    declarations.push_back(IFC4X1_types[1070]);
    declarations.push_back(IFC4X1_types[1071]);
    declarations.push_back(IFC4X1_types[1072]);
    declarations.push_back(IFC4X1_types[1073]);
    declarations.push_back(IFC4X1_types[1074]);
    declarations.push_back(IFC4X1_types[1075]);
    declarations.push_back(IFC4X1_types[1076]);
    declarations.push_back(IFC4X1_types[1077]);
    declarations.push_back(IFC4X1_types[1078]);
    declarations.push_back(IFC4X1_types[1079]);
    declarations.push_back(IFC4X1_types[1080]);
    declarations.push_back(IFC4X1_types[1081]);
    declarations.push_back(IFC4X1_types[1082]);
    declarations.push_back(IFC4X1_types[1083]);
    declarations.push_back(IFC4X1_types[1084]);
    declarations.push_back(IFC4X1_types[1085]);
    declarations.push_back(IFC4X1_types[1086]);
    declarations.push_back(IFC4X1_types[1087]);
    declarations.push_back(IFC4X1_types[1088]);
    declarations.push_back(IFC4X1_types[1089]);
    declarations.push_back(IFC4X1_types[1090]);
    declarations.push_back(IFC4X1_types[1091]);
    declarations.push_back(IFC4X1_types[1092]);
    declarations.push_back(IFC4X1_types[1093]);
    declarations.push_back(IFC4X1_types[1094]);
    declarations.push_back(IFC4X1_types[1095]);
    declarations.push_back(IFC4X1_types[1096]);
    declarations.push_back(IFC4X1_types[1097]);
    declarations.push_back(IFC4X1_types[1098]);
    declarations.push_back(IFC4X1_types[1099]);
    declarations.push_back(IFC4X1_types[1100]);
    declarations.push_back(IFC4X1_types[1101]);
    declarations.push_back(IFC4X1_types[1102]);
    declarations.push_back(IFC4X1_types[1103]);
    declarations.push_back(IFC4X1_types[1104]);
    declarations.push_back(IFC4X1_types[1105]);
    declarations.push_back(IFC4X1_types[1106]);
    declarations.push_back(IFC4X1_types[1107]);
    declarations.push_back(IFC4X1_types[1108]);
    declarations.push_back(IFC4X1_types[1109]);
    declarations.push_back(IFC4X1_types[1110]);
    declarations.push_back(IFC4X1_types[1111]);
    declarations.push_back(IFC4X1_types[1112]);
    declarations.push_back(IFC4X1_types[1113]);
    declarations.push_back(IFC4X1_types[1114]);
    declarations.push_back(IFC4X1_types[1115]);
    declarations.push_back(IFC4X1_types[1116]);
    declarations.push_back(IFC4X1_types[1117]);
    declarations.push_back(IFC4X1_types[1118]);
    declarations.push_back(IFC4X1_types[1119]);
    declarations.push_back(IFC4X1_types[1120]);
    declarations.push_back(IFC4X1_types[1121]);
    declarations.push_back(IFC4X1_types[1122]);
    declarations.push_back(IFC4X1_types[1123]);
    declarations.push_back(IFC4X1_types[1124]);
    declarations.push_back(IFC4X1_types[1125]);
    declarations.push_back(IFC4X1_types[1126]);
    declarations.push_back(IFC4X1_types[1127]);
    declarations.push_back(IFC4X1_types[1128]);
    declarations.push_back(IFC4X1_types[1129]);
    declarations.push_back(IFC4X1_types[1130]);
    declarations.push_back(IFC4X1_types[1131]);
    declarations.push_back(IFC4X1_types[1132]);
    declarations.push_back(IFC4X1_types[1133]);
    declarations.push_back(IFC4X1_types[1134]);
    declarations.push_back(IFC4X1_types[1135]);
    declarations.push_back(IFC4X1_types[1136]);
    declarations.push_back(IFC4X1_types[1137]);
    declarations.push_back(IFC4X1_types[1138]);
    declarations.push_back(IFC4X1_types[1139]);
    declarations.push_back(IFC4X1_types[1140]);
    declarations.push_back(IFC4X1_types[1141]);
    declarations.push_back(IFC4X1_types[1142]);
    declarations.push_back(IFC4X1_types[1143]);
    declarations.push_back(IFC4X1_types[1144]);
    declarations.push_back(IFC4X1_types[1145]);
    declarations.push_back(IFC4X1_types[1146]);
    declarations.push_back(IFC4X1_types[1147]);
    declarations.push_back(IFC4X1_types[1148]);
    declarations.push_back(IFC4X1_types[1149]);
    declarations.push_back(IFC4X1_types[1150]);
    declarations.push_back(IFC4X1_types[1151]);
    declarations.push_back(IFC4X1_types[1152]);
    declarations.push_back(IFC4X1_types[1153]);
    declarations.push_back(IFC4X1_types[1154]);
    declarations.push_back(IFC4X1_types[1155]);
    declarations.push_back(IFC4X1_types[1156]);
    declarations.push_back(IFC4X1_types[1157]);
    declarations.push_back(IFC4X1_types[1158]);
    declarations.push_back(IFC4X1_types[1159]);
    declarations.push_back(IFC4X1_types[1160]);
    declarations.push_back(IFC4X1_types[1161]);
    declarations.push_back(IFC4X1_types[1162]);
    declarations.push_back(IFC4X1_types[1163]);
    declarations.push_back(IFC4X1_types[1164]);
    declarations.push_back(IFC4X1_types[1165]);
    declarations.push_back(IFC4X1_types[1166]);
    declarations.push_back(IFC4X1_types[1167]);
    declarations.push_back(IFC4X1_types[1168]);
    declarations.push_back(IFC4X1_types[1169]);
    declarations.push_back(IFC4X1_types[1170]);
    declarations.push_back(IFC4X1_types[1171]);
    declarations.push_back(IFC4X1_types[1172]);
    declarations.push_back(IFC4X1_types[1173]);
    declarations.push_back(IFC4X1_types[1174]);
    declarations.push_back(IFC4X1_types[1175]);
    declarations.push_back(IFC4X1_types[1176]);
    declarations.push_back(IFC4X1_types[1177]);
    declarations.push_back(IFC4X1_types[1178]);
    declarations.push_back(IFC4X1_types[1179]);
    declarations.push_back(IFC4X1_types[1180]);
    declarations.push_back(IFC4X1_types[1181]);
    declarations.push_back(IFC4X1_types[1182]);
    declarations.push_back(IFC4X1_types[1183]);
    declarations.push_back(IFC4X1_types[1184]);
    declarations.push_back(IFC4X1_types[1185]);
    declarations.push_back(IFC4X1_types[1186]);
    declarations.push_back(IFC4X1_types[1187]);
    declarations.push_back(IFC4X1_types[1188]);
    declarations.push_back(IFC4X1_types[1189]);
    declarations.push_back(IFC4X1_types[1190]);
    declarations.push_back(IFC4X1_types[1191]);
    declarations.push_back(IFC4X1_types[1192]);
    declarations.push_back(IFC4X1_types[1193]);
    declarations.push_back(IFC4X1_types[1194]);
    declarations.push_back(IFC4X1_types[1195]);
    declarations.push_back(IFC4X1_types[1196]);
    declarations.push_back(IFC4X1_types[1197]);
    declarations.push_back(IFC4X1_types[1198]);
    declarations.push_back(IFC4X1_types[1199]);
    declarations.push_back(IFC4X1_types[1200]);
    return new schema_definition("IFC4X1", declarations, new IFC4X1_instance_factory());
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

