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
 * This file has been generated from IFC4x2.exp. Do not make modifications      *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Ifc4x2.h"

using namespace IfcParse;

declaration* IFC4X2_types[1223] = {nullptr};

class IFC4X2_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new ::Ifc4x2::IfcAbsorbedDoseMeasure(data);
            case 1: return new ::Ifc4x2::IfcAccelerationMeasure(data);
            case 2: return new ::Ifc4x2::IfcActionRequest(data);
            case 3: return new ::Ifc4x2::IfcActionRequestTypeEnum(data);
            case 4: return new ::Ifc4x2::IfcActionSourceTypeEnum(data);
            case 5: return new ::Ifc4x2::IfcActionTypeEnum(data);
            case 6: return new ::Ifc4x2::IfcActor(data);
            case 7: return new ::Ifc4x2::IfcActorRole(data);
            case 9: return new ::Ifc4x2::IfcActuator(data);
            case 10: return new ::Ifc4x2::IfcActuatorType(data);
            case 11: return new ::Ifc4x2::IfcActuatorTypeEnum(data);
            case 12: return new ::Ifc4x2::IfcAddress(data);
            case 13: return new ::Ifc4x2::IfcAddressTypeEnum(data);
            case 14: return new ::Ifc4x2::IfcAdvancedBrep(data);
            case 15: return new ::Ifc4x2::IfcAdvancedBrepWithVoids(data);
            case 16: return new ::Ifc4x2::IfcAdvancedFace(data);
            case 17: return new ::Ifc4x2::IfcAirTerminal(data);
            case 18: return new ::Ifc4x2::IfcAirTerminalBox(data);
            case 19: return new ::Ifc4x2::IfcAirTerminalBoxType(data);
            case 20: return new ::Ifc4x2::IfcAirTerminalBoxTypeEnum(data);
            case 21: return new ::Ifc4x2::IfcAirTerminalType(data);
            case 22: return new ::Ifc4x2::IfcAirTerminalTypeEnum(data);
            case 23: return new ::Ifc4x2::IfcAirToAirHeatRecovery(data);
            case 24: return new ::Ifc4x2::IfcAirToAirHeatRecoveryType(data);
            case 25: return new ::Ifc4x2::IfcAirToAirHeatRecoveryTypeEnum(data);
            case 26: return new ::Ifc4x2::IfcAlarm(data);
            case 27: return new ::Ifc4x2::IfcAlarmType(data);
            case 28: return new ::Ifc4x2::IfcAlarmTypeEnum(data);
            case 29: return new ::Ifc4x2::IfcAlignment(data);
            case 30: return new ::Ifc4x2::IfcAlignment2DHorizontal(data);
            case 31: return new ::Ifc4x2::IfcAlignment2DHorizontalSegment(data);
            case 32: return new ::Ifc4x2::IfcAlignment2DSegment(data);
            case 33: return new ::Ifc4x2::IfcAlignment2DVerSegCircularArc(data);
            case 34: return new ::Ifc4x2::IfcAlignment2DVerSegLine(data);
            case 35: return new ::Ifc4x2::IfcAlignment2DVerSegParabolicArc(data);
            case 36: return new ::Ifc4x2::IfcAlignment2DVertical(data);
            case 37: return new ::Ifc4x2::IfcAlignment2DVerticalSegment(data);
            case 38: return new ::Ifc4x2::IfcAlignmentCurve(data);
            case 39: return new ::Ifc4x2::IfcAlignmentTypeEnum(data);
            case 40: return new ::Ifc4x2::IfcAmountOfSubstanceMeasure(data);
            case 41: return new ::Ifc4x2::IfcAnalysisModelTypeEnum(data);
            case 42: return new ::Ifc4x2::IfcAnalysisTheoryTypeEnum(data);
            case 43: return new ::Ifc4x2::IfcAngularVelocityMeasure(data);
            case 44: return new ::Ifc4x2::IfcAnnotation(data);
            case 45: return new ::Ifc4x2::IfcAnnotationFillArea(data);
            case 46: return new ::Ifc4x2::IfcApplication(data);
            case 47: return new ::Ifc4x2::IfcAppliedValue(data);
            case 49: return new ::Ifc4x2::IfcApproval(data);
            case 50: return new ::Ifc4x2::IfcApprovalRelationship(data);
            case 51: return new ::Ifc4x2::IfcArbitraryClosedProfileDef(data);
            case 52: return new ::Ifc4x2::IfcArbitraryOpenProfileDef(data);
            case 53: return new ::Ifc4x2::IfcArbitraryProfileDefWithVoids(data);
            case 54: return new ::Ifc4x2::IfcArcIndex(data);
            case 55: return new ::Ifc4x2::IfcAreaDensityMeasure(data);
            case 56: return new ::Ifc4x2::IfcAreaMeasure(data);
            case 57: return new ::Ifc4x2::IfcArithmeticOperatorEnum(data);
            case 58: return new ::Ifc4x2::IfcAssemblyPlaceEnum(data);
            case 59: return new ::Ifc4x2::IfcAsset(data);
            case 60: return new ::Ifc4x2::IfcAsymmetricIShapeProfileDef(data);
            case 61: return new ::Ifc4x2::IfcAudioVisualAppliance(data);
            case 62: return new ::Ifc4x2::IfcAudioVisualApplianceType(data);
            case 63: return new ::Ifc4x2::IfcAudioVisualApplianceTypeEnum(data);
            case 64: return new ::Ifc4x2::IfcAxis1Placement(data);
            case 66: return new ::Ifc4x2::IfcAxis2Placement2D(data);
            case 67: return new ::Ifc4x2::IfcAxis2Placement3D(data);
            case 68: return new ::Ifc4x2::IfcBeam(data);
            case 69: return new ::Ifc4x2::IfcBeamStandardCase(data);
            case 70: return new ::Ifc4x2::IfcBeamType(data);
            case 71: return new ::Ifc4x2::IfcBeamTypeEnum(data);
            case 72: return new ::Ifc4x2::IfcBearing(data);
            case 73: return new ::Ifc4x2::IfcBearingType(data);
            case 74: return new ::Ifc4x2::IfcBearingTypeDisplacementEnum(data);
            case 75: return new ::Ifc4x2::IfcBearingTypeEnum(data);
            case 76: return new ::Ifc4x2::IfcBenchmarkEnum(data);
            case 78: return new ::Ifc4x2::IfcBinary(data);
            case 79: return new ::Ifc4x2::IfcBlobTexture(data);
            case 80: return new ::Ifc4x2::IfcBlock(data);
            case 81: return new ::Ifc4x2::IfcBoiler(data);
            case 82: return new ::Ifc4x2::IfcBoilerType(data);
            case 83: return new ::Ifc4x2::IfcBoilerTypeEnum(data);
            case 84: return new ::Ifc4x2::IfcBoolean(data);
            case 85: return new ::Ifc4x2::IfcBooleanClippingResult(data);
            case 87: return new ::Ifc4x2::IfcBooleanOperator(data);
            case 88: return new ::Ifc4x2::IfcBooleanResult(data);
            case 89: return new ::Ifc4x2::IfcBoundaryCondition(data);
            case 90: return new ::Ifc4x2::IfcBoundaryCurve(data);
            case 91: return new ::Ifc4x2::IfcBoundaryEdgeCondition(data);
            case 92: return new ::Ifc4x2::IfcBoundaryFaceCondition(data);
            case 93: return new ::Ifc4x2::IfcBoundaryNodeCondition(data);
            case 94: return new ::Ifc4x2::IfcBoundaryNodeConditionWarping(data);
            case 95: return new ::Ifc4x2::IfcBoundedCurve(data);
            case 96: return new ::Ifc4x2::IfcBoundedSurface(data);
            case 97: return new ::Ifc4x2::IfcBoundingBox(data);
            case 98: return new ::Ifc4x2::IfcBoxAlignment(data);
            case 99: return new ::Ifc4x2::IfcBoxedHalfSpace(data);
            case 100: return new ::Ifc4x2::IfcBridge(data);
            case 101: return new ::Ifc4x2::IfcBridgePart(data);
            case 102: return new ::Ifc4x2::IfcBridgePartTypeEnum(data);
            case 103: return new ::Ifc4x2::IfcBridgeTypeEnum(data);
            case 104: return new ::Ifc4x2::IfcBSplineCurve(data);
            case 105: return new ::Ifc4x2::IfcBSplineCurveForm(data);
            case 106: return new ::Ifc4x2::IfcBSplineCurveWithKnots(data);
            case 107: return new ::Ifc4x2::IfcBSplineSurface(data);
            case 108: return new ::Ifc4x2::IfcBSplineSurfaceForm(data);
            case 109: return new ::Ifc4x2::IfcBSplineSurfaceWithKnots(data);
            case 110: return new ::Ifc4x2::IfcBuilding(data);
            case 111: return new ::Ifc4x2::IfcBuildingElement(data);
            case 112: return new ::Ifc4x2::IfcBuildingElementPart(data);
            case 113: return new ::Ifc4x2::IfcBuildingElementPartType(data);
            case 114: return new ::Ifc4x2::IfcBuildingElementPartTypeEnum(data);
            case 115: return new ::Ifc4x2::IfcBuildingElementProxy(data);
            case 116: return new ::Ifc4x2::IfcBuildingElementProxyType(data);
            case 117: return new ::Ifc4x2::IfcBuildingElementProxyTypeEnum(data);
            case 118: return new ::Ifc4x2::IfcBuildingElementType(data);
            case 119: return new ::Ifc4x2::IfcBuildingStorey(data);
            case 120: return new ::Ifc4x2::IfcBuildingSystem(data);
            case 121: return new ::Ifc4x2::IfcBuildingSystemTypeEnum(data);
            case 122: return new ::Ifc4x2::IfcBurner(data);
            case 123: return new ::Ifc4x2::IfcBurnerType(data);
            case 124: return new ::Ifc4x2::IfcBurnerTypeEnum(data);
            case 125: return new ::Ifc4x2::IfcCableCarrierFitting(data);
            case 126: return new ::Ifc4x2::IfcCableCarrierFittingType(data);
            case 127: return new ::Ifc4x2::IfcCableCarrierFittingTypeEnum(data);
            case 128: return new ::Ifc4x2::IfcCableCarrierSegment(data);
            case 129: return new ::Ifc4x2::IfcCableCarrierSegmentType(data);
            case 130: return new ::Ifc4x2::IfcCableCarrierSegmentTypeEnum(data);
            case 131: return new ::Ifc4x2::IfcCableFitting(data);
            case 132: return new ::Ifc4x2::IfcCableFittingType(data);
            case 133: return new ::Ifc4x2::IfcCableFittingTypeEnum(data);
            case 134: return new ::Ifc4x2::IfcCableSegment(data);
            case 135: return new ::Ifc4x2::IfcCableSegmentType(data);
            case 136: return new ::Ifc4x2::IfcCableSegmentTypeEnum(data);
            case 137: return new ::Ifc4x2::IfcCaissonFoundation(data);
            case 138: return new ::Ifc4x2::IfcCaissonFoundationType(data);
            case 139: return new ::Ifc4x2::IfcCaissonFoundationTypeEnum(data);
            case 140: return new ::Ifc4x2::IfcCardinalPointReference(data);
            case 141: return new ::Ifc4x2::IfcCartesianPoint(data);
            case 142: return new ::Ifc4x2::IfcCartesianPointList(data);
            case 143: return new ::Ifc4x2::IfcCartesianPointList2D(data);
            case 144: return new ::Ifc4x2::IfcCartesianPointList3D(data);
            case 145: return new ::Ifc4x2::IfcCartesianTransformationOperator(data);
            case 146: return new ::Ifc4x2::IfcCartesianTransformationOperator2D(data);
            case 147: return new ::Ifc4x2::IfcCartesianTransformationOperator2DnonUniform(data);
            case 148: return new ::Ifc4x2::IfcCartesianTransformationOperator3D(data);
            case 149: return new ::Ifc4x2::IfcCartesianTransformationOperator3DnonUniform(data);
            case 150: return new ::Ifc4x2::IfcCenterLineProfileDef(data);
            case 151: return new ::Ifc4x2::IfcChangeActionEnum(data);
            case 152: return new ::Ifc4x2::IfcChiller(data);
            case 153: return new ::Ifc4x2::IfcChillerType(data);
            case 154: return new ::Ifc4x2::IfcChillerTypeEnum(data);
            case 155: return new ::Ifc4x2::IfcChimney(data);
            case 156: return new ::Ifc4x2::IfcChimneyType(data);
            case 157: return new ::Ifc4x2::IfcChimneyTypeEnum(data);
            case 158: return new ::Ifc4x2::IfcCircle(data);
            case 159: return new ::Ifc4x2::IfcCircleHollowProfileDef(data);
            case 160: return new ::Ifc4x2::IfcCircleProfileDef(data);
            case 161: return new ::Ifc4x2::IfcCircularArcSegment2D(data);
            case 162: return new ::Ifc4x2::IfcCivilElement(data);
            case 163: return new ::Ifc4x2::IfcCivilElementType(data);
            case 164: return new ::Ifc4x2::IfcClassification(data);
            case 165: return new ::Ifc4x2::IfcClassificationReference(data);
            case 168: return new ::Ifc4x2::IfcClosedShell(data);
            case 169: return new ::Ifc4x2::IfcCoil(data);
            case 170: return new ::Ifc4x2::IfcCoilType(data);
            case 171: return new ::Ifc4x2::IfcCoilTypeEnum(data);
            case 174: return new ::Ifc4x2::IfcColourRgb(data);
            case 175: return new ::Ifc4x2::IfcColourRgbList(data);
            case 176: return new ::Ifc4x2::IfcColourSpecification(data);
            case 177: return new ::Ifc4x2::IfcColumn(data);
            case 178: return new ::Ifc4x2::IfcColumnStandardCase(data);
            case 179: return new ::Ifc4x2::IfcColumnType(data);
            case 180: return new ::Ifc4x2::IfcColumnTypeEnum(data);
            case 181: return new ::Ifc4x2::IfcCommunicationsAppliance(data);
            case 182: return new ::Ifc4x2::IfcCommunicationsApplianceType(data);
            case 183: return new ::Ifc4x2::IfcCommunicationsApplianceTypeEnum(data);
            case 184: return new ::Ifc4x2::IfcComplexNumber(data);
            case 185: return new ::Ifc4x2::IfcComplexProperty(data);
            case 186: return new ::Ifc4x2::IfcComplexPropertyTemplate(data);
            case 187: return new ::Ifc4x2::IfcComplexPropertyTemplateTypeEnum(data);
            case 188: return new ::Ifc4x2::IfcCompositeCurve(data);
            case 189: return new ::Ifc4x2::IfcCompositeCurveOnSurface(data);
            case 190: return new ::Ifc4x2::IfcCompositeCurveSegment(data);
            case 191: return new ::Ifc4x2::IfcCompositeProfileDef(data);
            case 192: return new ::Ifc4x2::IfcCompoundPlaneAngleMeasure(data);
            case 193: return new ::Ifc4x2::IfcCompressor(data);
            case 194: return new ::Ifc4x2::IfcCompressorType(data);
            case 195: return new ::Ifc4x2::IfcCompressorTypeEnum(data);
            case 196: return new ::Ifc4x2::IfcCondenser(data);
            case 197: return new ::Ifc4x2::IfcCondenserType(data);
            case 198: return new ::Ifc4x2::IfcCondenserTypeEnum(data);
            case 199: return new ::Ifc4x2::IfcConic(data);
            case 200: return new ::Ifc4x2::IfcConnectedFaceSet(data);
            case 201: return new ::Ifc4x2::IfcConnectionCurveGeometry(data);
            case 202: return new ::Ifc4x2::IfcConnectionGeometry(data);
            case 203: return new ::Ifc4x2::IfcConnectionPointEccentricity(data);
            case 204: return new ::Ifc4x2::IfcConnectionPointGeometry(data);
            case 205: return new ::Ifc4x2::IfcConnectionSurfaceGeometry(data);
            case 206: return new ::Ifc4x2::IfcConnectionTypeEnum(data);
            case 207: return new ::Ifc4x2::IfcConnectionVolumeGeometry(data);
            case 208: return new ::Ifc4x2::IfcConstraint(data);
            case 209: return new ::Ifc4x2::IfcConstraintEnum(data);
            case 210: return new ::Ifc4x2::IfcConstructionEquipmentResource(data);
            case 211: return new ::Ifc4x2::IfcConstructionEquipmentResourceType(data);
            case 212: return new ::Ifc4x2::IfcConstructionEquipmentResourceTypeEnum(data);
            case 213: return new ::Ifc4x2::IfcConstructionMaterialResource(data);
            case 214: return new ::Ifc4x2::IfcConstructionMaterialResourceType(data);
            case 215: return new ::Ifc4x2::IfcConstructionMaterialResourceTypeEnum(data);
            case 216: return new ::Ifc4x2::IfcConstructionProductResource(data);
            case 217: return new ::Ifc4x2::IfcConstructionProductResourceType(data);
            case 218: return new ::Ifc4x2::IfcConstructionProductResourceTypeEnum(data);
            case 219: return new ::Ifc4x2::IfcConstructionResource(data);
            case 220: return new ::Ifc4x2::IfcConstructionResourceType(data);
            case 221: return new ::Ifc4x2::IfcContext(data);
            case 222: return new ::Ifc4x2::IfcContextDependentMeasure(data);
            case 223: return new ::Ifc4x2::IfcContextDependentUnit(data);
            case 224: return new ::Ifc4x2::IfcControl(data);
            case 225: return new ::Ifc4x2::IfcController(data);
            case 226: return new ::Ifc4x2::IfcControllerType(data);
            case 227: return new ::Ifc4x2::IfcControllerTypeEnum(data);
            case 228: return new ::Ifc4x2::IfcConversionBasedUnit(data);
            case 229: return new ::Ifc4x2::IfcConversionBasedUnitWithOffset(data);
            case 230: return new ::Ifc4x2::IfcCooledBeam(data);
            case 231: return new ::Ifc4x2::IfcCooledBeamType(data);
            case 232: return new ::Ifc4x2::IfcCooledBeamTypeEnum(data);
            case 233: return new ::Ifc4x2::IfcCoolingTower(data);
            case 234: return new ::Ifc4x2::IfcCoolingTowerType(data);
            case 235: return new ::Ifc4x2::IfcCoolingTowerTypeEnum(data);
            case 236: return new ::Ifc4x2::IfcCoordinateOperation(data);
            case 237: return new ::Ifc4x2::IfcCoordinateReferenceSystem(data);
            case 239: return new ::Ifc4x2::IfcCostItem(data);
            case 240: return new ::Ifc4x2::IfcCostItemTypeEnum(data);
            case 241: return new ::Ifc4x2::IfcCostSchedule(data);
            case 242: return new ::Ifc4x2::IfcCostScheduleTypeEnum(data);
            case 243: return new ::Ifc4x2::IfcCostValue(data);
            case 244: return new ::Ifc4x2::IfcCountMeasure(data);
            case 245: return new ::Ifc4x2::IfcCovering(data);
            case 246: return new ::Ifc4x2::IfcCoveringType(data);
            case 247: return new ::Ifc4x2::IfcCoveringTypeEnum(data);
            case 248: return new ::Ifc4x2::IfcCrewResource(data);
            case 249: return new ::Ifc4x2::IfcCrewResourceType(data);
            case 250: return new ::Ifc4x2::IfcCrewResourceTypeEnum(data);
            case 251: return new ::Ifc4x2::IfcCsgPrimitive3D(data);
            case 253: return new ::Ifc4x2::IfcCsgSolid(data);
            case 254: return new ::Ifc4x2::IfcCShapeProfileDef(data);
            case 255: return new ::Ifc4x2::IfcCurrencyRelationship(data);
            case 256: return new ::Ifc4x2::IfcCurtainWall(data);
            case 257: return new ::Ifc4x2::IfcCurtainWallType(data);
            case 258: return new ::Ifc4x2::IfcCurtainWallTypeEnum(data);
            case 259: return new ::Ifc4x2::IfcCurvatureMeasure(data);
            case 260: return new ::Ifc4x2::IfcCurve(data);
            case 261: return new ::Ifc4x2::IfcCurveBoundedPlane(data);
            case 262: return new ::Ifc4x2::IfcCurveBoundedSurface(data);
            case 264: return new ::Ifc4x2::IfcCurveInterpolationEnum(data);
            case 267: return new ::Ifc4x2::IfcCurveSegment2D(data);
            case 268: return new ::Ifc4x2::IfcCurveStyle(data);
            case 269: return new ::Ifc4x2::IfcCurveStyleFont(data);
            case 270: return new ::Ifc4x2::IfcCurveStyleFontAndScaling(data);
            case 271: return new ::Ifc4x2::IfcCurveStyleFontPattern(data);
            case 273: return new ::Ifc4x2::IfcCylindricalSurface(data);
            case 274: return new ::Ifc4x2::IfcDamper(data);
            case 275: return new ::Ifc4x2::IfcDamperType(data);
            case 276: return new ::Ifc4x2::IfcDamperTypeEnum(data);
            case 277: return new ::Ifc4x2::IfcDataOriginEnum(data);
            case 278: return new ::Ifc4x2::IfcDate(data);
            case 279: return new ::Ifc4x2::IfcDateTime(data);
            case 280: return new ::Ifc4x2::IfcDayInMonthNumber(data);
            case 281: return new ::Ifc4x2::IfcDayInWeekNumber(data);
            case 282: return new ::Ifc4x2::IfcDeepFoundation(data);
            case 283: return new ::Ifc4x2::IfcDeepFoundationType(data);
            case 286: return new ::Ifc4x2::IfcDerivedProfileDef(data);
            case 287: return new ::Ifc4x2::IfcDerivedUnit(data);
            case 288: return new ::Ifc4x2::IfcDerivedUnitElement(data);
            case 289: return new ::Ifc4x2::IfcDerivedUnitEnum(data);
            case 290: return new ::Ifc4x2::IfcDescriptiveMeasure(data);
            case 291: return new ::Ifc4x2::IfcDimensionalExponents(data);
            case 292: return new ::Ifc4x2::IfcDimensionCount(data);
            case 293: return new ::Ifc4x2::IfcDirection(data);
            case 294: return new ::Ifc4x2::IfcDirectionSenseEnum(data);
            case 295: return new ::Ifc4x2::IfcDiscreteAccessory(data);
            case 296: return new ::Ifc4x2::IfcDiscreteAccessoryType(data);
            case 297: return new ::Ifc4x2::IfcDiscreteAccessoryTypeEnum(data);
            case 298: return new ::Ifc4x2::IfcDistanceExpression(data);
            case 299: return new ::Ifc4x2::IfcDistributionChamberElement(data);
            case 300: return new ::Ifc4x2::IfcDistributionChamberElementType(data);
            case 301: return new ::Ifc4x2::IfcDistributionChamberElementTypeEnum(data);
            case 302: return new ::Ifc4x2::IfcDistributionCircuit(data);
            case 303: return new ::Ifc4x2::IfcDistributionControlElement(data);
            case 304: return new ::Ifc4x2::IfcDistributionControlElementType(data);
            case 305: return new ::Ifc4x2::IfcDistributionElement(data);
            case 306: return new ::Ifc4x2::IfcDistributionElementType(data);
            case 307: return new ::Ifc4x2::IfcDistributionFlowElement(data);
            case 308: return new ::Ifc4x2::IfcDistributionFlowElementType(data);
            case 309: return new ::Ifc4x2::IfcDistributionPort(data);
            case 310: return new ::Ifc4x2::IfcDistributionPortTypeEnum(data);
            case 311: return new ::Ifc4x2::IfcDistributionSystem(data);
            case 312: return new ::Ifc4x2::IfcDistributionSystemEnum(data);
            case 313: return new ::Ifc4x2::IfcDocumentConfidentialityEnum(data);
            case 314: return new ::Ifc4x2::IfcDocumentInformation(data);
            case 315: return new ::Ifc4x2::IfcDocumentInformationRelationship(data);
            case 316: return new ::Ifc4x2::IfcDocumentReference(data);
            case 318: return new ::Ifc4x2::IfcDocumentStatusEnum(data);
            case 319: return new ::Ifc4x2::IfcDoor(data);
            case 320: return new ::Ifc4x2::IfcDoorLiningProperties(data);
            case 321: return new ::Ifc4x2::IfcDoorPanelOperationEnum(data);
            case 322: return new ::Ifc4x2::IfcDoorPanelPositionEnum(data);
            case 323: return new ::Ifc4x2::IfcDoorPanelProperties(data);
            case 324: return new ::Ifc4x2::IfcDoorStandardCase(data);
            case 325: return new ::Ifc4x2::IfcDoorStyle(data);
            case 326: return new ::Ifc4x2::IfcDoorStyleConstructionEnum(data);
            case 327: return new ::Ifc4x2::IfcDoorStyleOperationEnum(data);
            case 328: return new ::Ifc4x2::IfcDoorType(data);
            case 329: return new ::Ifc4x2::IfcDoorTypeEnum(data);
            case 330: return new ::Ifc4x2::IfcDoorTypeOperationEnum(data);
            case 331: return new ::Ifc4x2::IfcDoseEquivalentMeasure(data);
            case 332: return new ::Ifc4x2::IfcDraughtingPreDefinedColour(data);
            case 333: return new ::Ifc4x2::IfcDraughtingPreDefinedCurveFont(data);
            case 334: return new ::Ifc4x2::IfcDuctFitting(data);
            case 335: return new ::Ifc4x2::IfcDuctFittingType(data);
            case 336: return new ::Ifc4x2::IfcDuctFittingTypeEnum(data);
            case 337: return new ::Ifc4x2::IfcDuctSegment(data);
            case 338: return new ::Ifc4x2::IfcDuctSegmentType(data);
            case 339: return new ::Ifc4x2::IfcDuctSegmentTypeEnum(data);
            case 340: return new ::Ifc4x2::IfcDuctSilencer(data);
            case 341: return new ::Ifc4x2::IfcDuctSilencerType(data);
            case 342: return new ::Ifc4x2::IfcDuctSilencerTypeEnum(data);
            case 343: return new ::Ifc4x2::IfcDuration(data);
            case 344: return new ::Ifc4x2::IfcDynamicViscosityMeasure(data);
            case 345: return new ::Ifc4x2::IfcEdge(data);
            case 346: return new ::Ifc4x2::IfcEdgeCurve(data);
            case 347: return new ::Ifc4x2::IfcEdgeLoop(data);
            case 348: return new ::Ifc4x2::IfcElectricAppliance(data);
            case 349: return new ::Ifc4x2::IfcElectricApplianceType(data);
            case 350: return new ::Ifc4x2::IfcElectricApplianceTypeEnum(data);
            case 351: return new ::Ifc4x2::IfcElectricCapacitanceMeasure(data);
            case 352: return new ::Ifc4x2::IfcElectricChargeMeasure(data);
            case 353: return new ::Ifc4x2::IfcElectricConductanceMeasure(data);
            case 354: return new ::Ifc4x2::IfcElectricCurrentMeasure(data);
            case 355: return new ::Ifc4x2::IfcElectricDistributionBoard(data);
            case 356: return new ::Ifc4x2::IfcElectricDistributionBoardType(data);
            case 357: return new ::Ifc4x2::IfcElectricDistributionBoardTypeEnum(data);
            case 358: return new ::Ifc4x2::IfcElectricFlowStorageDevice(data);
            case 359: return new ::Ifc4x2::IfcElectricFlowStorageDeviceType(data);
            case 360: return new ::Ifc4x2::IfcElectricFlowStorageDeviceTypeEnum(data);
            case 361: return new ::Ifc4x2::IfcElectricGenerator(data);
            case 362: return new ::Ifc4x2::IfcElectricGeneratorType(data);
            case 363: return new ::Ifc4x2::IfcElectricGeneratorTypeEnum(data);
            case 364: return new ::Ifc4x2::IfcElectricMotor(data);
            case 365: return new ::Ifc4x2::IfcElectricMotorType(data);
            case 366: return new ::Ifc4x2::IfcElectricMotorTypeEnum(data);
            case 367: return new ::Ifc4x2::IfcElectricResistanceMeasure(data);
            case 368: return new ::Ifc4x2::IfcElectricTimeControl(data);
            case 369: return new ::Ifc4x2::IfcElectricTimeControlType(data);
            case 370: return new ::Ifc4x2::IfcElectricTimeControlTypeEnum(data);
            case 371: return new ::Ifc4x2::IfcElectricVoltageMeasure(data);
            case 372: return new ::Ifc4x2::IfcElement(data);
            case 373: return new ::Ifc4x2::IfcElementarySurface(data);
            case 374: return new ::Ifc4x2::IfcElementAssembly(data);
            case 375: return new ::Ifc4x2::IfcElementAssemblyType(data);
            case 376: return new ::Ifc4x2::IfcElementAssemblyTypeEnum(data);
            case 377: return new ::Ifc4x2::IfcElementComponent(data);
            case 378: return new ::Ifc4x2::IfcElementComponentType(data);
            case 379: return new ::Ifc4x2::IfcElementCompositionEnum(data);
            case 380: return new ::Ifc4x2::IfcElementQuantity(data);
            case 381: return new ::Ifc4x2::IfcElementType(data);
            case 382: return new ::Ifc4x2::IfcEllipse(data);
            case 383: return new ::Ifc4x2::IfcEllipseProfileDef(data);
            case 384: return new ::Ifc4x2::IfcEnergyConversionDevice(data);
            case 385: return new ::Ifc4x2::IfcEnergyConversionDeviceType(data);
            case 386: return new ::Ifc4x2::IfcEnergyMeasure(data);
            case 387: return new ::Ifc4x2::IfcEngine(data);
            case 388: return new ::Ifc4x2::IfcEngineType(data);
            case 389: return new ::Ifc4x2::IfcEngineTypeEnum(data);
            case 390: return new ::Ifc4x2::IfcEvaporativeCooler(data);
            case 391: return new ::Ifc4x2::IfcEvaporativeCoolerType(data);
            case 392: return new ::Ifc4x2::IfcEvaporativeCoolerTypeEnum(data);
            case 393: return new ::Ifc4x2::IfcEvaporator(data);
            case 394: return new ::Ifc4x2::IfcEvaporatorType(data);
            case 395: return new ::Ifc4x2::IfcEvaporatorTypeEnum(data);
            case 396: return new ::Ifc4x2::IfcEvent(data);
            case 397: return new ::Ifc4x2::IfcEventTime(data);
            case 398: return new ::Ifc4x2::IfcEventTriggerTypeEnum(data);
            case 399: return new ::Ifc4x2::IfcEventType(data);
            case 400: return new ::Ifc4x2::IfcEventTypeEnum(data);
            case 401: return new ::Ifc4x2::IfcExtendedProperties(data);
            case 402: return new ::Ifc4x2::IfcExternalInformation(data);
            case 403: return new ::Ifc4x2::IfcExternallyDefinedHatchStyle(data);
            case 404: return new ::Ifc4x2::IfcExternallyDefinedSurfaceStyle(data);
            case 405: return new ::Ifc4x2::IfcExternallyDefinedTextFont(data);
            case 406: return new ::Ifc4x2::IfcExternalReference(data);
            case 407: return new ::Ifc4x2::IfcExternalReferenceRelationship(data);
            case 408: return new ::Ifc4x2::IfcExternalSpatialElement(data);
            case 409: return new ::Ifc4x2::IfcExternalSpatialElementTypeEnum(data);
            case 410: return new ::Ifc4x2::IfcExternalSpatialStructureElement(data);
            case 411: return new ::Ifc4x2::IfcExtrudedAreaSolid(data);
            case 412: return new ::Ifc4x2::IfcExtrudedAreaSolidTapered(data);
            case 413: return new ::Ifc4x2::IfcFace(data);
            case 414: return new ::Ifc4x2::IfcFaceBasedSurfaceModel(data);
            case 415: return new ::Ifc4x2::IfcFaceBound(data);
            case 416: return new ::Ifc4x2::IfcFaceOuterBound(data);
            case 417: return new ::Ifc4x2::IfcFaceSurface(data);
            case 418: return new ::Ifc4x2::IfcFacetedBrep(data);
            case 419: return new ::Ifc4x2::IfcFacetedBrepWithVoids(data);
            case 420: return new ::Ifc4x2::IfcFacility(data);
            case 421: return new ::Ifc4x2::IfcFacilityPart(data);
            case 422: return new ::Ifc4x2::IfcFailureConnectionCondition(data);
            case 423: return new ::Ifc4x2::IfcFan(data);
            case 424: return new ::Ifc4x2::IfcFanType(data);
            case 425: return new ::Ifc4x2::IfcFanTypeEnum(data);
            case 426: return new ::Ifc4x2::IfcFastener(data);
            case 427: return new ::Ifc4x2::IfcFastenerType(data);
            case 428: return new ::Ifc4x2::IfcFastenerTypeEnum(data);
            case 429: return new ::Ifc4x2::IfcFeatureElement(data);
            case 430: return new ::Ifc4x2::IfcFeatureElementAddition(data);
            case 431: return new ::Ifc4x2::IfcFeatureElementSubtraction(data);
            case 432: return new ::Ifc4x2::IfcFillAreaStyle(data);
            case 433: return new ::Ifc4x2::IfcFillAreaStyleHatching(data);
            case 434: return new ::Ifc4x2::IfcFillAreaStyleTiles(data);
            case 436: return new ::Ifc4x2::IfcFilter(data);
            case 437: return new ::Ifc4x2::IfcFilterType(data);
            case 438: return new ::Ifc4x2::IfcFilterTypeEnum(data);
            case 439: return new ::Ifc4x2::IfcFireSuppressionTerminal(data);
            case 440: return new ::Ifc4x2::IfcFireSuppressionTerminalType(data);
            case 441: return new ::Ifc4x2::IfcFireSuppressionTerminalTypeEnum(data);
            case 442: return new ::Ifc4x2::IfcFixedReferenceSweptAreaSolid(data);
            case 443: return new ::Ifc4x2::IfcFlowController(data);
            case 444: return new ::Ifc4x2::IfcFlowControllerType(data);
            case 445: return new ::Ifc4x2::IfcFlowDirectionEnum(data);
            case 446: return new ::Ifc4x2::IfcFlowFitting(data);
            case 447: return new ::Ifc4x2::IfcFlowFittingType(data);
            case 448: return new ::Ifc4x2::IfcFlowInstrument(data);
            case 449: return new ::Ifc4x2::IfcFlowInstrumentType(data);
            case 450: return new ::Ifc4x2::IfcFlowInstrumentTypeEnum(data);
            case 451: return new ::Ifc4x2::IfcFlowMeter(data);
            case 452: return new ::Ifc4x2::IfcFlowMeterType(data);
            case 453: return new ::Ifc4x2::IfcFlowMeterTypeEnum(data);
            case 454: return new ::Ifc4x2::IfcFlowMovingDevice(data);
            case 455: return new ::Ifc4x2::IfcFlowMovingDeviceType(data);
            case 456: return new ::Ifc4x2::IfcFlowSegment(data);
            case 457: return new ::Ifc4x2::IfcFlowSegmentType(data);
            case 458: return new ::Ifc4x2::IfcFlowStorageDevice(data);
            case 459: return new ::Ifc4x2::IfcFlowStorageDeviceType(data);
            case 460: return new ::Ifc4x2::IfcFlowTerminal(data);
            case 461: return new ::Ifc4x2::IfcFlowTerminalType(data);
            case 462: return new ::Ifc4x2::IfcFlowTreatmentDevice(data);
            case 463: return new ::Ifc4x2::IfcFlowTreatmentDeviceType(data);
            case 464: return new ::Ifc4x2::IfcFontStyle(data);
            case 465: return new ::Ifc4x2::IfcFontVariant(data);
            case 466: return new ::Ifc4x2::IfcFontWeight(data);
            case 467: return new ::Ifc4x2::IfcFooting(data);
            case 468: return new ::Ifc4x2::IfcFootingType(data);
            case 469: return new ::Ifc4x2::IfcFootingTypeEnum(data);
            case 470: return new ::Ifc4x2::IfcForceMeasure(data);
            case 471: return new ::Ifc4x2::IfcFrequencyMeasure(data);
            case 472: return new ::Ifc4x2::IfcFurnishingElement(data);
            case 473: return new ::Ifc4x2::IfcFurnishingElementType(data);
            case 474: return new ::Ifc4x2::IfcFurniture(data);
            case 475: return new ::Ifc4x2::IfcFurnitureType(data);
            case 476: return new ::Ifc4x2::IfcFurnitureTypeEnum(data);
            case 477: return new ::Ifc4x2::IfcGeographicElement(data);
            case 478: return new ::Ifc4x2::IfcGeographicElementType(data);
            case 479: return new ::Ifc4x2::IfcGeographicElementTypeEnum(data);
            case 480: return new ::Ifc4x2::IfcGeometricCurveSet(data);
            case 481: return new ::Ifc4x2::IfcGeometricProjectionEnum(data);
            case 482: return new ::Ifc4x2::IfcGeometricRepresentationContext(data);
            case 483: return new ::Ifc4x2::IfcGeometricRepresentationItem(data);
            case 484: return new ::Ifc4x2::IfcGeometricRepresentationSubContext(data);
            case 485: return new ::Ifc4x2::IfcGeometricSet(data);
            case 487: return new ::Ifc4x2::IfcGloballyUniqueId(data);
            case 488: return new ::Ifc4x2::IfcGlobalOrLocalEnum(data);
            case 489: return new ::Ifc4x2::IfcGrid(data);
            case 490: return new ::Ifc4x2::IfcGridAxis(data);
            case 491: return new ::Ifc4x2::IfcGridPlacement(data);
            case 493: return new ::Ifc4x2::IfcGridTypeEnum(data);
            case 494: return new ::Ifc4x2::IfcGroup(data);
            case 495: return new ::Ifc4x2::IfcHalfSpaceSolid(data);
            case 497: return new ::Ifc4x2::IfcHeatExchanger(data);
            case 498: return new ::Ifc4x2::IfcHeatExchangerType(data);
            case 499: return new ::Ifc4x2::IfcHeatExchangerTypeEnum(data);
            case 500: return new ::Ifc4x2::IfcHeatFluxDensityMeasure(data);
            case 501: return new ::Ifc4x2::IfcHeatingValueMeasure(data);
            case 502: return new ::Ifc4x2::IfcHumidifier(data);
            case 503: return new ::Ifc4x2::IfcHumidifierType(data);
            case 504: return new ::Ifc4x2::IfcHumidifierTypeEnum(data);
            case 505: return new ::Ifc4x2::IfcIdentifier(data);
            case 506: return new ::Ifc4x2::IfcIlluminanceMeasure(data);
            case 507: return new ::Ifc4x2::IfcImageTexture(data);
            case 508: return new ::Ifc4x2::IfcIndexedColourMap(data);
            case 509: return new ::Ifc4x2::IfcIndexedPolyCurve(data);
            case 510: return new ::Ifc4x2::IfcIndexedPolygonalFace(data);
            case 511: return new ::Ifc4x2::IfcIndexedPolygonalFaceWithVoids(data);
            case 512: return new ::Ifc4x2::IfcIndexedTextureMap(data);
            case 513: return new ::Ifc4x2::IfcIndexedTriangleTextureMap(data);
            case 514: return new ::Ifc4x2::IfcInductanceMeasure(data);
            case 515: return new ::Ifc4x2::IfcInteger(data);
            case 516: return new ::Ifc4x2::IfcIntegerCountRateMeasure(data);
            case 517: return new ::Ifc4x2::IfcInterceptor(data);
            case 518: return new ::Ifc4x2::IfcInterceptorType(data);
            case 519: return new ::Ifc4x2::IfcInterceptorTypeEnum(data);
            case 520: return new ::Ifc4x2::IfcInternalOrExternalEnum(data);
            case 521: return new ::Ifc4x2::IfcIntersectionCurve(data);
            case 522: return new ::Ifc4x2::IfcInventory(data);
            case 523: return new ::Ifc4x2::IfcInventoryTypeEnum(data);
            case 524: return new ::Ifc4x2::IfcIonConcentrationMeasure(data);
            case 525: return new ::Ifc4x2::IfcIrregularTimeSeries(data);
            case 526: return new ::Ifc4x2::IfcIrregularTimeSeriesValue(data);
            case 527: return new ::Ifc4x2::IfcIShapeProfileDef(data);
            case 528: return new ::Ifc4x2::IfcIsothermalMoistureCapacityMeasure(data);
            case 529: return new ::Ifc4x2::IfcJunctionBox(data);
            case 530: return new ::Ifc4x2::IfcJunctionBoxType(data);
            case 531: return new ::Ifc4x2::IfcJunctionBoxTypeEnum(data);
            case 532: return new ::Ifc4x2::IfcKinematicViscosityMeasure(data);
            case 533: return new ::Ifc4x2::IfcKnotType(data);
            case 534: return new ::Ifc4x2::IfcLabel(data);
            case 535: return new ::Ifc4x2::IfcLaborResource(data);
            case 536: return new ::Ifc4x2::IfcLaborResourceType(data);
            case 537: return new ::Ifc4x2::IfcLaborResourceTypeEnum(data);
            case 538: return new ::Ifc4x2::IfcLagTime(data);
            case 539: return new ::Ifc4x2::IfcLamp(data);
            case 540: return new ::Ifc4x2::IfcLampType(data);
            case 541: return new ::Ifc4x2::IfcLampTypeEnum(data);
            case 542: return new ::Ifc4x2::IfcLanguageId(data);
            case 544: return new ::Ifc4x2::IfcLayerSetDirectionEnum(data);
            case 545: return new ::Ifc4x2::IfcLengthMeasure(data);
            case 546: return new ::Ifc4x2::IfcLibraryInformation(data);
            case 547: return new ::Ifc4x2::IfcLibraryReference(data);
            case 549: return new ::Ifc4x2::IfcLightDistributionCurveEnum(data);
            case 550: return new ::Ifc4x2::IfcLightDistributionData(data);
            case 552: return new ::Ifc4x2::IfcLightEmissionSourceEnum(data);
            case 553: return new ::Ifc4x2::IfcLightFixture(data);
            case 554: return new ::Ifc4x2::IfcLightFixtureType(data);
            case 555: return new ::Ifc4x2::IfcLightFixtureTypeEnum(data);
            case 556: return new ::Ifc4x2::IfcLightIntensityDistribution(data);
            case 557: return new ::Ifc4x2::IfcLightSource(data);
            case 558: return new ::Ifc4x2::IfcLightSourceAmbient(data);
            case 559: return new ::Ifc4x2::IfcLightSourceDirectional(data);
            case 560: return new ::Ifc4x2::IfcLightSourceGoniometric(data);
            case 561: return new ::Ifc4x2::IfcLightSourcePositional(data);
            case 562: return new ::Ifc4x2::IfcLightSourceSpot(data);
            case 563: return new ::Ifc4x2::IfcLine(data);
            case 564: return new ::Ifc4x2::IfcLinearForceMeasure(data);
            case 565: return new ::Ifc4x2::IfcLinearMomentMeasure(data);
            case 566: return new ::Ifc4x2::IfcLinearPlacement(data);
            case 567: return new ::Ifc4x2::IfcLinearPositioningElement(data);
            case 568: return new ::Ifc4x2::IfcLinearStiffnessMeasure(data);
            case 569: return new ::Ifc4x2::IfcLinearVelocityMeasure(data);
            case 570: return new ::Ifc4x2::IfcLineIndex(data);
            case 571: return new ::Ifc4x2::IfcLineSegment2D(data);
            case 572: return new ::Ifc4x2::IfcLoadGroupTypeEnum(data);
            case 573: return new ::Ifc4x2::IfcLocalPlacement(data);
            case 574: return new ::Ifc4x2::IfcLogical(data);
            case 575: return new ::Ifc4x2::IfcLogicalOperatorEnum(data);
            case 576: return new ::Ifc4x2::IfcLoop(data);
            case 577: return new ::Ifc4x2::IfcLShapeProfileDef(data);
            case 578: return new ::Ifc4x2::IfcLuminousFluxMeasure(data);
            case 579: return new ::Ifc4x2::IfcLuminousIntensityDistributionMeasure(data);
            case 580: return new ::Ifc4x2::IfcLuminousIntensityMeasure(data);
            case 581: return new ::Ifc4x2::IfcMagneticFluxDensityMeasure(data);
            case 582: return new ::Ifc4x2::IfcMagneticFluxMeasure(data);
            case 583: return new ::Ifc4x2::IfcManifoldSolidBrep(data);
            case 584: return new ::Ifc4x2::IfcMapConversion(data);
            case 585: return new ::Ifc4x2::IfcMappedItem(data);
            case 586: return new ::Ifc4x2::IfcMassDensityMeasure(data);
            case 587: return new ::Ifc4x2::IfcMassFlowRateMeasure(data);
            case 588: return new ::Ifc4x2::IfcMassMeasure(data);
            case 589: return new ::Ifc4x2::IfcMassPerLengthMeasure(data);
            case 590: return new ::Ifc4x2::IfcMaterial(data);
            case 591: return new ::Ifc4x2::IfcMaterialClassificationRelationship(data);
            case 592: return new ::Ifc4x2::IfcMaterialConstituent(data);
            case 593: return new ::Ifc4x2::IfcMaterialConstituentSet(data);
            case 594: return new ::Ifc4x2::IfcMaterialDefinition(data);
            case 595: return new ::Ifc4x2::IfcMaterialDefinitionRepresentation(data);
            case 596: return new ::Ifc4x2::IfcMaterialLayer(data);
            case 597: return new ::Ifc4x2::IfcMaterialLayerSet(data);
            case 598: return new ::Ifc4x2::IfcMaterialLayerSetUsage(data);
            case 599: return new ::Ifc4x2::IfcMaterialLayerWithOffsets(data);
            case 600: return new ::Ifc4x2::IfcMaterialList(data);
            case 601: return new ::Ifc4x2::IfcMaterialProfile(data);
            case 602: return new ::Ifc4x2::IfcMaterialProfileSet(data);
            case 603: return new ::Ifc4x2::IfcMaterialProfileSetUsage(data);
            case 604: return new ::Ifc4x2::IfcMaterialProfileSetUsageTapering(data);
            case 605: return new ::Ifc4x2::IfcMaterialProfileWithOffsets(data);
            case 606: return new ::Ifc4x2::IfcMaterialProperties(data);
            case 607: return new ::Ifc4x2::IfcMaterialRelationship(data);
            case 609: return new ::Ifc4x2::IfcMaterialUsageDefinition(data);
            case 611: return new ::Ifc4x2::IfcMeasureWithUnit(data);
            case 612: return new ::Ifc4x2::IfcMechanicalFastener(data);
            case 613: return new ::Ifc4x2::IfcMechanicalFastenerType(data);
            case 614: return new ::Ifc4x2::IfcMechanicalFastenerTypeEnum(data);
            case 615: return new ::Ifc4x2::IfcMedicalDevice(data);
            case 616: return new ::Ifc4x2::IfcMedicalDeviceType(data);
            case 617: return new ::Ifc4x2::IfcMedicalDeviceTypeEnum(data);
            case 618: return new ::Ifc4x2::IfcMember(data);
            case 619: return new ::Ifc4x2::IfcMemberStandardCase(data);
            case 620: return new ::Ifc4x2::IfcMemberType(data);
            case 621: return new ::Ifc4x2::IfcMemberTypeEnum(data);
            case 622: return new ::Ifc4x2::IfcMetric(data);
            case 624: return new ::Ifc4x2::IfcMirroredProfileDef(data);
            case 625: return new ::Ifc4x2::IfcModulusOfElasticityMeasure(data);
            case 626: return new ::Ifc4x2::IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 627: return new ::Ifc4x2::IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 629: return new ::Ifc4x2::IfcModulusOfSubgradeReactionMeasure(data);
            case 632: return new ::Ifc4x2::IfcMoistureDiffusivityMeasure(data);
            case 633: return new ::Ifc4x2::IfcMolecularWeightMeasure(data);
            case 634: return new ::Ifc4x2::IfcMomentOfInertiaMeasure(data);
            case 635: return new ::Ifc4x2::IfcMonetaryMeasure(data);
            case 636: return new ::Ifc4x2::IfcMonetaryUnit(data);
            case 637: return new ::Ifc4x2::IfcMonthInYearNumber(data);
            case 638: return new ::Ifc4x2::IfcMotorConnection(data);
            case 639: return new ::Ifc4x2::IfcMotorConnectionType(data);
            case 640: return new ::Ifc4x2::IfcMotorConnectionTypeEnum(data);
            case 641: return new ::Ifc4x2::IfcNamedUnit(data);
            case 642: return new ::Ifc4x2::IfcNonNegativeLengthMeasure(data);
            case 643: return new ::Ifc4x2::IfcNormalisedRatioMeasure(data);
            case 644: return new ::Ifc4x2::IfcNullStyle(data);
            case 645: return new ::Ifc4x2::IfcNumericMeasure(data);
            case 646: return new ::Ifc4x2::IfcObject(data);
            case 647: return new ::Ifc4x2::IfcObjectDefinition(data);
            case 648: return new ::Ifc4x2::IfcObjective(data);
            case 649: return new ::Ifc4x2::IfcObjectiveEnum(data);
            case 650: return new ::Ifc4x2::IfcObjectPlacement(data);
            case 652: return new ::Ifc4x2::IfcObjectTypeEnum(data);
            case 653: return new ::Ifc4x2::IfcOccupant(data);
            case 654: return new ::Ifc4x2::IfcOccupantTypeEnum(data);
            case 655: return new ::Ifc4x2::IfcOffsetCurve(data);
            case 656: return new ::Ifc4x2::IfcOffsetCurve2D(data);
            case 657: return new ::Ifc4x2::IfcOffsetCurve3D(data);
            case 658: return new ::Ifc4x2::IfcOffsetCurveByDistances(data);
            case 659: return new ::Ifc4x2::IfcOpeningElement(data);
            case 660: return new ::Ifc4x2::IfcOpeningElementTypeEnum(data);
            case 661: return new ::Ifc4x2::IfcOpeningStandardCase(data);
            case 662: return new ::Ifc4x2::IfcOpenShell(data);
            case 663: return new ::Ifc4x2::IfcOrganization(data);
            case 664: return new ::Ifc4x2::IfcOrganizationRelationship(data);
            case 665: return new ::Ifc4x2::IfcOrientationExpression(data);
            case 666: return new ::Ifc4x2::IfcOrientedEdge(data);
            case 667: return new ::Ifc4x2::IfcOuterBoundaryCurve(data);
            case 668: return new ::Ifc4x2::IfcOutlet(data);
            case 669: return new ::Ifc4x2::IfcOutletType(data);
            case 670: return new ::Ifc4x2::IfcOutletTypeEnum(data);
            case 671: return new ::Ifc4x2::IfcOwnerHistory(data);
            case 672: return new ::Ifc4x2::IfcParameterizedProfileDef(data);
            case 673: return new ::Ifc4x2::IfcParameterValue(data);
            case 674: return new ::Ifc4x2::IfcPath(data);
            case 675: return new ::Ifc4x2::IfcPcurve(data);
            case 676: return new ::Ifc4x2::IfcPerformanceHistory(data);
            case 677: return new ::Ifc4x2::IfcPerformanceHistoryTypeEnum(data);
            case 678: return new ::Ifc4x2::IfcPermeableCoveringOperationEnum(data);
            case 679: return new ::Ifc4x2::IfcPermeableCoveringProperties(data);
            case 680: return new ::Ifc4x2::IfcPermit(data);
            case 681: return new ::Ifc4x2::IfcPermitTypeEnum(data);
            case 682: return new ::Ifc4x2::IfcPerson(data);
            case 683: return new ::Ifc4x2::IfcPersonAndOrganization(data);
            case 684: return new ::Ifc4x2::IfcPHMeasure(data);
            case 685: return new ::Ifc4x2::IfcPhysicalComplexQuantity(data);
            case 686: return new ::Ifc4x2::IfcPhysicalOrVirtualEnum(data);
            case 687: return new ::Ifc4x2::IfcPhysicalQuantity(data);
            case 688: return new ::Ifc4x2::IfcPhysicalSimpleQuantity(data);
            case 689: return new ::Ifc4x2::IfcPile(data);
            case 690: return new ::Ifc4x2::IfcPileConstructionEnum(data);
            case 691: return new ::Ifc4x2::IfcPileType(data);
            case 692: return new ::Ifc4x2::IfcPileTypeEnum(data);
            case 693: return new ::Ifc4x2::IfcPipeFitting(data);
            case 694: return new ::Ifc4x2::IfcPipeFittingType(data);
            case 695: return new ::Ifc4x2::IfcPipeFittingTypeEnum(data);
            case 696: return new ::Ifc4x2::IfcPipeSegment(data);
            case 697: return new ::Ifc4x2::IfcPipeSegmentType(data);
            case 698: return new ::Ifc4x2::IfcPipeSegmentTypeEnum(data);
            case 699: return new ::Ifc4x2::IfcPixelTexture(data);
            case 700: return new ::Ifc4x2::IfcPlacement(data);
            case 701: return new ::Ifc4x2::IfcPlanarBox(data);
            case 702: return new ::Ifc4x2::IfcPlanarExtent(data);
            case 703: return new ::Ifc4x2::IfcPlanarForceMeasure(data);
            case 704: return new ::Ifc4x2::IfcPlane(data);
            case 705: return new ::Ifc4x2::IfcPlaneAngleMeasure(data);
            case 706: return new ::Ifc4x2::IfcPlate(data);
            case 707: return new ::Ifc4x2::IfcPlateStandardCase(data);
            case 708: return new ::Ifc4x2::IfcPlateType(data);
            case 709: return new ::Ifc4x2::IfcPlateTypeEnum(data);
            case 710: return new ::Ifc4x2::IfcPoint(data);
            case 711: return new ::Ifc4x2::IfcPointOnCurve(data);
            case 712: return new ::Ifc4x2::IfcPointOnSurface(data);
            case 714: return new ::Ifc4x2::IfcPolygonalBoundedHalfSpace(data);
            case 715: return new ::Ifc4x2::IfcPolygonalFaceSet(data);
            case 716: return new ::Ifc4x2::IfcPolyline(data);
            case 717: return new ::Ifc4x2::IfcPolyLoop(data);
            case 718: return new ::Ifc4x2::IfcPort(data);
            case 719: return new ::Ifc4x2::IfcPositioningElement(data);
            case 720: return new ::Ifc4x2::IfcPositiveInteger(data);
            case 721: return new ::Ifc4x2::IfcPositiveLengthMeasure(data);
            case 722: return new ::Ifc4x2::IfcPositivePlaneAngleMeasure(data);
            case 723: return new ::Ifc4x2::IfcPositiveRatioMeasure(data);
            case 724: return new ::Ifc4x2::IfcPostalAddress(data);
            case 725: return new ::Ifc4x2::IfcPowerMeasure(data);
            case 726: return new ::Ifc4x2::IfcPreDefinedColour(data);
            case 727: return new ::Ifc4x2::IfcPreDefinedCurveFont(data);
            case 728: return new ::Ifc4x2::IfcPreDefinedItem(data);
            case 729: return new ::Ifc4x2::IfcPreDefinedProperties(data);
            case 730: return new ::Ifc4x2::IfcPreDefinedPropertySet(data);
            case 731: return new ::Ifc4x2::IfcPreDefinedTextFont(data);
            case 732: return new ::Ifc4x2::IfcPreferredSurfaceCurveRepresentation(data);
            case 733: return new ::Ifc4x2::IfcPresentableText(data);
            case 734: return new ::Ifc4x2::IfcPresentationItem(data);
            case 735: return new ::Ifc4x2::IfcPresentationLayerAssignment(data);
            case 736: return new ::Ifc4x2::IfcPresentationLayerWithStyle(data);
            case 737: return new ::Ifc4x2::IfcPresentationStyle(data);
            case 738: return new ::Ifc4x2::IfcPresentationStyleAssignment(data);
            case 740: return new ::Ifc4x2::IfcPressureMeasure(data);
            case 741: return new ::Ifc4x2::IfcProcedure(data);
            case 742: return new ::Ifc4x2::IfcProcedureType(data);
            case 743: return new ::Ifc4x2::IfcProcedureTypeEnum(data);
            case 744: return new ::Ifc4x2::IfcProcess(data);
            case 746: return new ::Ifc4x2::IfcProduct(data);
            case 747: return new ::Ifc4x2::IfcProductDefinitionShape(data);
            case 748: return new ::Ifc4x2::IfcProductRepresentation(data);
            case 751: return new ::Ifc4x2::IfcProfileDef(data);
            case 752: return new ::Ifc4x2::IfcProfileProperties(data);
            case 753: return new ::Ifc4x2::IfcProfileTypeEnum(data);
            case 754: return new ::Ifc4x2::IfcProject(data);
            case 755: return new ::Ifc4x2::IfcProjectedCRS(data);
            case 756: return new ::Ifc4x2::IfcProjectedOrTrueLengthEnum(data);
            case 757: return new ::Ifc4x2::IfcProjectionElement(data);
            case 758: return new ::Ifc4x2::IfcProjectionElementTypeEnum(data);
            case 759: return new ::Ifc4x2::IfcProjectLibrary(data);
            case 760: return new ::Ifc4x2::IfcProjectOrder(data);
            case 761: return new ::Ifc4x2::IfcProjectOrderTypeEnum(data);
            case 762: return new ::Ifc4x2::IfcProperty(data);
            case 763: return new ::Ifc4x2::IfcPropertyAbstraction(data);
            case 764: return new ::Ifc4x2::IfcPropertyBoundedValue(data);
            case 765: return new ::Ifc4x2::IfcPropertyDefinition(data);
            case 766: return new ::Ifc4x2::IfcPropertyDependencyRelationship(data);
            case 767: return new ::Ifc4x2::IfcPropertyEnumeratedValue(data);
            case 768: return new ::Ifc4x2::IfcPropertyEnumeration(data);
            case 769: return new ::Ifc4x2::IfcPropertyListValue(data);
            case 770: return new ::Ifc4x2::IfcPropertyReferenceValue(data);
            case 771: return new ::Ifc4x2::IfcPropertySet(data);
            case 772: return new ::Ifc4x2::IfcPropertySetDefinition(data);
            case 774: return new ::Ifc4x2::IfcPropertySetDefinitionSet(data);
            case 775: return new ::Ifc4x2::IfcPropertySetTemplate(data);
            case 776: return new ::Ifc4x2::IfcPropertySetTemplateTypeEnum(data);
            case 777: return new ::Ifc4x2::IfcPropertySingleValue(data);
            case 778: return new ::Ifc4x2::IfcPropertyTableValue(data);
            case 779: return new ::Ifc4x2::IfcPropertyTemplate(data);
            case 780: return new ::Ifc4x2::IfcPropertyTemplateDefinition(data);
            case 781: return new ::Ifc4x2::IfcProtectiveDevice(data);
            case 782: return new ::Ifc4x2::IfcProtectiveDeviceTrippingUnit(data);
            case 783: return new ::Ifc4x2::IfcProtectiveDeviceTrippingUnitType(data);
            case 784: return new ::Ifc4x2::IfcProtectiveDeviceTrippingUnitTypeEnum(data);
            case 785: return new ::Ifc4x2::IfcProtectiveDeviceType(data);
            case 786: return new ::Ifc4x2::IfcProtectiveDeviceTypeEnum(data);
            case 787: return new ::Ifc4x2::IfcProxy(data);
            case 788: return new ::Ifc4x2::IfcPump(data);
            case 789: return new ::Ifc4x2::IfcPumpType(data);
            case 790: return new ::Ifc4x2::IfcPumpTypeEnum(data);
            case 791: return new ::Ifc4x2::IfcQuantityArea(data);
            case 792: return new ::Ifc4x2::IfcQuantityCount(data);
            case 793: return new ::Ifc4x2::IfcQuantityLength(data);
            case 794: return new ::Ifc4x2::IfcQuantitySet(data);
            case 795: return new ::Ifc4x2::IfcQuantityTime(data);
            case 796: return new ::Ifc4x2::IfcQuantityVolume(data);
            case 797: return new ::Ifc4x2::IfcQuantityWeight(data);
            case 798: return new ::Ifc4x2::IfcRadioActivityMeasure(data);
            case 799: return new ::Ifc4x2::IfcRailing(data);
            case 800: return new ::Ifc4x2::IfcRailingType(data);
            case 801: return new ::Ifc4x2::IfcRailingTypeEnum(data);
            case 802: return new ::Ifc4x2::IfcRamp(data);
            case 803: return new ::Ifc4x2::IfcRampFlight(data);
            case 804: return new ::Ifc4x2::IfcRampFlightType(data);
            case 805: return new ::Ifc4x2::IfcRampFlightTypeEnum(data);
            case 806: return new ::Ifc4x2::IfcRampType(data);
            case 807: return new ::Ifc4x2::IfcRampTypeEnum(data);
            case 808: return new ::Ifc4x2::IfcRatioMeasure(data);
            case 809: return new ::Ifc4x2::IfcRationalBSplineCurveWithKnots(data);
            case 810: return new ::Ifc4x2::IfcRationalBSplineSurfaceWithKnots(data);
            case 811: return new ::Ifc4x2::IfcReal(data);
            case 812: return new ::Ifc4x2::IfcRectangleHollowProfileDef(data);
            case 813: return new ::Ifc4x2::IfcRectangleProfileDef(data);
            case 814: return new ::Ifc4x2::IfcRectangularPyramid(data);
            case 815: return new ::Ifc4x2::IfcRectangularTrimmedSurface(data);
            case 816: return new ::Ifc4x2::IfcRecurrencePattern(data);
            case 817: return new ::Ifc4x2::IfcRecurrenceTypeEnum(data);
            case 818: return new ::Ifc4x2::IfcReference(data);
            case 819: return new ::Ifc4x2::IfcReferent(data);
            case 820: return new ::Ifc4x2::IfcReferentTypeEnum(data);
            case 821: return new ::Ifc4x2::IfcReflectanceMethodEnum(data);
            case 822: return new ::Ifc4x2::IfcRegularTimeSeries(data);
            case 823: return new ::Ifc4x2::IfcReinforcementBarProperties(data);
            case 824: return new ::Ifc4x2::IfcReinforcementDefinitionProperties(data);
            case 825: return new ::Ifc4x2::IfcReinforcingBar(data);
            case 826: return new ::Ifc4x2::IfcReinforcingBarRoleEnum(data);
            case 827: return new ::Ifc4x2::IfcReinforcingBarSurfaceEnum(data);
            case 828: return new ::Ifc4x2::IfcReinforcingBarType(data);
            case 829: return new ::Ifc4x2::IfcReinforcingBarTypeEnum(data);
            case 830: return new ::Ifc4x2::IfcReinforcingElement(data);
            case 831: return new ::Ifc4x2::IfcReinforcingElementType(data);
            case 832: return new ::Ifc4x2::IfcReinforcingMesh(data);
            case 833: return new ::Ifc4x2::IfcReinforcingMeshType(data);
            case 834: return new ::Ifc4x2::IfcReinforcingMeshTypeEnum(data);
            case 835: return new ::Ifc4x2::IfcRelAggregates(data);
            case 836: return new ::Ifc4x2::IfcRelAssigns(data);
            case 837: return new ::Ifc4x2::IfcRelAssignsToActor(data);
            case 838: return new ::Ifc4x2::IfcRelAssignsToControl(data);
            case 839: return new ::Ifc4x2::IfcRelAssignsToGroup(data);
            case 840: return new ::Ifc4x2::IfcRelAssignsToGroupByFactor(data);
            case 841: return new ::Ifc4x2::IfcRelAssignsToProcess(data);
            case 842: return new ::Ifc4x2::IfcRelAssignsToProduct(data);
            case 843: return new ::Ifc4x2::IfcRelAssignsToResource(data);
            case 844: return new ::Ifc4x2::IfcRelAssociates(data);
            case 845: return new ::Ifc4x2::IfcRelAssociatesApproval(data);
            case 846: return new ::Ifc4x2::IfcRelAssociatesClassification(data);
            case 847: return new ::Ifc4x2::IfcRelAssociatesConstraint(data);
            case 848: return new ::Ifc4x2::IfcRelAssociatesDocument(data);
            case 849: return new ::Ifc4x2::IfcRelAssociatesLibrary(data);
            case 850: return new ::Ifc4x2::IfcRelAssociatesMaterial(data);
            case 851: return new ::Ifc4x2::IfcRelationship(data);
            case 852: return new ::Ifc4x2::IfcRelConnects(data);
            case 853: return new ::Ifc4x2::IfcRelConnectsElements(data);
            case 854: return new ::Ifc4x2::IfcRelConnectsPathElements(data);
            case 855: return new ::Ifc4x2::IfcRelConnectsPorts(data);
            case 856: return new ::Ifc4x2::IfcRelConnectsPortToElement(data);
            case 857: return new ::Ifc4x2::IfcRelConnectsStructuralActivity(data);
            case 858: return new ::Ifc4x2::IfcRelConnectsStructuralMember(data);
            case 859: return new ::Ifc4x2::IfcRelConnectsWithEccentricity(data);
            case 860: return new ::Ifc4x2::IfcRelConnectsWithRealizingElements(data);
            case 861: return new ::Ifc4x2::IfcRelContainedInSpatialStructure(data);
            case 862: return new ::Ifc4x2::IfcRelCoversBldgElements(data);
            case 863: return new ::Ifc4x2::IfcRelCoversSpaces(data);
            case 864: return new ::Ifc4x2::IfcRelDeclares(data);
            case 865: return new ::Ifc4x2::IfcRelDecomposes(data);
            case 866: return new ::Ifc4x2::IfcRelDefines(data);
            case 867: return new ::Ifc4x2::IfcRelDefinesByObject(data);
            case 868: return new ::Ifc4x2::IfcRelDefinesByProperties(data);
            case 869: return new ::Ifc4x2::IfcRelDefinesByTemplate(data);
            case 870: return new ::Ifc4x2::IfcRelDefinesByType(data);
            case 871: return new ::Ifc4x2::IfcRelFillsElement(data);
            case 872: return new ::Ifc4x2::IfcRelFlowControlElements(data);
            case 873: return new ::Ifc4x2::IfcRelInterferesElements(data);
            case 874: return new ::Ifc4x2::IfcRelNests(data);
            case 875: return new ::Ifc4x2::IfcRelPositions(data);
            case 876: return new ::Ifc4x2::IfcRelProjectsElement(data);
            case 877: return new ::Ifc4x2::IfcRelReferencedInSpatialStructure(data);
            case 878: return new ::Ifc4x2::IfcRelSequence(data);
            case 879: return new ::Ifc4x2::IfcRelServicesBuildings(data);
            case 880: return new ::Ifc4x2::IfcRelSpaceBoundary(data);
            case 881: return new ::Ifc4x2::IfcRelSpaceBoundary1stLevel(data);
            case 882: return new ::Ifc4x2::IfcRelSpaceBoundary2ndLevel(data);
            case 883: return new ::Ifc4x2::IfcRelVoidsElement(data);
            case 884: return new ::Ifc4x2::IfcReparametrisedCompositeCurveSegment(data);
            case 885: return new ::Ifc4x2::IfcRepresentation(data);
            case 886: return new ::Ifc4x2::IfcRepresentationContext(data);
            case 887: return new ::Ifc4x2::IfcRepresentationItem(data);
            case 888: return new ::Ifc4x2::IfcRepresentationMap(data);
            case 889: return new ::Ifc4x2::IfcResource(data);
            case 890: return new ::Ifc4x2::IfcResourceApprovalRelationship(data);
            case 891: return new ::Ifc4x2::IfcResourceConstraintRelationship(data);
            case 892: return new ::Ifc4x2::IfcResourceLevelRelationship(data);
            case 895: return new ::Ifc4x2::IfcResourceTime(data);
            case 896: return new ::Ifc4x2::IfcRevolvedAreaSolid(data);
            case 897: return new ::Ifc4x2::IfcRevolvedAreaSolidTapered(data);
            case 898: return new ::Ifc4x2::IfcRightCircularCone(data);
            case 899: return new ::Ifc4x2::IfcRightCircularCylinder(data);
            case 900: return new ::Ifc4x2::IfcRoleEnum(data);
            case 901: return new ::Ifc4x2::IfcRoof(data);
            case 902: return new ::Ifc4x2::IfcRoofType(data);
            case 903: return new ::Ifc4x2::IfcRoofTypeEnum(data);
            case 904: return new ::Ifc4x2::IfcRoot(data);
            case 905: return new ::Ifc4x2::IfcRotationalFrequencyMeasure(data);
            case 906: return new ::Ifc4x2::IfcRotationalMassMeasure(data);
            case 907: return new ::Ifc4x2::IfcRotationalStiffnessMeasure(data);
            case 909: return new ::Ifc4x2::IfcRoundedRectangleProfileDef(data);
            case 910: return new ::Ifc4x2::IfcSanitaryTerminal(data);
            case 911: return new ::Ifc4x2::IfcSanitaryTerminalType(data);
            case 912: return new ::Ifc4x2::IfcSanitaryTerminalTypeEnum(data);
            case 913: return new ::Ifc4x2::IfcSchedulingTime(data);
            case 914: return new ::Ifc4x2::IfcSeamCurve(data);
            case 915: return new ::Ifc4x2::IfcSectionalAreaIntegralMeasure(data);
            case 916: return new ::Ifc4x2::IfcSectionedSolid(data);
            case 917: return new ::Ifc4x2::IfcSectionedSolidHorizontal(data);
            case 918: return new ::Ifc4x2::IfcSectionedSpine(data);
            case 919: return new ::Ifc4x2::IfcSectionModulusMeasure(data);
            case 920: return new ::Ifc4x2::IfcSectionProperties(data);
            case 921: return new ::Ifc4x2::IfcSectionReinforcementProperties(data);
            case 922: return new ::Ifc4x2::IfcSectionTypeEnum(data);
            case 924: return new ::Ifc4x2::IfcSensor(data);
            case 925: return new ::Ifc4x2::IfcSensorType(data);
            case 926: return new ::Ifc4x2::IfcSensorTypeEnum(data);
            case 927: return new ::Ifc4x2::IfcSequenceEnum(data);
            case 928: return new ::Ifc4x2::IfcShadingDevice(data);
            case 929: return new ::Ifc4x2::IfcShadingDeviceType(data);
            case 930: return new ::Ifc4x2::IfcShadingDeviceTypeEnum(data);
            case 931: return new ::Ifc4x2::IfcShapeAspect(data);
            case 932: return new ::Ifc4x2::IfcShapeModel(data);
            case 933: return new ::Ifc4x2::IfcShapeRepresentation(data);
            case 934: return new ::Ifc4x2::IfcShearModulusMeasure(data);
            case 936: return new ::Ifc4x2::IfcShellBasedSurfaceModel(data);
            case 937: return new ::Ifc4x2::IfcSimpleProperty(data);
            case 938: return new ::Ifc4x2::IfcSimplePropertyTemplate(data);
            case 939: return new ::Ifc4x2::IfcSimplePropertyTemplateTypeEnum(data);
            case 941: return new ::Ifc4x2::IfcSIPrefix(data);
            case 942: return new ::Ifc4x2::IfcSite(data);
            case 943: return new ::Ifc4x2::IfcSIUnit(data);
            case 944: return new ::Ifc4x2::IfcSIUnitName(data);
            case 946: return new ::Ifc4x2::IfcSlab(data);
            case 947: return new ::Ifc4x2::IfcSlabElementedCase(data);
            case 948: return new ::Ifc4x2::IfcSlabStandardCase(data);
            case 949: return new ::Ifc4x2::IfcSlabType(data);
            case 950: return new ::Ifc4x2::IfcSlabTypeEnum(data);
            case 951: return new ::Ifc4x2::IfcSlippageConnectionCondition(data);
            case 952: return new ::Ifc4x2::IfcSolarDevice(data);
            case 953: return new ::Ifc4x2::IfcSolarDeviceType(data);
            case 954: return new ::Ifc4x2::IfcSolarDeviceTypeEnum(data);
            case 955: return new ::Ifc4x2::IfcSolidAngleMeasure(data);
            case 956: return new ::Ifc4x2::IfcSolidModel(data);
            case 958: return new ::Ifc4x2::IfcSoundPowerLevelMeasure(data);
            case 959: return new ::Ifc4x2::IfcSoundPowerMeasure(data);
            case 960: return new ::Ifc4x2::IfcSoundPressureLevelMeasure(data);
            case 961: return new ::Ifc4x2::IfcSoundPressureMeasure(data);
            case 962: return new ::Ifc4x2::IfcSpace(data);
            case 964: return new ::Ifc4x2::IfcSpaceHeater(data);
            case 965: return new ::Ifc4x2::IfcSpaceHeaterType(data);
            case 966: return new ::Ifc4x2::IfcSpaceHeaterTypeEnum(data);
            case 967: return new ::Ifc4x2::IfcSpaceType(data);
            case 968: return new ::Ifc4x2::IfcSpaceTypeEnum(data);
            case 969: return new ::Ifc4x2::IfcSpatialElement(data);
            case 970: return new ::Ifc4x2::IfcSpatialElementType(data);
            case 971: return new ::Ifc4x2::IfcSpatialStructureElement(data);
            case 972: return new ::Ifc4x2::IfcSpatialStructureElementType(data);
            case 973: return new ::Ifc4x2::IfcSpatialZone(data);
            case 974: return new ::Ifc4x2::IfcSpatialZoneType(data);
            case 975: return new ::Ifc4x2::IfcSpatialZoneTypeEnum(data);
            case 976: return new ::Ifc4x2::IfcSpecificHeatCapacityMeasure(data);
            case 977: return new ::Ifc4x2::IfcSpecularExponent(data);
            case 979: return new ::Ifc4x2::IfcSpecularRoughness(data);
            case 980: return new ::Ifc4x2::IfcSphere(data);
            case 981: return new ::Ifc4x2::IfcSphericalSurface(data);
            case 982: return new ::Ifc4x2::IfcStackTerminal(data);
            case 983: return new ::Ifc4x2::IfcStackTerminalType(data);
            case 984: return new ::Ifc4x2::IfcStackTerminalTypeEnum(data);
            case 985: return new ::Ifc4x2::IfcStair(data);
            case 986: return new ::Ifc4x2::IfcStairFlight(data);
            case 987: return new ::Ifc4x2::IfcStairFlightType(data);
            case 988: return new ::Ifc4x2::IfcStairFlightTypeEnum(data);
            case 989: return new ::Ifc4x2::IfcStairType(data);
            case 990: return new ::Ifc4x2::IfcStairTypeEnum(data);
            case 991: return new ::Ifc4x2::IfcStateEnum(data);
            case 992: return new ::Ifc4x2::IfcStructuralAction(data);
            case 993: return new ::Ifc4x2::IfcStructuralActivity(data);
            case 995: return new ::Ifc4x2::IfcStructuralAnalysisModel(data);
            case 996: return new ::Ifc4x2::IfcStructuralConnection(data);
            case 997: return new ::Ifc4x2::IfcStructuralConnectionCondition(data);
            case 998: return new ::Ifc4x2::IfcStructuralCurveAction(data);
            case 999: return new ::Ifc4x2::IfcStructuralCurveActivityTypeEnum(data);
            case 1000: return new ::Ifc4x2::IfcStructuralCurveConnection(data);
            case 1001: return new ::Ifc4x2::IfcStructuralCurveMember(data);
            case 1002: return new ::Ifc4x2::IfcStructuralCurveMemberTypeEnum(data);
            case 1003: return new ::Ifc4x2::IfcStructuralCurveMemberVarying(data);
            case 1004: return new ::Ifc4x2::IfcStructuralCurveReaction(data);
            case 1005: return new ::Ifc4x2::IfcStructuralItem(data);
            case 1006: return new ::Ifc4x2::IfcStructuralLinearAction(data);
            case 1007: return new ::Ifc4x2::IfcStructuralLoad(data);
            case 1008: return new ::Ifc4x2::IfcStructuralLoadCase(data);
            case 1009: return new ::Ifc4x2::IfcStructuralLoadConfiguration(data);
            case 1010: return new ::Ifc4x2::IfcStructuralLoadGroup(data);
            case 1011: return new ::Ifc4x2::IfcStructuralLoadLinearForce(data);
            case 1012: return new ::Ifc4x2::IfcStructuralLoadOrResult(data);
            case 1013: return new ::Ifc4x2::IfcStructuralLoadPlanarForce(data);
            case 1014: return new ::Ifc4x2::IfcStructuralLoadSingleDisplacement(data);
            case 1015: return new ::Ifc4x2::IfcStructuralLoadSingleDisplacementDistortion(data);
            case 1016: return new ::Ifc4x2::IfcStructuralLoadSingleForce(data);
            case 1017: return new ::Ifc4x2::IfcStructuralLoadSingleForceWarping(data);
            case 1018: return new ::Ifc4x2::IfcStructuralLoadStatic(data);
            case 1019: return new ::Ifc4x2::IfcStructuralLoadTemperature(data);
            case 1020: return new ::Ifc4x2::IfcStructuralMember(data);
            case 1021: return new ::Ifc4x2::IfcStructuralPlanarAction(data);
            case 1022: return new ::Ifc4x2::IfcStructuralPointAction(data);
            case 1023: return new ::Ifc4x2::IfcStructuralPointConnection(data);
            case 1024: return new ::Ifc4x2::IfcStructuralPointReaction(data);
            case 1025: return new ::Ifc4x2::IfcStructuralReaction(data);
            case 1026: return new ::Ifc4x2::IfcStructuralResultGroup(data);
            case 1027: return new ::Ifc4x2::IfcStructuralSurfaceAction(data);
            case 1028: return new ::Ifc4x2::IfcStructuralSurfaceActivityTypeEnum(data);
            case 1029: return new ::Ifc4x2::IfcStructuralSurfaceConnection(data);
            case 1030: return new ::Ifc4x2::IfcStructuralSurfaceMember(data);
            case 1031: return new ::Ifc4x2::IfcStructuralSurfaceMemberTypeEnum(data);
            case 1032: return new ::Ifc4x2::IfcStructuralSurfaceMemberVarying(data);
            case 1033: return new ::Ifc4x2::IfcStructuralSurfaceReaction(data);
            case 1035: return new ::Ifc4x2::IfcStyledItem(data);
            case 1036: return new ::Ifc4x2::IfcStyledRepresentation(data);
            case 1037: return new ::Ifc4x2::IfcStyleModel(data);
            case 1038: return new ::Ifc4x2::IfcSubContractResource(data);
            case 1039: return new ::Ifc4x2::IfcSubContractResourceType(data);
            case 1040: return new ::Ifc4x2::IfcSubContractResourceTypeEnum(data);
            case 1041: return new ::Ifc4x2::IfcSubedge(data);
            case 1042: return new ::Ifc4x2::IfcSurface(data);
            case 1043: return new ::Ifc4x2::IfcSurfaceCurve(data);
            case 1044: return new ::Ifc4x2::IfcSurfaceCurveSweptAreaSolid(data);
            case 1045: return new ::Ifc4x2::IfcSurfaceFeature(data);
            case 1046: return new ::Ifc4x2::IfcSurfaceFeatureTypeEnum(data);
            case 1047: return new ::Ifc4x2::IfcSurfaceOfLinearExtrusion(data);
            case 1048: return new ::Ifc4x2::IfcSurfaceOfRevolution(data);
            case 1050: return new ::Ifc4x2::IfcSurfaceReinforcementArea(data);
            case 1051: return new ::Ifc4x2::IfcSurfaceSide(data);
            case 1052: return new ::Ifc4x2::IfcSurfaceStyle(data);
            case 1054: return new ::Ifc4x2::IfcSurfaceStyleLighting(data);
            case 1055: return new ::Ifc4x2::IfcSurfaceStyleRefraction(data);
            case 1056: return new ::Ifc4x2::IfcSurfaceStyleRendering(data);
            case 1057: return new ::Ifc4x2::IfcSurfaceStyleShading(data);
            case 1058: return new ::Ifc4x2::IfcSurfaceStyleWithTextures(data);
            case 1059: return new ::Ifc4x2::IfcSurfaceTexture(data);
            case 1060: return new ::Ifc4x2::IfcSweptAreaSolid(data);
            case 1061: return new ::Ifc4x2::IfcSweptDiskSolid(data);
            case 1062: return new ::Ifc4x2::IfcSweptDiskSolidPolygonal(data);
            case 1063: return new ::Ifc4x2::IfcSweptSurface(data);
            case 1064: return new ::Ifc4x2::IfcSwitchingDevice(data);
            case 1065: return new ::Ifc4x2::IfcSwitchingDeviceType(data);
            case 1066: return new ::Ifc4x2::IfcSwitchingDeviceTypeEnum(data);
            case 1067: return new ::Ifc4x2::IfcSystem(data);
            case 1068: return new ::Ifc4x2::IfcSystemFurnitureElement(data);
            case 1069: return new ::Ifc4x2::IfcSystemFurnitureElementType(data);
            case 1070: return new ::Ifc4x2::IfcSystemFurnitureElementTypeEnum(data);
            case 1071: return new ::Ifc4x2::IfcTable(data);
            case 1072: return new ::Ifc4x2::IfcTableColumn(data);
            case 1073: return new ::Ifc4x2::IfcTableRow(data);
            case 1074: return new ::Ifc4x2::IfcTank(data);
            case 1075: return new ::Ifc4x2::IfcTankType(data);
            case 1076: return new ::Ifc4x2::IfcTankTypeEnum(data);
            case 1077: return new ::Ifc4x2::IfcTask(data);
            case 1078: return new ::Ifc4x2::IfcTaskDurationEnum(data);
            case 1079: return new ::Ifc4x2::IfcTaskTime(data);
            case 1080: return new ::Ifc4x2::IfcTaskTimeRecurring(data);
            case 1081: return new ::Ifc4x2::IfcTaskType(data);
            case 1082: return new ::Ifc4x2::IfcTaskTypeEnum(data);
            case 1083: return new ::Ifc4x2::IfcTelecomAddress(data);
            case 1084: return new ::Ifc4x2::IfcTemperatureGradientMeasure(data);
            case 1085: return new ::Ifc4x2::IfcTemperatureRateOfChangeMeasure(data);
            case 1086: return new ::Ifc4x2::IfcTendon(data);
            case 1087: return new ::Ifc4x2::IfcTendonAnchor(data);
            case 1088: return new ::Ifc4x2::IfcTendonAnchorType(data);
            case 1089: return new ::Ifc4x2::IfcTendonAnchorTypeEnum(data);
            case 1090: return new ::Ifc4x2::IfcTendonConduit(data);
            case 1091: return new ::Ifc4x2::IfcTendonConduitType(data);
            case 1092: return new ::Ifc4x2::IfcTendonConduitTypeEnum(data);
            case 1093: return new ::Ifc4x2::IfcTendonType(data);
            case 1094: return new ::Ifc4x2::IfcTendonTypeEnum(data);
            case 1095: return new ::Ifc4x2::IfcTessellatedFaceSet(data);
            case 1096: return new ::Ifc4x2::IfcTessellatedItem(data);
            case 1097: return new ::Ifc4x2::IfcText(data);
            case 1098: return new ::Ifc4x2::IfcTextAlignment(data);
            case 1099: return new ::Ifc4x2::IfcTextDecoration(data);
            case 1100: return new ::Ifc4x2::IfcTextFontName(data);
            case 1102: return new ::Ifc4x2::IfcTextLiteral(data);
            case 1103: return new ::Ifc4x2::IfcTextLiteralWithExtent(data);
            case 1104: return new ::Ifc4x2::IfcTextPath(data);
            case 1105: return new ::Ifc4x2::IfcTextStyle(data);
            case 1106: return new ::Ifc4x2::IfcTextStyleFontModel(data);
            case 1107: return new ::Ifc4x2::IfcTextStyleForDefinedFont(data);
            case 1108: return new ::Ifc4x2::IfcTextStyleTextModel(data);
            case 1109: return new ::Ifc4x2::IfcTextTransformation(data);
            case 1110: return new ::Ifc4x2::IfcTextureCoordinate(data);
            case 1111: return new ::Ifc4x2::IfcTextureCoordinateGenerator(data);
            case 1112: return new ::Ifc4x2::IfcTextureMap(data);
            case 1113: return new ::Ifc4x2::IfcTextureVertex(data);
            case 1114: return new ::Ifc4x2::IfcTextureVertexList(data);
            case 1115: return new ::Ifc4x2::IfcThermalAdmittanceMeasure(data);
            case 1116: return new ::Ifc4x2::IfcThermalConductivityMeasure(data);
            case 1117: return new ::Ifc4x2::IfcThermalExpansionCoefficientMeasure(data);
            case 1118: return new ::Ifc4x2::IfcThermalResistanceMeasure(data);
            case 1119: return new ::Ifc4x2::IfcThermalTransmittanceMeasure(data);
            case 1120: return new ::Ifc4x2::IfcThermodynamicTemperatureMeasure(data);
            case 1121: return new ::Ifc4x2::IfcTime(data);
            case 1122: return new ::Ifc4x2::IfcTimeMeasure(data);
            case 1124: return new ::Ifc4x2::IfcTimePeriod(data);
            case 1125: return new ::Ifc4x2::IfcTimeSeries(data);
            case 1126: return new ::Ifc4x2::IfcTimeSeriesDataTypeEnum(data);
            case 1127: return new ::Ifc4x2::IfcTimeSeriesValue(data);
            case 1128: return new ::Ifc4x2::IfcTimeStamp(data);
            case 1129: return new ::Ifc4x2::IfcTopologicalRepresentationItem(data);
            case 1130: return new ::Ifc4x2::IfcTopologyRepresentation(data);
            case 1131: return new ::Ifc4x2::IfcToroidalSurface(data);
            case 1132: return new ::Ifc4x2::IfcTorqueMeasure(data);
            case 1133: return new ::Ifc4x2::IfcTransformer(data);
            case 1134: return new ::Ifc4x2::IfcTransformerType(data);
            case 1135: return new ::Ifc4x2::IfcTransformerTypeEnum(data);
            case 1136: return new ::Ifc4x2::IfcTransitionCode(data);
            case 1137: return new ::Ifc4x2::IfcTransitionCurveSegment2D(data);
            case 1138: return new ::Ifc4x2::IfcTransitionCurveType(data);
            case 1140: return new ::Ifc4x2::IfcTransportElement(data);
            case 1141: return new ::Ifc4x2::IfcTransportElementType(data);
            case 1142: return new ::Ifc4x2::IfcTransportElementTypeEnum(data);
            case 1143: return new ::Ifc4x2::IfcTrapeziumProfileDef(data);
            case 1144: return new ::Ifc4x2::IfcTriangulatedFaceSet(data);
            case 1145: return new ::Ifc4x2::IfcTriangulatedIrregularNetwork(data);
            case 1146: return new ::Ifc4x2::IfcTrimmedCurve(data);
            case 1147: return new ::Ifc4x2::IfcTrimmingPreference(data);
            case 1149: return new ::Ifc4x2::IfcTShapeProfileDef(data);
            case 1150: return new ::Ifc4x2::IfcTubeBundle(data);
            case 1151: return new ::Ifc4x2::IfcTubeBundleType(data);
            case 1152: return new ::Ifc4x2::IfcTubeBundleTypeEnum(data);
            case 1153: return new ::Ifc4x2::IfcTypeObject(data);
            case 1154: return new ::Ifc4x2::IfcTypeProcess(data);
            case 1155: return new ::Ifc4x2::IfcTypeProduct(data);
            case 1156: return new ::Ifc4x2::IfcTypeResource(data);
            case 1158: return new ::Ifc4x2::IfcUnitaryControlElement(data);
            case 1159: return new ::Ifc4x2::IfcUnitaryControlElementType(data);
            case 1160: return new ::Ifc4x2::IfcUnitaryControlElementTypeEnum(data);
            case 1161: return new ::Ifc4x2::IfcUnitaryEquipment(data);
            case 1162: return new ::Ifc4x2::IfcUnitaryEquipmentType(data);
            case 1163: return new ::Ifc4x2::IfcUnitaryEquipmentTypeEnum(data);
            case 1164: return new ::Ifc4x2::IfcUnitAssignment(data);
            case 1165: return new ::Ifc4x2::IfcUnitEnum(data);
            case 1166: return new ::Ifc4x2::IfcURIReference(data);
            case 1167: return new ::Ifc4x2::IfcUShapeProfileDef(data);
            case 1169: return new ::Ifc4x2::IfcValve(data);
            case 1170: return new ::Ifc4x2::IfcValveType(data);
            case 1171: return new ::Ifc4x2::IfcValveTypeEnum(data);
            case 1172: return new ::Ifc4x2::IfcVaporPermeabilityMeasure(data);
            case 1173: return new ::Ifc4x2::IfcVector(data);
            case 1175: return new ::Ifc4x2::IfcVertex(data);
            case 1176: return new ::Ifc4x2::IfcVertexLoop(data);
            case 1177: return new ::Ifc4x2::IfcVertexPoint(data);
            case 1178: return new ::Ifc4x2::IfcVibrationDamper(data);
            case 1179: return new ::Ifc4x2::IfcVibrationDamperType(data);
            case 1180: return new ::Ifc4x2::IfcVibrationDamperTypeEnum(data);
            case 1181: return new ::Ifc4x2::IfcVibrationIsolator(data);
            case 1182: return new ::Ifc4x2::IfcVibrationIsolatorType(data);
            case 1183: return new ::Ifc4x2::IfcVibrationIsolatorTypeEnum(data);
            case 1184: return new ::Ifc4x2::IfcVirtualElement(data);
            case 1185: return new ::Ifc4x2::IfcVirtualGridIntersection(data);
            case 1186: return new ::Ifc4x2::IfcVoidingFeature(data);
            case 1187: return new ::Ifc4x2::IfcVoidingFeatureTypeEnum(data);
            case 1188: return new ::Ifc4x2::IfcVolumeMeasure(data);
            case 1189: return new ::Ifc4x2::IfcVolumetricFlowRateMeasure(data);
            case 1190: return new ::Ifc4x2::IfcWall(data);
            case 1191: return new ::Ifc4x2::IfcWallElementedCase(data);
            case 1192: return new ::Ifc4x2::IfcWallStandardCase(data);
            case 1193: return new ::Ifc4x2::IfcWallType(data);
            case 1194: return new ::Ifc4x2::IfcWallTypeEnum(data);
            case 1195: return new ::Ifc4x2::IfcWarpingConstantMeasure(data);
            case 1196: return new ::Ifc4x2::IfcWarpingMomentMeasure(data);
            case 1198: return new ::Ifc4x2::IfcWasteTerminal(data);
            case 1199: return new ::Ifc4x2::IfcWasteTerminalType(data);
            case 1200: return new ::Ifc4x2::IfcWasteTerminalTypeEnum(data);
            case 1201: return new ::Ifc4x2::IfcWindow(data);
            case 1202: return new ::Ifc4x2::IfcWindowLiningProperties(data);
            case 1203: return new ::Ifc4x2::IfcWindowPanelOperationEnum(data);
            case 1204: return new ::Ifc4x2::IfcWindowPanelPositionEnum(data);
            case 1205: return new ::Ifc4x2::IfcWindowPanelProperties(data);
            case 1206: return new ::Ifc4x2::IfcWindowStandardCase(data);
            case 1207: return new ::Ifc4x2::IfcWindowStyle(data);
            case 1208: return new ::Ifc4x2::IfcWindowStyleConstructionEnum(data);
            case 1209: return new ::Ifc4x2::IfcWindowStyleOperationEnum(data);
            case 1210: return new ::Ifc4x2::IfcWindowType(data);
            case 1211: return new ::Ifc4x2::IfcWindowTypeEnum(data);
            case 1212: return new ::Ifc4x2::IfcWindowTypePartitioningEnum(data);
            case 1213: return new ::Ifc4x2::IfcWorkCalendar(data);
            case 1214: return new ::Ifc4x2::IfcWorkCalendarTypeEnum(data);
            case 1215: return new ::Ifc4x2::IfcWorkControl(data);
            case 1216: return new ::Ifc4x2::IfcWorkPlan(data);
            case 1217: return new ::Ifc4x2::IfcWorkPlanTypeEnum(data);
            case 1218: return new ::Ifc4x2::IfcWorkSchedule(data);
            case 1219: return new ::Ifc4x2::IfcWorkScheduleTypeEnum(data);
            case 1220: return new ::Ifc4x2::IfcWorkTime(data);
            case 1221: return new ::Ifc4x2::IfcZone(data);
            case 1222: return new ::Ifc4x2::IfcZShapeProfileDef(data);
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
        
IfcParse::schema_definition* IFC4X2_populate_schema() {
    IFC4X2_types[0] = new type_declaration("IfcAbsorbedDoseMeasure", 0, new simple_type(simple_type::real_type));
    IFC4X2_types[1] = new type_declaration("IfcAccelerationMeasure", 1, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("EMAIL");
        items.push_back("FAX");
        items.push_back("NOTDEFINED");
        items.push_back("PHONE");
        items.push_back("POST");
        items.push_back("USERDEFINED");
        items.push_back("VERBAL");
        IFC4X2_types[3] = new enumeration_type("IfcActionRequestTypeEnum", 3, items);
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
        IFC4X2_types[4] = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IFC4X2_types[5] = new enumeration_type("IfcActionTypeEnum", 5, items);
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
        IFC4X2_types[11] = new enumeration_type("IfcActuatorTypeEnum", 11, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4X2_types[13] = new enumeration_type("IfcAddressTypeEnum", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IFC4X2_types[20] = new enumeration_type("IfcAirTerminalBoxTypeEnum", 20, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("DIFFUSER");
        items.push_back("GRILLE");
        items.push_back("LOUVRE");
        items.push_back("NOTDEFINED");
        items.push_back("REGISTER");
        items.push_back("USERDEFINED");
        IFC4X2_types[22] = new enumeration_type("IfcAirTerminalTypeEnum", 22, items);
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
        IFC4X2_types[25] = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 25, items);
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
        IFC4X2_types[28] = new enumeration_type("IfcAlarmTypeEnum", 28, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[39] = new enumeration_type("IfcAlignmentTypeEnum", 39, items);
    }
    IFC4X2_types[40] = new type_declaration("IfcAmountOfSubstanceMeasure", 40, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IFC4X2_types[41] = new enumeration_type("IfcAnalysisModelTypeEnum", 41, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IFC4X2_types[42] = new enumeration_type("IfcAnalysisTheoryTypeEnum", 42, items);
    }
    IFC4X2_types[43] = new type_declaration("IfcAngularVelocityMeasure", 43, new simple_type(simple_type::real_type));
    IFC4X2_types[55] = new type_declaration("IfcAreaDensityMeasure", 55, new simple_type(simple_type::real_type));
    IFC4X2_types[56] = new type_declaration("IfcAreaMeasure", 56, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IFC4X2_types[57] = new enumeration_type("IfcArithmeticOperatorEnum", 57, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IFC4X2_types[58] = new enumeration_type("IfcAssemblyPlaceEnum", 58, items);
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
        IFC4X2_types[63] = new enumeration_type("IfcAudioVisualApplianceTypeEnum", 63, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IFC4X2_types[105] = new enumeration_type("IfcBSplineCurveForm", 105, items);
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
        IFC4X2_types[108] = new enumeration_type("IfcBSplineSurfaceForm", 108, items);
    }
    {
        std::vector<std::string> items; items.reserve(14);
        items.push_back("BEAM");
        items.push_back("CORNICE");
        items.push_back("DIAPHRAGM");
        items.push_back("EDGEBEAM");
        items.push_back("GIRDER_SEGMENT");
        items.push_back("HATSTONE");
        items.push_back("HOLLOWCORE");
        items.push_back("JOIST");
        items.push_back("LINTEL");
        items.push_back("NOTDEFINED");
        items.push_back("PIERCAP");
        items.push_back("SPANDREL");
        items.push_back("T_BEAM");
        items.push_back("USERDEFINED");
        IFC4X2_types[71] = new enumeration_type("IfcBeamTypeEnum", 71, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FIXED_MOVEMENT");
        items.push_back("FREE_MOVEMENT");
        items.push_back("GUIDED_LONGITUDINAL");
        items.push_back("GUIDED_TRANSVERSAL");
        items.push_back("NOTDEFINED");
        IFC4X2_types[74] = new enumeration_type("IfcBearingTypeDisplacementEnum", 74, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("CYLINDRICAL");
        items.push_back("DISK");
        items.push_back("ELASTOMERIC");
        items.push_back("GUIDE");
        items.push_back("NOTDEFINED");
        items.push_back("POT");
        items.push_back("ROCKER");
        items.push_back("ROLLER");
        items.push_back("SPHERICAL");
        items.push_back("USERDEFINED");
        IFC4X2_types[75] = new enumeration_type("IfcBearingTypeEnum", 75, items);
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
        IFC4X2_types[76] = new enumeration_type("IfcBenchmarkEnum", 76, items);
    }
    IFC4X2_types[78] = new type_declaration("IfcBinary", 78, new simple_type(simple_type::binary_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IFC4X2_types[83] = new enumeration_type("IfcBoilerTypeEnum", 83, items);
    }
    IFC4X2_types[84] = new type_declaration("IfcBoolean", 84, new simple_type(simple_type::boolean_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IFC4X2_types[87] = new enumeration_type("IfcBooleanOperator", 87, items);
    }
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("ABUTMENT");
        items.push_back("DECK");
        items.push_back("DECK_SEGMENT");
        items.push_back("FOUNDATION");
        items.push_back("NOTDEFINED");
        items.push_back("PIER");
        items.push_back("PIER_SEGMENT");
        items.push_back("PYLON");
        items.push_back("SUBSTRUCTURE");
        items.push_back("SUPERSTRUCTURE");
        items.push_back("SURFACESTRUCTURE");
        items.push_back("USERDEFINED");
        IFC4X2_types[102] = new enumeration_type("IfcBridgePartTypeEnum", 102, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("ARCHED");
        items.push_back("CABLE_STAYED");
        items.push_back("CANTILEVER");
        items.push_back("CULVERT");
        items.push_back("FRAMEWORK");
        items.push_back("GIRDER");
        items.push_back("NOTDEFINED");
        items.push_back("SUSPENSION");
        items.push_back("TRUSS");
        items.push_back("USERDEFINED");
        IFC4X2_types[103] = new enumeration_type("IfcBridgeTypeEnum", 103, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("APRON");
        items.push_back("INSULATION");
        items.push_back("NOTDEFINED");
        items.push_back("PRECASTPANEL");
        items.push_back("USERDEFINED");
        IFC4X2_types[114] = new enumeration_type("IfcBuildingElementPartTypeEnum", 114, items);
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
        IFC4X2_types[117] = new enumeration_type("IfcBuildingElementProxyTypeEnum", 117, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("FENESTRATION");
        items.push_back("FOUNDATION");
        items.push_back("LOADBEARING");
        items.push_back("NOTDEFINED");
        items.push_back("OUTERSHELL");
        items.push_back("PRESTRESSING");
        items.push_back("REINFORCING");
        items.push_back("SHADING");
        items.push_back("TRANSPORT");
        items.push_back("USERDEFINED");
        IFC4X2_types[121] = new enumeration_type("IfcBuildingSystemTypeEnum", 121, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[124] = new enumeration_type("IfcBurnerTypeEnum", 124, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IFC4X2_types[127] = new enumeration_type("IfcCableCarrierFittingTypeEnum", 127, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[130] = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 130, items);
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
        IFC4X2_types[133] = new enumeration_type("IfcCableFittingTypeEnum", 133, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BUSBARSEGMENT");
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("CORESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[136] = new enumeration_type("IfcCableSegmentTypeEnum", 136, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CAISSON");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WELL");
        IFC4X2_types[139] = new enumeration_type("IfcCaissonFoundationTypeEnum", 139, items);
    }
    IFC4X2_types[140] = new type_declaration("IfcCardinalPointReference", 140, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("NOCHANGE");
        items.push_back("NOTDEFINED");
        IFC4X2_types[151] = new enumeration_type("IfcChangeActionEnum", 151, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IFC4X2_types[154] = new enumeration_type("IfcChillerTypeEnum", 154, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[157] = new enumeration_type("IfcChimneyTypeEnum", 157, items);
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
        IFC4X2_types[171] = new enumeration_type("IfcCoilTypeEnum", 171, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("PIERSTEM");
        items.push_back("PIERSTEM_SEGMENT");
        items.push_back("PILASTER");
        items.push_back("STANDCOLUMN");
        items.push_back("USERDEFINED");
        IFC4X2_types[180] = new enumeration_type("IfcColumnTypeEnum", 180, items);
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
        IFC4X2_types[183] = new enumeration_type("IfcCommunicationsApplianceTypeEnum", 183, items);
    }
    IFC4X2_types[184] = new type_declaration("IfcComplexNumber", 184, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("P_COMPLEX");
        items.push_back("Q_COMPLEX");
        IFC4X2_types[187] = new enumeration_type("IfcComplexPropertyTemplateTypeEnum", 187, items);
    }
    IFC4X2_types[192] = new type_declaration("IfcCompoundPlaneAngleMeasure", 192, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
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
        IFC4X2_types[195] = new enumeration_type("IfcCompressorTypeEnum", 195, items);
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
        IFC4X2_types[198] = new enumeration_type("IfcCondenserTypeEnum", 198, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IFC4X2_types[206] = new enumeration_type("IfcConnectionTypeEnum", 206, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IFC4X2_types[209] = new enumeration_type("IfcConstraintEnum", 209, items);
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
        IFC4X2_types[212] = new enumeration_type("IfcConstructionEquipmentResourceTypeEnum", 212, items);
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
        IFC4X2_types[215] = new enumeration_type("IfcConstructionMaterialResourceTypeEnum", 215, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ASSEMBLY");
        items.push_back("FORMWORK");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[218] = new enumeration_type("IfcConstructionProductResourceTypeEnum", 218, items);
    }
    IFC4X2_types[222] = new type_declaration("IfcContextDependentMeasure", 222, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("FLOATING");
        items.push_back("MULTIPOSITION");
        items.push_back("NOTDEFINED");
        items.push_back("PROGRAMMABLE");
        items.push_back("PROPORTIONAL");
        items.push_back("TWOPOSITION");
        items.push_back("USERDEFINED");
        IFC4X2_types[227] = new enumeration_type("IfcControllerTypeEnum", 227, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IFC4X2_types[232] = new enumeration_type("IfcCooledBeamTypeEnum", 232, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[235] = new enumeration_type("IfcCoolingTowerTypeEnum", 235, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[240] = new enumeration_type("IfcCostItemTypeEnum", 240, items);
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
        IFC4X2_types[242] = new enumeration_type("IfcCostScheduleTypeEnum", 242, items);
    }
    IFC4X2_types[244] = new type_declaration("IfcCountMeasure", 244, new simple_type(simple_type::number_type));
    {
        std::vector<std::string> items; items.reserve(13);
        items.push_back("CEILING");
        items.push_back("CLADDING");
        items.push_back("COPING");
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
        IFC4X2_types[247] = new enumeration_type("IfcCoveringTypeEnum", 247, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4X2_types[250] = new enumeration_type("IfcCrewResourceTypeEnum", 250, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[258] = new enumeration_type("IfcCurtainWallTypeEnum", 258, items);
    }
    IFC4X2_types[259] = new type_declaration("IfcCurvatureMeasure", 259, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LINEAR");
        items.push_back("LOG_LINEAR");
        items.push_back("LOG_LOG");
        items.push_back("NOTDEFINED");
        IFC4X2_types[264] = new enumeration_type("IfcCurveInterpolationEnum", 264, items);
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
        IFC4X2_types[276] = new enumeration_type("IfcDamperTypeEnum", 276, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IFC4X2_types[277] = new enumeration_type("IfcDataOriginEnum", 277, items);
    }
    IFC4X2_types[278] = new type_declaration("IfcDate", 278, new simple_type(simple_type::string_type));
    IFC4X2_types[279] = new type_declaration("IfcDateTime", 279, new simple_type(simple_type::string_type));
    IFC4X2_types[280] = new type_declaration("IfcDayInMonthNumber", 280, new simple_type(simple_type::integer_type));
    IFC4X2_types[281] = new type_declaration("IfcDayInWeekNumber", 281, new simple_type(simple_type::integer_type));
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
        IFC4X2_types[289] = new enumeration_type("IfcDerivedUnitEnum", 289, items);
    }
    IFC4X2_types[290] = new type_declaration("IfcDescriptiveMeasure", 290, new simple_type(simple_type::string_type));
    IFC4X2_types[292] = new type_declaration("IfcDimensionCount", 292, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4X2_types[294] = new enumeration_type("IfcDirectionSenseEnum", 294, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ANCHORPLATE");
        items.push_back("BRACKET");
        items.push_back("EXPANSION_JOINT_DEVICE");
        items.push_back("NOTDEFINED");
        items.push_back("SHOE");
        items.push_back("USERDEFINED");
        IFC4X2_types[297] = new enumeration_type("IfcDiscreteAccessoryTypeEnum", 297, items);
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
        IFC4X2_types[301] = new enumeration_type("IfcDistributionChamberElementTypeEnum", 301, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLE");
        items.push_back("CABLECARRIER");
        items.push_back("DUCT");
        items.push_back("NOTDEFINED");
        items.push_back("PIPE");
        items.push_back("USERDEFINED");
        IFC4X2_types[310] = new enumeration_type("IfcDistributionPortTypeEnum", 310, items);
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
        IFC4X2_types[312] = new enumeration_type("IfcDistributionSystemEnum", 312, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IFC4X2_types[313] = new enumeration_type("IfcDocumentConfidentialityEnum", 313, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IFC4X2_types[318] = new enumeration_type("IfcDocumentStatusEnum", 318, items);
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
        IFC4X2_types[321] = new enumeration_type("IfcDoorPanelOperationEnum", 321, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IFC4X2_types[322] = new enumeration_type("IfcDoorPanelPositionEnum", 322, items);
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
        IFC4X2_types[326] = new enumeration_type("IfcDoorStyleConstructionEnum", 326, items);
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
        IFC4X2_types[327] = new enumeration_type("IfcDoorStyleOperationEnum", 327, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DOOR");
        items.push_back("GATE");
        items.push_back("NOTDEFINED");
        items.push_back("TRAPDOOR");
        items.push_back("USERDEFINED");
        IFC4X2_types[329] = new enumeration_type("IfcDoorTypeEnum", 329, items);
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
        IFC4X2_types[330] = new enumeration_type("IfcDoorTypeOperationEnum", 330, items);
    }
    IFC4X2_types[331] = new type_declaration("IfcDoseEquivalentMeasure", 331, new simple_type(simple_type::real_type));
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
        IFC4X2_types[336] = new enumeration_type("IfcDuctFittingTypeEnum", 336, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IFC4X2_types[339] = new enumeration_type("IfcDuctSegmentTypeEnum", 339, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IFC4X2_types[342] = new enumeration_type("IfcDuctSilencerTypeEnum", 342, items);
    }
    IFC4X2_types[343] = new type_declaration("IfcDuration", 343, new simple_type(simple_type::string_type));
    IFC4X2_types[344] = new type_declaration("IfcDynamicViscosityMeasure", 344, new simple_type(simple_type::real_type));
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
        IFC4X2_types[350] = new enumeration_type("IfcElectricApplianceTypeEnum", 350, items);
    }
    IFC4X2_types[351] = new type_declaration("IfcElectricCapacitanceMeasure", 351, new simple_type(simple_type::real_type));
    IFC4X2_types[352] = new type_declaration("IfcElectricChargeMeasure", 352, new simple_type(simple_type::real_type));
    IFC4X2_types[353] = new type_declaration("IfcElectricConductanceMeasure", 353, new simple_type(simple_type::real_type));
    IFC4X2_types[354] = new type_declaration("IfcElectricCurrentMeasure", 354, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONSUMERUNIT");
        items.push_back("DISTRIBUTIONBOARD");
        items.push_back("MOTORCONTROLCENTRE");
        items.push_back("NOTDEFINED");
        items.push_back("SWITCHBOARD");
        items.push_back("USERDEFINED");
        IFC4X2_types[357] = new enumeration_type("IfcElectricDistributionBoardTypeEnum", 357, items);
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
        IFC4X2_types[360] = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 360, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CHP");
        items.push_back("ENGINEGENERATOR");
        items.push_back("NOTDEFINED");
        items.push_back("STANDALONE");
        items.push_back("USERDEFINED");
        IFC4X2_types[363] = new enumeration_type("IfcElectricGeneratorTypeEnum", 363, items);
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
        IFC4X2_types[366] = new enumeration_type("IfcElectricMotorTypeEnum", 366, items);
    }
    IFC4X2_types[367] = new type_declaration("IfcElectricResistanceMeasure", 367, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IFC4X2_types[370] = new enumeration_type("IfcElectricTimeControlTypeEnum", 370, items);
    }
    IFC4X2_types[371] = new type_declaration("IfcElectricVoltageMeasure", 371, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(16);
        items.push_back("ABUTMENT");
        items.push_back("ACCESSORY_ASSEMBLY");
        items.push_back("ARCH");
        items.push_back("BEAM_GRID");
        items.push_back("BRACED_FRAME");
        items.push_back("CROSS_BRACING");
        items.push_back("DECK");
        items.push_back("GIRDER");
        items.push_back("NOTDEFINED");
        items.push_back("PIER");
        items.push_back("PYLON");
        items.push_back("REINFORCEMENT_UNIT");
        items.push_back("RIGID_FRAME");
        items.push_back("SLAB_FIELD");
        items.push_back("TRUSS");
        items.push_back("USERDEFINED");
        IFC4X2_types[376] = new enumeration_type("IfcElementAssemblyTypeEnum", 376, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IFC4X2_types[379] = new enumeration_type("IfcElementCompositionEnum", 379, items);
    }
    IFC4X2_types[386] = new type_declaration("IfcEnergyMeasure", 386, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("EXTERNALCOMBUSTION");
        items.push_back("INTERNALCOMBUSTION");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[389] = new enumeration_type("IfcEngineTypeEnum", 389, items);
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
        IFC4X2_types[392] = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 392, items);
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
        IFC4X2_types[395] = new enumeration_type("IfcEvaporatorTypeEnum", 395, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EVENTCOMPLEX");
        items.push_back("EVENTMESSAGE");
        items.push_back("EVENTRULE");
        items.push_back("EVENTTIME");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[398] = new enumeration_type("IfcEventTriggerTypeEnum", 398, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ENDEVENT");
        items.push_back("INTERMEDIATEEVENT");
        items.push_back("NOTDEFINED");
        items.push_back("STARTEVENT");
        items.push_back("USERDEFINED");
        IFC4X2_types[400] = new enumeration_type("IfcEventTypeEnum", 400, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[409] = new enumeration_type("IfcExternalSpatialElementTypeEnum", 409, items);
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
        IFC4X2_types[425] = new enumeration_type("IfcFanTypeEnum", 425, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GLUE");
        items.push_back("MORTAR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WELD");
        IFC4X2_types[428] = new enumeration_type("IfcFastenerTypeEnum", 428, items);
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
        IFC4X2_types[438] = new enumeration_type("IfcFilterTypeEnum", 438, items);
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
        IFC4X2_types[441] = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 441, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IFC4X2_types[445] = new enumeration_type("IfcFlowDirectionEnum", 445, items);
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
        IFC4X2_types[450] = new enumeration_type("IfcFlowInstrumentTypeEnum", 450, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ENERGYMETER");
        items.push_back("GASMETER");
        items.push_back("NOTDEFINED");
        items.push_back("OILMETER");
        items.push_back("USERDEFINED");
        items.push_back("WATERMETER");
        IFC4X2_types[453] = new enumeration_type("IfcFlowMeterTypeEnum", 453, items);
    }
    IFC4X2_types[464] = new type_declaration("IfcFontStyle", 464, new simple_type(simple_type::string_type));
    IFC4X2_types[465] = new type_declaration("IfcFontVariant", 465, new simple_type(simple_type::string_type));
    IFC4X2_types[466] = new type_declaration("IfcFontWeight", 466, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CAISSON_FOUNDATION");
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IFC4X2_types[469] = new enumeration_type("IfcFootingTypeEnum", 469, items);
    }
    IFC4X2_types[470] = new type_declaration("IfcForceMeasure", 470, new simple_type(simple_type::real_type));
    IFC4X2_types[471] = new type_declaration("IfcFrequencyMeasure", 471, new simple_type(simple_type::real_type));
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
        IFC4X2_types[476] = new enumeration_type("IfcFurnitureTypeEnum", 476, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SOIL_BORING_POINT");
        items.push_back("TERRAIN");
        items.push_back("USERDEFINED");
        IFC4X2_types[479] = new enumeration_type("IfcGeographicElementTypeEnum", 479, items);
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
        IFC4X2_types[481] = new enumeration_type("IfcGeometricProjectionEnum", 481, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IFC4X2_types[488] = new enumeration_type("IfcGlobalOrLocalEnum", 488, items);
    }
    IFC4X2_types[487] = new type_declaration("IfcGloballyUniqueId", 487, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("IRREGULAR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIAL");
        items.push_back("RECTANGULAR");
        items.push_back("TRIANGULAR");
        items.push_back("USERDEFINED");
        IFC4X2_types[493] = new enumeration_type("IfcGridTypeEnum", 493, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IFC4X2_types[499] = new enumeration_type("IfcHeatExchangerTypeEnum", 499, items);
    }
    IFC4X2_types[500] = new type_declaration("IfcHeatFluxDensityMeasure", 500, new simple_type(simple_type::real_type));
    IFC4X2_types[501] = new type_declaration("IfcHeatingValueMeasure", 501, new simple_type(simple_type::real_type));
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
        IFC4X2_types[504] = new enumeration_type("IfcHumidifierTypeEnum", 504, items);
    }
    IFC4X2_types[505] = new type_declaration("IfcIdentifier", 505, new simple_type(simple_type::string_type));
    IFC4X2_types[506] = new type_declaration("IfcIlluminanceMeasure", 506, new simple_type(simple_type::real_type));
    IFC4X2_types[514] = new type_declaration("IfcInductanceMeasure", 514, new simple_type(simple_type::real_type));
    IFC4X2_types[515] = new type_declaration("IfcInteger", 515, new simple_type(simple_type::integer_type));
    IFC4X2_types[516] = new type_declaration("IfcIntegerCountRateMeasure", 516, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CYCLONIC");
        items.push_back("GREASE");
        items.push_back("NOTDEFINED");
        items.push_back("OIL");
        items.push_back("PETROL");
        items.push_back("USERDEFINED");
        IFC4X2_types[519] = new enumeration_type("IfcInterceptorTypeEnum", 519, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IFC4X2_types[520] = new enumeration_type("IfcInternalOrExternalEnum", 520, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IFC4X2_types[523] = new enumeration_type("IfcInventoryTypeEnum", 523, items);
    }
    IFC4X2_types[524] = new type_declaration("IfcIonConcentrationMeasure", 524, new simple_type(simple_type::real_type));
    IFC4X2_types[528] = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 528, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DATA");
        items.push_back("NOTDEFINED");
        items.push_back("POWER");
        items.push_back("USERDEFINED");
        IFC4X2_types[531] = new enumeration_type("IfcJunctionBoxTypeEnum", 531, items);
    }
    IFC4X2_types[532] = new type_declaration("IfcKinematicViscosityMeasure", 532, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("PIECEWISE_BEZIER_KNOTS");
        items.push_back("QUASI_UNIFORM_KNOTS");
        items.push_back("UNIFORM_KNOTS");
        items.push_back("UNSPECIFIED");
        IFC4X2_types[533] = new enumeration_type("IfcKnotType", 533, items);
    }
    IFC4X2_types[534] = new type_declaration("IfcLabel", 534, new simple_type(simple_type::string_type));
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
        IFC4X2_types[537] = new enumeration_type("IfcLaborResourceTypeEnum", 537, items);
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
        IFC4X2_types[541] = new enumeration_type("IfcLampTypeEnum", 541, items);
    }
    IFC4X2_types[542] = new type_declaration("IfcLanguageId", 542, new named_type(IFC4X2_types[505]));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IFC4X2_types[544] = new enumeration_type("IfcLayerSetDirectionEnum", 544, items);
    }
    IFC4X2_types[545] = new type_declaration("IfcLengthMeasure", 545, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IFC4X2_types[549] = new enumeration_type("IfcLightDistributionCurveEnum", 549, items);
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
        IFC4X2_types[552] = new enumeration_type("IfcLightEmissionSourceEnum", 552, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("SECURITYLIGHTING");
        items.push_back("USERDEFINED");
        IFC4X2_types[555] = new enumeration_type("IfcLightFixtureTypeEnum", 555, items);
    }
    IFC4X2_types[564] = new type_declaration("IfcLinearForceMeasure", 564, new simple_type(simple_type::real_type));
    IFC4X2_types[565] = new type_declaration("IfcLinearMomentMeasure", 565, new simple_type(simple_type::real_type));
    IFC4X2_types[568] = new type_declaration("IfcLinearStiffnessMeasure", 568, new simple_type(simple_type::real_type));
    IFC4X2_types[569] = new type_declaration("IfcLinearVelocityMeasure", 569, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[572] = new enumeration_type("IfcLoadGroupTypeEnum", 572, items);
    }
    IFC4X2_types[574] = new type_declaration("IfcLogical", 574, new simple_type(simple_type::logical_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALNOTAND");
        items.push_back("LOGICALNOTOR");
        items.push_back("LOGICALOR");
        items.push_back("LOGICALXOR");
        IFC4X2_types[575] = new enumeration_type("IfcLogicalOperatorEnum", 575, items);
    }
    IFC4X2_types[578] = new type_declaration("IfcLuminousFluxMeasure", 578, new simple_type(simple_type::real_type));
    IFC4X2_types[579] = new type_declaration("IfcLuminousIntensityDistributionMeasure", 579, new simple_type(simple_type::real_type));
    IFC4X2_types[580] = new type_declaration("IfcLuminousIntensityMeasure", 580, new simple_type(simple_type::real_type));
    IFC4X2_types[581] = new type_declaration("IfcMagneticFluxDensityMeasure", 581, new simple_type(simple_type::real_type));
    IFC4X2_types[582] = new type_declaration("IfcMagneticFluxMeasure", 582, new simple_type(simple_type::real_type));
    IFC4X2_types[586] = new type_declaration("IfcMassDensityMeasure", 586, new simple_type(simple_type::real_type));
    IFC4X2_types[587] = new type_declaration("IfcMassFlowRateMeasure", 587, new simple_type(simple_type::real_type));
    IFC4X2_types[588] = new type_declaration("IfcMassMeasure", 588, new simple_type(simple_type::real_type));
    IFC4X2_types[589] = new type_declaration("IfcMassPerLengthMeasure", 589, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(13);
        items.push_back("ANCHORBOLT");
        items.push_back("BOLT");
        items.push_back("COUPLER");
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
        IFC4X2_types[614] = new enumeration_type("IfcMechanicalFastenerTypeEnum", 614, items);
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
        IFC4X2_types[617] = new enumeration_type("IfcMedicalDeviceTypeEnum", 617, items);
    }
    {
        std::vector<std::string> items; items.reserve(19);
        items.push_back("ARCH_SEGMENT");
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
        items.push_back("STAY_CABLE");
        items.push_back("STIFFENING_RIB");
        items.push_back("STRINGER");
        items.push_back("STRUT");
        items.push_back("STUD");
        items.push_back("SUSPENDER");
        items.push_back("SUSPENSION_CABLE");
        items.push_back("USERDEFINED");
        IFC4X2_types[621] = new enumeration_type("IfcMemberTypeEnum", 621, items);
    }
    IFC4X2_types[625] = new type_declaration("IfcModulusOfElasticityMeasure", 625, new simple_type(simple_type::real_type));
    IFC4X2_types[626] = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 626, new simple_type(simple_type::real_type));
    IFC4X2_types[627] = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 627, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[627]);
        IFC4X2_types[628] = new select_type("IfcModulusOfRotationalSubgradeReactionSelect", 628, items);
    }
    IFC4X2_types[629] = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 629, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[629]);
        IFC4X2_types[630] = new select_type("IfcModulusOfSubgradeReactionSelect", 630, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[626]);
        IFC4X2_types[631] = new select_type("IfcModulusOfTranslationalSubgradeReactionSelect", 631, items);
    }
    IFC4X2_types[632] = new type_declaration("IfcMoistureDiffusivityMeasure", 632, new simple_type(simple_type::real_type));
    IFC4X2_types[633] = new type_declaration("IfcMolecularWeightMeasure", 633, new simple_type(simple_type::real_type));
    IFC4X2_types[634] = new type_declaration("IfcMomentOfInertiaMeasure", 634, new simple_type(simple_type::real_type));
    IFC4X2_types[635] = new type_declaration("IfcMonetaryMeasure", 635, new simple_type(simple_type::real_type));
    IFC4X2_types[637] = new type_declaration("IfcMonthInYearNumber", 637, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[640] = new enumeration_type("IfcMotorConnectionTypeEnum", 640, items);
    }
    IFC4X2_types[642] = new type_declaration("IfcNonNegativeLengthMeasure", 642, new named_type(IFC4X2_types[545]));
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IFC4X2_types[644] = new enumeration_type("IfcNullStyle", 644, items);
    }
    IFC4X2_types[645] = new type_declaration("IfcNumericMeasure", 645, new simple_type(simple_type::number_type));
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
        IFC4X2_types[652] = new enumeration_type("IfcObjectTypeEnum", 652, items);
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
        IFC4X2_types[649] = new enumeration_type("IfcObjectiveEnum", 649, items);
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
        IFC4X2_types[654] = new enumeration_type("IfcOccupantTypeEnum", 654, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OPENING");
        items.push_back("RECESS");
        items.push_back("USERDEFINED");
        IFC4X2_types[660] = new enumeration_type("IfcOpeningElementTypeEnum", 660, items);
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
        IFC4X2_types[670] = new enumeration_type("IfcOutletTypeEnum", 670, items);
    }
    IFC4X2_types[684] = new type_declaration("IfcPHMeasure", 684, new simple_type(simple_type::real_type));
    IFC4X2_types[673] = new type_declaration("IfcParameterValue", 673, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[677] = new enumeration_type("IfcPerformanceHistoryTypeEnum", 677, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IFC4X2_types[678] = new enumeration_type("IfcPermeableCoveringOperationEnum", 678, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACCESS");
        items.push_back("BUILDING");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4X2_types[681] = new enumeration_type("IfcPermitTypeEnum", 681, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IFC4X2_types[686] = new enumeration_type("IfcPhysicalOrVirtualEnum", 686, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IFC4X2_types[690] = new enumeration_type("IfcPileConstructionEnum", 690, items);
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
        IFC4X2_types[692] = new enumeration_type("IfcPileTypeEnum", 692, items);
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
        IFC4X2_types[695] = new enumeration_type("IfcPipeFittingTypeEnum", 695, items);
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
        IFC4X2_types[698] = new enumeration_type("IfcPipeSegmentTypeEnum", 698, items);
    }
    IFC4X2_types[703] = new type_declaration("IfcPlanarForceMeasure", 703, new simple_type(simple_type::real_type));
    IFC4X2_types[705] = new type_declaration("IfcPlaneAngleMeasure", 705, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("BASE_PLATE");
        items.push_back("COVER_PLATE");
        items.push_back("CURTAIN_PANEL");
        items.push_back("FLANGE_PLATE");
        items.push_back("GUSSET_PLATE");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("SPLICE_PLATE");
        items.push_back("STIFFENER_PLATE");
        items.push_back("USERDEFINED");
        items.push_back("WEB_PLATE");
        IFC4X2_types[709] = new enumeration_type("IfcPlateTypeEnum", 709, items);
    }
    IFC4X2_types[720] = new type_declaration("IfcPositiveInteger", 720, new named_type(IFC4X2_types[515]));
    IFC4X2_types[721] = new type_declaration("IfcPositiveLengthMeasure", 721, new named_type(IFC4X2_types[545]));
    IFC4X2_types[722] = new type_declaration("IfcPositivePlaneAngleMeasure", 722, new named_type(IFC4X2_types[705]));
    IFC4X2_types[725] = new type_declaration("IfcPowerMeasure", 725, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CURVE3D");
        items.push_back("PCURVE_S1");
        items.push_back("PCURVE_S2");
        IFC4X2_types[732] = new enumeration_type("IfcPreferredSurfaceCurveRepresentation", 732, items);
    }
    IFC4X2_types[733] = new type_declaration("IfcPresentableText", 733, new simple_type(simple_type::string_type));
    IFC4X2_types[740] = new type_declaration("IfcPressureMeasure", 740, new simple_type(simple_type::real_type));
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
        IFC4X2_types[743] = new enumeration_type("IfcProcedureTypeEnum", 743, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IFC4X2_types[753] = new enumeration_type("IfcProfileTypeEnum", 753, items);
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
        IFC4X2_types[761] = new enumeration_type("IfcProjectOrderTypeEnum", 761, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IFC4X2_types[756] = new enumeration_type("IfcProjectedOrTrueLengthEnum", 756, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("BLISTER");
        items.push_back("DEVIATOR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[758] = new enumeration_type("IfcProjectionElementTypeEnum", 758, items);
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
        IFC4X2_types[776] = new enumeration_type("IfcPropertySetTemplateTypeEnum", 776, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ELECTROMAGNETIC");
        items.push_back("ELECTRONIC");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENT");
        items.push_back("THERMAL");
        items.push_back("USERDEFINED");
        IFC4X2_types[784] = new enumeration_type("IfcProtectiveDeviceTrippingUnitTypeEnum", 784, items);
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
        IFC4X2_types[786] = new enumeration_type("IfcProtectiveDeviceTypeEnum", 786, items);
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
        IFC4X2_types[790] = new enumeration_type("IfcPumpTypeEnum", 790, items);
    }
    IFC4X2_types[798] = new type_declaration("IfcRadioActivityMeasure", 798, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[801] = new enumeration_type("IfcRailingTypeEnum", 801, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IFC4X2_types[805] = new enumeration_type("IfcRampFlightTypeEnum", 805, items);
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
        IFC4X2_types[807] = new enumeration_type("IfcRampTypeEnum", 807, items);
    }
    IFC4X2_types[808] = new type_declaration("IfcRatioMeasure", 808, new simple_type(simple_type::real_type));
    IFC4X2_types[811] = new type_declaration("IfcReal", 811, new simple_type(simple_type::real_type));
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
        IFC4X2_types[817] = new enumeration_type("IfcRecurrenceTypeEnum", 817, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("KILOPOINT");
        items.push_back("MILEPOINT");
        items.push_back("NOTDEFINED");
        items.push_back("STATION");
        items.push_back("USERDEFINED");
        IFC4X2_types[820] = new enumeration_type("IfcReferentTypeEnum", 820, items);
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
        IFC4X2_types[821] = new enumeration_type("IfcReflectanceMethodEnum", 821, items);
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
        IFC4X2_types[826] = new enumeration_type("IfcReinforcingBarRoleEnum", 826, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IFC4X2_types[827] = new enumeration_type("IfcReinforcingBarSurfaceEnum", 827, items);
    }
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("ANCHORING");
        items.push_back("EDGE");
        items.push_back("LIGATURE");
        items.push_back("MAIN");
        items.push_back("NOTDEFINED");
        items.push_back("PUNCHING");
        items.push_back("RING");
        items.push_back("SHEAR");
        items.push_back("SPACEBAR");
        items.push_back("STUD");
        items.push_back("USERDEFINED");
        IFC4X2_types[829] = new enumeration_type("IfcReinforcingBarTypeEnum", 829, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[834] = new enumeration_type("IfcReinforcingMeshTypeEnum", 834, items);
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
        IFC4X2_types[900] = new enumeration_type("IfcRoleEnum", 900, items);
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
        IFC4X2_types[903] = new enumeration_type("IfcRoofTypeEnum", 903, items);
    }
    IFC4X2_types[905] = new type_declaration("IfcRotationalFrequencyMeasure", 905, new simple_type(simple_type::real_type));
    IFC4X2_types[906] = new type_declaration("IfcRotationalMassMeasure", 906, new simple_type(simple_type::real_type));
    IFC4X2_types[907] = new type_declaration("IfcRotationalStiffnessMeasure", 907, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[907]);
        IFC4X2_types[908] = new select_type("IfcRotationalStiffnessSelect", 908, items);
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
        IFC4X2_types[941] = new enumeration_type("IfcSIPrefix", 941, items);
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
        IFC4X2_types[944] = new enumeration_type("IfcSIUnitName", 944, items);
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
        IFC4X2_types[912] = new enumeration_type("IfcSanitaryTerminalTypeEnum", 912, items);
    }
    IFC4X2_types[919] = new type_declaration("IfcSectionModulusMeasure", 919, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IFC4X2_types[922] = new enumeration_type("IfcSectionTypeEnum", 922, items);
    }
    IFC4X2_types[915] = new type_declaration("IfcSectionalAreaIntegralMeasure", 915, new simple_type(simple_type::real_type));
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
        IFC4X2_types[926] = new enumeration_type("IfcSensorTypeEnum", 926, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        items.push_back("USERDEFINED");
        IFC4X2_types[927] = new enumeration_type("IfcSequenceEnum", 927, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AWNING");
        items.push_back("JALOUSIE");
        items.push_back("NOTDEFINED");
        items.push_back("SHUTTER");
        items.push_back("USERDEFINED");
        IFC4X2_types[930] = new enumeration_type("IfcShadingDeviceTypeEnum", 930, items);
    }
    IFC4X2_types[934] = new type_declaration("IfcShearModulusMeasure", 934, new simple_type(simple_type::real_type));
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
        IFC4X2_types[939] = new enumeration_type("IfcSimplePropertyTemplateTypeEnum", 939, items);
    }
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("APPROACH_SLAB");
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("PAVING");
        items.push_back("ROOF");
        items.push_back("SIDEWALK");
        items.push_back("USERDEFINED");
        items.push_back("WEARING");
        IFC4X2_types[950] = new enumeration_type("IfcSlabTypeEnum", 950, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SOLARCOLLECTOR");
        items.push_back("SOLARPANEL");
        items.push_back("USERDEFINED");
        IFC4X2_types[954] = new enumeration_type("IfcSolarDeviceTypeEnum", 954, items);
    }
    IFC4X2_types[955] = new type_declaration("IfcSolidAngleMeasure", 955, new simple_type(simple_type::real_type));
    IFC4X2_types[958] = new type_declaration("IfcSoundPowerLevelMeasure", 958, new simple_type(simple_type::real_type));
    IFC4X2_types[959] = new type_declaration("IfcSoundPowerMeasure", 959, new simple_type(simple_type::real_type));
    IFC4X2_types[960] = new type_declaration("IfcSoundPressureLevelMeasure", 960, new simple_type(simple_type::real_type));
    IFC4X2_types[961] = new type_declaration("IfcSoundPressureMeasure", 961, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONVECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIATOR");
        items.push_back("USERDEFINED");
        IFC4X2_types[966] = new enumeration_type("IfcSpaceHeaterTypeEnum", 966, items);
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
        IFC4X2_types[968] = new enumeration_type("IfcSpaceTypeEnum", 968, items);
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
        IFC4X2_types[975] = new enumeration_type("IfcSpatialZoneTypeEnum", 975, items);
    }
    IFC4X2_types[976] = new type_declaration("IfcSpecificHeatCapacityMeasure", 976, new simple_type(simple_type::real_type));
    IFC4X2_types[977] = new type_declaration("IfcSpecularExponent", 977, new simple_type(simple_type::real_type));
    IFC4X2_types[979] = new type_declaration("IfcSpecularRoughness", 979, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IFC4X2_types[984] = new enumeration_type("IfcStackTerminalTypeEnum", 984, items);
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
        IFC4X2_types[988] = new enumeration_type("IfcStairFlightTypeEnum", 988, items);
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
        IFC4X2_types[990] = new enumeration_type("IfcStairTypeEnum", 990, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IFC4X2_types[991] = new enumeration_type("IfcStateEnum", 991, items);
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
        IFC4X2_types[999] = new enumeration_type("IfcStructuralCurveActivityTypeEnum", 999, items);
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
        IFC4X2_types[1002] = new enumeration_type("IfcStructuralCurveMemberTypeEnum", 1002, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BILINEAR");
        items.push_back("CONST");
        items.push_back("DISCRETE");
        items.push_back("ISOCONTOUR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[1028] = new enumeration_type("IfcStructuralSurfaceActivityTypeEnum", 1028, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IFC4X2_types[1031] = new enumeration_type("IfcStructuralSurfaceMemberTypeEnum", 1031, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4X2_types[1040] = new enumeration_type("IfcSubContractResourceTypeEnum", 1040, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("DEFECT");
        items.push_back("MARK");
        items.push_back("NOTDEFINED");
        items.push_back("TAG");
        items.push_back("TREATMENT");
        items.push_back("USERDEFINED");
        IFC4X2_types[1046] = new enumeration_type("IfcSurfaceFeatureTypeEnum", 1046, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4X2_types[1051] = new enumeration_type("IfcSurfaceSide", 1051, items);
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
        IFC4X2_types[1066] = new enumeration_type("IfcSwitchingDeviceTypeEnum", 1066, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PANEL");
        items.push_back("USERDEFINED");
        items.push_back("WORKSURFACE");
        IFC4X2_types[1070] = new enumeration_type("IfcSystemFurnitureElementTypeEnum", 1070, items);
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
        IFC4X2_types[1076] = new enumeration_type("IfcTankTypeEnum", 1076, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ELAPSEDTIME");
        items.push_back("NOTDEFINED");
        items.push_back("WORKTIME");
        IFC4X2_types[1078] = new enumeration_type("IfcTaskDurationEnum", 1078, items);
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
        IFC4X2_types[1082] = new enumeration_type("IfcTaskTypeEnum", 1082, items);
    }
    IFC4X2_types[1084] = new type_declaration("IfcTemperatureGradientMeasure", 1084, new simple_type(simple_type::real_type));
    IFC4X2_types[1085] = new type_declaration("IfcTemperatureRateOfChangeMeasure", 1085, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COUPLER");
        items.push_back("FIXED_END");
        items.push_back("NOTDEFINED");
        items.push_back("TENSIONING_END");
        items.push_back("USERDEFINED");
        IFC4X2_types[1089] = new enumeration_type("IfcTendonAnchorTypeEnum", 1089, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("COUPLER");
        items.push_back("DIABOLO");
        items.push_back("DUCT");
        items.push_back("GROUTING_DUCT");
        items.push_back("NOTDEFINED");
        items.push_back("TRUMPET");
        items.push_back("USERDEFINED");
        IFC4X2_types[1092] = new enumeration_type("IfcTendonConduitTypeEnum", 1092, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IFC4X2_types[1094] = new enumeration_type("IfcTendonTypeEnum", 1094, items);
    }
    IFC4X2_types[1097] = new type_declaration("IfcText", 1097, new simple_type(simple_type::string_type));
    IFC4X2_types[1098] = new type_declaration("IfcTextAlignment", 1098, new simple_type(simple_type::string_type));
    IFC4X2_types[1099] = new type_declaration("IfcTextDecoration", 1099, new simple_type(simple_type::string_type));
    IFC4X2_types[1100] = new type_declaration("IfcTextFontName", 1100, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IFC4X2_types[1104] = new enumeration_type("IfcTextPath", 1104, items);
    }
    IFC4X2_types[1109] = new type_declaration("IfcTextTransformation", 1109, new simple_type(simple_type::string_type));
    IFC4X2_types[1115] = new type_declaration("IfcThermalAdmittanceMeasure", 1115, new simple_type(simple_type::real_type));
    IFC4X2_types[1116] = new type_declaration("IfcThermalConductivityMeasure", 1116, new simple_type(simple_type::real_type));
    IFC4X2_types[1117] = new type_declaration("IfcThermalExpansionCoefficientMeasure", 1117, new simple_type(simple_type::real_type));
    IFC4X2_types[1118] = new type_declaration("IfcThermalResistanceMeasure", 1118, new simple_type(simple_type::real_type));
    IFC4X2_types[1119] = new type_declaration("IfcThermalTransmittanceMeasure", 1119, new simple_type(simple_type::real_type));
    IFC4X2_types[1120] = new type_declaration("IfcThermodynamicTemperatureMeasure", 1120, new simple_type(simple_type::real_type));
    IFC4X2_types[1121] = new type_declaration("IfcTime", 1121, new simple_type(simple_type::string_type));
    IFC4X2_types[1122] = new type_declaration("IfcTimeMeasure", 1122, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[343]);
        items.push_back(IFC4X2_types[808]);
        IFC4X2_types[1123] = new select_type("IfcTimeOrRatioSelect", 1123, items);
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
        IFC4X2_types[1126] = new enumeration_type("IfcTimeSeriesDataTypeEnum", 1126, items);
    }
    IFC4X2_types[1128] = new type_declaration("IfcTimeStamp", 1128, new simple_type(simple_type::integer_type));
    IFC4X2_types[1132] = new type_declaration("IfcTorqueMeasure", 1132, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("INVERTER");
        items.push_back("NOTDEFINED");
        items.push_back("RECTIFIER");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IFC4X2_types[1135] = new enumeration_type("IfcTransformerTypeEnum", 1135, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IFC4X2_types[1136] = new enumeration_type("IfcTransitionCode", 1136, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BIQUADRATICPARABOLA");
        items.push_back("BLOSSCURVE");
        items.push_back("CLOTHOIDCURVE");
        items.push_back("COSINECURVE");
        items.push_back("CUBICPARABOLA");
        items.push_back("SINECURVE");
        IFC4X2_types[1138] = new enumeration_type("IfcTransitionCurveType", 1138, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[568]);
        IFC4X2_types[1139] = new select_type("IfcTranslationalStiffnessSelect", 1139, items);
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
        IFC4X2_types[1142] = new enumeration_type("IfcTransportElementTypeEnum", 1142, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IFC4X2_types[1147] = new enumeration_type("IfcTrimmingPreference", 1147, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4X2_types[1152] = new enumeration_type("IfcTubeBundleTypeEnum", 1152, items);
    }
    IFC4X2_types[1166] = new type_declaration("IfcURIReference", 1166, new simple_type(simple_type::string_type));
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
        IFC4X2_types[1165] = new enumeration_type("IfcUnitEnum", 1165, items);
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
        IFC4X2_types[1160] = new enumeration_type("IfcUnitaryControlElementTypeEnum", 1160, items);
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
        IFC4X2_types[1163] = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 1163, items);
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
        IFC4X2_types[1171] = new enumeration_type("IfcValveTypeEnum", 1171, items);
    }
    IFC4X2_types[1172] = new type_declaration("IfcVaporPermeabilityMeasure", 1172, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("AXIAL_YIELD");
        items.push_back("BENDING_YIELD");
        items.push_back("FRICTION");
        items.push_back("NOTDEFINED");
        items.push_back("RUBBER");
        items.push_back("SHEAR_YIELD");
        items.push_back("USERDEFINED");
        items.push_back("VISCOUS");
        IFC4X2_types[1180] = new enumeration_type("IfcVibrationDamperTypeEnum", 1180, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BASE");
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IFC4X2_types[1183] = new enumeration_type("IfcVibrationIsolatorTypeEnum", 1183, items);
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
        IFC4X2_types[1187] = new enumeration_type("IfcVoidingFeatureTypeEnum", 1187, items);
    }
    IFC4X2_types[1188] = new type_declaration("IfcVolumeMeasure", 1188, new simple_type(simple_type::real_type));
    IFC4X2_types[1189] = new type_declaration("IfcVolumetricFlowRateMeasure", 1189, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("ELEMENTEDWALL");
        items.push_back("MOVABLE");
        items.push_back("NOTDEFINED");
        items.push_back("PARAPET");
        items.push_back("PARTITIONING");
        items.push_back("PLUMBINGWALL");
        items.push_back("POLYGONAL");
        items.push_back("RETAININGWALL");
        items.push_back("SHEAR");
        items.push_back("SOLIDWALL");
        items.push_back("STANDARD");
        items.push_back("USERDEFINED");
        IFC4X2_types[1194] = new enumeration_type("IfcWallTypeEnum", 1194, items);
    }
    IFC4X2_types[1195] = new type_declaration("IfcWarpingConstantMeasure", 1195, new simple_type(simple_type::real_type));
    IFC4X2_types[1196] = new type_declaration("IfcWarpingMomentMeasure", 1196, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[1196]);
        IFC4X2_types[1197] = new select_type("IfcWarpingStiffnessSelect", 1197, items);
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
        IFC4X2_types[1200] = new enumeration_type("IfcWasteTerminalTypeEnum", 1200, items);
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
        IFC4X2_types[1203] = new enumeration_type("IfcWindowPanelOperationEnum", 1203, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IFC4X2_types[1204] = new enumeration_type("IfcWindowPanelPositionEnum", 1204, items);
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
        IFC4X2_types[1208] = new enumeration_type("IfcWindowStyleConstructionEnum", 1208, items);
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
        IFC4X2_types[1209] = new enumeration_type("IfcWindowStyleOperationEnum", 1209, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LIGHTDOME");
        items.push_back("NOTDEFINED");
        items.push_back("SKYLIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDOW");
        IFC4X2_types[1211] = new enumeration_type("IfcWindowTypeEnum", 1211, items);
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
        IFC4X2_types[1212] = new enumeration_type("IfcWindowTypePartitioningEnum", 1212, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FIRSTSHIFT");
        items.push_back("NOTDEFINED");
        items.push_back("SECONDSHIFT");
        items.push_back("THIRDSHIFT");
        items.push_back("USERDEFINED");
        IFC4X2_types[1214] = new enumeration_type("IfcWorkCalendarTypeEnum", 1214, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4X2_types[1217] = new enumeration_type("IfcWorkPlanTypeEnum", 1217, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4X2_types[1219] = new enumeration_type("IfcWorkScheduleTypeEnum", 1219, items);
    }
    IFC4X2_types[7] = new entity("IfcActorRole", false, 7, (entity*) 0);
    IFC4X2_types[12] = new entity("IfcAddress", true, 12, (entity*) 0);
    IFC4X2_types[46] = new entity("IfcApplication", false, 46, (entity*) 0);
    IFC4X2_types[47] = new entity("IfcAppliedValue", false, 47, (entity*) 0);
    IFC4X2_types[49] = new entity("IfcApproval", false, 49, (entity*) 0);
    IFC4X2_types[89] = new entity("IfcBoundaryCondition", true, 89, (entity*) 0);
    IFC4X2_types[91] = new entity("IfcBoundaryEdgeCondition", false, 91, (entity*) IFC4X2_types[89]);
    IFC4X2_types[92] = new entity("IfcBoundaryFaceCondition", false, 92, (entity*) IFC4X2_types[89]);
    IFC4X2_types[93] = new entity("IfcBoundaryNodeCondition", false, 93, (entity*) IFC4X2_types[89]);
    IFC4X2_types[94] = new entity("IfcBoundaryNodeConditionWarping", false, 94, (entity*) IFC4X2_types[93]);
    IFC4X2_types[202] = new entity("IfcConnectionGeometry", true, 202, (entity*) 0);
    IFC4X2_types[204] = new entity("IfcConnectionPointGeometry", false, 204, (entity*) IFC4X2_types[202]);
    IFC4X2_types[205] = new entity("IfcConnectionSurfaceGeometry", false, 205, (entity*) IFC4X2_types[202]);
    IFC4X2_types[207] = new entity("IfcConnectionVolumeGeometry", false, 207, (entity*) IFC4X2_types[202]);
    IFC4X2_types[208] = new entity("IfcConstraint", true, 208, (entity*) 0);
    IFC4X2_types[236] = new entity("IfcCoordinateOperation", true, 236, (entity*) 0);
    IFC4X2_types[237] = new entity("IfcCoordinateReferenceSystem", true, 237, (entity*) 0);
    IFC4X2_types[243] = new entity("IfcCostValue", false, 243, (entity*) IFC4X2_types[47]);
    IFC4X2_types[287] = new entity("IfcDerivedUnit", false, 287, (entity*) 0);
    IFC4X2_types[288] = new entity("IfcDerivedUnitElement", false, 288, (entity*) 0);
    IFC4X2_types[291] = new entity("IfcDimensionalExponents", false, 291, (entity*) 0);
    IFC4X2_types[402] = new entity("IfcExternalInformation", true, 402, (entity*) 0);
    IFC4X2_types[406] = new entity("IfcExternalReference", true, 406, (entity*) 0);
    IFC4X2_types[403] = new entity("IfcExternallyDefinedHatchStyle", false, 403, (entity*) IFC4X2_types[406]);
    IFC4X2_types[404] = new entity("IfcExternallyDefinedSurfaceStyle", false, 404, (entity*) IFC4X2_types[406]);
    IFC4X2_types[405] = new entity("IfcExternallyDefinedTextFont", false, 405, (entity*) IFC4X2_types[406]);
    IFC4X2_types[490] = new entity("IfcGridAxis", false, 490, (entity*) 0);
    IFC4X2_types[526] = new entity("IfcIrregularTimeSeriesValue", false, 526, (entity*) 0);
    IFC4X2_types[546] = new entity("IfcLibraryInformation", false, 546, (entity*) IFC4X2_types[402]);
    IFC4X2_types[547] = new entity("IfcLibraryReference", false, 547, (entity*) IFC4X2_types[406]);
    IFC4X2_types[550] = new entity("IfcLightDistributionData", false, 550, (entity*) 0);
    IFC4X2_types[556] = new entity("IfcLightIntensityDistribution", false, 556, (entity*) 0);
    IFC4X2_types[584] = new entity("IfcMapConversion", false, 584, (entity*) IFC4X2_types[236]);
    IFC4X2_types[591] = new entity("IfcMaterialClassificationRelationship", false, 591, (entity*) 0);
    IFC4X2_types[594] = new entity("IfcMaterialDefinition", true, 594, (entity*) 0);
    IFC4X2_types[596] = new entity("IfcMaterialLayer", false, 596, (entity*) IFC4X2_types[594]);
    IFC4X2_types[597] = new entity("IfcMaterialLayerSet", false, 597, (entity*) IFC4X2_types[594]);
    IFC4X2_types[599] = new entity("IfcMaterialLayerWithOffsets", false, 599, (entity*) IFC4X2_types[596]);
    IFC4X2_types[600] = new entity("IfcMaterialList", false, 600, (entity*) 0);
    IFC4X2_types[601] = new entity("IfcMaterialProfile", false, 601, (entity*) IFC4X2_types[594]);
    IFC4X2_types[602] = new entity("IfcMaterialProfileSet", false, 602, (entity*) IFC4X2_types[594]);
    IFC4X2_types[605] = new entity("IfcMaterialProfileWithOffsets", false, 605, (entity*) IFC4X2_types[601]);
    IFC4X2_types[609] = new entity("IfcMaterialUsageDefinition", true, 609, (entity*) 0);
    IFC4X2_types[611] = new entity("IfcMeasureWithUnit", false, 611, (entity*) 0);
    IFC4X2_types[622] = new entity("IfcMetric", false, 622, (entity*) IFC4X2_types[208]);
    IFC4X2_types[636] = new entity("IfcMonetaryUnit", false, 636, (entity*) 0);
    IFC4X2_types[641] = new entity("IfcNamedUnit", true, 641, (entity*) 0);
    IFC4X2_types[650] = new entity("IfcObjectPlacement", true, 650, (entity*) 0);
    IFC4X2_types[648] = new entity("IfcObjective", false, 648, (entity*) IFC4X2_types[208]);
    IFC4X2_types[663] = new entity("IfcOrganization", false, 663, (entity*) 0);
    IFC4X2_types[671] = new entity("IfcOwnerHistory", false, 671, (entity*) 0);
    IFC4X2_types[682] = new entity("IfcPerson", false, 682, (entity*) 0);
    IFC4X2_types[683] = new entity("IfcPersonAndOrganization", false, 683, (entity*) 0);
    IFC4X2_types[687] = new entity("IfcPhysicalQuantity", true, 687, (entity*) 0);
    IFC4X2_types[688] = new entity("IfcPhysicalSimpleQuantity", true, 688, (entity*) IFC4X2_types[687]);
    IFC4X2_types[724] = new entity("IfcPostalAddress", false, 724, (entity*) IFC4X2_types[12]);
    IFC4X2_types[734] = new entity("IfcPresentationItem", true, 734, (entity*) 0);
    IFC4X2_types[735] = new entity("IfcPresentationLayerAssignment", false, 735, (entity*) 0);
    IFC4X2_types[736] = new entity("IfcPresentationLayerWithStyle", false, 736, (entity*) IFC4X2_types[735]);
    IFC4X2_types[737] = new entity("IfcPresentationStyle", true, 737, (entity*) 0);
    IFC4X2_types[738] = new entity("IfcPresentationStyleAssignment", false, 738, (entity*) 0);
    IFC4X2_types[748] = new entity("IfcProductRepresentation", true, 748, (entity*) 0);
    IFC4X2_types[751] = new entity("IfcProfileDef", false, 751, (entity*) 0);
    IFC4X2_types[755] = new entity("IfcProjectedCRS", false, 755, (entity*) IFC4X2_types[237]);
    IFC4X2_types[763] = new entity("IfcPropertyAbstraction", true, 763, (entity*) 0);
    IFC4X2_types[768] = new entity("IfcPropertyEnumeration", false, 768, (entity*) IFC4X2_types[763]);
    IFC4X2_types[791] = new entity("IfcQuantityArea", false, 791, (entity*) IFC4X2_types[688]);
    IFC4X2_types[792] = new entity("IfcQuantityCount", false, 792, (entity*) IFC4X2_types[688]);
    IFC4X2_types[793] = new entity("IfcQuantityLength", false, 793, (entity*) IFC4X2_types[688]);
    IFC4X2_types[795] = new entity("IfcQuantityTime", false, 795, (entity*) IFC4X2_types[688]);
    IFC4X2_types[796] = new entity("IfcQuantityVolume", false, 796, (entity*) IFC4X2_types[688]);
    IFC4X2_types[797] = new entity("IfcQuantityWeight", false, 797, (entity*) IFC4X2_types[688]);
    IFC4X2_types[816] = new entity("IfcRecurrencePattern", false, 816, (entity*) 0);
    IFC4X2_types[818] = new entity("IfcReference", false, 818, (entity*) 0);
    IFC4X2_types[885] = new entity("IfcRepresentation", true, 885, (entity*) 0);
    IFC4X2_types[886] = new entity("IfcRepresentationContext", true, 886, (entity*) 0);
    IFC4X2_types[887] = new entity("IfcRepresentationItem", true, 887, (entity*) 0);
    IFC4X2_types[888] = new entity("IfcRepresentationMap", false, 888, (entity*) 0);
    IFC4X2_types[892] = new entity("IfcResourceLevelRelationship", true, 892, (entity*) 0);
    IFC4X2_types[904] = new entity("IfcRoot", true, 904, (entity*) 0);
    IFC4X2_types[943] = new entity("IfcSIUnit", false, 943, (entity*) IFC4X2_types[641]);
    IFC4X2_types[913] = new entity("IfcSchedulingTime", true, 913, (entity*) 0);
    IFC4X2_types[931] = new entity("IfcShapeAspect", false, 931, (entity*) 0);
    IFC4X2_types[932] = new entity("IfcShapeModel", true, 932, (entity*) IFC4X2_types[885]);
    IFC4X2_types[933] = new entity("IfcShapeRepresentation", false, 933, (entity*) IFC4X2_types[932]);
    IFC4X2_types[997] = new entity("IfcStructuralConnectionCondition", true, 997, (entity*) 0);
    IFC4X2_types[1007] = new entity("IfcStructuralLoad", true, 1007, (entity*) 0);
    IFC4X2_types[1009] = new entity("IfcStructuralLoadConfiguration", false, 1009, (entity*) IFC4X2_types[1007]);
    IFC4X2_types[1012] = new entity("IfcStructuralLoadOrResult", true, 1012, (entity*) IFC4X2_types[1007]);
    IFC4X2_types[1018] = new entity("IfcStructuralLoadStatic", true, 1018, (entity*) IFC4X2_types[1012]);
    IFC4X2_types[1019] = new entity("IfcStructuralLoadTemperature", false, 1019, (entity*) IFC4X2_types[1018]);
    IFC4X2_types[1037] = new entity("IfcStyleModel", true, 1037, (entity*) IFC4X2_types[885]);
    IFC4X2_types[1035] = new entity("IfcStyledItem", false, 1035, (entity*) IFC4X2_types[887]);
    IFC4X2_types[1036] = new entity("IfcStyledRepresentation", false, 1036, (entity*) IFC4X2_types[1037]);
    IFC4X2_types[1050] = new entity("IfcSurfaceReinforcementArea", false, 1050, (entity*) IFC4X2_types[1012]);
    IFC4X2_types[1052] = new entity("IfcSurfaceStyle", false, 1052, (entity*) IFC4X2_types[737]);
    IFC4X2_types[1054] = new entity("IfcSurfaceStyleLighting", false, 1054, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1055] = new entity("IfcSurfaceStyleRefraction", false, 1055, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1057] = new entity("IfcSurfaceStyleShading", false, 1057, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1058] = new entity("IfcSurfaceStyleWithTextures", false, 1058, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1059] = new entity("IfcSurfaceTexture", true, 1059, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1071] = new entity("IfcTable", false, 1071, (entity*) 0);
    IFC4X2_types[1072] = new entity("IfcTableColumn", false, 1072, (entity*) 0);
    IFC4X2_types[1073] = new entity("IfcTableRow", false, 1073, (entity*) 0);
    IFC4X2_types[1079] = new entity("IfcTaskTime", false, 1079, (entity*) IFC4X2_types[913]);
    IFC4X2_types[1080] = new entity("IfcTaskTimeRecurring", false, 1080, (entity*) IFC4X2_types[1079]);
    IFC4X2_types[1083] = new entity("IfcTelecomAddress", false, 1083, (entity*) IFC4X2_types[12]);
    IFC4X2_types[1105] = new entity("IfcTextStyle", false, 1105, (entity*) IFC4X2_types[737]);
    IFC4X2_types[1107] = new entity("IfcTextStyleForDefinedFont", false, 1107, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1108] = new entity("IfcTextStyleTextModel", false, 1108, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1110] = new entity("IfcTextureCoordinate", true, 1110, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1111] = new entity("IfcTextureCoordinateGenerator", false, 1111, (entity*) IFC4X2_types[1110]);
    IFC4X2_types[1112] = new entity("IfcTextureMap", false, 1112, (entity*) IFC4X2_types[1110]);
    IFC4X2_types[1113] = new entity("IfcTextureVertex", false, 1113, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1114] = new entity("IfcTextureVertexList", false, 1114, (entity*) IFC4X2_types[734]);
    IFC4X2_types[1124] = new entity("IfcTimePeriod", false, 1124, (entity*) 0);
    IFC4X2_types[1125] = new entity("IfcTimeSeries", true, 1125, (entity*) 0);
    IFC4X2_types[1127] = new entity("IfcTimeSeriesValue", false, 1127, (entity*) 0);
    IFC4X2_types[1129] = new entity("IfcTopologicalRepresentationItem", true, 1129, (entity*) IFC4X2_types[887]);
    IFC4X2_types[1130] = new entity("IfcTopologyRepresentation", false, 1130, (entity*) IFC4X2_types[932]);
    IFC4X2_types[1164] = new entity("IfcUnitAssignment", false, 1164, (entity*) 0);
    IFC4X2_types[1175] = new entity("IfcVertex", false, 1175, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[1177] = new entity("IfcVertexPoint", false, 1177, (entity*) IFC4X2_types[1175]);
    IFC4X2_types[1185] = new entity("IfcVirtualGridIntersection", false, 1185, (entity*) 0);
    IFC4X2_types[1220] = new entity("IfcWorkTime", false, 1220, (entity*) IFC4X2_types[913]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[663]);
        items.push_back(IFC4X2_types[682]);
        items.push_back(IFC4X2_types[683]);
        IFC4X2_types[8] = new select_type("IfcActorSelect", 8, items);
    }
    IFC4X2_types[54] = new type_declaration("IfcArcIndex", 54, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[720])));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[545]);
        items.push_back(IFC4X2_types[705]);
        IFC4X2_types[77] = new select_type("IfcBendingParameterSelect", 77, items);
    }
    IFC4X2_types[98] = new type_declaration("IfcBoxAlignment", 98, new named_type(IFC4X2_types[534]));
    {
        std::vector<const declaration*> items; items.reserve(71);
        items.push_back(IFC4X2_types[0]);
        items.push_back(IFC4X2_types[1]);
        items.push_back(IFC4X2_types[43]);
        items.push_back(IFC4X2_types[55]);
        items.push_back(IFC4X2_types[192]);
        items.push_back(IFC4X2_types[259]);
        items.push_back(IFC4X2_types[331]);
        items.push_back(IFC4X2_types[344]);
        items.push_back(IFC4X2_types[351]);
        items.push_back(IFC4X2_types[352]);
        items.push_back(IFC4X2_types[353]);
        items.push_back(IFC4X2_types[367]);
        items.push_back(IFC4X2_types[371]);
        items.push_back(IFC4X2_types[386]);
        items.push_back(IFC4X2_types[470]);
        items.push_back(IFC4X2_types[471]);
        items.push_back(IFC4X2_types[500]);
        items.push_back(IFC4X2_types[501]);
        items.push_back(IFC4X2_types[506]);
        items.push_back(IFC4X2_types[514]);
        items.push_back(IFC4X2_types[516]);
        items.push_back(IFC4X2_types[524]);
        items.push_back(IFC4X2_types[528]);
        items.push_back(IFC4X2_types[532]);
        items.push_back(IFC4X2_types[564]);
        items.push_back(IFC4X2_types[565]);
        items.push_back(IFC4X2_types[568]);
        items.push_back(IFC4X2_types[569]);
        items.push_back(IFC4X2_types[578]);
        items.push_back(IFC4X2_types[579]);
        items.push_back(IFC4X2_types[581]);
        items.push_back(IFC4X2_types[582]);
        items.push_back(IFC4X2_types[586]);
        items.push_back(IFC4X2_types[587]);
        items.push_back(IFC4X2_types[589]);
        items.push_back(IFC4X2_types[625]);
        items.push_back(IFC4X2_types[626]);
        items.push_back(IFC4X2_types[627]);
        items.push_back(IFC4X2_types[629]);
        items.push_back(IFC4X2_types[632]);
        items.push_back(IFC4X2_types[633]);
        items.push_back(IFC4X2_types[634]);
        items.push_back(IFC4X2_types[635]);
        items.push_back(IFC4X2_types[684]);
        items.push_back(IFC4X2_types[703]);
        items.push_back(IFC4X2_types[725]);
        items.push_back(IFC4X2_types[740]);
        items.push_back(IFC4X2_types[798]);
        items.push_back(IFC4X2_types[905]);
        items.push_back(IFC4X2_types[906]);
        items.push_back(IFC4X2_types[907]);
        items.push_back(IFC4X2_types[919]);
        items.push_back(IFC4X2_types[915]);
        items.push_back(IFC4X2_types[934]);
        items.push_back(IFC4X2_types[958]);
        items.push_back(IFC4X2_types[959]);
        items.push_back(IFC4X2_types[960]);
        items.push_back(IFC4X2_types[961]);
        items.push_back(IFC4X2_types[976]);
        items.push_back(IFC4X2_types[1084]);
        items.push_back(IFC4X2_types[1085]);
        items.push_back(IFC4X2_types[1115]);
        items.push_back(IFC4X2_types[1116]);
        items.push_back(IFC4X2_types[1117]);
        items.push_back(IFC4X2_types[1118]);
        items.push_back(IFC4X2_types[1119]);
        items.push_back(IFC4X2_types[1132]);
        items.push_back(IFC4X2_types[1172]);
        items.push_back(IFC4X2_types[1189]);
        items.push_back(IFC4X2_types[1195]);
        items.push_back(IFC4X2_types[1196]);
        IFC4X2_types[285] = new select_type("IfcDerivedMeasureValue", 285, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[885]);
        items.push_back(IFC4X2_types[887]);
        IFC4X2_types[543] = new select_type("IfcLayeredItem", 543, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[546]);
        items.push_back(IFC4X2_types[547]);
        IFC4X2_types[548] = new select_type("IfcLibrarySelect", 548, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[406]);
        items.push_back(IFC4X2_types[556]);
        IFC4X2_types[551] = new select_type("IfcLightDistributionDataSourceSelect", 551, items);
    }
    IFC4X2_types[570] = new type_declaration("IfcLineIndex", 570, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[720])));
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[594]);
        items.push_back(IFC4X2_types[600]);
        items.push_back(IFC4X2_types[609]);
        IFC4X2_types[608] = new select_type("IfcMaterialSelect", 608, items);
    }
    IFC4X2_types[643] = new type_declaration("IfcNormalisedRatioMeasure", 643, new named_type(IFC4X2_types[808]));
    {
        std::vector<const declaration*> items; items.reserve(9);
        items.push_back(IFC4X2_types[12]);
        items.push_back(IFC4X2_types[47]);
        items.push_back(IFC4X2_types[406]);
        items.push_back(IFC4X2_types[594]);
        items.push_back(IFC4X2_types[663]);
        items.push_back(IFC4X2_types[682]);
        items.push_back(IFC4X2_types[683]);
        items.push_back(IFC4X2_types[1071]);
        items.push_back(IFC4X2_types[1125]);
        IFC4X2_types[651] = new select_type("IfcObjectReferenceSelect", 651, items);
    }
    IFC4X2_types[723] = new type_declaration("IfcPositiveRatioMeasure", 723, new named_type(IFC4X2_types[808]));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[54]);
        items.push_back(IFC4X2_types[570]);
        IFC4X2_types[923] = new select_type("IfcSegmentIndexSelect", 923, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(14);
        items.push_back(IFC4X2_types[78]);
        items.push_back(IFC4X2_types[84]);
        items.push_back(IFC4X2_types[278]);
        items.push_back(IFC4X2_types[279]);
        items.push_back(IFC4X2_types[343]);
        items.push_back(IFC4X2_types[505]);
        items.push_back(IFC4X2_types[515]);
        items.push_back(IFC4X2_types[534]);
        items.push_back(IFC4X2_types[574]);
        items.push_back(IFC4X2_types[720]);
        items.push_back(IFC4X2_types[811]);
        items.push_back(IFC4X2_types[1097]);
        items.push_back(IFC4X2_types[1121]);
        items.push_back(IFC4X2_types[1128]);
        IFC4X2_types[940] = new select_type("IfcSimpleValue", 940, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4X2_types[290]);
        items.push_back(IFC4X2_types[545]);
        items.push_back(IFC4X2_types[643]);
        items.push_back(IFC4X2_types[721]);
        items.push_back(IFC4X2_types[723]);
        items.push_back(IFC4X2_types[808]);
        IFC4X2_types[945] = new select_type("IfcSizeSelect", 945, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[977]);
        items.push_back(IFC4X2_types[979]);
        IFC4X2_types[978] = new select_type("IfcSpecularHighlightSelect", 978, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[737]);
        items.push_back(IFC4X2_types[738]);
        IFC4X2_types[1034] = new select_type("IfcStyleAssignmentSelect", 1034, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4X2_types[404]);
        items.push_back(IFC4X2_types[1054]);
        items.push_back(IFC4X2_types[1055]);
        items.push_back(IFC4X2_types[1057]);
        items.push_back(IFC4X2_types[1058]);
        IFC4X2_types[1053] = new select_type("IfcSurfaceStyleElementSelect", 1053, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[287]);
        items.push_back(IFC4X2_types[636]);
        items.push_back(IFC4X2_types[641]);
        IFC4X2_types[1157] = new select_type("IfcUnit", 1157, items);
    }
    IFC4X2_types[50] = new entity("IfcApprovalRelationship", false, 50, (entity*) IFC4X2_types[892]);
    IFC4X2_types[51] = new entity("IfcArbitraryClosedProfileDef", false, 51, (entity*) IFC4X2_types[751]);
    IFC4X2_types[52] = new entity("IfcArbitraryOpenProfileDef", false, 52, (entity*) IFC4X2_types[751]);
    IFC4X2_types[53] = new entity("IfcArbitraryProfileDefWithVoids", false, 53, (entity*) IFC4X2_types[51]);
    IFC4X2_types[79] = new entity("IfcBlobTexture", false, 79, (entity*) IFC4X2_types[1059]);
    IFC4X2_types[150] = new entity("IfcCenterLineProfileDef", false, 150, (entity*) IFC4X2_types[52]);
    IFC4X2_types[164] = new entity("IfcClassification", false, 164, (entity*) IFC4X2_types[402]);
    IFC4X2_types[165] = new entity("IfcClassificationReference", false, 165, (entity*) IFC4X2_types[406]);
    IFC4X2_types[175] = new entity("IfcColourRgbList", false, 175, (entity*) IFC4X2_types[734]);
    IFC4X2_types[176] = new entity("IfcColourSpecification", true, 176, (entity*) IFC4X2_types[734]);
    IFC4X2_types[191] = new entity("IfcCompositeProfileDef", false, 191, (entity*) IFC4X2_types[751]);
    IFC4X2_types[200] = new entity("IfcConnectedFaceSet", false, 200, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[201] = new entity("IfcConnectionCurveGeometry", false, 201, (entity*) IFC4X2_types[202]);
    IFC4X2_types[203] = new entity("IfcConnectionPointEccentricity", false, 203, (entity*) IFC4X2_types[204]);
    IFC4X2_types[223] = new entity("IfcContextDependentUnit", false, 223, (entity*) IFC4X2_types[641]);
    IFC4X2_types[228] = new entity("IfcConversionBasedUnit", false, 228, (entity*) IFC4X2_types[641]);
    IFC4X2_types[229] = new entity("IfcConversionBasedUnitWithOffset", false, 229, (entity*) IFC4X2_types[228]);
    IFC4X2_types[255] = new entity("IfcCurrencyRelationship", false, 255, (entity*) IFC4X2_types[892]);
    IFC4X2_types[268] = new entity("IfcCurveStyle", false, 268, (entity*) IFC4X2_types[737]);
    IFC4X2_types[269] = new entity("IfcCurveStyleFont", false, 269, (entity*) IFC4X2_types[734]);
    IFC4X2_types[270] = new entity("IfcCurveStyleFontAndScaling", false, 270, (entity*) IFC4X2_types[734]);
    IFC4X2_types[271] = new entity("IfcCurveStyleFontPattern", false, 271, (entity*) IFC4X2_types[734]);
    IFC4X2_types[286] = new entity("IfcDerivedProfileDef", false, 286, (entity*) IFC4X2_types[751]);
    IFC4X2_types[314] = new entity("IfcDocumentInformation", false, 314, (entity*) IFC4X2_types[402]);
    IFC4X2_types[315] = new entity("IfcDocumentInformationRelationship", false, 315, (entity*) IFC4X2_types[892]);
    IFC4X2_types[316] = new entity("IfcDocumentReference", false, 316, (entity*) IFC4X2_types[406]);
    IFC4X2_types[345] = new entity("IfcEdge", false, 345, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[346] = new entity("IfcEdgeCurve", false, 346, (entity*) IFC4X2_types[345]);
    IFC4X2_types[397] = new entity("IfcEventTime", false, 397, (entity*) IFC4X2_types[913]);
    IFC4X2_types[401] = new entity("IfcExtendedProperties", true, 401, (entity*) IFC4X2_types[763]);
    IFC4X2_types[407] = new entity("IfcExternalReferenceRelationship", false, 407, (entity*) IFC4X2_types[892]);
    IFC4X2_types[413] = new entity("IfcFace", false, 413, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[415] = new entity("IfcFaceBound", false, 415, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[416] = new entity("IfcFaceOuterBound", false, 416, (entity*) IFC4X2_types[415]);
    IFC4X2_types[417] = new entity("IfcFaceSurface", false, 417, (entity*) IFC4X2_types[413]);
    IFC4X2_types[422] = new entity("IfcFailureConnectionCondition", false, 422, (entity*) IFC4X2_types[997]);
    IFC4X2_types[432] = new entity("IfcFillAreaStyle", false, 432, (entity*) IFC4X2_types[737]);
    IFC4X2_types[482] = new entity("IfcGeometricRepresentationContext", false, 482, (entity*) IFC4X2_types[886]);
    IFC4X2_types[483] = new entity("IfcGeometricRepresentationItem", true, 483, (entity*) IFC4X2_types[887]);
    IFC4X2_types[484] = new entity("IfcGeometricRepresentationSubContext", false, 484, (entity*) IFC4X2_types[482]);
    IFC4X2_types[485] = new entity("IfcGeometricSet", false, 485, (entity*) IFC4X2_types[483]);
    IFC4X2_types[491] = new entity("IfcGridPlacement", false, 491, (entity*) IFC4X2_types[650]);
    IFC4X2_types[495] = new entity("IfcHalfSpaceSolid", false, 495, (entity*) IFC4X2_types[483]);
    IFC4X2_types[507] = new entity("IfcImageTexture", false, 507, (entity*) IFC4X2_types[1059]);
    IFC4X2_types[508] = new entity("IfcIndexedColourMap", false, 508, (entity*) IFC4X2_types[734]);
    IFC4X2_types[512] = new entity("IfcIndexedTextureMap", true, 512, (entity*) IFC4X2_types[1110]);
    IFC4X2_types[513] = new entity("IfcIndexedTriangleTextureMap", false, 513, (entity*) IFC4X2_types[512]);
    IFC4X2_types[525] = new entity("IfcIrregularTimeSeries", false, 525, (entity*) IFC4X2_types[1125]);
    IFC4X2_types[538] = new entity("IfcLagTime", false, 538, (entity*) IFC4X2_types[913]);
    IFC4X2_types[557] = new entity("IfcLightSource", true, 557, (entity*) IFC4X2_types[483]);
    IFC4X2_types[558] = new entity("IfcLightSourceAmbient", false, 558, (entity*) IFC4X2_types[557]);
    IFC4X2_types[559] = new entity("IfcLightSourceDirectional", false, 559, (entity*) IFC4X2_types[557]);
    IFC4X2_types[560] = new entity("IfcLightSourceGoniometric", false, 560, (entity*) IFC4X2_types[557]);
    IFC4X2_types[561] = new entity("IfcLightSourcePositional", false, 561, (entity*) IFC4X2_types[557]);
    IFC4X2_types[562] = new entity("IfcLightSourceSpot", false, 562, (entity*) IFC4X2_types[561]);
    IFC4X2_types[566] = new entity("IfcLinearPlacement", false, 566, (entity*) IFC4X2_types[650]);
    IFC4X2_types[573] = new entity("IfcLocalPlacement", false, 573, (entity*) IFC4X2_types[650]);
    IFC4X2_types[576] = new entity("IfcLoop", false, 576, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[585] = new entity("IfcMappedItem", false, 585, (entity*) IFC4X2_types[887]);
    IFC4X2_types[590] = new entity("IfcMaterial", false, 590, (entity*) IFC4X2_types[594]);
    IFC4X2_types[592] = new entity("IfcMaterialConstituent", false, 592, (entity*) IFC4X2_types[594]);
    IFC4X2_types[593] = new entity("IfcMaterialConstituentSet", false, 593, (entity*) IFC4X2_types[594]);
    IFC4X2_types[595] = new entity("IfcMaterialDefinitionRepresentation", false, 595, (entity*) IFC4X2_types[748]);
    IFC4X2_types[598] = new entity("IfcMaterialLayerSetUsage", false, 598, (entity*) IFC4X2_types[609]);
    IFC4X2_types[603] = new entity("IfcMaterialProfileSetUsage", false, 603, (entity*) IFC4X2_types[609]);
    IFC4X2_types[604] = new entity("IfcMaterialProfileSetUsageTapering", false, 604, (entity*) IFC4X2_types[603]);
    IFC4X2_types[606] = new entity("IfcMaterialProperties", false, 606, (entity*) IFC4X2_types[401]);
    IFC4X2_types[607] = new entity("IfcMaterialRelationship", false, 607, (entity*) IFC4X2_types[892]);
    IFC4X2_types[624] = new entity("IfcMirroredProfileDef", false, 624, (entity*) IFC4X2_types[286]);
    IFC4X2_types[647] = new entity("IfcObjectDefinition", true, 647, (entity*) IFC4X2_types[904]);
    IFC4X2_types[662] = new entity("IfcOpenShell", false, 662, (entity*) IFC4X2_types[200]);
    IFC4X2_types[664] = new entity("IfcOrganizationRelationship", false, 664, (entity*) IFC4X2_types[892]);
    IFC4X2_types[665] = new entity("IfcOrientationExpression", false, 665, (entity*) IFC4X2_types[483]);
    IFC4X2_types[666] = new entity("IfcOrientedEdge", false, 666, (entity*) IFC4X2_types[345]);
    IFC4X2_types[672] = new entity("IfcParameterizedProfileDef", true, 672, (entity*) IFC4X2_types[751]);
    IFC4X2_types[674] = new entity("IfcPath", false, 674, (entity*) IFC4X2_types[1129]);
    IFC4X2_types[685] = new entity("IfcPhysicalComplexQuantity", false, 685, (entity*) IFC4X2_types[687]);
    IFC4X2_types[699] = new entity("IfcPixelTexture", false, 699, (entity*) IFC4X2_types[1059]);
    IFC4X2_types[700] = new entity("IfcPlacement", true, 700, (entity*) IFC4X2_types[483]);
    IFC4X2_types[702] = new entity("IfcPlanarExtent", false, 702, (entity*) IFC4X2_types[483]);
    IFC4X2_types[710] = new entity("IfcPoint", true, 710, (entity*) IFC4X2_types[483]);
    IFC4X2_types[711] = new entity("IfcPointOnCurve", false, 711, (entity*) IFC4X2_types[710]);
    IFC4X2_types[712] = new entity("IfcPointOnSurface", false, 712, (entity*) IFC4X2_types[710]);
    IFC4X2_types[717] = new entity("IfcPolyLoop", false, 717, (entity*) IFC4X2_types[576]);
    IFC4X2_types[714] = new entity("IfcPolygonalBoundedHalfSpace", false, 714, (entity*) IFC4X2_types[495]);
    IFC4X2_types[728] = new entity("IfcPreDefinedItem", true, 728, (entity*) IFC4X2_types[734]);
    IFC4X2_types[729] = new entity("IfcPreDefinedProperties", true, 729, (entity*) IFC4X2_types[763]);
    IFC4X2_types[731] = new entity("IfcPreDefinedTextFont", true, 731, (entity*) IFC4X2_types[728]);
    IFC4X2_types[747] = new entity("IfcProductDefinitionShape", false, 747, (entity*) IFC4X2_types[748]);
    IFC4X2_types[752] = new entity("IfcProfileProperties", false, 752, (entity*) IFC4X2_types[401]);
    IFC4X2_types[762] = new entity("IfcProperty", true, 762, (entity*) IFC4X2_types[763]);
    IFC4X2_types[765] = new entity("IfcPropertyDefinition", true, 765, (entity*) IFC4X2_types[904]);
    IFC4X2_types[766] = new entity("IfcPropertyDependencyRelationship", false, 766, (entity*) IFC4X2_types[892]);
    IFC4X2_types[772] = new entity("IfcPropertySetDefinition", true, 772, (entity*) IFC4X2_types[765]);
    IFC4X2_types[780] = new entity("IfcPropertyTemplateDefinition", true, 780, (entity*) IFC4X2_types[765]);
    IFC4X2_types[794] = new entity("IfcQuantitySet", true, 794, (entity*) IFC4X2_types[772]);
    IFC4X2_types[813] = new entity("IfcRectangleProfileDef", false, 813, (entity*) IFC4X2_types[672]);
    IFC4X2_types[822] = new entity("IfcRegularTimeSeries", false, 822, (entity*) IFC4X2_types[1125]);
    IFC4X2_types[823] = new entity("IfcReinforcementBarProperties", false, 823, (entity*) IFC4X2_types[729]);
    IFC4X2_types[851] = new entity("IfcRelationship", true, 851, (entity*) IFC4X2_types[904]);
    IFC4X2_types[890] = new entity("IfcResourceApprovalRelationship", false, 890, (entity*) IFC4X2_types[892]);
    IFC4X2_types[891] = new entity("IfcResourceConstraintRelationship", false, 891, (entity*) IFC4X2_types[892]);
    IFC4X2_types[895] = new entity("IfcResourceTime", false, 895, (entity*) IFC4X2_types[913]);
    IFC4X2_types[909] = new entity("IfcRoundedRectangleProfileDef", false, 909, (entity*) IFC4X2_types[813]);
    IFC4X2_types[920] = new entity("IfcSectionProperties", false, 920, (entity*) IFC4X2_types[729]);
    IFC4X2_types[921] = new entity("IfcSectionReinforcementProperties", false, 921, (entity*) IFC4X2_types[729]);
    IFC4X2_types[918] = new entity("IfcSectionedSpine", false, 918, (entity*) IFC4X2_types[483]);
    IFC4X2_types[936] = new entity("IfcShellBasedSurfaceModel", false, 936, (entity*) IFC4X2_types[483]);
    IFC4X2_types[937] = new entity("IfcSimpleProperty", true, 937, (entity*) IFC4X2_types[762]);
    IFC4X2_types[951] = new entity("IfcSlippageConnectionCondition", false, 951, (entity*) IFC4X2_types[997]);
    IFC4X2_types[956] = new entity("IfcSolidModel", true, 956, (entity*) IFC4X2_types[483]);
    IFC4X2_types[1011] = new entity("IfcStructuralLoadLinearForce", false, 1011, (entity*) IFC4X2_types[1018]);
    IFC4X2_types[1013] = new entity("IfcStructuralLoadPlanarForce", false, 1013, (entity*) IFC4X2_types[1018]);
    IFC4X2_types[1014] = new entity("IfcStructuralLoadSingleDisplacement", false, 1014, (entity*) IFC4X2_types[1018]);
    IFC4X2_types[1015] = new entity("IfcStructuralLoadSingleDisplacementDistortion", false, 1015, (entity*) IFC4X2_types[1014]);
    IFC4X2_types[1016] = new entity("IfcStructuralLoadSingleForce", false, 1016, (entity*) IFC4X2_types[1018]);
    IFC4X2_types[1017] = new entity("IfcStructuralLoadSingleForceWarping", false, 1017, (entity*) IFC4X2_types[1016]);
    IFC4X2_types[1041] = new entity("IfcSubedge", false, 1041, (entity*) IFC4X2_types[345]);
    IFC4X2_types[1042] = new entity("IfcSurface", true, 1042, (entity*) IFC4X2_types[483]);
    IFC4X2_types[1056] = new entity("IfcSurfaceStyleRendering", false, 1056, (entity*) IFC4X2_types[1057]);
    IFC4X2_types[1060] = new entity("IfcSweptAreaSolid", true, 1060, (entity*) IFC4X2_types[956]);
    IFC4X2_types[1061] = new entity("IfcSweptDiskSolid", false, 1061, (entity*) IFC4X2_types[956]);
    IFC4X2_types[1062] = new entity("IfcSweptDiskSolidPolygonal", false, 1062, (entity*) IFC4X2_types[1061]);
    IFC4X2_types[1063] = new entity("IfcSweptSurface", true, 1063, (entity*) IFC4X2_types[1042]);
    IFC4X2_types[1149] = new entity("IfcTShapeProfileDef", false, 1149, (entity*) IFC4X2_types[672]);
    IFC4X2_types[1096] = new entity("IfcTessellatedItem", true, 1096, (entity*) IFC4X2_types[483]);
    IFC4X2_types[1102] = new entity("IfcTextLiteral", false, 1102, (entity*) IFC4X2_types[483]);
    IFC4X2_types[1103] = new entity("IfcTextLiteralWithExtent", false, 1103, (entity*) IFC4X2_types[1102]);
    IFC4X2_types[1106] = new entity("IfcTextStyleFontModel", false, 1106, (entity*) IFC4X2_types[731]);
    IFC4X2_types[1143] = new entity("IfcTrapeziumProfileDef", false, 1143, (entity*) IFC4X2_types[672]);
    IFC4X2_types[1153] = new entity("IfcTypeObject", false, 1153, (entity*) IFC4X2_types[647]);
    IFC4X2_types[1154] = new entity("IfcTypeProcess", true, 1154, (entity*) IFC4X2_types[1153]);
    IFC4X2_types[1155] = new entity("IfcTypeProduct", false, 1155, (entity*) IFC4X2_types[1153]);
    IFC4X2_types[1156] = new entity("IfcTypeResource", true, 1156, (entity*) IFC4X2_types[1153]);
    IFC4X2_types[1167] = new entity("IfcUShapeProfileDef", false, 1167, (entity*) IFC4X2_types[672]);
    IFC4X2_types[1173] = new entity("IfcVector", false, 1173, (entity*) IFC4X2_types[483]);
    IFC4X2_types[1176] = new entity("IfcVertexLoop", false, 1176, (entity*) IFC4X2_types[576]);
    IFC4X2_types[1207] = new entity("IfcWindowStyle", false, 1207, (entity*) IFC4X2_types[1155]);
    IFC4X2_types[1222] = new entity("IfcZShapeProfileDef", false, 1222, (entity*) IFC4X2_types[672]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[164]);
        items.push_back(IFC4X2_types[165]);
        IFC4X2_types[166] = new select_type("IfcClassificationReferenceSelect", 166, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[164]);
        items.push_back(IFC4X2_types[165]);
        IFC4X2_types[167] = new select_type("IfcClassificationSelect", 167, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[237]);
        items.push_back(IFC4X2_types[482]);
        IFC4X2_types[238] = new select_type("IfcCoordinateReferenceSystemSelect", 238, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[647]);
        items.push_back(IFC4X2_types[765]);
        IFC4X2_types[284] = new select_type("IfcDefinitionSelect", 284, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[314]);
        items.push_back(IFC4X2_types[316]);
        IFC4X2_types[317] = new select_type("IfcDocumentSelect", 317, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[721]);
        items.push_back(IFC4X2_types[1173]);
        IFC4X2_types[496] = new select_type("IfcHatchLineDistanceSelect", 496, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(23);
        items.push_back(IFC4X2_types[40]);
        items.push_back(IFC4X2_types[56]);
        items.push_back(IFC4X2_types[184]);
        items.push_back(IFC4X2_types[222]);
        items.push_back(IFC4X2_types[244]);
        items.push_back(IFC4X2_types[290]);
        items.push_back(IFC4X2_types[354]);
        items.push_back(IFC4X2_types[545]);
        items.push_back(IFC4X2_types[580]);
        items.push_back(IFC4X2_types[588]);
        items.push_back(IFC4X2_types[642]);
        items.push_back(IFC4X2_types[643]);
        items.push_back(IFC4X2_types[645]);
        items.push_back(IFC4X2_types[673]);
        items.push_back(IFC4X2_types[705]);
        items.push_back(IFC4X2_types[721]);
        items.push_back(IFC4X2_types[722]);
        items.push_back(IFC4X2_types[723]);
        items.push_back(IFC4X2_types[808]);
        items.push_back(IFC4X2_types[955]);
        items.push_back(IFC4X2_types[1120]);
        items.push_back(IFC4X2_types[1122]);
        items.push_back(IFC4X2_types[1188]);
        IFC4X2_types[610] = new select_type("IfcMeasureValue", 610, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[710]);
        items.push_back(IFC4X2_types[1177]);
        IFC4X2_types[713] = new select_type("IfcPointOrVertexPoint", 713, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4X2_types[268]);
        items.push_back(IFC4X2_types[432]);
        items.push_back(IFC4X2_types[644]);
        items.push_back(IFC4X2_types[1052]);
        items.push_back(IFC4X2_types[1105]);
        IFC4X2_types[739] = new select_type("IfcPresentationStyleSelect", 739, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[747]);
        items.push_back(IFC4X2_types[888]);
        IFC4X2_types[749] = new select_type("IfcProductRepresentationSelect", 749, items);
    }
    IFC4X2_types[774] = new type_declaration("IfcPropertySetDefinitionSet", 774, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[772])));
    {
        std::vector<const declaration*> items; items.reserve(17);
        items.push_back(IFC4X2_types[7]);
        items.push_back(IFC4X2_types[47]);
        items.push_back(IFC4X2_types[49]);
        items.push_back(IFC4X2_types[208]);
        items.push_back(IFC4X2_types[223]);
        items.push_back(IFC4X2_types[228]);
        items.push_back(IFC4X2_types[402]);
        items.push_back(IFC4X2_types[406]);
        items.push_back(IFC4X2_types[594]);
        items.push_back(IFC4X2_types[663]);
        items.push_back(IFC4X2_types[682]);
        items.push_back(IFC4X2_types[683]);
        items.push_back(IFC4X2_types[687]);
        items.push_back(IFC4X2_types[751]);
        items.push_back(IFC4X2_types[763]);
        items.push_back(IFC4X2_types[931]);
        items.push_back(IFC4X2_types[1125]);
        IFC4X2_types[893] = new select_type("IfcResourceObjectSelect", 893, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[405]);
        items.push_back(IFC4X2_types[731]);
        IFC4X2_types[1101] = new select_type("IfcTextFontSelect", 1101, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[285]);
        items.push_back(IFC4X2_types[610]);
        items.push_back(IFC4X2_types[940]);
        IFC4X2_types[1168] = new select_type("IfcValue", 1168, items);
    }
    IFC4X2_types[16] = new entity("IfcAdvancedFace", false, 16, (entity*) IFC4X2_types[417]);
    IFC4X2_types[30] = new entity("IfcAlignment2DHorizontal", false, 30, (entity*) IFC4X2_types[483]);
    IFC4X2_types[32] = new entity("IfcAlignment2DSegment", true, 32, (entity*) IFC4X2_types[483]);
    IFC4X2_types[36] = new entity("IfcAlignment2DVertical", false, 36, (entity*) IFC4X2_types[483]);
    IFC4X2_types[37] = new entity("IfcAlignment2DVerticalSegment", true, 37, (entity*) IFC4X2_types[32]);
    IFC4X2_types[45] = new entity("IfcAnnotationFillArea", false, 45, (entity*) IFC4X2_types[483]);
    IFC4X2_types[60] = new entity("IfcAsymmetricIShapeProfileDef", false, 60, (entity*) IFC4X2_types[672]);
    IFC4X2_types[64] = new entity("IfcAxis1Placement", false, 64, (entity*) IFC4X2_types[700]);
    IFC4X2_types[66] = new entity("IfcAxis2Placement2D", false, 66, (entity*) IFC4X2_types[700]);
    IFC4X2_types[67] = new entity("IfcAxis2Placement3D", false, 67, (entity*) IFC4X2_types[700]);
    IFC4X2_types[88] = new entity("IfcBooleanResult", false, 88, (entity*) IFC4X2_types[483]);
    IFC4X2_types[96] = new entity("IfcBoundedSurface", true, 96, (entity*) IFC4X2_types[1042]);
    IFC4X2_types[97] = new entity("IfcBoundingBox", false, 97, (entity*) IFC4X2_types[483]);
    IFC4X2_types[99] = new entity("IfcBoxedHalfSpace", false, 99, (entity*) IFC4X2_types[495]);
    IFC4X2_types[254] = new entity("IfcCShapeProfileDef", false, 254, (entity*) IFC4X2_types[672]);
    IFC4X2_types[141] = new entity("IfcCartesianPoint", false, 141, (entity*) IFC4X2_types[710]);
    IFC4X2_types[142] = new entity("IfcCartesianPointList", true, 142, (entity*) IFC4X2_types[483]);
    IFC4X2_types[143] = new entity("IfcCartesianPointList2D", false, 143, (entity*) IFC4X2_types[142]);
    IFC4X2_types[144] = new entity("IfcCartesianPointList3D", false, 144, (entity*) IFC4X2_types[142]);
    IFC4X2_types[145] = new entity("IfcCartesianTransformationOperator", true, 145, (entity*) IFC4X2_types[483]);
    IFC4X2_types[146] = new entity("IfcCartesianTransformationOperator2D", false, 146, (entity*) IFC4X2_types[145]);
    IFC4X2_types[147] = new entity("IfcCartesianTransformationOperator2DnonUniform", false, 147, (entity*) IFC4X2_types[146]);
    IFC4X2_types[148] = new entity("IfcCartesianTransformationOperator3D", false, 148, (entity*) IFC4X2_types[145]);
    IFC4X2_types[149] = new entity("IfcCartesianTransformationOperator3DnonUniform", false, 149, (entity*) IFC4X2_types[148]);
    IFC4X2_types[160] = new entity("IfcCircleProfileDef", false, 160, (entity*) IFC4X2_types[672]);
    IFC4X2_types[168] = new entity("IfcClosedShell", false, 168, (entity*) IFC4X2_types[200]);
    IFC4X2_types[174] = new entity("IfcColourRgb", false, 174, (entity*) IFC4X2_types[176]);
    IFC4X2_types[185] = new entity("IfcComplexProperty", false, 185, (entity*) IFC4X2_types[762]);
    IFC4X2_types[190] = new entity("IfcCompositeCurveSegment", false, 190, (entity*) IFC4X2_types[483]);
    IFC4X2_types[220] = new entity("IfcConstructionResourceType", true, 220, (entity*) IFC4X2_types[1156]);
    IFC4X2_types[221] = new entity("IfcContext", true, 221, (entity*) IFC4X2_types[647]);
    IFC4X2_types[249] = new entity("IfcCrewResourceType", false, 249, (entity*) IFC4X2_types[220]);
    IFC4X2_types[251] = new entity("IfcCsgPrimitive3D", true, 251, (entity*) IFC4X2_types[483]);
    IFC4X2_types[253] = new entity("IfcCsgSolid", false, 253, (entity*) IFC4X2_types[956]);
    IFC4X2_types[260] = new entity("IfcCurve", true, 260, (entity*) IFC4X2_types[483]);
    IFC4X2_types[261] = new entity("IfcCurveBoundedPlane", false, 261, (entity*) IFC4X2_types[96]);
    IFC4X2_types[262] = new entity("IfcCurveBoundedSurface", false, 262, (entity*) IFC4X2_types[96]);
    IFC4X2_types[293] = new entity("IfcDirection", false, 293, (entity*) IFC4X2_types[483]);
    IFC4X2_types[298] = new entity("IfcDistanceExpression", false, 298, (entity*) IFC4X2_types[483]);
    IFC4X2_types[325] = new entity("IfcDoorStyle", false, 325, (entity*) IFC4X2_types[1155]);
    IFC4X2_types[347] = new entity("IfcEdgeLoop", false, 347, (entity*) IFC4X2_types[576]);
    IFC4X2_types[380] = new entity("IfcElementQuantity", false, 380, (entity*) IFC4X2_types[794]);
    IFC4X2_types[381] = new entity("IfcElementType", true, 381, (entity*) IFC4X2_types[1155]);
    IFC4X2_types[373] = new entity("IfcElementarySurface", true, 373, (entity*) IFC4X2_types[1042]);
    IFC4X2_types[383] = new entity("IfcEllipseProfileDef", false, 383, (entity*) IFC4X2_types[672]);
    IFC4X2_types[399] = new entity("IfcEventType", false, 399, (entity*) IFC4X2_types[1154]);
    IFC4X2_types[411] = new entity("IfcExtrudedAreaSolid", false, 411, (entity*) IFC4X2_types[1060]);
    IFC4X2_types[412] = new entity("IfcExtrudedAreaSolidTapered", false, 412, (entity*) IFC4X2_types[411]);
    IFC4X2_types[414] = new entity("IfcFaceBasedSurfaceModel", false, 414, (entity*) IFC4X2_types[483]);
    IFC4X2_types[433] = new entity("IfcFillAreaStyleHatching", false, 433, (entity*) IFC4X2_types[483]);
    IFC4X2_types[434] = new entity("IfcFillAreaStyleTiles", false, 434, (entity*) IFC4X2_types[483]);
    IFC4X2_types[442] = new entity("IfcFixedReferenceSweptAreaSolid", false, 442, (entity*) IFC4X2_types[1060]);
    IFC4X2_types[473] = new entity("IfcFurnishingElementType", false, 473, (entity*) IFC4X2_types[381]);
    IFC4X2_types[475] = new entity("IfcFurnitureType", false, 475, (entity*) IFC4X2_types[473]);
    IFC4X2_types[478] = new entity("IfcGeographicElementType", false, 478, (entity*) IFC4X2_types[381]);
    IFC4X2_types[480] = new entity("IfcGeometricCurveSet", false, 480, (entity*) IFC4X2_types[485]);
    IFC4X2_types[527] = new entity("IfcIShapeProfileDef", false, 527, (entity*) IFC4X2_types[672]);
    IFC4X2_types[510] = new entity("IfcIndexedPolygonalFace", false, 510, (entity*) IFC4X2_types[1096]);
    IFC4X2_types[511] = new entity("IfcIndexedPolygonalFaceWithVoids", false, 511, (entity*) IFC4X2_types[510]);
    IFC4X2_types[577] = new entity("IfcLShapeProfileDef", false, 577, (entity*) IFC4X2_types[672]);
    IFC4X2_types[536] = new entity("IfcLaborResourceType", false, 536, (entity*) IFC4X2_types[220]);
    IFC4X2_types[563] = new entity("IfcLine", false, 563, (entity*) IFC4X2_types[260]);
    IFC4X2_types[583] = new entity("IfcManifoldSolidBrep", true, 583, (entity*) IFC4X2_types[956]);
    IFC4X2_types[646] = new entity("IfcObject", true, 646, (entity*) IFC4X2_types[647]);
    IFC4X2_types[655] = new entity("IfcOffsetCurve", true, 655, (entity*) IFC4X2_types[260]);
    IFC4X2_types[656] = new entity("IfcOffsetCurve2D", false, 656, (entity*) IFC4X2_types[655]);
    IFC4X2_types[657] = new entity("IfcOffsetCurve3D", false, 657, (entity*) IFC4X2_types[655]);
    IFC4X2_types[658] = new entity("IfcOffsetCurveByDistances", false, 658, (entity*) IFC4X2_types[655]);
    IFC4X2_types[675] = new entity("IfcPcurve", false, 675, (entity*) IFC4X2_types[260]);
    IFC4X2_types[701] = new entity("IfcPlanarBox", false, 701, (entity*) IFC4X2_types[702]);
    IFC4X2_types[704] = new entity("IfcPlane", false, 704, (entity*) IFC4X2_types[373]);
    IFC4X2_types[726] = new entity("IfcPreDefinedColour", true, 726, (entity*) IFC4X2_types[728]);
    IFC4X2_types[727] = new entity("IfcPreDefinedCurveFont", true, 727, (entity*) IFC4X2_types[728]);
    IFC4X2_types[730] = new entity("IfcPreDefinedPropertySet", true, 730, (entity*) IFC4X2_types[772]);
    IFC4X2_types[742] = new entity("IfcProcedureType", false, 742, (entity*) IFC4X2_types[1154]);
    IFC4X2_types[744] = new entity("IfcProcess", true, 744, (entity*) IFC4X2_types[646]);
    IFC4X2_types[746] = new entity("IfcProduct", true, 746, (entity*) IFC4X2_types[646]);
    IFC4X2_types[754] = new entity("IfcProject", false, 754, (entity*) IFC4X2_types[221]);
    IFC4X2_types[759] = new entity("IfcProjectLibrary", false, 759, (entity*) IFC4X2_types[221]);
    IFC4X2_types[764] = new entity("IfcPropertyBoundedValue", false, 764, (entity*) IFC4X2_types[937]);
    IFC4X2_types[767] = new entity("IfcPropertyEnumeratedValue", false, 767, (entity*) IFC4X2_types[937]);
    IFC4X2_types[769] = new entity("IfcPropertyListValue", false, 769, (entity*) IFC4X2_types[937]);
    IFC4X2_types[770] = new entity("IfcPropertyReferenceValue", false, 770, (entity*) IFC4X2_types[937]);
    IFC4X2_types[771] = new entity("IfcPropertySet", false, 771, (entity*) IFC4X2_types[772]);
    IFC4X2_types[775] = new entity("IfcPropertySetTemplate", false, 775, (entity*) IFC4X2_types[780]);
    IFC4X2_types[777] = new entity("IfcPropertySingleValue", false, 777, (entity*) IFC4X2_types[937]);
    IFC4X2_types[778] = new entity("IfcPropertyTableValue", false, 778, (entity*) IFC4X2_types[937]);
    IFC4X2_types[779] = new entity("IfcPropertyTemplate", true, 779, (entity*) IFC4X2_types[780]);
    IFC4X2_types[787] = new entity("IfcProxy", false, 787, (entity*) IFC4X2_types[746]);
    IFC4X2_types[812] = new entity("IfcRectangleHollowProfileDef", false, 812, (entity*) IFC4X2_types[813]);
    IFC4X2_types[814] = new entity("IfcRectangularPyramid", false, 814, (entity*) IFC4X2_types[251]);
    IFC4X2_types[815] = new entity("IfcRectangularTrimmedSurface", false, 815, (entity*) IFC4X2_types[96]);
    IFC4X2_types[824] = new entity("IfcReinforcementDefinitionProperties", false, 824, (entity*) IFC4X2_types[730]);
    IFC4X2_types[836] = new entity("IfcRelAssigns", true, 836, (entity*) IFC4X2_types[851]);
    IFC4X2_types[837] = new entity("IfcRelAssignsToActor", false, 837, (entity*) IFC4X2_types[836]);
    IFC4X2_types[838] = new entity("IfcRelAssignsToControl", false, 838, (entity*) IFC4X2_types[836]);
    IFC4X2_types[839] = new entity("IfcRelAssignsToGroup", false, 839, (entity*) IFC4X2_types[836]);
    IFC4X2_types[840] = new entity("IfcRelAssignsToGroupByFactor", false, 840, (entity*) IFC4X2_types[839]);
    IFC4X2_types[841] = new entity("IfcRelAssignsToProcess", false, 841, (entity*) IFC4X2_types[836]);
    IFC4X2_types[842] = new entity("IfcRelAssignsToProduct", false, 842, (entity*) IFC4X2_types[836]);
    IFC4X2_types[843] = new entity("IfcRelAssignsToResource", false, 843, (entity*) IFC4X2_types[836]);
    IFC4X2_types[844] = new entity("IfcRelAssociates", true, 844, (entity*) IFC4X2_types[851]);
    IFC4X2_types[845] = new entity("IfcRelAssociatesApproval", false, 845, (entity*) IFC4X2_types[844]);
    IFC4X2_types[846] = new entity("IfcRelAssociatesClassification", false, 846, (entity*) IFC4X2_types[844]);
    IFC4X2_types[847] = new entity("IfcRelAssociatesConstraint", false, 847, (entity*) IFC4X2_types[844]);
    IFC4X2_types[848] = new entity("IfcRelAssociatesDocument", false, 848, (entity*) IFC4X2_types[844]);
    IFC4X2_types[849] = new entity("IfcRelAssociatesLibrary", false, 849, (entity*) IFC4X2_types[844]);
    IFC4X2_types[850] = new entity("IfcRelAssociatesMaterial", false, 850, (entity*) IFC4X2_types[844]);
    IFC4X2_types[852] = new entity("IfcRelConnects", true, 852, (entity*) IFC4X2_types[851]);
    IFC4X2_types[853] = new entity("IfcRelConnectsElements", false, 853, (entity*) IFC4X2_types[852]);
    IFC4X2_types[854] = new entity("IfcRelConnectsPathElements", false, 854, (entity*) IFC4X2_types[853]);
    IFC4X2_types[856] = new entity("IfcRelConnectsPortToElement", false, 856, (entity*) IFC4X2_types[852]);
    IFC4X2_types[855] = new entity("IfcRelConnectsPorts", false, 855, (entity*) IFC4X2_types[852]);
    IFC4X2_types[857] = new entity("IfcRelConnectsStructuralActivity", false, 857, (entity*) IFC4X2_types[852]);
    IFC4X2_types[858] = new entity("IfcRelConnectsStructuralMember", false, 858, (entity*) IFC4X2_types[852]);
    IFC4X2_types[859] = new entity("IfcRelConnectsWithEccentricity", false, 859, (entity*) IFC4X2_types[858]);
    IFC4X2_types[860] = new entity("IfcRelConnectsWithRealizingElements", false, 860, (entity*) IFC4X2_types[853]);
    IFC4X2_types[861] = new entity("IfcRelContainedInSpatialStructure", false, 861, (entity*) IFC4X2_types[852]);
    IFC4X2_types[862] = new entity("IfcRelCoversBldgElements", false, 862, (entity*) IFC4X2_types[852]);
    IFC4X2_types[863] = new entity("IfcRelCoversSpaces", false, 863, (entity*) IFC4X2_types[852]);
    IFC4X2_types[864] = new entity("IfcRelDeclares", false, 864, (entity*) IFC4X2_types[851]);
    IFC4X2_types[865] = new entity("IfcRelDecomposes", true, 865, (entity*) IFC4X2_types[851]);
    IFC4X2_types[866] = new entity("IfcRelDefines", true, 866, (entity*) IFC4X2_types[851]);
    IFC4X2_types[867] = new entity("IfcRelDefinesByObject", false, 867, (entity*) IFC4X2_types[866]);
    IFC4X2_types[868] = new entity("IfcRelDefinesByProperties", false, 868, (entity*) IFC4X2_types[866]);
    IFC4X2_types[869] = new entity("IfcRelDefinesByTemplate", false, 869, (entity*) IFC4X2_types[866]);
    IFC4X2_types[870] = new entity("IfcRelDefinesByType", false, 870, (entity*) IFC4X2_types[866]);
    IFC4X2_types[871] = new entity("IfcRelFillsElement", false, 871, (entity*) IFC4X2_types[852]);
    IFC4X2_types[872] = new entity("IfcRelFlowControlElements", false, 872, (entity*) IFC4X2_types[852]);
    IFC4X2_types[873] = new entity("IfcRelInterferesElements", false, 873, (entity*) IFC4X2_types[852]);
    IFC4X2_types[874] = new entity("IfcRelNests", false, 874, (entity*) IFC4X2_types[865]);
    IFC4X2_types[875] = new entity("IfcRelPositions", false, 875, (entity*) IFC4X2_types[852]);
    IFC4X2_types[876] = new entity("IfcRelProjectsElement", false, 876, (entity*) IFC4X2_types[865]);
    IFC4X2_types[877] = new entity("IfcRelReferencedInSpatialStructure", false, 877, (entity*) IFC4X2_types[852]);
    IFC4X2_types[878] = new entity("IfcRelSequence", false, 878, (entity*) IFC4X2_types[852]);
    IFC4X2_types[879] = new entity("IfcRelServicesBuildings", false, 879, (entity*) IFC4X2_types[852]);
    IFC4X2_types[880] = new entity("IfcRelSpaceBoundary", false, 880, (entity*) IFC4X2_types[852]);
    IFC4X2_types[881] = new entity("IfcRelSpaceBoundary1stLevel", false, 881, (entity*) IFC4X2_types[880]);
    IFC4X2_types[882] = new entity("IfcRelSpaceBoundary2ndLevel", false, 882, (entity*) IFC4X2_types[881]);
    IFC4X2_types[883] = new entity("IfcRelVoidsElement", false, 883, (entity*) IFC4X2_types[865]);
    IFC4X2_types[884] = new entity("IfcReparametrisedCompositeCurveSegment", false, 884, (entity*) IFC4X2_types[190]);
    IFC4X2_types[889] = new entity("IfcResource", true, 889, (entity*) IFC4X2_types[646]);
    IFC4X2_types[896] = new entity("IfcRevolvedAreaSolid", false, 896, (entity*) IFC4X2_types[1060]);
    IFC4X2_types[897] = new entity("IfcRevolvedAreaSolidTapered", false, 897, (entity*) IFC4X2_types[896]);
    IFC4X2_types[898] = new entity("IfcRightCircularCone", false, 898, (entity*) IFC4X2_types[251]);
    IFC4X2_types[899] = new entity("IfcRightCircularCylinder", false, 899, (entity*) IFC4X2_types[251]);
    IFC4X2_types[916] = new entity("IfcSectionedSolid", true, 916, (entity*) IFC4X2_types[956]);
    IFC4X2_types[917] = new entity("IfcSectionedSolidHorizontal", false, 917, (entity*) IFC4X2_types[916]);
    IFC4X2_types[938] = new entity("IfcSimplePropertyTemplate", false, 938, (entity*) IFC4X2_types[779]);
    IFC4X2_types[969] = new entity("IfcSpatialElement", true, 969, (entity*) IFC4X2_types[746]);
    IFC4X2_types[970] = new entity("IfcSpatialElementType", true, 970, (entity*) IFC4X2_types[1155]);
    IFC4X2_types[971] = new entity("IfcSpatialStructureElement", true, 971, (entity*) IFC4X2_types[969]);
    IFC4X2_types[972] = new entity("IfcSpatialStructureElementType", true, 972, (entity*) IFC4X2_types[970]);
    IFC4X2_types[973] = new entity("IfcSpatialZone", false, 973, (entity*) IFC4X2_types[969]);
    IFC4X2_types[974] = new entity("IfcSpatialZoneType", false, 974, (entity*) IFC4X2_types[970]);
    IFC4X2_types[980] = new entity("IfcSphere", false, 980, (entity*) IFC4X2_types[251]);
    IFC4X2_types[981] = new entity("IfcSphericalSurface", false, 981, (entity*) IFC4X2_types[373]);
    IFC4X2_types[993] = new entity("IfcStructuralActivity", true, 993, (entity*) IFC4X2_types[746]);
    IFC4X2_types[1005] = new entity("IfcStructuralItem", true, 1005, (entity*) IFC4X2_types[746]);
    IFC4X2_types[1020] = new entity("IfcStructuralMember", true, 1020, (entity*) IFC4X2_types[1005]);
    IFC4X2_types[1025] = new entity("IfcStructuralReaction", true, 1025, (entity*) IFC4X2_types[993]);
    IFC4X2_types[1030] = new entity("IfcStructuralSurfaceMember", false, 1030, (entity*) IFC4X2_types[1020]);
    IFC4X2_types[1032] = new entity("IfcStructuralSurfaceMemberVarying", false, 1032, (entity*) IFC4X2_types[1030]);
    IFC4X2_types[1033] = new entity("IfcStructuralSurfaceReaction", false, 1033, (entity*) IFC4X2_types[1025]);
    IFC4X2_types[1039] = new entity("IfcSubContractResourceType", false, 1039, (entity*) IFC4X2_types[220]);
    IFC4X2_types[1043] = new entity("IfcSurfaceCurve", false, 1043, (entity*) IFC4X2_types[260]);
    IFC4X2_types[1044] = new entity("IfcSurfaceCurveSweptAreaSolid", false, 1044, (entity*) IFC4X2_types[1060]);
    IFC4X2_types[1047] = new entity("IfcSurfaceOfLinearExtrusion", false, 1047, (entity*) IFC4X2_types[1063]);
    IFC4X2_types[1048] = new entity("IfcSurfaceOfRevolution", false, 1048, (entity*) IFC4X2_types[1063]);
    IFC4X2_types[1069] = new entity("IfcSystemFurnitureElementType", false, 1069, (entity*) IFC4X2_types[473]);
    IFC4X2_types[1077] = new entity("IfcTask", false, 1077, (entity*) IFC4X2_types[744]);
    IFC4X2_types[1081] = new entity("IfcTaskType", false, 1081, (entity*) IFC4X2_types[1154]);
    IFC4X2_types[1095] = new entity("IfcTessellatedFaceSet", true, 1095, (entity*) IFC4X2_types[1096]);
    IFC4X2_types[1131] = new entity("IfcToroidalSurface", false, 1131, (entity*) IFC4X2_types[373]);
    IFC4X2_types[1141] = new entity("IfcTransportElementType", false, 1141, (entity*) IFC4X2_types[381]);
    IFC4X2_types[1144] = new entity("IfcTriangulatedFaceSet", false, 1144, (entity*) IFC4X2_types[1095]);
    IFC4X2_types[1145] = new entity("IfcTriangulatedIrregularNetwork", false, 1145, (entity*) IFC4X2_types[1144]);
    IFC4X2_types[1202] = new entity("IfcWindowLiningProperties", false, 1202, (entity*) IFC4X2_types[730]);
    IFC4X2_types[1205] = new entity("IfcWindowPanelProperties", false, 1205, (entity*) IFC4X2_types[730]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[611]);
        items.push_back(IFC4X2_types[818]);
        items.push_back(IFC4X2_types[1168]);
        IFC4X2_types[48] = new select_type("IfcAppliedValueSelect", 48, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[66]);
        items.push_back(IFC4X2_types[67]);
        IFC4X2_types[65] = new select_type("IfcAxis2Placement", 65, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4X2_types[88]);
        items.push_back(IFC4X2_types[251]);
        items.push_back(IFC4X2_types[495]);
        items.push_back(IFC4X2_types[956]);
        items.push_back(IFC4X2_types[1095]);
        IFC4X2_types[86] = new select_type("IfcBooleanOperand", 86, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[176]);
        items.push_back(IFC4X2_types[726]);
        IFC4X2_types[172] = new select_type("IfcColour", 172, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[174]);
        items.push_back(IFC4X2_types[643]);
        IFC4X2_types[173] = new select_type("IfcColourOrFactor", 173, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[88]);
        items.push_back(IFC4X2_types[251]);
        IFC4X2_types[252] = new select_type("IfcCsgSelect", 252, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[269]);
        items.push_back(IFC4X2_types[727]);
        IFC4X2_types[272] = new select_type("IfcCurveStyleFontSelect", 272, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC4X2_types[172]);
        items.push_back(IFC4X2_types[403]);
        items.push_back(IFC4X2_types[433]);
        items.push_back(IFC4X2_types[434]);
        IFC4X2_types[435] = new select_type("IfcFillStyleSelect", 435, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[260]);
        items.push_back(IFC4X2_types[710]);
        items.push_back(IFC4X2_types[1042]);
        IFC4X2_types[486] = new select_type("IfcGeometricSetSelect", 486, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[293]);
        items.push_back(IFC4X2_types[1185]);
        IFC4X2_types[492] = new select_type("IfcGridPlacementDirectionSelect", 492, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4X2_types[47]);
        items.push_back(IFC4X2_types[611]);
        items.push_back(IFC4X2_types[818]);
        items.push_back(IFC4X2_types[1071]);
        items.push_back(IFC4X2_types[1125]);
        items.push_back(IFC4X2_types[1168]);
        IFC4X2_types[623] = new select_type("IfcMetricValueSelect", 623, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[744]);
        items.push_back(IFC4X2_types[1154]);
        IFC4X2_types[745] = new select_type("IfcProcessSelect", 745, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[746]);
        items.push_back(IFC4X2_types[1155]);
        IFC4X2_types[750] = new select_type("IfcProductSelect", 750, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[772]);
        items.push_back(IFC4X2_types[774]);
        IFC4X2_types[773] = new select_type("IfcPropertySetDefinitionSelect", 773, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[889]);
        items.push_back(IFC4X2_types[1156]);
        IFC4X2_types[894] = new select_type("IfcResourceSelect", 894, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[168]);
        items.push_back(IFC4X2_types[662]);
        IFC4X2_types[935] = new select_type("IfcShell", 935, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[168]);
        items.push_back(IFC4X2_types[956]);
        IFC4X2_types[957] = new select_type("IfcSolidOrShell", 957, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[414]);
        items.push_back(IFC4X2_types[417]);
        items.push_back(IFC4X2_types[1042]);
        IFC4X2_types[1049] = new select_type("IfcSurfaceOrFaceSurface", 1049, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[141]);
        items.push_back(IFC4X2_types[673]);
        IFC4X2_types[1148] = new select_type("IfcTrimmingSelect", 1148, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[293]);
        items.push_back(IFC4X2_types[1173]);
        IFC4X2_types[1174] = new select_type("IfcVectorOrDirection", 1174, items);
    }
    IFC4X2_types[6] = new entity("IfcActor", false, 6, (entity*) IFC4X2_types[646]);
    IFC4X2_types[14] = new entity("IfcAdvancedBrep", false, 14, (entity*) IFC4X2_types[583]);
    IFC4X2_types[15] = new entity("IfcAdvancedBrepWithVoids", false, 15, (entity*) IFC4X2_types[14]);
    IFC4X2_types[31] = new entity("IfcAlignment2DHorizontalSegment", false, 31, (entity*) IFC4X2_types[32]);
    IFC4X2_types[33] = new entity("IfcAlignment2DVerSegCircularArc", false, 33, (entity*) IFC4X2_types[37]);
    IFC4X2_types[34] = new entity("IfcAlignment2DVerSegLine", false, 34, (entity*) IFC4X2_types[37]);
    IFC4X2_types[35] = new entity("IfcAlignment2DVerSegParabolicArc", false, 35, (entity*) IFC4X2_types[37]);
    IFC4X2_types[44] = new entity("IfcAnnotation", false, 44, (entity*) IFC4X2_types[746]);
    IFC4X2_types[107] = new entity("IfcBSplineSurface", true, 107, (entity*) IFC4X2_types[96]);
    IFC4X2_types[109] = new entity("IfcBSplineSurfaceWithKnots", false, 109, (entity*) IFC4X2_types[107]);
    IFC4X2_types[80] = new entity("IfcBlock", false, 80, (entity*) IFC4X2_types[251]);
    IFC4X2_types[85] = new entity("IfcBooleanClippingResult", false, 85, (entity*) IFC4X2_types[88]);
    IFC4X2_types[95] = new entity("IfcBoundedCurve", true, 95, (entity*) IFC4X2_types[260]);
    IFC4X2_types[118] = new entity("IfcBuildingElementType", true, 118, (entity*) IFC4X2_types[381]);
    IFC4X2_types[156] = new entity("IfcChimneyType", false, 156, (entity*) IFC4X2_types[118]);
    IFC4X2_types[159] = new entity("IfcCircleHollowProfileDef", false, 159, (entity*) IFC4X2_types[160]);
    IFC4X2_types[163] = new entity("IfcCivilElementType", false, 163, (entity*) IFC4X2_types[381]);
    IFC4X2_types[179] = new entity("IfcColumnType", false, 179, (entity*) IFC4X2_types[118]);
    IFC4X2_types[186] = new entity("IfcComplexPropertyTemplate", false, 186, (entity*) IFC4X2_types[779]);
    IFC4X2_types[188] = new entity("IfcCompositeCurve", false, 188, (entity*) IFC4X2_types[95]);
    IFC4X2_types[189] = new entity("IfcCompositeCurveOnSurface", false, 189, (entity*) IFC4X2_types[188]);
    IFC4X2_types[199] = new entity("IfcConic", true, 199, (entity*) IFC4X2_types[260]);
    IFC4X2_types[211] = new entity("IfcConstructionEquipmentResourceType", false, 211, (entity*) IFC4X2_types[220]);
    IFC4X2_types[214] = new entity("IfcConstructionMaterialResourceType", false, 214, (entity*) IFC4X2_types[220]);
    IFC4X2_types[217] = new entity("IfcConstructionProductResourceType", false, 217, (entity*) IFC4X2_types[220]);
    IFC4X2_types[219] = new entity("IfcConstructionResource", true, 219, (entity*) IFC4X2_types[889]);
    IFC4X2_types[224] = new entity("IfcControl", true, 224, (entity*) IFC4X2_types[646]);
    IFC4X2_types[239] = new entity("IfcCostItem", false, 239, (entity*) IFC4X2_types[224]);
    IFC4X2_types[241] = new entity("IfcCostSchedule", false, 241, (entity*) IFC4X2_types[224]);
    IFC4X2_types[246] = new entity("IfcCoveringType", false, 246, (entity*) IFC4X2_types[118]);
    IFC4X2_types[248] = new entity("IfcCrewResource", false, 248, (entity*) IFC4X2_types[219]);
    IFC4X2_types[257] = new entity("IfcCurtainWallType", false, 257, (entity*) IFC4X2_types[118]);
    IFC4X2_types[267] = new entity("IfcCurveSegment2D", true, 267, (entity*) IFC4X2_types[95]);
    IFC4X2_types[273] = new entity("IfcCylindricalSurface", false, 273, (entity*) IFC4X2_types[373]);
    IFC4X2_types[283] = new entity("IfcDeepFoundationType", false, 283, (entity*) IFC4X2_types[118]);
    IFC4X2_types[306] = new entity("IfcDistributionElementType", false, 306, (entity*) IFC4X2_types[381]);
    IFC4X2_types[308] = new entity("IfcDistributionFlowElementType", true, 308, (entity*) IFC4X2_types[306]);
    IFC4X2_types[320] = new entity("IfcDoorLiningProperties", false, 320, (entity*) IFC4X2_types[730]);
    IFC4X2_types[323] = new entity("IfcDoorPanelProperties", false, 323, (entity*) IFC4X2_types[730]);
    IFC4X2_types[328] = new entity("IfcDoorType", false, 328, (entity*) IFC4X2_types[118]);
    IFC4X2_types[332] = new entity("IfcDraughtingPreDefinedColour", false, 332, (entity*) IFC4X2_types[726]);
    IFC4X2_types[333] = new entity("IfcDraughtingPreDefinedCurveFont", false, 333, (entity*) IFC4X2_types[727]);
    IFC4X2_types[372] = new entity("IfcElement", true, 372, (entity*) IFC4X2_types[746]);
    IFC4X2_types[374] = new entity("IfcElementAssembly", false, 374, (entity*) IFC4X2_types[372]);
    IFC4X2_types[375] = new entity("IfcElementAssemblyType", false, 375, (entity*) IFC4X2_types[381]);
    IFC4X2_types[377] = new entity("IfcElementComponent", true, 377, (entity*) IFC4X2_types[372]);
    IFC4X2_types[378] = new entity("IfcElementComponentType", true, 378, (entity*) IFC4X2_types[381]);
    IFC4X2_types[382] = new entity("IfcEllipse", false, 382, (entity*) IFC4X2_types[199]);
    IFC4X2_types[385] = new entity("IfcEnergyConversionDeviceType", true, 385, (entity*) IFC4X2_types[308]);
    IFC4X2_types[388] = new entity("IfcEngineType", false, 388, (entity*) IFC4X2_types[385]);
    IFC4X2_types[391] = new entity("IfcEvaporativeCoolerType", false, 391, (entity*) IFC4X2_types[385]);
    IFC4X2_types[394] = new entity("IfcEvaporatorType", false, 394, (entity*) IFC4X2_types[385]);
    IFC4X2_types[396] = new entity("IfcEvent", false, 396, (entity*) IFC4X2_types[744]);
    IFC4X2_types[410] = new entity("IfcExternalSpatialStructureElement", true, 410, (entity*) IFC4X2_types[969]);
    IFC4X2_types[418] = new entity("IfcFacetedBrep", false, 418, (entity*) IFC4X2_types[583]);
    IFC4X2_types[419] = new entity("IfcFacetedBrepWithVoids", false, 419, (entity*) IFC4X2_types[418]);
    IFC4X2_types[420] = new entity("IfcFacility", false, 420, (entity*) IFC4X2_types[971]);
    IFC4X2_types[421] = new entity("IfcFacilityPart", false, 421, (entity*) IFC4X2_types[971]);
    IFC4X2_types[426] = new entity("IfcFastener", false, 426, (entity*) IFC4X2_types[377]);
    IFC4X2_types[427] = new entity("IfcFastenerType", false, 427, (entity*) IFC4X2_types[378]);
    IFC4X2_types[429] = new entity("IfcFeatureElement", true, 429, (entity*) IFC4X2_types[372]);
    IFC4X2_types[430] = new entity("IfcFeatureElementAddition", true, 430, (entity*) IFC4X2_types[429]);
    IFC4X2_types[431] = new entity("IfcFeatureElementSubtraction", true, 431, (entity*) IFC4X2_types[429]);
    IFC4X2_types[444] = new entity("IfcFlowControllerType", true, 444, (entity*) IFC4X2_types[308]);
    IFC4X2_types[447] = new entity("IfcFlowFittingType", true, 447, (entity*) IFC4X2_types[308]);
    IFC4X2_types[452] = new entity("IfcFlowMeterType", false, 452, (entity*) IFC4X2_types[444]);
    IFC4X2_types[455] = new entity("IfcFlowMovingDeviceType", true, 455, (entity*) IFC4X2_types[308]);
    IFC4X2_types[457] = new entity("IfcFlowSegmentType", true, 457, (entity*) IFC4X2_types[308]);
    IFC4X2_types[459] = new entity("IfcFlowStorageDeviceType", true, 459, (entity*) IFC4X2_types[308]);
    IFC4X2_types[461] = new entity("IfcFlowTerminalType", true, 461, (entity*) IFC4X2_types[308]);
    IFC4X2_types[463] = new entity("IfcFlowTreatmentDeviceType", true, 463, (entity*) IFC4X2_types[308]);
    IFC4X2_types[468] = new entity("IfcFootingType", false, 468, (entity*) IFC4X2_types[118]);
    IFC4X2_types[472] = new entity("IfcFurnishingElement", false, 472, (entity*) IFC4X2_types[372]);
    IFC4X2_types[474] = new entity("IfcFurniture", false, 474, (entity*) IFC4X2_types[472]);
    IFC4X2_types[477] = new entity("IfcGeographicElement", false, 477, (entity*) IFC4X2_types[372]);
    IFC4X2_types[494] = new entity("IfcGroup", false, 494, (entity*) IFC4X2_types[646]);
    IFC4X2_types[498] = new entity("IfcHeatExchangerType", false, 498, (entity*) IFC4X2_types[385]);
    IFC4X2_types[503] = new entity("IfcHumidifierType", false, 503, (entity*) IFC4X2_types[385]);
    IFC4X2_types[509] = new entity("IfcIndexedPolyCurve", false, 509, (entity*) IFC4X2_types[95]);
    IFC4X2_types[518] = new entity("IfcInterceptorType", false, 518, (entity*) IFC4X2_types[463]);
    IFC4X2_types[521] = new entity("IfcIntersectionCurve", false, 521, (entity*) IFC4X2_types[1043]);
    IFC4X2_types[522] = new entity("IfcInventory", false, 522, (entity*) IFC4X2_types[494]);
    IFC4X2_types[530] = new entity("IfcJunctionBoxType", false, 530, (entity*) IFC4X2_types[447]);
    IFC4X2_types[535] = new entity("IfcLaborResource", false, 535, (entity*) IFC4X2_types[219]);
    IFC4X2_types[540] = new entity("IfcLampType", false, 540, (entity*) IFC4X2_types[461]);
    IFC4X2_types[554] = new entity("IfcLightFixtureType", false, 554, (entity*) IFC4X2_types[461]);
    IFC4X2_types[571] = new entity("IfcLineSegment2D", false, 571, (entity*) IFC4X2_types[267]);
    IFC4X2_types[612] = new entity("IfcMechanicalFastener", false, 612, (entity*) IFC4X2_types[377]);
    IFC4X2_types[613] = new entity("IfcMechanicalFastenerType", false, 613, (entity*) IFC4X2_types[378]);
    IFC4X2_types[616] = new entity("IfcMedicalDeviceType", false, 616, (entity*) IFC4X2_types[461]);
    IFC4X2_types[620] = new entity("IfcMemberType", false, 620, (entity*) IFC4X2_types[118]);
    IFC4X2_types[639] = new entity("IfcMotorConnectionType", false, 639, (entity*) IFC4X2_types[385]);
    IFC4X2_types[653] = new entity("IfcOccupant", false, 653, (entity*) IFC4X2_types[6]);
    IFC4X2_types[659] = new entity("IfcOpeningElement", false, 659, (entity*) IFC4X2_types[431]);
    IFC4X2_types[661] = new entity("IfcOpeningStandardCase", false, 661, (entity*) IFC4X2_types[659]);
    IFC4X2_types[669] = new entity("IfcOutletType", false, 669, (entity*) IFC4X2_types[461]);
    IFC4X2_types[676] = new entity("IfcPerformanceHistory", false, 676, (entity*) IFC4X2_types[224]);
    IFC4X2_types[679] = new entity("IfcPermeableCoveringProperties", false, 679, (entity*) IFC4X2_types[730]);
    IFC4X2_types[680] = new entity("IfcPermit", false, 680, (entity*) IFC4X2_types[224]);
    IFC4X2_types[691] = new entity("IfcPileType", false, 691, (entity*) IFC4X2_types[283]);
    IFC4X2_types[694] = new entity("IfcPipeFittingType", false, 694, (entity*) IFC4X2_types[447]);
    IFC4X2_types[697] = new entity("IfcPipeSegmentType", false, 697, (entity*) IFC4X2_types[457]);
    IFC4X2_types[708] = new entity("IfcPlateType", false, 708, (entity*) IFC4X2_types[118]);
    IFC4X2_types[715] = new entity("IfcPolygonalFaceSet", false, 715, (entity*) IFC4X2_types[1095]);
    IFC4X2_types[716] = new entity("IfcPolyline", false, 716, (entity*) IFC4X2_types[95]);
    IFC4X2_types[718] = new entity("IfcPort", true, 718, (entity*) IFC4X2_types[746]);
    IFC4X2_types[719] = new entity("IfcPositioningElement", true, 719, (entity*) IFC4X2_types[746]);
    IFC4X2_types[741] = new entity("IfcProcedure", false, 741, (entity*) IFC4X2_types[744]);
    IFC4X2_types[760] = new entity("IfcProjectOrder", false, 760, (entity*) IFC4X2_types[224]);
    IFC4X2_types[757] = new entity("IfcProjectionElement", false, 757, (entity*) IFC4X2_types[430]);
    IFC4X2_types[785] = new entity("IfcProtectiveDeviceType", false, 785, (entity*) IFC4X2_types[444]);
    IFC4X2_types[789] = new entity("IfcPumpType", false, 789, (entity*) IFC4X2_types[455]);
    IFC4X2_types[800] = new entity("IfcRailingType", false, 800, (entity*) IFC4X2_types[118]);
    IFC4X2_types[804] = new entity("IfcRampFlightType", false, 804, (entity*) IFC4X2_types[118]);
    IFC4X2_types[806] = new entity("IfcRampType", false, 806, (entity*) IFC4X2_types[118]);
    IFC4X2_types[810] = new entity("IfcRationalBSplineSurfaceWithKnots", false, 810, (entity*) IFC4X2_types[109]);
    IFC4X2_types[819] = new entity("IfcReferent", false, 819, (entity*) IFC4X2_types[719]);
    IFC4X2_types[830] = new entity("IfcReinforcingElement", true, 830, (entity*) IFC4X2_types[377]);
    IFC4X2_types[831] = new entity("IfcReinforcingElementType", true, 831, (entity*) IFC4X2_types[378]);
    IFC4X2_types[832] = new entity("IfcReinforcingMesh", false, 832, (entity*) IFC4X2_types[830]);
    IFC4X2_types[833] = new entity("IfcReinforcingMeshType", false, 833, (entity*) IFC4X2_types[831]);
    IFC4X2_types[835] = new entity("IfcRelAggregates", false, 835, (entity*) IFC4X2_types[865]);
    IFC4X2_types[902] = new entity("IfcRoofType", false, 902, (entity*) IFC4X2_types[118]);
    IFC4X2_types[911] = new entity("IfcSanitaryTerminalType", false, 911, (entity*) IFC4X2_types[461]);
    IFC4X2_types[914] = new entity("IfcSeamCurve", false, 914, (entity*) IFC4X2_types[1043]);
    IFC4X2_types[929] = new entity("IfcShadingDeviceType", false, 929, (entity*) IFC4X2_types[118]);
    IFC4X2_types[942] = new entity("IfcSite", false, 942, (entity*) IFC4X2_types[971]);
    IFC4X2_types[949] = new entity("IfcSlabType", false, 949, (entity*) IFC4X2_types[118]);
    IFC4X2_types[953] = new entity("IfcSolarDeviceType", false, 953, (entity*) IFC4X2_types[385]);
    IFC4X2_types[962] = new entity("IfcSpace", false, 962, (entity*) IFC4X2_types[971]);
    IFC4X2_types[965] = new entity("IfcSpaceHeaterType", false, 965, (entity*) IFC4X2_types[461]);
    IFC4X2_types[967] = new entity("IfcSpaceType", false, 967, (entity*) IFC4X2_types[972]);
    IFC4X2_types[983] = new entity("IfcStackTerminalType", false, 983, (entity*) IFC4X2_types[461]);
    IFC4X2_types[987] = new entity("IfcStairFlightType", false, 987, (entity*) IFC4X2_types[118]);
    IFC4X2_types[989] = new entity("IfcStairType", false, 989, (entity*) IFC4X2_types[118]);
    IFC4X2_types[992] = new entity("IfcStructuralAction", true, 992, (entity*) IFC4X2_types[993]);
    IFC4X2_types[996] = new entity("IfcStructuralConnection", true, 996, (entity*) IFC4X2_types[1005]);
    IFC4X2_types[998] = new entity("IfcStructuralCurveAction", false, 998, (entity*) IFC4X2_types[992]);
    IFC4X2_types[1000] = new entity("IfcStructuralCurveConnection", false, 1000, (entity*) IFC4X2_types[996]);
    IFC4X2_types[1001] = new entity("IfcStructuralCurveMember", false, 1001, (entity*) IFC4X2_types[1020]);
    IFC4X2_types[1003] = new entity("IfcStructuralCurveMemberVarying", false, 1003, (entity*) IFC4X2_types[1001]);
    IFC4X2_types[1004] = new entity("IfcStructuralCurveReaction", false, 1004, (entity*) IFC4X2_types[1025]);
    IFC4X2_types[1006] = new entity("IfcStructuralLinearAction", false, 1006, (entity*) IFC4X2_types[998]);
    IFC4X2_types[1010] = new entity("IfcStructuralLoadGroup", false, 1010, (entity*) IFC4X2_types[494]);
    IFC4X2_types[1022] = new entity("IfcStructuralPointAction", false, 1022, (entity*) IFC4X2_types[992]);
    IFC4X2_types[1023] = new entity("IfcStructuralPointConnection", false, 1023, (entity*) IFC4X2_types[996]);
    IFC4X2_types[1024] = new entity("IfcStructuralPointReaction", false, 1024, (entity*) IFC4X2_types[1025]);
    IFC4X2_types[1026] = new entity("IfcStructuralResultGroup", false, 1026, (entity*) IFC4X2_types[494]);
    IFC4X2_types[1027] = new entity("IfcStructuralSurfaceAction", false, 1027, (entity*) IFC4X2_types[992]);
    IFC4X2_types[1029] = new entity("IfcStructuralSurfaceConnection", false, 1029, (entity*) IFC4X2_types[996]);
    IFC4X2_types[1038] = new entity("IfcSubContractResource", false, 1038, (entity*) IFC4X2_types[219]);
    IFC4X2_types[1045] = new entity("IfcSurfaceFeature", false, 1045, (entity*) IFC4X2_types[429]);
    IFC4X2_types[1065] = new entity("IfcSwitchingDeviceType", false, 1065, (entity*) IFC4X2_types[444]);
    IFC4X2_types[1067] = new entity("IfcSystem", false, 1067, (entity*) IFC4X2_types[494]);
    IFC4X2_types[1068] = new entity("IfcSystemFurnitureElement", false, 1068, (entity*) IFC4X2_types[472]);
    IFC4X2_types[1075] = new entity("IfcTankType", false, 1075, (entity*) IFC4X2_types[459]);
    IFC4X2_types[1086] = new entity("IfcTendon", false, 1086, (entity*) IFC4X2_types[830]);
    IFC4X2_types[1087] = new entity("IfcTendonAnchor", false, 1087, (entity*) IFC4X2_types[830]);
    IFC4X2_types[1088] = new entity("IfcTendonAnchorType", false, 1088, (entity*) IFC4X2_types[831]);
    IFC4X2_types[1090] = new entity("IfcTendonConduit", false, 1090, (entity*) IFC4X2_types[830]);
    IFC4X2_types[1091] = new entity("IfcTendonConduitType", false, 1091, (entity*) IFC4X2_types[831]);
    IFC4X2_types[1093] = new entity("IfcTendonType", false, 1093, (entity*) IFC4X2_types[831]);
    IFC4X2_types[1134] = new entity("IfcTransformerType", false, 1134, (entity*) IFC4X2_types[385]);
    IFC4X2_types[1137] = new entity("IfcTransitionCurveSegment2D", false, 1137, (entity*) IFC4X2_types[267]);
    IFC4X2_types[1140] = new entity("IfcTransportElement", false, 1140, (entity*) IFC4X2_types[372]);
    IFC4X2_types[1146] = new entity("IfcTrimmedCurve", false, 1146, (entity*) IFC4X2_types[95]);
    IFC4X2_types[1151] = new entity("IfcTubeBundleType", false, 1151, (entity*) IFC4X2_types[385]);
    IFC4X2_types[1162] = new entity("IfcUnitaryEquipmentType", false, 1162, (entity*) IFC4X2_types[385]);
    IFC4X2_types[1170] = new entity("IfcValveType", false, 1170, (entity*) IFC4X2_types[444]);
    IFC4X2_types[1178] = new entity("IfcVibrationDamper", false, 1178, (entity*) IFC4X2_types[377]);
    IFC4X2_types[1179] = new entity("IfcVibrationDamperType", false, 1179, (entity*) IFC4X2_types[378]);
    IFC4X2_types[1181] = new entity("IfcVibrationIsolator", false, 1181, (entity*) IFC4X2_types[377]);
    IFC4X2_types[1182] = new entity("IfcVibrationIsolatorType", false, 1182, (entity*) IFC4X2_types[378]);
    IFC4X2_types[1184] = new entity("IfcVirtualElement", false, 1184, (entity*) IFC4X2_types[372]);
    IFC4X2_types[1186] = new entity("IfcVoidingFeature", false, 1186, (entity*) IFC4X2_types[431]);
    IFC4X2_types[1193] = new entity("IfcWallType", false, 1193, (entity*) IFC4X2_types[118]);
    IFC4X2_types[1199] = new entity("IfcWasteTerminalType", false, 1199, (entity*) IFC4X2_types[461]);
    IFC4X2_types[1210] = new entity("IfcWindowType", false, 1210, (entity*) IFC4X2_types[118]);
    IFC4X2_types[1213] = new entity("IfcWorkCalendar", false, 1213, (entity*) IFC4X2_types[224]);
    IFC4X2_types[1215] = new entity("IfcWorkControl", true, 1215, (entity*) IFC4X2_types[224]);
    IFC4X2_types[1216] = new entity("IfcWorkPlan", false, 1216, (entity*) IFC4X2_types[1215]);
    IFC4X2_types[1218] = new entity("IfcWorkSchedule", false, 1218, (entity*) IFC4X2_types[1215]);
    IFC4X2_types[1221] = new entity("IfcZone", false, 1221, (entity*) IFC4X2_types[1067]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[270]);
        items.push_back(IFC4X2_types[272]);
        IFC4X2_types[263] = new select_type("IfcCurveFontOrScaledCurveFontSelect", 263, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4X2_types[189]);
        items.push_back(IFC4X2_types[675]);
        items.push_back(IFC4X2_types[1043]);
        IFC4X2_types[265] = new select_type("IfcCurveOnSurface", 265, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[95]);
        items.push_back(IFC4X2_types[346]);
        IFC4X2_types[266] = new select_type("IfcCurveOrEdgeCurve", 266, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[372]);
        items.push_back(IFC4X2_types[1005]);
        IFC4X2_types[994] = new select_type("IfcStructuralActivityAssignmentSelect", 994, items);
    }
    IFC4X2_types[2] = new entity("IfcActionRequest", false, 2, (entity*) IFC4X2_types[224]);
    IFC4X2_types[19] = new entity("IfcAirTerminalBoxType", false, 19, (entity*) IFC4X2_types[444]);
    IFC4X2_types[21] = new entity("IfcAirTerminalType", false, 21, (entity*) IFC4X2_types[461]);
    IFC4X2_types[24] = new entity("IfcAirToAirHeatRecoveryType", false, 24, (entity*) IFC4X2_types[385]);
    IFC4X2_types[38] = new entity("IfcAlignmentCurve", false, 38, (entity*) IFC4X2_types[95]);
    IFC4X2_types[59] = new entity("IfcAsset", false, 59, (entity*) IFC4X2_types[494]);
    IFC4X2_types[62] = new entity("IfcAudioVisualApplianceType", false, 62, (entity*) IFC4X2_types[461]);
    IFC4X2_types[104] = new entity("IfcBSplineCurve", true, 104, (entity*) IFC4X2_types[95]);
    IFC4X2_types[106] = new entity("IfcBSplineCurveWithKnots", false, 106, (entity*) IFC4X2_types[104]);
    IFC4X2_types[70] = new entity("IfcBeamType", false, 70, (entity*) IFC4X2_types[118]);
    IFC4X2_types[73] = new entity("IfcBearingType", false, 73, (entity*) IFC4X2_types[118]);
    IFC4X2_types[82] = new entity("IfcBoilerType", false, 82, (entity*) IFC4X2_types[385]);
    IFC4X2_types[90] = new entity("IfcBoundaryCurve", false, 90, (entity*) IFC4X2_types[189]);
    IFC4X2_types[100] = new entity("IfcBridge", false, 100, (entity*) IFC4X2_types[420]);
    IFC4X2_types[101] = new entity("IfcBridgePart", false, 101, (entity*) IFC4X2_types[421]);
    IFC4X2_types[110] = new entity("IfcBuilding", false, 110, (entity*) IFC4X2_types[420]);
    IFC4X2_types[111] = new entity("IfcBuildingElement", true, 111, (entity*) IFC4X2_types[372]);
    IFC4X2_types[112] = new entity("IfcBuildingElementPart", false, 112, (entity*) IFC4X2_types[377]);
    IFC4X2_types[113] = new entity("IfcBuildingElementPartType", false, 113, (entity*) IFC4X2_types[378]);
    IFC4X2_types[115] = new entity("IfcBuildingElementProxy", false, 115, (entity*) IFC4X2_types[111]);
    IFC4X2_types[116] = new entity("IfcBuildingElementProxyType", false, 116, (entity*) IFC4X2_types[118]);
    IFC4X2_types[119] = new entity("IfcBuildingStorey", false, 119, (entity*) IFC4X2_types[421]);
    IFC4X2_types[120] = new entity("IfcBuildingSystem", false, 120, (entity*) IFC4X2_types[1067]);
    IFC4X2_types[123] = new entity("IfcBurnerType", false, 123, (entity*) IFC4X2_types[385]);
    IFC4X2_types[126] = new entity("IfcCableCarrierFittingType", false, 126, (entity*) IFC4X2_types[447]);
    IFC4X2_types[129] = new entity("IfcCableCarrierSegmentType", false, 129, (entity*) IFC4X2_types[457]);
    IFC4X2_types[132] = new entity("IfcCableFittingType", false, 132, (entity*) IFC4X2_types[447]);
    IFC4X2_types[135] = new entity("IfcCableSegmentType", false, 135, (entity*) IFC4X2_types[457]);
    IFC4X2_types[138] = new entity("IfcCaissonFoundationType", false, 138, (entity*) IFC4X2_types[283]);
    IFC4X2_types[153] = new entity("IfcChillerType", false, 153, (entity*) IFC4X2_types[385]);
    IFC4X2_types[155] = new entity("IfcChimney", false, 155, (entity*) IFC4X2_types[111]);
    IFC4X2_types[158] = new entity("IfcCircle", false, 158, (entity*) IFC4X2_types[199]);
    IFC4X2_types[161] = new entity("IfcCircularArcSegment2D", false, 161, (entity*) IFC4X2_types[267]);
    IFC4X2_types[162] = new entity("IfcCivilElement", false, 162, (entity*) IFC4X2_types[372]);
    IFC4X2_types[170] = new entity("IfcCoilType", false, 170, (entity*) IFC4X2_types[385]);
    IFC4X2_types[177] = new entity("IfcColumn", false, 177, (entity*) IFC4X2_types[111]);
    IFC4X2_types[178] = new entity("IfcColumnStandardCase", false, 178, (entity*) IFC4X2_types[177]);
    IFC4X2_types[182] = new entity("IfcCommunicationsApplianceType", false, 182, (entity*) IFC4X2_types[461]);
    IFC4X2_types[194] = new entity("IfcCompressorType", false, 194, (entity*) IFC4X2_types[455]);
    IFC4X2_types[197] = new entity("IfcCondenserType", false, 197, (entity*) IFC4X2_types[385]);
    IFC4X2_types[210] = new entity("IfcConstructionEquipmentResource", false, 210, (entity*) IFC4X2_types[219]);
    IFC4X2_types[213] = new entity("IfcConstructionMaterialResource", false, 213, (entity*) IFC4X2_types[219]);
    IFC4X2_types[216] = new entity("IfcConstructionProductResource", false, 216, (entity*) IFC4X2_types[219]);
    IFC4X2_types[231] = new entity("IfcCooledBeamType", false, 231, (entity*) IFC4X2_types[385]);
    IFC4X2_types[234] = new entity("IfcCoolingTowerType", false, 234, (entity*) IFC4X2_types[385]);
    IFC4X2_types[245] = new entity("IfcCovering", false, 245, (entity*) IFC4X2_types[111]);
    IFC4X2_types[256] = new entity("IfcCurtainWall", false, 256, (entity*) IFC4X2_types[111]);
    IFC4X2_types[275] = new entity("IfcDamperType", false, 275, (entity*) IFC4X2_types[444]);
    IFC4X2_types[282] = new entity("IfcDeepFoundation", false, 282, (entity*) IFC4X2_types[111]);
    IFC4X2_types[295] = new entity("IfcDiscreteAccessory", false, 295, (entity*) IFC4X2_types[377]);
    IFC4X2_types[296] = new entity("IfcDiscreteAccessoryType", false, 296, (entity*) IFC4X2_types[378]);
    IFC4X2_types[300] = new entity("IfcDistributionChamberElementType", false, 300, (entity*) IFC4X2_types[308]);
    IFC4X2_types[304] = new entity("IfcDistributionControlElementType", true, 304, (entity*) IFC4X2_types[306]);
    IFC4X2_types[305] = new entity("IfcDistributionElement", false, 305, (entity*) IFC4X2_types[372]);
    IFC4X2_types[307] = new entity("IfcDistributionFlowElement", false, 307, (entity*) IFC4X2_types[305]);
    IFC4X2_types[309] = new entity("IfcDistributionPort", false, 309, (entity*) IFC4X2_types[718]);
    IFC4X2_types[311] = new entity("IfcDistributionSystem", false, 311, (entity*) IFC4X2_types[1067]);
    IFC4X2_types[319] = new entity("IfcDoor", false, 319, (entity*) IFC4X2_types[111]);
    IFC4X2_types[324] = new entity("IfcDoorStandardCase", false, 324, (entity*) IFC4X2_types[319]);
    IFC4X2_types[335] = new entity("IfcDuctFittingType", false, 335, (entity*) IFC4X2_types[447]);
    IFC4X2_types[338] = new entity("IfcDuctSegmentType", false, 338, (entity*) IFC4X2_types[457]);
    IFC4X2_types[341] = new entity("IfcDuctSilencerType", false, 341, (entity*) IFC4X2_types[463]);
    IFC4X2_types[349] = new entity("IfcElectricApplianceType", false, 349, (entity*) IFC4X2_types[461]);
    IFC4X2_types[356] = new entity("IfcElectricDistributionBoardType", false, 356, (entity*) IFC4X2_types[444]);
    IFC4X2_types[359] = new entity("IfcElectricFlowStorageDeviceType", false, 359, (entity*) IFC4X2_types[459]);
    IFC4X2_types[362] = new entity("IfcElectricGeneratorType", false, 362, (entity*) IFC4X2_types[385]);
    IFC4X2_types[365] = new entity("IfcElectricMotorType", false, 365, (entity*) IFC4X2_types[385]);
    IFC4X2_types[369] = new entity("IfcElectricTimeControlType", false, 369, (entity*) IFC4X2_types[444]);
    IFC4X2_types[384] = new entity("IfcEnergyConversionDevice", false, 384, (entity*) IFC4X2_types[307]);
    IFC4X2_types[387] = new entity("IfcEngine", false, 387, (entity*) IFC4X2_types[384]);
    IFC4X2_types[390] = new entity("IfcEvaporativeCooler", false, 390, (entity*) IFC4X2_types[384]);
    IFC4X2_types[393] = new entity("IfcEvaporator", false, 393, (entity*) IFC4X2_types[384]);
    IFC4X2_types[408] = new entity("IfcExternalSpatialElement", false, 408, (entity*) IFC4X2_types[410]);
    IFC4X2_types[424] = new entity("IfcFanType", false, 424, (entity*) IFC4X2_types[455]);
    IFC4X2_types[437] = new entity("IfcFilterType", false, 437, (entity*) IFC4X2_types[463]);
    IFC4X2_types[440] = new entity("IfcFireSuppressionTerminalType", false, 440, (entity*) IFC4X2_types[461]);
    IFC4X2_types[443] = new entity("IfcFlowController", false, 443, (entity*) IFC4X2_types[307]);
    IFC4X2_types[446] = new entity("IfcFlowFitting", false, 446, (entity*) IFC4X2_types[307]);
    IFC4X2_types[449] = new entity("IfcFlowInstrumentType", false, 449, (entity*) IFC4X2_types[304]);
    IFC4X2_types[451] = new entity("IfcFlowMeter", false, 451, (entity*) IFC4X2_types[443]);
    IFC4X2_types[454] = new entity("IfcFlowMovingDevice", false, 454, (entity*) IFC4X2_types[307]);
    IFC4X2_types[456] = new entity("IfcFlowSegment", false, 456, (entity*) IFC4X2_types[307]);
    IFC4X2_types[458] = new entity("IfcFlowStorageDevice", false, 458, (entity*) IFC4X2_types[307]);
    IFC4X2_types[460] = new entity("IfcFlowTerminal", false, 460, (entity*) IFC4X2_types[307]);
    IFC4X2_types[462] = new entity("IfcFlowTreatmentDevice", false, 462, (entity*) IFC4X2_types[307]);
    IFC4X2_types[467] = new entity("IfcFooting", false, 467, (entity*) IFC4X2_types[111]);
    IFC4X2_types[489] = new entity("IfcGrid", false, 489, (entity*) IFC4X2_types[719]);
    IFC4X2_types[497] = new entity("IfcHeatExchanger", false, 497, (entity*) IFC4X2_types[384]);
    IFC4X2_types[502] = new entity("IfcHumidifier", false, 502, (entity*) IFC4X2_types[384]);
    IFC4X2_types[517] = new entity("IfcInterceptor", false, 517, (entity*) IFC4X2_types[462]);
    IFC4X2_types[529] = new entity("IfcJunctionBox", false, 529, (entity*) IFC4X2_types[446]);
    IFC4X2_types[539] = new entity("IfcLamp", false, 539, (entity*) IFC4X2_types[460]);
    IFC4X2_types[553] = new entity("IfcLightFixture", false, 553, (entity*) IFC4X2_types[460]);
    IFC4X2_types[567] = new entity("IfcLinearPositioningElement", false, 567, (entity*) IFC4X2_types[719]);
    IFC4X2_types[615] = new entity("IfcMedicalDevice", false, 615, (entity*) IFC4X2_types[460]);
    IFC4X2_types[618] = new entity("IfcMember", false, 618, (entity*) IFC4X2_types[111]);
    IFC4X2_types[619] = new entity("IfcMemberStandardCase", false, 619, (entity*) IFC4X2_types[618]);
    IFC4X2_types[638] = new entity("IfcMotorConnection", false, 638, (entity*) IFC4X2_types[384]);
    IFC4X2_types[667] = new entity("IfcOuterBoundaryCurve", false, 667, (entity*) IFC4X2_types[90]);
    IFC4X2_types[668] = new entity("IfcOutlet", false, 668, (entity*) IFC4X2_types[460]);
    IFC4X2_types[689] = new entity("IfcPile", false, 689, (entity*) IFC4X2_types[282]);
    IFC4X2_types[693] = new entity("IfcPipeFitting", false, 693, (entity*) IFC4X2_types[446]);
    IFC4X2_types[696] = new entity("IfcPipeSegment", false, 696, (entity*) IFC4X2_types[456]);
    IFC4X2_types[706] = new entity("IfcPlate", false, 706, (entity*) IFC4X2_types[111]);
    IFC4X2_types[707] = new entity("IfcPlateStandardCase", false, 707, (entity*) IFC4X2_types[706]);
    IFC4X2_types[781] = new entity("IfcProtectiveDevice", false, 781, (entity*) IFC4X2_types[443]);
    IFC4X2_types[783] = new entity("IfcProtectiveDeviceTrippingUnitType", false, 783, (entity*) IFC4X2_types[304]);
    IFC4X2_types[788] = new entity("IfcPump", false, 788, (entity*) IFC4X2_types[454]);
    IFC4X2_types[799] = new entity("IfcRailing", false, 799, (entity*) IFC4X2_types[111]);
    IFC4X2_types[802] = new entity("IfcRamp", false, 802, (entity*) IFC4X2_types[111]);
    IFC4X2_types[803] = new entity("IfcRampFlight", false, 803, (entity*) IFC4X2_types[111]);
    IFC4X2_types[809] = new entity("IfcRationalBSplineCurveWithKnots", false, 809, (entity*) IFC4X2_types[106]);
    IFC4X2_types[825] = new entity("IfcReinforcingBar", false, 825, (entity*) IFC4X2_types[830]);
    IFC4X2_types[828] = new entity("IfcReinforcingBarType", false, 828, (entity*) IFC4X2_types[831]);
    IFC4X2_types[901] = new entity("IfcRoof", false, 901, (entity*) IFC4X2_types[111]);
    IFC4X2_types[910] = new entity("IfcSanitaryTerminal", false, 910, (entity*) IFC4X2_types[460]);
    IFC4X2_types[925] = new entity("IfcSensorType", false, 925, (entity*) IFC4X2_types[304]);
    IFC4X2_types[928] = new entity("IfcShadingDevice", false, 928, (entity*) IFC4X2_types[111]);
    IFC4X2_types[946] = new entity("IfcSlab", false, 946, (entity*) IFC4X2_types[111]);
    IFC4X2_types[947] = new entity("IfcSlabElementedCase", false, 947, (entity*) IFC4X2_types[946]);
    IFC4X2_types[948] = new entity("IfcSlabStandardCase", false, 948, (entity*) IFC4X2_types[946]);
    IFC4X2_types[952] = new entity("IfcSolarDevice", false, 952, (entity*) IFC4X2_types[384]);
    IFC4X2_types[964] = new entity("IfcSpaceHeater", false, 964, (entity*) IFC4X2_types[460]);
    IFC4X2_types[982] = new entity("IfcStackTerminal", false, 982, (entity*) IFC4X2_types[460]);
    IFC4X2_types[985] = new entity("IfcStair", false, 985, (entity*) IFC4X2_types[111]);
    IFC4X2_types[986] = new entity("IfcStairFlight", false, 986, (entity*) IFC4X2_types[111]);
    IFC4X2_types[995] = new entity("IfcStructuralAnalysisModel", false, 995, (entity*) IFC4X2_types[1067]);
    IFC4X2_types[1008] = new entity("IfcStructuralLoadCase", false, 1008, (entity*) IFC4X2_types[1010]);
    IFC4X2_types[1021] = new entity("IfcStructuralPlanarAction", false, 1021, (entity*) IFC4X2_types[1027]);
    IFC4X2_types[1064] = new entity("IfcSwitchingDevice", false, 1064, (entity*) IFC4X2_types[443]);
    IFC4X2_types[1074] = new entity("IfcTank", false, 1074, (entity*) IFC4X2_types[458]);
    IFC4X2_types[1133] = new entity("IfcTransformer", false, 1133, (entity*) IFC4X2_types[384]);
    IFC4X2_types[1150] = new entity("IfcTubeBundle", false, 1150, (entity*) IFC4X2_types[384]);
    IFC4X2_types[1159] = new entity("IfcUnitaryControlElementType", false, 1159, (entity*) IFC4X2_types[304]);
    IFC4X2_types[1161] = new entity("IfcUnitaryEquipment", false, 1161, (entity*) IFC4X2_types[384]);
    IFC4X2_types[1169] = new entity("IfcValve", false, 1169, (entity*) IFC4X2_types[443]);
    IFC4X2_types[1190] = new entity("IfcWall", false, 1190, (entity*) IFC4X2_types[111]);
    IFC4X2_types[1191] = new entity("IfcWallElementedCase", false, 1191, (entity*) IFC4X2_types[1190]);
    IFC4X2_types[1192] = new entity("IfcWallStandardCase", false, 1192, (entity*) IFC4X2_types[1190]);
    IFC4X2_types[1198] = new entity("IfcWasteTerminal", false, 1198, (entity*) IFC4X2_types[460]);
    IFC4X2_types[1201] = new entity("IfcWindow", false, 1201, (entity*) IFC4X2_types[111]);
    IFC4X2_types[1206] = new entity("IfcWindowStandardCase", false, 1206, (entity*) IFC4X2_types[1201]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4X2_types[408]);
        items.push_back(IFC4X2_types[962]);
        IFC4X2_types[963] = new select_type("IfcSpaceBoundarySelect", 963, items);
    }
    IFC4X2_types[10] = new entity("IfcActuatorType", false, 10, (entity*) IFC4X2_types[304]);
    IFC4X2_types[17] = new entity("IfcAirTerminal", false, 17, (entity*) IFC4X2_types[460]);
    IFC4X2_types[18] = new entity("IfcAirTerminalBox", false, 18, (entity*) IFC4X2_types[443]);
    IFC4X2_types[23] = new entity("IfcAirToAirHeatRecovery", false, 23, (entity*) IFC4X2_types[384]);
    IFC4X2_types[27] = new entity("IfcAlarmType", false, 27, (entity*) IFC4X2_types[304]);
    IFC4X2_types[29] = new entity("IfcAlignment", false, 29, (entity*) IFC4X2_types[567]);
    IFC4X2_types[61] = new entity("IfcAudioVisualAppliance", false, 61, (entity*) IFC4X2_types[460]);
    IFC4X2_types[68] = new entity("IfcBeam", false, 68, (entity*) IFC4X2_types[111]);
    IFC4X2_types[69] = new entity("IfcBeamStandardCase", false, 69, (entity*) IFC4X2_types[68]);
    IFC4X2_types[72] = new entity("IfcBearing", false, 72, (entity*) IFC4X2_types[111]);
    IFC4X2_types[81] = new entity("IfcBoiler", false, 81, (entity*) IFC4X2_types[384]);
    IFC4X2_types[122] = new entity("IfcBurner", false, 122, (entity*) IFC4X2_types[384]);
    IFC4X2_types[125] = new entity("IfcCableCarrierFitting", false, 125, (entity*) IFC4X2_types[446]);
    IFC4X2_types[128] = new entity("IfcCableCarrierSegment", false, 128, (entity*) IFC4X2_types[456]);
    IFC4X2_types[131] = new entity("IfcCableFitting", false, 131, (entity*) IFC4X2_types[446]);
    IFC4X2_types[134] = new entity("IfcCableSegment", false, 134, (entity*) IFC4X2_types[456]);
    IFC4X2_types[137] = new entity("IfcCaissonFoundation", false, 137, (entity*) IFC4X2_types[282]);
    IFC4X2_types[152] = new entity("IfcChiller", false, 152, (entity*) IFC4X2_types[384]);
    IFC4X2_types[169] = new entity("IfcCoil", false, 169, (entity*) IFC4X2_types[384]);
    IFC4X2_types[181] = new entity("IfcCommunicationsAppliance", false, 181, (entity*) IFC4X2_types[460]);
    IFC4X2_types[193] = new entity("IfcCompressor", false, 193, (entity*) IFC4X2_types[454]);
    IFC4X2_types[196] = new entity("IfcCondenser", false, 196, (entity*) IFC4X2_types[384]);
    IFC4X2_types[226] = new entity("IfcControllerType", false, 226, (entity*) IFC4X2_types[304]);
    IFC4X2_types[230] = new entity("IfcCooledBeam", false, 230, (entity*) IFC4X2_types[384]);
    IFC4X2_types[233] = new entity("IfcCoolingTower", false, 233, (entity*) IFC4X2_types[384]);
    IFC4X2_types[274] = new entity("IfcDamper", false, 274, (entity*) IFC4X2_types[443]);
    IFC4X2_types[299] = new entity("IfcDistributionChamberElement", false, 299, (entity*) IFC4X2_types[307]);
    IFC4X2_types[302] = new entity("IfcDistributionCircuit", false, 302, (entity*) IFC4X2_types[311]);
    IFC4X2_types[303] = new entity("IfcDistributionControlElement", false, 303, (entity*) IFC4X2_types[305]);
    IFC4X2_types[334] = new entity("IfcDuctFitting", false, 334, (entity*) IFC4X2_types[446]);
    IFC4X2_types[337] = new entity("IfcDuctSegment", false, 337, (entity*) IFC4X2_types[456]);
    IFC4X2_types[340] = new entity("IfcDuctSilencer", false, 340, (entity*) IFC4X2_types[462]);
    IFC4X2_types[348] = new entity("IfcElectricAppliance", false, 348, (entity*) IFC4X2_types[460]);
    IFC4X2_types[355] = new entity("IfcElectricDistributionBoard", false, 355, (entity*) IFC4X2_types[443]);
    IFC4X2_types[358] = new entity("IfcElectricFlowStorageDevice", false, 358, (entity*) IFC4X2_types[458]);
    IFC4X2_types[361] = new entity("IfcElectricGenerator", false, 361, (entity*) IFC4X2_types[384]);
    IFC4X2_types[364] = new entity("IfcElectricMotor", false, 364, (entity*) IFC4X2_types[384]);
    IFC4X2_types[368] = new entity("IfcElectricTimeControl", false, 368, (entity*) IFC4X2_types[443]);
    IFC4X2_types[423] = new entity("IfcFan", false, 423, (entity*) IFC4X2_types[454]);
    IFC4X2_types[436] = new entity("IfcFilter", false, 436, (entity*) IFC4X2_types[462]);
    IFC4X2_types[439] = new entity("IfcFireSuppressionTerminal", false, 439, (entity*) IFC4X2_types[460]);
    IFC4X2_types[448] = new entity("IfcFlowInstrument", false, 448, (entity*) IFC4X2_types[303]);
    IFC4X2_types[782] = new entity("IfcProtectiveDeviceTrippingUnit", false, 782, (entity*) IFC4X2_types[303]);
    IFC4X2_types[924] = new entity("IfcSensor", false, 924, (entity*) IFC4X2_types[303]);
    IFC4X2_types[1158] = new entity("IfcUnitaryControlElement", false, 1158, (entity*) IFC4X2_types[303]);
    IFC4X2_types[9] = new entity("IfcActuator", false, 9, (entity*) IFC4X2_types[303]);
    IFC4X2_types[26] = new entity("IfcAlarm", false, 26, (entity*) IFC4X2_types[303]);
    IFC4X2_types[225] = new entity("IfcController", false, 225, (entity*) IFC4X2_types[303]);
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[3]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[2])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TheActor", new named_type(IFC4X2_types[8]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[6])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Role", new named_type(IFC4X2_types[900]), false));
        attributes.push_back(new attribute("UserDefinedRole", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[7])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[11]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[9])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[11]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[10])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X2_types[13]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("UserDefinedPurpose", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[12])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[14])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[168])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[15])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[16])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[22]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[17])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[20]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[18])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[20]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[19])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[22]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[21])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[25]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[23])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[25]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[24])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[28]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[26])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[28]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[27])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[39]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[29])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("StartDistAlong", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[31])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[30])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CurveGeometry", new named_type(IFC4X2_types[267]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[31])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TangentialContinuity", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("StartTag", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("EndTag", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[32])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("IsConvex", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[33])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[34])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ParabolaConstant", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("IsConvex", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[35])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[37])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[36])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("StartDistAlong", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("HorizontalLength", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("StartHeight", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("StartGradient", new named_type(IFC4X2_types[808]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[37])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Horizontal", new named_type(IFC4X2_types[30]), false));
        attributes.push_back(new attribute("Vertical", new named_type(IFC4X2_types[36]), true));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[38])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[44])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[260])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[45])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ApplicationDeveloper", new named_type(IFC4X2_types[663]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("ApplicationFullName", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("ApplicationIdentifier", new named_type(IFC4X2_types[505]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[46])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("AppliedValue", new named_type(IFC4X2_types[48]), true));
        attributes.push_back(new attribute("UnitBasis", new named_type(IFC4X2_types[611]), true));
        attributes.push_back(new attribute("ApplicableDate", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("FixedUntilDate", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Condition", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("ArithmeticOperator", new named_type(IFC4X2_types[57]), true));
        attributes.push_back(new attribute("Components", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[47])), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[47])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Identifier", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("TimeOfApproval", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Level", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Qualifier", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("RequestingApproval", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("GivingApproval", new named_type(IFC4X2_types[8]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[49])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4X2_types[49]), false));
        attributes.push_back(new attribute("RelatedApprovals", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[49])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[50])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OuterCurve", new named_type(IFC4X2_types[260]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[51])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Curve", new named_type(IFC4X2_types[95]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[52])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[260])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[53])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC4X2_types[243]), true));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC4X2_types[243]), true));
        attributes.push_back(new attribute("TotalReplacementCost", new named_type(IFC4X2_types[243]), true));
        attributes.push_back(new attribute("Owner", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("User", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("ResponsiblePerson", new named_type(IFC4X2_types[682]), true));
        attributes.push_back(new attribute("IncorporationDate", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("DepreciatedValue", new named_type(IFC4X2_types[243]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[59])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("BottomFlangeWidth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("BottomFlangeThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("BottomFlangeFilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("TopFlangeWidth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("TopFlangeThickness", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("TopFlangeFilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("BottomFlangeEdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("BottomFlangeSlope", new named_type(IFC4X2_types[705]), true));
        attributes.push_back(new attribute("TopFlangeEdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("TopFlangeSlope", new named_type(IFC4X2_types[705]), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[60])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[63]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[61])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[63]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[62])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X2_types[293]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[64])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4X2_types[293]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[66])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X2_types[293]), true));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4X2_types[293]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[67])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Degree", new named_type(IFC4X2_types[515]), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[141])), false));
        attributes.push_back(new attribute("CurveForm", new named_type(IFC4X2_types[105]), false));
        attributes.push_back(new attribute("ClosedCurve", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X2_types[574]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[104])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("KnotMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[515])), false));
        attributes.push_back(new attribute("Knots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[673])), false));
        attributes.push_back(new attribute("KnotSpec", new named_type(IFC4X2_types[533]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[106])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("UDegree", new named_type(IFC4X2_types[515]), false));
        attributes.push_back(new attribute("VDegree", new named_type(IFC4X2_types[515]), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[141]))), false));
        attributes.push_back(new attribute("SurfaceForm", new named_type(IFC4X2_types[108]), false));
        attributes.push_back(new attribute("UClosed", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("VClosed", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X2_types[574]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[107])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("UMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[515])), false));
        attributes.push_back(new attribute("VMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[515])), false));
        attributes.push_back(new attribute("UKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[673])), false));
        attributes.push_back(new attribute("VKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[673])), false));
        attributes.push_back(new attribute("KnotSpec", new named_type(IFC4X2_types[533]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[109])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[71]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[68])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[69])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[71]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[70])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[75]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[72])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[75]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[73])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RasterFormat", new named_type(IFC4X2_types[505]), false));
        attributes.push_back(new attribute("RasterCode", new named_type(IFC4X2_types[78]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[79])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("ZLength", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[80])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[83]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[81])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[83]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[82])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[85])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Operator", new named_type(IFC4X2_types[87]), false));
        attributes.push_back(new attribute("FirstOperand", new named_type(IFC4X2_types[86]), false));
        attributes.push_back(new attribute("SecondOperand", new named_type(IFC4X2_types[86]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[88])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[89])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[90])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TranslationalStiffnessByLengthX", new named_type(IFC4X2_types[631]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByLengthY", new named_type(IFC4X2_types[631]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByLengthZ", new named_type(IFC4X2_types[631]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthX", new named_type(IFC4X2_types[628]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthY", new named_type(IFC4X2_types[628]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthZ", new named_type(IFC4X2_types[628]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[91])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TranslationalStiffnessByAreaX", new named_type(IFC4X2_types[630]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByAreaY", new named_type(IFC4X2_types[630]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByAreaZ", new named_type(IFC4X2_types[630]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[92])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TranslationalStiffnessX", new named_type(IFC4X2_types[1139]), true));
        attributes.push_back(new attribute("TranslationalStiffnessY", new named_type(IFC4X2_types[1139]), true));
        attributes.push_back(new attribute("TranslationalStiffnessZ", new named_type(IFC4X2_types[1139]), true));
        attributes.push_back(new attribute("RotationalStiffnessX", new named_type(IFC4X2_types[908]), true));
        attributes.push_back(new attribute("RotationalStiffnessY", new named_type(IFC4X2_types[908]), true));
        attributes.push_back(new attribute("RotationalStiffnessZ", new named_type(IFC4X2_types[908]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[93])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingStiffness", new named_type(IFC4X2_types[1197]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[94])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[95])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[96])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Corner", new named_type(IFC4X2_types[141]), false));
        attributes.push_back(new attribute("XDim", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("ZDim", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[97])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Enclosure", new named_type(IFC4X2_types[97]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[99])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[103]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[100])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[102]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[101])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ElevationOfRefHeight", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("ElevationOfTerrain", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("BuildingAddress", new named_type(IFC4X2_types[724]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[110])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[111])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[114]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[114]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[113])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[117]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[115])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[117]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[116])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[118])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elevation", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[119])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[121]), true));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[120])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[124]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[122])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[124]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[123])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("Girth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("InternalFilletRadius", new named_type(IFC4X2_types[642]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[254])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[127]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[125])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[127]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[126])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[130]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[128])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[130]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[129])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[133]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[133]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[132])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[136]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[136]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[135])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[139]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[137])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[139]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[138])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4X2_types[545])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[141])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[142])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X2_types[545]))), false));
        attributes.push_back(new attribute("TagList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[143])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[545]))), false));
        attributes.push_back(new attribute("TagList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[144])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Axis1", new named_type(IFC4X2_types[293]), true));
        attributes.push_back(new attribute("Axis2", new named_type(IFC4X2_types[293]), true));
        attributes.push_back(new attribute("LocalOrigin", new named_type(IFC4X2_types[141]), false));
        attributes.push_back(new attribute("Scale", new named_type(IFC4X2_types[811]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[145])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[146])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Scale2", new named_type(IFC4X2_types[811]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[147])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis3", new named_type(IFC4X2_types[293]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[148])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Scale2", new named_type(IFC4X2_types[811]), true));
        attributes.push_back(new attribute("Scale3", new named_type(IFC4X2_types[811]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[149])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Thickness", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[150])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[154]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[152])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[154]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[153])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[157]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[155])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[157]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[156])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[158])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[159])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[160])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("IsCCW", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[161])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[162])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[163])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Source", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Edition", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("EditionDate", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4X2_types[1166]), true));
        attributes.push_back(new attribute("ReferenceTokens", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[505])), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[164])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ReferencedSource", new named_type(IFC4X2_types[166]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Sort", new named_type(IFC4X2_types[505]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[165])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[168])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[171]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[169])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[171]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[170])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Red", new named_type(IFC4X2_types[643]), false));
        attributes.push_back(new attribute("Green", new named_type(IFC4X2_types[643]), false));
        attributes.push_back(new attribute("Blue", new named_type(IFC4X2_types[643]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[174])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ColourList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[643]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[175])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[176])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[180]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[177])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[178])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[180]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[179])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[183]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[181])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[183]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[182])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4X2_types[505]), false));
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[762])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[185])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4X2_types[187]), true));
        attributes.push_back(new attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[779])), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[186])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[190])), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X2_types[574]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[188])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[189])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Transition", new named_type(IFC4X2_types[1136]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("ParentCurve", new named_type(IFC4X2_types[260]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[190])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4X2_types[751])), false));
        attributes.push_back(new attribute("Label", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[191])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[195]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[193])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[195]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[194])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[198]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[196])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[198]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[197])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[65]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[199])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[413])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[200])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CurveOnRelatingElement", new named_type(IFC4X2_types[266]), false));
        attributes.push_back(new attribute("CurveOnRelatedElement", new named_type(IFC4X2_types[266]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[201])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[202])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("EccentricityInX", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("EccentricityInY", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("EccentricityInZ", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[203])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PointOnRelatingElement", new named_type(IFC4X2_types[713]), false));
        attributes.push_back(new attribute("PointOnRelatedElement", new named_type(IFC4X2_types[713]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[204])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceOnRelatingElement", new named_type(IFC4X2_types[1049]), false));
        attributes.push_back(new attribute("SurfaceOnRelatedElement", new named_type(IFC4X2_types[1049]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[205])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VolumeOnRelatingElement", new named_type(IFC4X2_types[957]), false));
        attributes.push_back(new attribute("VolumeOnRelatedElement", new named_type(IFC4X2_types[957]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[207])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("ConstraintGrade", new named_type(IFC4X2_types[209]), false));
        attributes.push_back(new attribute("ConstraintSource", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("CreatingActor", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("UserDefinedGrade", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[208])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[212]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[210])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[212]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[211])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[215]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[213])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[215]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[214])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[218]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[216])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[218]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[217])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Usage", new named_type(IFC4X2_types[895]), true));
        attributes.push_back(new attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[47])), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC4X2_types[687]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[219])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[47])), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC4X2_types[687]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[220])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Phase", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[886])), true));
        attributes.push_back(new attribute("UnitsInContext", new named_type(IFC4X2_types[1164]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[221])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[223])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[224])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[227]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[225])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[227]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[226])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("ConversionFactor", new named_type(IFC4X2_types[611]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[228])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConversionOffset", new named_type(IFC4X2_types[811]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[229])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[232]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[230])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[232]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[231])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[235]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[233])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[235]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[234])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SourceCRS", new named_type(IFC4X2_types[238]), false));
        attributes.push_back(new attribute("TargetCRS", new named_type(IFC4X2_types[237]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[236])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("GeodeticDatum", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("VerticalDatum", new named_type(IFC4X2_types[505]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[237])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[240]), true));
        attributes.push_back(new attribute("CostValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[243])), true));
        attributes.push_back(new attribute("CostQuantities", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[687])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[239])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[242]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("SubmittedOn", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("UpdateDate", new named_type(IFC4X2_types[279]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[241])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[243])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[247]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[245])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[247]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[246])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[250]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[248])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[250]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[249])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[67]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[251])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TreeRootExpression", new named_type(IFC4X2_types[252]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[253])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingMonetaryUnit", new named_type(IFC4X2_types[636]), false));
        attributes.push_back(new attribute("RelatedMonetaryUnit", new named_type(IFC4X2_types[636]), false));
        attributes.push_back(new attribute("ExchangeRate", new named_type(IFC4X2_types[723]), false));
        attributes.push_back(new attribute("RateDateTime", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("RateSource", new named_type(IFC4X2_types[546]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[255])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[258]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[256])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[258]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[257])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[260])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X2_types[704]), false));
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X2_types[260])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[261])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X2_types[1042]), false));
        attributes.push_back(new attribute("Boundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[90])), false));
        attributes.push_back(new attribute("ImplicitOuter", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[262])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("StartPoint", new named_type(IFC4X2_types[141]), false));
        attributes.push_back(new attribute("StartDirection", new named_type(IFC4X2_types[705]), false));
        attributes.push_back(new attribute("SegmentLength", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[267])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CurveFont", new named_type(IFC4X2_types[263]), true));
        attributes.push_back(new attribute("CurveWidth", new named_type(IFC4X2_types[945]), true));
        attributes.push_back(new attribute("CurveColour", new named_type(IFC4X2_types[172]), true));
        attributes.push_back(new attribute("ModelOrDraughting", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[268])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[271])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[269])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("CurveFont", new named_type(IFC4X2_types[272]), false));
        attributes.push_back(new attribute("CurveFontScaling", new named_type(IFC4X2_types[723]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[270])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VisibleSegmentLength", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("InvisibleSegmentLength", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[271])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[273])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[276]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[274])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[276]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[275])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[282])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[283])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ParentProfile", new named_type(IFC4X2_types[751]), false));
        attributes.push_back(new attribute("Operator", new named_type(IFC4X2_types[146]), false));
        attributes.push_back(new attribute("Label", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[286])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[288])), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC4X2_types[289]), false));
        attributes.push_back(new attribute("UserDefinedType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[287])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[641]), false));
        attributes.push_back(new attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[288])->set_attributes(attributes, derived);
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
        ((entity*)IFC4X2_types[291])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X2_types[811])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[293])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[297]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[295])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[297]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[296])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("DistanceAlong", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("OffsetLateral", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("OffsetVertical", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("OffsetLongitudinal", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("AlongHorizontal", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[298])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[301]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[299])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[301]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[300])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[302])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[303])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[304])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[305])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[306])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[307])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[308])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("FlowDirection", new named_type(IFC4X2_types[445]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[310]), true));
        attributes.push_back(new attribute("SystemType", new named_type(IFC4X2_types[312]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[309])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[312]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[311])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4X2_types[1166]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("IntendedUse", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Scope", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Revision", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("DocumentOwner", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[8])), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("LastRevisionTime", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ElectronicFormat", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("ValidFrom", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("ValidUntil", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("Confidentiality", new named_type(IFC4X2_types[313]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[318]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[314])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC4X2_types[314]), false));
        attributes.push_back(new attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[314])), false));
        attributes.push_back(new attribute("RelationshipType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[315])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("ReferencedDocument", new named_type(IFC4X2_types[314]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[316])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[329]), true));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X2_types[330]), true));
        attributes.push_back(new attribute("UserDefinedOperationType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[319])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(13);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("ThresholdDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("ThresholdThickness", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("TransomOffset", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("ThresholdOffset", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("CasingThickness", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("CasingDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X2_types[931]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetX", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetY", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[320])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PanelDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PanelOperation", new named_type(IFC4X2_types[321]), false));
        attributes.push_back(new attribute("PanelWidth", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4X2_types[322]), false));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X2_types[931]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[323])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[324])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X2_types[327]), false));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4X2_types[326]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("Sizeable", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[325])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[329]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X2_types[330]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("UserDefinedOperationType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[328])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[332])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[333])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[336]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[334])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[336]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[335])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[339]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[337])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[339]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[338])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[342]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[340])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[342]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[341])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeStart", new named_type(IFC4X2_types[1175]), false));
        attributes.push_back(new attribute("EdgeEnd", new named_type(IFC4X2_types[1175]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[345])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeGeometry", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[346])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[666])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[347])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[350]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[348])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[350]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[349])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[357]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[355])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[357]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[356])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[360]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[358])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[360]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[359])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[363]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[361])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[363]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[362])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[366]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[364])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[366]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[365])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[370]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[368])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[370]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[369])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Tag", new named_type(IFC4X2_types[505]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[372])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC4X2_types[58]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[376]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[374])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[376]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[375])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[377])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[378])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MethodOfMeasurement", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[687])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[380])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[381])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[67]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[373])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[382])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[383])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[384])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[385])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[389]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[387])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[389]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[388])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[392]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[390])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[392]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[391])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[395]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[393])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[395]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[394])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[400]), true));
        attributes.push_back(new attribute("EventTriggerType", new named_type(IFC4X2_types[398]), true));
        attributes.push_back(new attribute("UserDefinedEventTriggerType", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("EventOccurenceTime", new named_type(IFC4X2_types[397]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[396])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ActualDate", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("EarlyDate", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("LateDate", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ScheduleDate", new named_type(IFC4X2_types[279]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[397])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[400]), false));
        attributes.push_back(new attribute("EventTriggerType", new named_type(IFC4X2_types[398]), false));
        attributes.push_back(new attribute("UserDefinedEventTriggerType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[399])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Properties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[762])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[401])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[402])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Location", new named_type(IFC4X2_types[1166]), true));
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[406])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingReference", new named_type(IFC4X2_types[406]), false));
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[893])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[407])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[409]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[408])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[410])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[403])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[404])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[405])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC4X2_types[293]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[411])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EndSweptArea", new named_type(IFC4X2_types[751]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[412])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[415])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[413])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[200])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[414])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Bound", new named_type(IFC4X2_types[576]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[415])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[416])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FaceSurface", new named_type(IFC4X2_types[1042]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[417])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[418])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[168])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[419])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[420])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[421])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TensionFailureX", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("TensionFailureY", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("TensionFailureZ", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("CompressionFailureX", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("CompressionFailureY", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("CompressionFailureZ", new named_type(IFC4X2_types[470]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[422])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[425]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[423])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[425]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[424])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[428]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[426])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[428]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[427])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[429])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[430])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[431])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[435])), false));
        attributes.push_back(new attribute("ModelorDraughting", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[432])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("HatchLineAppearance", new named_type(IFC4X2_types[268]), false));
        attributes.push_back(new attribute("StartOfNextHatchLine", new named_type(IFC4X2_types[496]), false));
        attributes.push_back(new attribute("PointOfReferenceHatchLine", new named_type(IFC4X2_types[141]), true));
        attributes.push_back(new attribute("PatternStart", new named_type(IFC4X2_types[141]), true));
        attributes.push_back(new attribute("HatchLineAngle", new named_type(IFC4X2_types[705]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[433])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TilingPattern", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X2_types[1173])), false));
        attributes.push_back(new attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1035])), false));
        attributes.push_back(new attribute("TilingScale", new named_type(IFC4X2_types[723]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[434])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[438]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[436])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[438]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[437])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[441]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[439])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[441]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[440])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4X2_types[673]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4X2_types[673]), true));
        attributes.push_back(new attribute("FixedReference", new named_type(IFC4X2_types[293]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[442])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[443])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[444])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[446])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[447])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[450]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[448])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[450]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[449])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[453]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[451])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[453]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[452])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[454])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[455])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[456])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[457])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[458])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[459])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[460])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[461])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[462])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[463])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[469]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[467])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[469]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[468])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[472])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[473])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[476]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[474])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC4X2_types[58]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[476]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[475])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[479]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[477])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[479]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[478])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[480])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CoordinateSpaceDimension", new named_type(IFC4X2_types[292]), false));
        attributes.push_back(new attribute("Precision", new named_type(IFC4X2_types[811]), true));
        attributes.push_back(new attribute("WorldCoordinateSystem", new named_type(IFC4X2_types[65]), false));
        attributes.push_back(new attribute("TrueNorth", new named_type(IFC4X2_types[293]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[482])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[483])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ParentContext", new named_type(IFC4X2_types[482]), false));
        attributes.push_back(new attribute("TargetScale", new named_type(IFC4X2_types[723]), true));
        attributes.push_back(new attribute("TargetView", new named_type(IFC4X2_types[481]), false));
        attributes.push_back(new attribute("UserDefinedTargetView", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[484])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[486])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[485])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[490])), false));
        attributes.push_back(new attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[490])), false));
        attributes.push_back(new attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[490])), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[493]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[489])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("AxisTag", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("AxisCurve", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[490])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementLocation", new named_type(IFC4X2_types[1185]), false));
        attributes.push_back(new attribute("PlacementRefDirection", new named_type(IFC4X2_types[492]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[491])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[494])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseSurface", new named_type(IFC4X2_types[1042]), false));
        attributes.push_back(new attribute("AgreementFlag", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[495])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[499]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[497])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[499]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[498])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[504]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[502])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[504]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[503])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4X2_types[705]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[527])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("URLReference", new named_type(IFC4X2_types[1166]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[507])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4X2_types[1095]), false));
        attributes.push_back(new attribute("Opacity", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("Colours", new named_type(IFC4X2_types[175]), false));
        attributes.push_back(new attribute("ColourIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[720])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[508])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Points", new named_type(IFC4X2_types[142]), false));
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[923])), true));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[509])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X2_types[720])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[510])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCoordIndices", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X2_types[720]))), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[511])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4X2_types[1095]), false));
        attributes.push_back(new attribute("TexCoords", new named_type(IFC4X2_types[1114]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[512])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TexCoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[720]))), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[513])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[519]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[517])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[519]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[518])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[521])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[523]), true));
        attributes.push_back(new attribute("Jurisdiction", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[682])), true));
        attributes.push_back(new attribute("LastUpdateDate", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC4X2_types[243]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC4X2_types[243]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[522])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[526])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[525])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStamp", new named_type(IFC4X2_types[279]), false));
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[526])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[531]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[529])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[531]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[530])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("Thickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("LegSlope", new named_type(IFC4X2_types[705]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[577])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[537]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[535])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[537]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[536])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LagValue", new named_type(IFC4X2_types[1123]), false));
        attributes.push_back(new attribute("DurationType", new named_type(IFC4X2_types[1078]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[538])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[541]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[539])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[541]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[540])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Publisher", new named_type(IFC4X2_types[8]), true));
        attributes.push_back(new attribute("VersionDate", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4X2_types[1166]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[546])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Language", new named_type(IFC4X2_types[542]), true));
        attributes.push_back(new attribute("ReferencedLibrary", new named_type(IFC4X2_types[546]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[547])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MainPlaneAngle", new named_type(IFC4X2_types[705]), false));
        attributes.push_back(new attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[705])), false));
        attributes.push_back(new attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[579])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[550])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[555]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[553])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[555]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[554])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LightDistributionCurve", new named_type(IFC4X2_types[549]), false));
        attributes.push_back(new attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[550])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[556])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("LightColour", new named_type(IFC4X2_types[174]), false));
        attributes.push_back(new attribute("AmbientIntensity", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("Intensity", new named_type(IFC4X2_types[643]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[557])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[558])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X2_types[293]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[559])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[67]), false));
        attributes.push_back(new attribute("ColourAppearance", new named_type(IFC4X2_types[174]), true));
        attributes.push_back(new attribute("ColourTemperature", new named_type(IFC4X2_types[1120]), false));
        attributes.push_back(new attribute("LuminousFlux", new named_type(IFC4X2_types[578]), false));
        attributes.push_back(new attribute("LightEmissionSource", new named_type(IFC4X2_types[552]), false));
        attributes.push_back(new attribute("LightDistributionDataSource", new named_type(IFC4X2_types[551]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[560])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[141]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("ConstantAttenuation", new named_type(IFC4X2_types[811]), false));
        attributes.push_back(new attribute("DistanceAttenuation", new named_type(IFC4X2_types[811]), false));
        attributes.push_back(new attribute("QuadricAttenuation", new named_type(IFC4X2_types[811]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[561])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X2_types[293]), false));
        attributes.push_back(new attribute("ConcentrationExponent", new named_type(IFC4X2_types[811]), true));
        attributes.push_back(new attribute("SpreadAngle", new named_type(IFC4X2_types[722]), false));
        attributes.push_back(new attribute("BeamWidthAngle", new named_type(IFC4X2_types[722]), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[562])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Pnt", new named_type(IFC4X2_types[141]), false));
        attributes.push_back(new attribute("Dir", new named_type(IFC4X2_types[1173]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[563])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[571])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PlacementMeasuredAlong", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("Distance", new named_type(IFC4X2_types[298]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X2_types[665]), true));
        attributes.push_back(new attribute("CartesianPosition", new named_type(IFC4X2_types[67]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[566])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X2_types[260]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[567])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelativePlacement", new named_type(IFC4X2_types[65]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[573])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[576])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Outer", new named_type(IFC4X2_types[168]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[583])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Eastings", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("Northings", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("OrthogonalHeight", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("XAxisAbscissa", new named_type(IFC4X2_types[811]), true));
        attributes.push_back(new attribute("XAxisOrdinate", new named_type(IFC4X2_types[811]), true));
        attributes.push_back(new attribute("Scale", new named_type(IFC4X2_types[811]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[584])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingSource", new named_type(IFC4X2_types[888]), false));
        attributes.push_back(new attribute("MappingTarget", new named_type(IFC4X2_types[145]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[585])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[590])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[167])), false));
        attributes.push_back(new attribute("ClassifiedMaterial", new named_type(IFC4X2_types[590]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[591])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Material", new named_type(IFC4X2_types[590]), false));
        attributes.push_back(new attribute("Fraction", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[592])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("MaterialConstituents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[592])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[593])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[594])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RepresentedMaterial", new named_type(IFC4X2_types[590]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[595])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Material", new named_type(IFC4X2_types[590]), true));
        attributes.push_back(new attribute("LayerThickness", new named_type(IFC4X2_types[642]), false));
        attributes.push_back(new attribute("IsVentilated", new named_type(IFC4X2_types[574]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Priority", new named_type(IFC4X2_types[515]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[596])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[596])), false));
        attributes.push_back(new attribute("LayerSetName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[597])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ForLayerSet", new named_type(IFC4X2_types[597]), false));
        attributes.push_back(new attribute("LayerSetDirection", new named_type(IFC4X2_types[544]), false));
        attributes.push_back(new attribute("DirectionSense", new named_type(IFC4X2_types[294]), false));
        attributes.push_back(new attribute("OffsetFromReferenceLine", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("ReferenceExtent", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[598])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OffsetDirection", new named_type(IFC4X2_types[544]), false));
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X2_types[545])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[599])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[590])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[600])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Material", new named_type(IFC4X2_types[590]), true));
        attributes.push_back(new attribute("Profile", new named_type(IFC4X2_types[751]), false));
        attributes.push_back(new attribute("Priority", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[601])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("MaterialProfiles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[601])), false));
        attributes.push_back(new attribute("CompositeProfile", new named_type(IFC4X2_types[191]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[602])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ForProfileSet", new named_type(IFC4X2_types[602]), false));
        attributes.push_back(new attribute("CardinalPoint", new named_type(IFC4X2_types[140]), true));
        attributes.push_back(new attribute("ReferenceExtent", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[603])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ForProfileEndSet", new named_type(IFC4X2_types[602]), false));
        attributes.push_back(new attribute("CardinalEndPoint", new named_type(IFC4X2_types[140]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[604])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4X2_types[545])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[605])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Material", new named_type(IFC4X2_types[594]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[606])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC4X2_types[590]), false));
        attributes.push_back(new attribute("RelatedMaterials", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[590])), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[607])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[609])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ValueComponent", new named_type(IFC4X2_types[1168]), false));
        attributes.push_back(new attribute("UnitComponent", new named_type(IFC4X2_types[1157]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[611])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[614]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[612])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[614]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[613])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[617]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[615])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[617]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[616])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[621]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[618])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[619])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[621]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[620])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Benchmark", new named_type(IFC4X2_types[76]), false));
        attributes.push_back(new attribute("ValueSource", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("DataValue", new named_type(IFC4X2_types[623]), true));
        attributes.push_back(new attribute("ReferencePath", new named_type(IFC4X2_types[818]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[622])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(false);
        ((entity*)IFC4X2_types[624])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Currency", new named_type(IFC4X2_types[534]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[636])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[640]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[638])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[640]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[639])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Dimensions", new named_type(IFC4X2_types[291]), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC4X2_types[1165]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[641])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[646])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[647])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PlacementRelTo", new named_type(IFC4X2_types[650]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[650])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BenchmarkValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[208])), true));
        attributes.push_back(new attribute("LogicalAggregator", new named_type(IFC4X2_types[575]), true));
        attributes.push_back(new attribute("ObjectiveQualifier", new named_type(IFC4X2_types[649]), false));
        attributes.push_back(new attribute("UserDefinedQualifier", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[648])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[654]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[653])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4X2_types[260]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[655])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Distance", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X2_types[574]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[656])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Distance", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4X2_types[293]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[657])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[298])), false));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[658])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[662])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[660]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[659])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[661])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[12])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[663])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOrganization", new named_type(IFC4X2_types[663]), false));
        attributes.push_back(new attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[663])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[664])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LateralAxisDirection", new named_type(IFC4X2_types[293]), false));
        attributes.push_back(new attribute("VerticalAxisDirection", new named_type(IFC4X2_types[293]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[665])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeElement", new named_type(IFC4X2_types[345]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[666])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[667])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[670]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[668])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[670]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[669])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("OwningUser", new named_type(IFC4X2_types[683]), false));
        attributes.push_back(new attribute("OwningApplication", new named_type(IFC4X2_types[46]), false));
        attributes.push_back(new attribute("State", new named_type(IFC4X2_types[991]), true));
        attributes.push_back(new attribute("ChangeAction", new named_type(IFC4X2_types[151]), true));
        attributes.push_back(new attribute("LastModifiedDate", new named_type(IFC4X2_types[1128]), true));
        attributes.push_back(new attribute("LastModifyingUser", new named_type(IFC4X2_types[683]), true));
        attributes.push_back(new attribute("LastModifyingApplication", new named_type(IFC4X2_types[46]), true));
        attributes.push_back(new attribute("CreationDate", new named_type(IFC4X2_types[1128]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[671])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[66]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[672])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[666])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[674])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X2_types[1042]), false));
        attributes.push_back(new attribute("ReferenceCurve", new named_type(IFC4X2_types[260]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[675])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LifeCyclePhase", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[677]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[676])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X2_types[678]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4X2_types[1204]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X2_types[931]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[679])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[681]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[680])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("FamilyName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("GivenName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[12])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[682])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ThePerson", new named_type(IFC4X2_types[682]), false));
        attributes.push_back(new attribute("TheOrganization", new named_type(IFC4X2_types[663]), false));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[7])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[683])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[687])), false));
        attributes.push_back(new attribute("Discrimination", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Quality", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Usage", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[685])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[687])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[641]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[688])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[692]), true));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4X2_types[690]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[689])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[692]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[691])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[695]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[693])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[695]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[694])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[698]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[696])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[698]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[697])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Width", new named_type(IFC4X2_types[515]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC4X2_types[515]), false));
        attributes.push_back(new attribute("ColourComponents", new named_type(IFC4X2_types[515]), false));
        attributes.push_back(new attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[78])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[699])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Location", new named_type(IFC4X2_types[141]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[700])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Placement", new named_type(IFC4X2_types[65]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[701])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SizeInX", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("SizeInY", new named_type(IFC4X2_types[545]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[702])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[704])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[709]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[706])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[707])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[709]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[708])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[710])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("PointParameter", new named_type(IFC4X2_types[673]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[711])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X2_types[1042]), false));
        attributes.push_back(new attribute("PointParameterU", new named_type(IFC4X2_types[673]), false));
        attributes.push_back(new attribute("PointParameterV", new named_type(IFC4X2_types[673]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[712])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X2_types[141])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[717])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[67]), false));
        attributes.push_back(new attribute("PolygonalBoundary", new named_type(IFC4X2_types[95]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[714])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Closed", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("Faces", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[510])), false));
        attributes.push_back(new attribute("PnIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[720])), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[715])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[141])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[716])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[718])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[719])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("InternalLocation", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("PostalBox", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Town", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Region", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("PostalCode", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Country", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[724])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[726])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[727])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[728])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[729])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[730])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[731])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[734])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[543])), false));
        attributes.push_back(new attribute("Identifier", new named_type(IFC4X2_types[505]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[735])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("LayerOn", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("LayerFrozen", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("LayerBlocked", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4X2_types[737])), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[736])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[737])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[739])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[738])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[743]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[741])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[743]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[742])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[744])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ObjectPlacement", new named_type(IFC4X2_types[650]), true));
        attributes.push_back(new attribute("Representation", new named_type(IFC4X2_types[748]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[746])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[747])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[885])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[748])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProfileType", new named_type(IFC4X2_types[753]), false));
        attributes.push_back(new attribute("ProfileName", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[751])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ProfileDefinition", new named_type(IFC4X2_types[751]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[752])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[754])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[759])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[761]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[760])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MapProjection", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("MapZone", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("MapUnit", new named_type(IFC4X2_types[641]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[755])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[758]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[757])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[762])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[763])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("UpperBoundValue", new named_type(IFC4X2_types[1168]), true));
        attributes.push_back(new attribute("LowerBoundValue", new named_type(IFC4X2_types[1168]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[1157]), true));
        attributes.push_back(new attribute("SetPointValue", new named_type(IFC4X2_types[1168]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[764])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[765])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DependingProperty", new named_type(IFC4X2_types[762]), false));
        attributes.push_back(new attribute("DependantProperty", new named_type(IFC4X2_types[762]), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[766])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), true));
        attributes.push_back(new attribute("EnumerationReference", new named_type(IFC4X2_types[768]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[767])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), false));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[1157]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[768])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[1157]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[769])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("PropertyReference", new named_type(IFC4X2_types[651]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[770])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[762])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[771])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[772])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4X2_types[776]), true));
        attributes.push_back(new attribute("ApplicableEntity", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[779])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[775])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("NominalValue", new named_type(IFC4X2_types[1168]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[1157]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[777])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), true));
        attributes.push_back(new attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("DefiningUnit", new named_type(IFC4X2_types[1157]), true));
        attributes.push_back(new attribute("DefinedUnit", new named_type(IFC4X2_types[1157]), true));
        attributes.push_back(new attribute("CurveInterpolation", new named_type(IFC4X2_types[264]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[778])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[779])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[780])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[786]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[781])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[784]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[782])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[784]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[783])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[786]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[785])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProxyType", new named_type(IFC4X2_types[652]), false));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[787])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[790]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[788])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[790]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[789])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AreaValue", new named_type(IFC4X2_types[56]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[791])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CountValue", new named_type(IFC4X2_types[244]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[792])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LengthValue", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[793])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[794])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeValue", new named_type(IFC4X2_types[1122]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[795])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VolumeValue", new named_type(IFC4X2_types[1188]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[796])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("WeightValue", new named_type(IFC4X2_types[588]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[797])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[801]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[799])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[801]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[800])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[807]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[802])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[805]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[803])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[805]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[804])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[807]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[806])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[811])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[809])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[811]))), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[810])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("InnerFilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("OuterFilletRadius", new named_type(IFC4X2_types[642]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[812])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("XDim", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[813])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[814])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4X2_types[1042]), false));
        attributes.push_back(new attribute("U1", new named_type(IFC4X2_types[673]), false));
        attributes.push_back(new attribute("V1", new named_type(IFC4X2_types[673]), false));
        attributes.push_back(new attribute("U2", new named_type(IFC4X2_types[673]), false));
        attributes.push_back(new attribute("V2", new named_type(IFC4X2_types[673]), false));
        attributes.push_back(new attribute("Usense", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("Vsense", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[815])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("RecurrenceType", new named_type(IFC4X2_types[817]), false));
        attributes.push_back(new attribute("DayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[280])), true));
        attributes.push_back(new attribute("WeekdayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[281])), true));
        attributes.push_back(new attribute("MonthComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[637])), true));
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("Interval", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("Occurrences", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("TimePeriods", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1124])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[816])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("TypeIdentifier", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("AttributeIdentifier", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("InstanceName", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("ListPositions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[515])), true));
        attributes.push_back(new attribute("InnerReference", new named_type(IFC4X2_types[818]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[818])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[820]), true));
        attributes.push_back(new attribute("RestartDistance", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[819])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStep", new named_type(IFC4X2_types[1122]), false));
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1127])), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[822])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TotalCrossSectionArea", new named_type(IFC4X2_types[56]), false));
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4X2_types[827]), true));
        attributes.push_back(new attribute("EffectiveDepth", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("NominalBarDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("BarCount", new named_type(IFC4X2_types[244]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[823])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DefinitionType", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[921])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[824])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("BarLength", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[829]), true));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4X2_types[827]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[825])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[829]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("BarLength", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4X2_types[827]), true));
        attributes.push_back(new attribute("BendingShapeCode", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[77])), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[828])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[830])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[831])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("MeshLength", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[834]), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[832])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[834]), false));
        attributes.push_back(new attribute("MeshLength", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("BendingShapeCode", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[77])), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[833])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4X2_types[647]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[647])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[835])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[647])), false));
        attributes.push_back(new attribute("RelatedObjectsType", new named_type(IFC4X2_types[652]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[836])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingActor", new named_type(IFC4X2_types[6]), false));
        attributes.push_back(new attribute("ActingRole", new named_type(IFC4X2_types[7]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[837])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingControl", new named_type(IFC4X2_types[224]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[838])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingGroup", new named_type(IFC4X2_types[494]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[839])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Factor", new named_type(IFC4X2_types[808]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[840])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC4X2_types[745]), false));
        attributes.push_back(new attribute("QuantityInProcess", new named_type(IFC4X2_types[611]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[841])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingProduct", new named_type(IFC4X2_types[750]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[842])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingResource", new named_type(IFC4X2_types[894]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[843])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[284])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[844])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4X2_types[49]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[845])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingClassification", new named_type(IFC4X2_types[167]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[846])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Intent", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC4X2_types[208]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[847])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC4X2_types[317]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[848])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingLibrary", new named_type(IFC4X2_types[548]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[849])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC4X2_types[608]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[850])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[852])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC4X2_types[202]), true));
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4X2_types[372]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[853])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X2_types[515])), false));
        attributes.push_back(new attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4X2_types[515])), false));
        attributes.push_back(new attribute("RelatedConnectionType", new named_type(IFC4X2_types[206]), false));
        attributes.push_back(new attribute("RelatingConnectionType", new named_type(IFC4X2_types[206]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[854])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC4X2_types[718]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4X2_types[305]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[856])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC4X2_types[718]), false));
        attributes.push_back(new attribute("RelatedPort", new named_type(IFC4X2_types[718]), false));
        attributes.push_back(new attribute("RealizingElement", new named_type(IFC4X2_types[372]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[855])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X2_types[994]), false));
        attributes.push_back(new attribute("RelatedStructuralActivity", new named_type(IFC4X2_types[993]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[857])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("RelatingStructuralMember", new named_type(IFC4X2_types[1020]), false));
        attributes.push_back(new attribute("RelatedStructuralConnection", new named_type(IFC4X2_types[996]), false));
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC4X2_types[89]), true));
        attributes.push_back(new attribute("AdditionalConditions", new named_type(IFC4X2_types[997]), true));
        attributes.push_back(new attribute("SupportedLength", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC4X2_types[67]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[858])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConnectionConstraint", new named_type(IFC4X2_types[202]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[859])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[372])), false));
        attributes.push_back(new attribute("ConnectionType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[860])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[746])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC4X2_types[969]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[861])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[245])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[862])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC4X2_types[962]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[245])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[863])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingContext", new named_type(IFC4X2_types[221]), false));
        attributes.push_back(new attribute("RelatedDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[284])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[864])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[865])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[866])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[646])), false));
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4X2_types[646]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[867])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[647])), false));
        attributes.push_back(new attribute("RelatingPropertyDefinition", new named_type(IFC4X2_types[773]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[868])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[772])), false));
        attributes.push_back(new attribute("RelatingTemplate", new named_type(IFC4X2_types[775]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[869])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[646])), false));
        attributes.push_back(new attribute("RelatingType", new named_type(IFC4X2_types[1153]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[870])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOpeningElement", new named_type(IFC4X2_types[659]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC4X2_types[372]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[871])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[303])), false));
        attributes.push_back(new attribute("RelatingFlowElement", new named_type(IFC4X2_types[307]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[872])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("InterferenceGeometry", new named_type(IFC4X2_types[202]), true));
        attributes.push_back(new attribute("InterferenceType", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("ImpliedOrder", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[873])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4X2_types[647]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[647])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[874])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingPositioningElement", new named_type(IFC4X2_types[719]), false));
        attributes.push_back(new attribute("RelatedProducts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[746])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[875])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("RelatedFeatureElement", new named_type(IFC4X2_types[430]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[876])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[746])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC4X2_types[969]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[877])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC4X2_types[744]), false));
        attributes.push_back(new attribute("RelatedProcess", new named_type(IFC4X2_types[744]), false));
        attributes.push_back(new attribute("TimeLag", new named_type(IFC4X2_types[538]), true));
        attributes.push_back(new attribute("SequenceType", new named_type(IFC4X2_types[927]), true));
        attributes.push_back(new attribute("UserDefinedSequenceType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[878])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSystem", new named_type(IFC4X2_types[1067]), false));
        attributes.push_back(new attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[969])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[879])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC4X2_types[963]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC4X2_types[202]), true));
        attributes.push_back(new attribute("PhysicalOrVirtualBoundary", new named_type(IFC4X2_types[686]), false));
        attributes.push_back(new attribute("InternalOrExternalBoundary", new named_type(IFC4X2_types[520]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[880])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentBoundary", new named_type(IFC4X2_types[881]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[881])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CorrespondingBoundary", new named_type(IFC4X2_types[882]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[882])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC4X2_types[372]), false));
        attributes.push_back(new attribute("RelatedOpeningElement", new named_type(IFC4X2_types[431]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[883])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[851])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParamLength", new named_type(IFC4X2_types[673]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[884])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ContextOfItems", new named_type(IFC4X2_types[886]), false));
        attributes.push_back(new attribute("RepresentationIdentifier", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("RepresentationType", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[887])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[885])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ContextIdentifier", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("ContextType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[886])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[887])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingOrigin", new named_type(IFC4X2_types[65]), false));
        attributes.push_back(new attribute("MappedRepresentation", new named_type(IFC4X2_types[885]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[888])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[889])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[893])), false));
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4X2_types[49]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[890])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC4X2_types[208]), false));
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[893])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[891])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[892])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new attribute("ScheduleWork", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("ScheduleUsage", new named_type(IFC4X2_types[723]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ScheduleContour", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("LevelingDelay", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("IsOverAllocated", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ActualWork", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("ActualUsage", new named_type(IFC4X2_types[723]), true));
        attributes.push_back(new attribute("ActualStart", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("RemainingWork", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("RemainingUsage", new named_type(IFC4X2_types[723]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC4X2_types[723]), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[895])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X2_types[64]), false));
        attributes.push_back(new attribute("Angle", new named_type(IFC4X2_types[705]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[896])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EndSweptArea", new named_type(IFC4X2_types[751]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[897])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("BottomRadius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[898])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[899])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[903]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[901])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[903]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[902])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("GlobalId", new named_type(IFC4X2_types[487]), false));
        attributes.push_back(new attribute("OwnerHistory", new named_type(IFC4X2_types[671]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[904])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RoundingRadius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[909])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Prefix", new named_type(IFC4X2_types[941]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[944]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[943])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[912]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[910])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[912]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[911])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC4X2_types[277]), true));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[913])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[914])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SectionType", new named_type(IFC4X2_types[922]), false));
        attributes.push_back(new attribute("StartProfile", new named_type(IFC4X2_types[751]), false));
        attributes.push_back(new attribute("EndProfile", new named_type(IFC4X2_types[751]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[920])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LongitudinalStartPosition", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("LongitudinalEndPosition", new named_type(IFC4X2_types[545]), false));
        attributes.push_back(new attribute("TransversePosition", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("ReinforcementRole", new named_type(IFC4X2_types[826]), false));
        attributes.push_back(new attribute("SectionDefinition", new named_type(IFC4X2_types[920]), false));
        attributes.push_back(new attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[823])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[921])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[751])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[916])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[298])), false));
        attributes.push_back(new attribute("FixedAxisVertical", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[917])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SpineCurve", new named_type(IFC4X2_types[188]), false));
        attributes.push_back(new attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[751])), false));
        attributes.push_back(new attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4X2_types[67])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[918])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[926]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[924])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[926]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[925])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[930]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[928])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[930]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[929])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[932])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("ProductDefinitional", new named_type(IFC4X2_types[574]), false));
        attributes.push_back(new attribute("PartOfProductDefinitionShape", new named_type(IFC4X2_types[749]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[931])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[932])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[933])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[935])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[936])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[937])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4X2_types[939]), true));
        attributes.push_back(new attribute("PrimaryMeasureType", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("SecondaryMeasureType", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Enumerators", new named_type(IFC4X2_types[768]), true));
        attributes.push_back(new attribute("PrimaryUnit", new named_type(IFC4X2_types[1157]), true));
        attributes.push_back(new attribute("SecondaryUnit", new named_type(IFC4X2_types[1157]), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("AccessState", new named_type(IFC4X2_types[991]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[938])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RefLatitude", new named_type(IFC4X2_types[192]), true));
        attributes.push_back(new attribute("RefLongitude", new named_type(IFC4X2_types[192]), true));
        attributes.push_back(new attribute("RefElevation", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("LandTitleNumber", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("SiteAddress", new named_type(IFC4X2_types[724]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[942])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[950]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[946])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[947])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[948])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[950]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[949])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SlippageX", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("SlippageY", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("SlippageZ", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[951])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[954]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[952])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[954]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[953])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[956])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[968]), true));
        attributes.push_back(new attribute("ElevationWithFlooring", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[962])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[966]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[964])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[966]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[965])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[968]), false));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[967])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[969])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[970])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CompositionType", new named_type(IFC4X2_types[379]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[971])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[972])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[975]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[973])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[975]), false));
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[974])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[980])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[981])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[984]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[982])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[984]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[983])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[990]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[985])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NumberOfRisers", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("NumberOfTreads", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("RiserHeight", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("TreadLength", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[988]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[986])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[988]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[987])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[990]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[989])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DestabilizingLoad", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[992])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AppliedLoad", new named_type(IFC4X2_types[1007]), false));
        attributes.push_back(new attribute("GlobalOrLocal", new named_type(IFC4X2_types[488]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[993])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[41]), false));
        attributes.push_back(new attribute("OrientationOf2DPlane", new named_type(IFC4X2_types[67]), true));
        attributes.push_back(new attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1010])), true));
        attributes.push_back(new attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1026])), true));
        attributes.push_back(new attribute("SharedPlacement", new named_type(IFC4X2_types[650]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[995])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC4X2_types[89]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[996])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[997])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC4X2_types[756]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[999]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[998])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4X2_types[293]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1000])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1002]), false));
        attributes.push_back(new attribute("Axis", new named_type(IFC4X2_types[293]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1001])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1003])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[999]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1004])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1005])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1006])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1007])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SelfWeightCoefficients", new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[808])), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1008])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1012])), false));
        attributes.push_back(new attribute("Locations", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X2_types[545]))), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1009])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[572]), false));
        attributes.push_back(new attribute("ActionType", new named_type(IFC4X2_types[5]), false));
        attributes.push_back(new attribute("ActionSource", new named_type(IFC4X2_types[4]), false));
        attributes.push_back(new attribute("Coefficient", new named_type(IFC4X2_types[808]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1010])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LinearForceX", new named_type(IFC4X2_types[564]), true));
        attributes.push_back(new attribute("LinearForceY", new named_type(IFC4X2_types[564]), true));
        attributes.push_back(new attribute("LinearForceZ", new named_type(IFC4X2_types[564]), true));
        attributes.push_back(new attribute("LinearMomentX", new named_type(IFC4X2_types[565]), true));
        attributes.push_back(new attribute("LinearMomentY", new named_type(IFC4X2_types[565]), true));
        attributes.push_back(new attribute("LinearMomentZ", new named_type(IFC4X2_types[565]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1011])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1012])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PlanarForceX", new named_type(IFC4X2_types[703]), true));
        attributes.push_back(new attribute("PlanarForceY", new named_type(IFC4X2_types[703]), true));
        attributes.push_back(new attribute("PlanarForceZ", new named_type(IFC4X2_types[703]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1013])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DisplacementX", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("DisplacementY", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("DisplacementZ", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("RotationalDisplacementRX", new named_type(IFC4X2_types[705]), true));
        attributes.push_back(new attribute("RotationalDisplacementRY", new named_type(IFC4X2_types[705]), true));
        attributes.push_back(new attribute("RotationalDisplacementRZ", new named_type(IFC4X2_types[705]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1014])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Distortion", new named_type(IFC4X2_types[259]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1015])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("ForceX", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("ForceY", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("ForceZ", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("MomentX", new named_type(IFC4X2_types[1132]), true));
        attributes.push_back(new attribute("MomentY", new named_type(IFC4X2_types[1132]), true));
        attributes.push_back(new attribute("MomentZ", new named_type(IFC4X2_types[1132]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1016])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingMoment", new named_type(IFC4X2_types[1196]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1017])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1018])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DeltaTConstant", new named_type(IFC4X2_types[1120]), true));
        attributes.push_back(new attribute("DeltaTY", new named_type(IFC4X2_types[1120]), true));
        attributes.push_back(new attribute("DeltaTZ", new named_type(IFC4X2_types[1120]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1019])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1020])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1021])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1022])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC4X2_types[67]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1023])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1024])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1025])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TheoryType", new named_type(IFC4X2_types[42]), false));
        attributes.push_back(new attribute("ResultForLoadGroup", new named_type(IFC4X2_types[1010]), true));
        attributes.push_back(new attribute("IsLinear", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1026])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC4X2_types[756]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1028]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1027])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1029])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1031]), false));
        attributes.push_back(new attribute("Thickness", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1030])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1032])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1028]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1033])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1037])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Item", new named_type(IFC4X2_types[887]), true));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1034])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1035])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1036])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1040]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1038])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1040]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1039])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentEdge", new named_type(IFC4X2_types[345]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1041])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[1042])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Curve3D", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("AssociatedGeometry", new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4X2_types[675])), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC4X2_types[732]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1043])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4X2_types[673]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4X2_types[673]), true));
        attributes.push_back(new attribute("ReferenceSurface", new named_type(IFC4X2_types[1042]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1044])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1046]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1045])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC4X2_types[293]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[545]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1047])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AxisPosition", new named_type(IFC4X2_types[64]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1048])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SurfaceReinforcement1", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X2_types[545])), true));
        attributes.push_back(new attribute("SurfaceReinforcement2", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X2_types[545])), true));
        attributes.push_back(new attribute("ShearReinforcement", new named_type(IFC4X2_types[808]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1050])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Side", new named_type(IFC4X2_types[1051]), false));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4X2_types[1053])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1052])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC4X2_types[174]), false));
        attributes.push_back(new attribute("DiffuseReflectionColour", new named_type(IFC4X2_types[174]), false));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC4X2_types[174]), false));
        attributes.push_back(new attribute("ReflectanceColour", new named_type(IFC4X2_types[174]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1054])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RefractionIndex", new named_type(IFC4X2_types[811]), true));
        attributes.push_back(new attribute("DispersionFactor", new named_type(IFC4X2_types[811]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1055])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("DiffuseColour", new named_type(IFC4X2_types[173]), true));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC4X2_types[173]), true));
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC4X2_types[173]), true));
        attributes.push_back(new attribute("ReflectionColour", new named_type(IFC4X2_types[173]), true));
        attributes.push_back(new attribute("SpecularColour", new named_type(IFC4X2_types[173]), true));
        attributes.push_back(new attribute("SpecularHighlight", new named_type(IFC4X2_types[978]), true));
        attributes.push_back(new attribute("ReflectanceMethod", new named_type(IFC4X2_types[821]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1056])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceColour", new named_type(IFC4X2_types[174]), false));
        attributes.push_back(new attribute("Transparency", new named_type(IFC4X2_types[643]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1057])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1059])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1058])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RepeatS", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("RepeatT", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("Mode", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("TextureTransform", new named_type(IFC4X2_types[146]), true));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[505])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1059])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptArea", new named_type(IFC4X2_types[751]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[67]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1060])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("InnerRadius", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4X2_types[673]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4X2_types[673]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1061])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1062])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptCurve", new named_type(IFC4X2_types[751]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC4X2_types[67]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1063])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1066]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1064])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1066]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1065])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1067])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1070]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1068])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1070]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1069])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("WebEdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("WebSlope", new named_type(IFC4X2_types[705]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4X2_types[705]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1149])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1073])), true));
        attributes.push_back(new attribute("Columns", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1072])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1071])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Identifier", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[1157]), true));
        attributes.push_back(new attribute("ReferencePath", new named_type(IFC4X2_types[818]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1072])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), true));
        attributes.push_back(new attribute("IsHeading", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1073])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1076]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1074])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1076]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1075])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Status", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("IsMilestone", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("Priority", new named_type(IFC4X2_types[515]), true));
        attributes.push_back(new attribute("TaskTime", new named_type(IFC4X2_types[1079]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1082]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1077])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("DurationType", new named_type(IFC4X2_types[1078]), true));
        attributes.push_back(new attribute("ScheduleDuration", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("EarlyStart", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("EarlyFinish", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("LateStart", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("LateFinish", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("FreeFloat", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("IsCritical", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ActualDuration", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("ActualStart", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC4X2_types[279]), true));
        attributes.push_back(new attribute("RemainingTime", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC4X2_types[723]), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1079])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Recurrence", new named_type(IFC4X2_types[816]), false));
        std::vector<bool> derived; derived.reserve(21);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1080])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1082]), false));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1081])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("PagerNumber", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[534])), true));
        attributes.push_back(new attribute("WWWHomePageURL", new named_type(IFC4X2_types[1166]), true));
        attributes.push_back(new attribute("MessagingIDs", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1166])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1083])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1094]), true));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("TensionForce", new named_type(IFC4X2_types[470]), true));
        attributes.push_back(new attribute("PreStress", new named_type(IFC4X2_types[740]), true));
        attributes.push_back(new attribute("FrictionCoefficient", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("AnchorageSlip", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("MinCurvatureRadius", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1086])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1089]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1087])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1089]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1088])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1092]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1090])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1092]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1091])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1094]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4X2_types[56]), true));
        attributes.push_back(new attribute("SheathDiameter", new named_type(IFC4X2_types[721]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1093])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new named_type(IFC4X2_types[144]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1095])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[1096])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Literal", new named_type(IFC4X2_types[733]), false));
        attributes.push_back(new attribute("Placement", new named_type(IFC4X2_types[65]), false));
        attributes.push_back(new attribute("Path", new named_type(IFC4X2_types[1104]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1102])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Extent", new named_type(IFC4X2_types[702]), false));
        attributes.push_back(new attribute("BoxAlignment", new named_type(IFC4X2_types[98]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1103])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("TextCharacterAppearance", new named_type(IFC4X2_types[1107]), true));
        attributes.push_back(new attribute("TextStyle", new named_type(IFC4X2_types[1108]), true));
        attributes.push_back(new attribute("TextFontStyle", new named_type(IFC4X2_types[1101]), false));
        attributes.push_back(new attribute("ModelOrDraughting", new named_type(IFC4X2_types[84]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1105])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1100])), false));
        attributes.push_back(new attribute("FontStyle", new named_type(IFC4X2_types[464]), true));
        attributes.push_back(new attribute("FontVariant", new named_type(IFC4X2_types[465]), true));
        attributes.push_back(new attribute("FontWeight", new named_type(IFC4X2_types[466]), true));
        attributes.push_back(new attribute("FontSize", new named_type(IFC4X2_types[945]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1106])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Colour", new named_type(IFC4X2_types[172]), false));
        attributes.push_back(new attribute("BackgroundColour", new named_type(IFC4X2_types[172]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1107])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("TextIndent", new named_type(IFC4X2_types[945]), true));
        attributes.push_back(new attribute("TextAlign", new named_type(IFC4X2_types[1098]), true));
        attributes.push_back(new attribute("TextDecoration", new named_type(IFC4X2_types[1099]), true));
        attributes.push_back(new attribute("LetterSpacing", new named_type(IFC4X2_types[945]), true));
        attributes.push_back(new attribute("WordSpacing", new named_type(IFC4X2_types[945]), true));
        attributes.push_back(new attribute("TextTransform", new named_type(IFC4X2_types[1109]), true));
        attributes.push_back(new attribute("LineHeight", new named_type(IFC4X2_types[945]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1108])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Maps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1059])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1110])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Mode", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[811])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1111])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Vertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4X2_types[1113])), false));
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4X2_types[413]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X2_types[673])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1113])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TexCoordsList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X2_types[673]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1114])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("StartTime", new named_type(IFC4X2_types[1121]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC4X2_types[1121]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1124])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Name", new named_type(IFC4X2_types[534]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC4X2_types[279]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC4X2_types[279]), false));
        attributes.push_back(new attribute("TimeSeriesDataType", new named_type(IFC4X2_types[1126]), false));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC4X2_types[277]), false));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4X2_types[1157]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1125])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[1168])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1127])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[1129])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1130])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MajorRadius", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("MinorRadius", new named_type(IFC4X2_types[721]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1135]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1133])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1135]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("StartRadius", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("EndRadius", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("IsStartRadiusCCW", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("IsEndRadiusCCW", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("TransitionCurveType", new named_type(IFC4X2_types[1138]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1137])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1142]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1140])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1142]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1141])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BottomXDim", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("TopXDim", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("TopXOffset", new named_type(IFC4X2_types[545]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1143])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Normals", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[673]))), true));
        attributes.push_back(new attribute("Closed", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4X2_types[720]))), false));
        attributes.push_back(new attribute("PnIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[720])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1144])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Flags", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[515])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1145])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4X2_types[260]), false));
        attributes.push_back(new attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X2_types[1148])), false));
        attributes.push_back(new attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4X2_types[1148])), false));
        attributes.push_back(new attribute("SenseAgreement", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC4X2_types[1147]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1146])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1152]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1150])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1152]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1151])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ApplicableOccurrence", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[772])), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1153])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("ProcessType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1154])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4X2_types[888])), true));
        attributes.push_back(new attribute("Tag", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1155])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Identification", new named_type(IFC4X2_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4X2_types[1097]), true));
        attributes.push_back(new attribute("ResourceType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1156])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4X2_types[705]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1167])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1157])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1164])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1160]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1158])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1160]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1159])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1163]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1161])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1163]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1162])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1171]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1169])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1171]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1170])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4X2_types[293]), false));
        attributes.push_back(new attribute("Magnitude", new named_type(IFC4X2_types[545]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1173])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4X2_types[1175])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LoopVertex", new named_type(IFC4X2_types[1175]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1176])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("VertexGeometry", new named_type(IFC4X2_types[710]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4X2_types[1177])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1180]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1178])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1180]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1179])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1183]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1181])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1183]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1182])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1184])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4X2_types[490])), false));
        attributes.push_back(new attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4X2_types[545])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1185])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1187]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1186])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1194]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1190])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1191])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1192])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1194]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1193])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1200]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1198])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1200]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1199])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1211]), true));
        attributes.push_back(new attribute("PartitioningType", new named_type(IFC4X2_types[1212]), true));
        attributes.push_back(new attribute("UserDefinedPartitioningType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1201])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("MullionThickness", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("FirstTransomOffset", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("SecondTransomOffset", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("FirstMullionOffset", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("SecondMullionOffset", new named_type(IFC4X2_types[643]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X2_types[931]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetX", new named_type(IFC4X2_types[545]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetY", new named_type(IFC4X2_types[545]), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1202])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X2_types[1203]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4X2_types[1204]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC4X2_types[721]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4X2_types[931]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1205])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1206])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4X2_types[1208]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4X2_types[1209]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X2_types[84]), false));
        attributes.push_back(new attribute("Sizeable", new named_type(IFC4X2_types[84]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1207])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1211]), false));
        attributes.push_back(new attribute("PartitioningType", new named_type(IFC4X2_types[1212]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4X2_types[84]), true));
        attributes.push_back(new attribute("UserDefinedPartitioningType", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1210])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WorkingTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1220])), true));
        attributes.push_back(new attribute("ExceptionTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[1220])), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1214]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1213])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("CreationDate", new named_type(IFC4X2_types[279]), false));
        attributes.push_back(new attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4X2_types[682])), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4X2_types[534]), true));
        attributes.push_back(new attribute("Duration", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC4X2_types[343]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC4X2_types[279]), false));
        attributes.push_back(new attribute("FinishTime", new named_type(IFC4X2_types[279]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1215])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1217]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1216])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4X2_types[1219]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1218])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RecurrencePattern", new named_type(IFC4X2_types[816]), true));
        attributes.push_back(new attribute("Start", new named_type(IFC4X2_types[278]), true));
        attributes.push_back(new attribute("Finish", new named_type(IFC4X2_types[278]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1220])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4X2_types[721]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4X2_types[642]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4X2_types[642]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1222])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LongName", new named_type(IFC4X2_types[534]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4X2_types[1221])->set_attributes(attributes, derived);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsActingUpon", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[837]), ((entity*) IFC4X2_types[837])->attributes()[0]));
        ((entity*) IFC4X2_types[6])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[7])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("OfPerson", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[682]), ((entity*) IFC4X2_types[682])->attributes()[7]));
        attributes.push_back(new inverse_attribute("OfOrganization", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[663]), ((entity*) IFC4X2_types[663])->attributes()[4]));
        ((entity*) IFC4X2_types[12])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToAlignmentCurve", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[38]), ((entity*) IFC4X2_types[38])->attributes()[0]));
        ((entity*) IFC4X2_types[30])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToHorizontal", inverse_attribute::set_type, 1, 1, ((entity*) IFC4X2_types[30]), ((entity*) IFC4X2_types[30])->attributes()[1]));
        ((entity*) IFC4X2_types[31])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToAlignmentCurve", inverse_attribute::set_type, 1, 1, ((entity*) IFC4X2_types[38]), ((entity*) IFC4X2_types[38])->attributes()[1]));
        ((entity*) IFC4X2_types[36])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToVertical", inverse_attribute::set_type, 1, 1, ((entity*) IFC4X2_types[36]), ((entity*) IFC4X2_types[36])->attributes()[0]));
        ((entity*) IFC4X2_types[37])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[861]), ((entity*) IFC4X2_types[861])->attributes()[0]));
        ((entity*) IFC4X2_types[44])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[47])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ApprovedObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[845]), ((entity*) IFC4X2_types[845])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ApprovedResources", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[890]), ((entity*) IFC4X2_types[890])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[50]), ((entity*) IFC4X2_types[50])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[50]), ((entity*) IFC4X2_types[50])->attributes()[0]));
        ((entity*) IFC4X2_types[49])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("PositioningElement", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X2_types[567]), ((entity*) IFC4X2_types[567])->attributes()[0]));
        ((entity*) IFC4X2_types[95])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ClassificationForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[846]), ((entity*) IFC4X2_types[846])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[165]), ((entity*) IFC4X2_types[165])->attributes()[0]));
        ((entity*) IFC4X2_types[164])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ClassificationRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[846]), ((entity*) IFC4X2_types[846])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[165]), ((entity*) IFC4X2_types[165])->attributes()[0]));
        ((entity*) IFC4X2_types[165])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("UsingCurves", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[188]), ((entity*) IFC4X2_types[188])->attributes()[0]));
        ((entity*) IFC4X2_types[190])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PropertiesForConstraint", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[891]), ((entity*) IFC4X2_types[891])->attributes()[0]));
        ((entity*) IFC4X2_types[208])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[868]), ((entity*) IFC4X2_types[868])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Declares", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[864]), ((entity*) IFC4X2_types[864])->attributes()[0]));
        ((entity*) IFC4X2_types[221])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[223])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Controls", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[838]), ((entity*) IFC4X2_types[838])->attributes()[0]));
        ((entity*) IFC4X2_types[224])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[228])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasCoordinateOperation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[236]), ((entity*) IFC4X2_types[236])->attributes()[0]));
        ((entity*) IFC4X2_types[237])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("CoversSpaces", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[863]), ((entity*) IFC4X2_types[863])->attributes()[1]));
        attributes.push_back(new inverse_attribute("CoversElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[862]), ((entity*) IFC4X2_types[862])->attributes()[1]));
        ((entity*) IFC4X2_types[245])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToFlowElement", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[872]), ((entity*) IFC4X2_types[872])->attributes()[0]));
        ((entity*) IFC4X2_types[303])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasPorts", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[856]), ((entity*) IFC4X2_types[856])->attributes()[1]));
        ((entity*) IFC4X2_types[305])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasControlElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[872]), ((entity*) IFC4X2_types[872])->attributes()[1]));
        ((entity*) IFC4X2_types[307])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("DocumentInfoForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[848]), ((entity*) IFC4X2_types[848])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasDocumentReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[316]), ((entity*) IFC4X2_types[316])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[315]), ((entity*) IFC4X2_types[315])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointer", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[315]), ((entity*) IFC4X2_types[315])->attributes()[0]));
        ((entity*) IFC4X2_types[314])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("DocumentRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[848]), ((entity*) IFC4X2_types[848])->attributes()[0]));
        ((entity*) IFC4X2_types[316])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new inverse_attribute("FillsVoids", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[871]), ((entity*) IFC4X2_types[871])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[853]), ((entity*) IFC4X2_types[853])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsInterferedByElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[873]), ((entity*) IFC4X2_types[873])->attributes()[1]));
        attributes.push_back(new inverse_attribute("InterferesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[873]), ((entity*) IFC4X2_types[873])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasProjections", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[876]), ((entity*) IFC4X2_types[876])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedInStructures", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[877]), ((entity*) IFC4X2_types[877])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasOpenings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[883]), ((entity*) IFC4X2_types[883])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsConnectionRealization", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[860]), ((entity*) IFC4X2_types[860])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ProvidesBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[880]), ((entity*) IFC4X2_types[880])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[853]), ((entity*) IFC4X2_types[853])->attributes()[2]));
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[861]), ((entity*) IFC4X2_types[861])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[862]), ((entity*) IFC4X2_types[862])->attributes()[0]));
        ((entity*) IFC4X2_types[372])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ExternalReferenceForResources", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[0]));
        ((entity*) IFC4X2_types[406])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[880]), ((entity*) IFC4X2_types[880])->attributes()[0]));
        ((entity*) IFC4X2_types[408])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasTextureMaps", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[1112]), ((entity*) IFC4X2_types[1112])->attributes()[1]));
        ((entity*) IFC4X2_types[413])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ProjectsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X2_types[876]), ((entity*) IFC4X2_types[876])->attributes()[1]));
        ((entity*) IFC4X2_types[430])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("VoidsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X2_types[883]), ((entity*) IFC4X2_types[883])->attributes()[1]));
        ((entity*) IFC4X2_types[431])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasSubContexts", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[484]), ((entity*) IFC4X2_types[484])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasCoordinateOperation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[236]), ((entity*) IFC4X2_types[236])->attributes()[0]));
        ((entity*) IFC4X2_types[482])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("PartOfW", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[489]), ((entity*) IFC4X2_types[489])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfV", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[489]), ((entity*) IFC4X2_types[489])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfU", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[489]), ((entity*) IFC4X2_types[489])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasIntersections", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[1185]), ((entity*) IFC4X2_types[1185])->attributes()[0]));
        ((entity*) IFC4X2_types[490])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsGroupedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[839]), ((entity*) IFC4X2_types[839])->attributes()[0]));
        ((entity*) IFC4X2_types[494])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToFaceSet", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[715]), ((entity*) IFC4X2_types[715])->attributes()[1]));
        ((entity*) IFC4X2_types[510])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LibraryInfoForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[849]), ((entity*) IFC4X2_types[849])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasLibraryReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[547]), ((entity*) IFC4X2_types[547])->attributes()[2]));
        ((entity*) IFC4X2_types[546])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("LibraryRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[849]), ((entity*) IFC4X2_types[849])->attributes()[0]));
        ((entity*) IFC4X2_types[547])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("HasRepresentation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[595]), ((entity*) IFC4X2_types[595])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[607]), ((entity*) IFC4X2_types[607])->attributes()[1]));
        attributes.push_back(new inverse_attribute("RelatesTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[607]), ((entity*) IFC4X2_types[607])->attributes()[0]));
        ((entity*) IFC4X2_types[590])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialConstituentSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X2_types[593]), ((entity*) IFC4X2_types[593])->attributes()[2]));
        ((entity*) IFC4X2_types[592])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("AssociatedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[850]), ((entity*) IFC4X2_types[850])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasProperties", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[606]), ((entity*) IFC4X2_types[606])->attributes()[0]));
        ((entity*) IFC4X2_types[594])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialLayerSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X2_types[597]), ((entity*) IFC4X2_types[597])->attributes()[0]));
        ((entity*) IFC4X2_types[596])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialProfileSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4X2_types[602]), ((entity*) IFC4X2_types[602])->attributes()[2]));
        ((entity*) IFC4X2_types[601])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssociatedTo", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[850]), ((entity*) IFC4X2_types[850])->attributes()[0]));
        ((entity*) IFC4X2_types[609])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("IsDeclaredBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[867]), ((entity*) IFC4X2_types[867])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Declares", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[867]), ((entity*) IFC4X2_types[867])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsTypedBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[870]), ((entity*) IFC4X2_types[870])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[868]), ((entity*) IFC4X2_types[868])->attributes()[0]));
        ((entity*) IFC4X2_types[646])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new inverse_attribute("HasAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[836]), ((entity*) IFC4X2_types[836])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Nests", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[874]), ((entity*) IFC4X2_types[874])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsNestedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[874]), ((entity*) IFC4X2_types[874])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasContext", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[864]), ((entity*) IFC4X2_types[864])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsDecomposedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[835]), ((entity*) IFC4X2_types[835])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Decomposes", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[835]), ((entity*) IFC4X2_types[835])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[844]), ((entity*) IFC4X2_types[844])->attributes()[0]));
        ((entity*) IFC4X2_types[647])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("PlacesObject", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[746]), ((entity*) IFC4X2_types[746])->attributes()[0]));
        ((entity*) IFC4X2_types[650])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasFillings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[871]), ((entity*) IFC4X2_types[871])->attributes()[0]));
        ((entity*) IFC4X2_types[659])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsRelatedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[664]), ((entity*) IFC4X2_types[664])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[664]), ((entity*) IFC4X2_types[664])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Engages", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[683]), ((entity*) IFC4X2_types[683])->attributes()[1]));
        ((entity*) IFC4X2_types[663])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("EngagedIn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[683]), ((entity*) IFC4X2_types[683])->attributes()[0]));
        ((entity*) IFC4X2_types[682])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[685]), ((entity*) IFC4X2_types[685])->attributes()[0]));
        ((entity*) IFC4X2_types[687])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainedIn", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[856]), ((entity*) IFC4X2_types[856])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[855]), ((entity*) IFC4X2_types[855])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[855]), ((entity*) IFC4X2_types[855])->attributes()[0]));
        ((entity*) IFC4X2_types[718])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[861]), ((entity*) IFC4X2_types[861])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Positions", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[875]), ((entity*) IFC4X2_types[875])->attributes()[0]));
        ((entity*) IFC4X2_types[719])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsPredecessorTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[878]), ((entity*) IFC4X2_types[878])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsSuccessorFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[878]), ((entity*) IFC4X2_types[878])->attributes()[1]));
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[841]), ((entity*) IFC4X2_types[841])->attributes()[0]));
        ((entity*) IFC4X2_types[744])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[842]), ((entity*) IFC4X2_types[842])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PositionedRelativeTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[875]), ((entity*) IFC4X2_types[875])->attributes()[1]));
        ((entity*) IFC4X2_types[746])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ShapeOfProduct", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[746]), ((entity*) IFC4X2_types[746])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[931]), ((entity*) IFC4X2_types[931])->attributes()[4]));
        ((entity*) IFC4X2_types[747])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasProperties", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[752]), ((entity*) IFC4X2_types[752])->attributes()[0]));
        ((entity*) IFC4X2_types[751])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new inverse_attribute("PartOfPset", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[771]), ((entity*) IFC4X2_types[771])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyForDependance", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[766]), ((entity*) IFC4X2_types[766])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyDependsOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[766]), ((entity*) IFC4X2_types[766])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[185]), ((entity*) IFC4X2_types[185])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasConstraints", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[891]), ((entity*) IFC4X2_types[891])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasApprovals", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[890]), ((entity*) IFC4X2_types[890])->attributes()[0]));
        ((entity*) IFC4X2_types[762])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[763])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasContext", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[864]), ((entity*) IFC4X2_types[864])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[844]), ((entity*) IFC4X2_types[844])->attributes()[0]));
        ((entity*) IFC4X2_types[765])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("DefinesType", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[1153]), ((entity*) IFC4X2_types[1153])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[869]), ((entity*) IFC4X2_types[869])->attributes()[0]));
        attributes.push_back(new inverse_attribute("DefinesOccurrence", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[868]), ((entity*) IFC4X2_types[868])->attributes()[1]));
        ((entity*) IFC4X2_types[772])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Defines", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[869]), ((entity*) IFC4X2_types[869])->attributes()[1]));
        ((entity*) IFC4X2_types[775])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PartOfComplexTemplate", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[186]), ((entity*) IFC4X2_types[186])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfPsetTemplate", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[775]), ((entity*) IFC4X2_types[775])->attributes()[2]));
        ((entity*) IFC4X2_types[779])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("InnerBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[881]), ((entity*) IFC4X2_types[881])->attributes()[0]));
        ((entity*) IFC4X2_types[881])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Corresponds", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[882]), ((entity*) IFC4X2_types[882])->attributes()[0]));
        ((entity*) IFC4X2_types[882])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("RepresentationMap", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[888]), ((entity*) IFC4X2_types[888])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LayerAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[735]), ((entity*) IFC4X2_types[735])->attributes()[2]));
        attributes.push_back(new inverse_attribute("OfProductRepresentation", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[748]), ((entity*) IFC4X2_types[748])->attributes()[2]));
        ((entity*) IFC4X2_types[885])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("RepresentationsInContext", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[885]), ((entity*) IFC4X2_types[885])->attributes()[0]));
        ((entity*) IFC4X2_types[886])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LayerAssignment", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[735]), ((entity*) IFC4X2_types[735])->attributes()[2]));
        attributes.push_back(new inverse_attribute("StyledByItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[1035]), ((entity*) IFC4X2_types[1035])->attributes()[0]));
        ((entity*) IFC4X2_types[887])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[931]), ((entity*) IFC4X2_types[931])->attributes()[4]));
        attributes.push_back(new inverse_attribute("MapUsage", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[585]), ((entity*) IFC4X2_types[585])->attributes()[0]));
        ((entity*) IFC4X2_types[888])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[843]), ((entity*) IFC4X2_types[843])->attributes()[0]));
        ((entity*) IFC4X2_types[889])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[931])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OfShapeAspect", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[931]), ((entity*) IFC4X2_types[931])->attributes()[0]));
        ((entity*) IFC4X2_types[932])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[863]), ((entity*) IFC4X2_types[863])->attributes()[0]));
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[880]), ((entity*) IFC4X2_types[880])->attributes()[0]));
        ((entity*) IFC4X2_types[962])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainsElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[861]), ((entity*) IFC4X2_types[861])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ServicedBySystems", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[879]), ((entity*) IFC4X2_types[879])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ReferencesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[877]), ((entity*) IFC4X2_types[877])->attributes()[1]));
        ((entity*) IFC4X2_types[969])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToStructuralItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[857]), ((entity*) IFC4X2_types[857])->attributes()[1]));
        ((entity*) IFC4X2_types[993])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectsStructuralMembers", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[858]), ((entity*) IFC4X2_types[858])->attributes()[1]));
        ((entity*) IFC4X2_types[996])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedStructuralActivity", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[857]), ((entity*) IFC4X2_types[857])->attributes()[0]));
        ((entity*) IFC4X2_types[1005])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("SourceOfResultGroup", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[1026]), ((entity*) IFC4X2_types[1026])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LoadGroupFor", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[995]), ((entity*) IFC4X2_types[995])->attributes()[2]));
        ((entity*) IFC4X2_types[1010])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[858]), ((entity*) IFC4X2_types[858])->attributes()[0]));
        ((entity*) IFC4X2_types[1020])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResultGroupFor", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[995]), ((entity*) IFC4X2_types[995])->attributes()[3]));
        ((entity*) IFC4X2_types[1026])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsMappedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[1110]), ((entity*) IFC4X2_types[1110])->attributes()[0]));
        attributes.push_back(new inverse_attribute("UsedInStyles", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[1058]), ((entity*) IFC4X2_types[1058])->attributes()[0]));
        ((entity*) IFC4X2_types[1059])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ServicesBuildings", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[879]), ((entity*) IFC4X2_types[879])->attributes()[0]));
        ((entity*) IFC4X2_types[1067])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasColours", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[508]), ((entity*) IFC4X2_types[508])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasTextures", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[512]), ((entity*) IFC4X2_types[512])->attributes()[0]));
        ((entity*) IFC4X2_types[1095])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 1, -1, ((entity*) IFC4X2_types[407]), ((entity*) IFC4X2_types[407])->attributes()[1]));
        ((entity*) IFC4X2_types[1125])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Types", inverse_attribute::set_type, 0, 1, ((entity*) IFC4X2_types[870]), ((entity*) IFC4X2_types[870])->attributes()[1]));
        ((entity*) IFC4X2_types[1153])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[841]), ((entity*) IFC4X2_types[841])->attributes()[0]));
        ((entity*) IFC4X2_types[1154])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[842]), ((entity*) IFC4X2_types[842])->attributes()[0]));
        ((entity*) IFC4X2_types[1155])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC4X2_types[843]), ((entity*) IFC4X2_types[843])->attributes()[0]));
        ((entity*) IFC4X2_types[1156])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X2_types[2]));defs.push_back(((entity*) IFC4X2_types[239]));defs.push_back(((entity*) IFC4X2_types[241]));defs.push_back(((entity*) IFC4X2_types[676]));defs.push_back(((entity*) IFC4X2_types[680]));defs.push_back(((entity*) IFC4X2_types[760]));defs.push_back(((entity*) IFC4X2_types[1213]));defs.push_back(((entity*) IFC4X2_types[1215]));
        ((entity*) IFC4X2_types[224])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[6]));defs.push_back(((entity*) IFC4X2_types[224]));defs.push_back(((entity*) IFC4X2_types[494]));defs.push_back(((entity*) IFC4X2_types[744]));defs.push_back(((entity*) IFC4X2_types[746]));defs.push_back(((entity*) IFC4X2_types[889]));
        ((entity*) IFC4X2_types[646])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[9]));defs.push_back(((entity*) IFC4X2_types[26]));defs.push_back(((entity*) IFC4X2_types[225]));defs.push_back(((entity*) IFC4X2_types[448]));defs.push_back(((entity*) IFC4X2_types[782]));defs.push_back(((entity*) IFC4X2_types[924]));defs.push_back(((entity*) IFC4X2_types[1158]));
        ((entity*) IFC4X2_types[303])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[10]));defs.push_back(((entity*) IFC4X2_types[27]));defs.push_back(((entity*) IFC4X2_types[226]));defs.push_back(((entity*) IFC4X2_types[449]));defs.push_back(((entity*) IFC4X2_types[783]));defs.push_back(((entity*) IFC4X2_types[925]));defs.push_back(((entity*) IFC4X2_types[1159]));
        ((entity*) IFC4X2_types[304])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[14]));defs.push_back(((entity*) IFC4X2_types[418]));
        ((entity*) IFC4X2_types[583])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[15]));
        ((entity*) IFC4X2_types[14])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[16]));
        ((entity*) IFC4X2_types[417])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(13);
        defs.push_back(((entity*) IFC4X2_types[17]));defs.push_back(((entity*) IFC4X2_types[61]));defs.push_back(((entity*) IFC4X2_types[181]));defs.push_back(((entity*) IFC4X2_types[348]));defs.push_back(((entity*) IFC4X2_types[439]));defs.push_back(((entity*) IFC4X2_types[539]));defs.push_back(((entity*) IFC4X2_types[553]));defs.push_back(((entity*) IFC4X2_types[615]));defs.push_back(((entity*) IFC4X2_types[668]));defs.push_back(((entity*) IFC4X2_types[910]));defs.push_back(((entity*) IFC4X2_types[964]));defs.push_back(((entity*) IFC4X2_types[982]));defs.push_back(((entity*) IFC4X2_types[1198]));
        ((entity*) IFC4X2_types[460])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X2_types[18]));defs.push_back(((entity*) IFC4X2_types[274]));defs.push_back(((entity*) IFC4X2_types[355]));defs.push_back(((entity*) IFC4X2_types[368]));defs.push_back(((entity*) IFC4X2_types[451]));defs.push_back(((entity*) IFC4X2_types[781]));defs.push_back(((entity*) IFC4X2_types[1064]));defs.push_back(((entity*) IFC4X2_types[1169]));
        ((entity*) IFC4X2_types[443])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X2_types[19]));defs.push_back(((entity*) IFC4X2_types[275]));defs.push_back(((entity*) IFC4X2_types[356]));defs.push_back(((entity*) IFC4X2_types[369]));defs.push_back(((entity*) IFC4X2_types[452]));defs.push_back(((entity*) IFC4X2_types[785]));defs.push_back(((entity*) IFC4X2_types[1065]));defs.push_back(((entity*) IFC4X2_types[1170]));
        ((entity*) IFC4X2_types[444])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(13);
        defs.push_back(((entity*) IFC4X2_types[21]));defs.push_back(((entity*) IFC4X2_types[62]));defs.push_back(((entity*) IFC4X2_types[182]));defs.push_back(((entity*) IFC4X2_types[349]));defs.push_back(((entity*) IFC4X2_types[440]));defs.push_back(((entity*) IFC4X2_types[540]));defs.push_back(((entity*) IFC4X2_types[554]));defs.push_back(((entity*) IFC4X2_types[616]));defs.push_back(((entity*) IFC4X2_types[669]));defs.push_back(((entity*) IFC4X2_types[911]));defs.push_back(((entity*) IFC4X2_types[965]));defs.push_back(((entity*) IFC4X2_types[983]));defs.push_back(((entity*) IFC4X2_types[1199]));
        ((entity*) IFC4X2_types[461])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC4X2_types[23]));defs.push_back(((entity*) IFC4X2_types[81]));defs.push_back(((entity*) IFC4X2_types[122]));defs.push_back(((entity*) IFC4X2_types[152]));defs.push_back(((entity*) IFC4X2_types[169]));defs.push_back(((entity*) IFC4X2_types[196]));defs.push_back(((entity*) IFC4X2_types[230]));defs.push_back(((entity*) IFC4X2_types[233]));defs.push_back(((entity*) IFC4X2_types[361]));defs.push_back(((entity*) IFC4X2_types[364]));defs.push_back(((entity*) IFC4X2_types[387]));defs.push_back(((entity*) IFC4X2_types[390]));defs.push_back(((entity*) IFC4X2_types[393]));defs.push_back(((entity*) IFC4X2_types[497]));defs.push_back(((entity*) IFC4X2_types[502]));defs.push_back(((entity*) IFC4X2_types[638]));defs.push_back(((entity*) IFC4X2_types[952]));defs.push_back(((entity*) IFC4X2_types[1133]));defs.push_back(((entity*) IFC4X2_types[1150]));defs.push_back(((entity*) IFC4X2_types[1161]));
        ((entity*) IFC4X2_types[384])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC4X2_types[24]));defs.push_back(((entity*) IFC4X2_types[82]));defs.push_back(((entity*) IFC4X2_types[123]));defs.push_back(((entity*) IFC4X2_types[153]));defs.push_back(((entity*) IFC4X2_types[170]));defs.push_back(((entity*) IFC4X2_types[197]));defs.push_back(((entity*) IFC4X2_types[231]));defs.push_back(((entity*) IFC4X2_types[234]));defs.push_back(((entity*) IFC4X2_types[362]));defs.push_back(((entity*) IFC4X2_types[365]));defs.push_back(((entity*) IFC4X2_types[388]));defs.push_back(((entity*) IFC4X2_types[391]));defs.push_back(((entity*) IFC4X2_types[394]));defs.push_back(((entity*) IFC4X2_types[498]));defs.push_back(((entity*) IFC4X2_types[503]));defs.push_back(((entity*) IFC4X2_types[639]));defs.push_back(((entity*) IFC4X2_types[953]));defs.push_back(((entity*) IFC4X2_types[1134]));defs.push_back(((entity*) IFC4X2_types[1151]));defs.push_back(((entity*) IFC4X2_types[1162]));
        ((entity*) IFC4X2_types[385])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[29]));
        ((entity*) IFC4X2_types[567])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(30);
        defs.push_back(((entity*) IFC4X2_types[30]));defs.push_back(((entity*) IFC4X2_types[32]));defs.push_back(((entity*) IFC4X2_types[36]));defs.push_back(((entity*) IFC4X2_types[45]));defs.push_back(((entity*) IFC4X2_types[88]));defs.push_back(((entity*) IFC4X2_types[97]));defs.push_back(((entity*) IFC4X2_types[142]));defs.push_back(((entity*) IFC4X2_types[145]));defs.push_back(((entity*) IFC4X2_types[190]));defs.push_back(((entity*) IFC4X2_types[251]));defs.push_back(((entity*) IFC4X2_types[260]));defs.push_back(((entity*) IFC4X2_types[293]));defs.push_back(((entity*) IFC4X2_types[298]));defs.push_back(((entity*) IFC4X2_types[414]));defs.push_back(((entity*) IFC4X2_types[433]));defs.push_back(((entity*) IFC4X2_types[434]));defs.push_back(((entity*) IFC4X2_types[485]));defs.push_back(((entity*) IFC4X2_types[495]));defs.push_back(((entity*) IFC4X2_types[557]));defs.push_back(((entity*) IFC4X2_types[665]));defs.push_back(((entity*) IFC4X2_types[700]));defs.push_back(((entity*) IFC4X2_types[702]));defs.push_back(((entity*) IFC4X2_types[710]));defs.push_back(((entity*) IFC4X2_types[918]));defs.push_back(((entity*) IFC4X2_types[936]));defs.push_back(((entity*) IFC4X2_types[956]));defs.push_back(((entity*) IFC4X2_types[1042]));defs.push_back(((entity*) IFC4X2_types[1096]));defs.push_back(((entity*) IFC4X2_types[1102]));defs.push_back(((entity*) IFC4X2_types[1173]));
        ((entity*) IFC4X2_types[483])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[31]));defs.push_back(((entity*) IFC4X2_types[37]));
        ((entity*) IFC4X2_types[32])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[33]));defs.push_back(((entity*) IFC4X2_types[34]));defs.push_back(((entity*) IFC4X2_types[35]));
        ((entity*) IFC4X2_types[37])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[38]));defs.push_back(((entity*) IFC4X2_types[104]));defs.push_back(((entity*) IFC4X2_types[188]));defs.push_back(((entity*) IFC4X2_types[267]));defs.push_back(((entity*) IFC4X2_types[509]));defs.push_back(((entity*) IFC4X2_types[716]));defs.push_back(((entity*) IFC4X2_types[1146]));
        ((entity*) IFC4X2_types[95])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X2_types[44]));defs.push_back(((entity*) IFC4X2_types[372]));defs.push_back(((entity*) IFC4X2_types[718]));defs.push_back(((entity*) IFC4X2_types[719]));defs.push_back(((entity*) IFC4X2_types[787]));defs.push_back(((entity*) IFC4X2_types[969]));defs.push_back(((entity*) IFC4X2_types[993]));defs.push_back(((entity*) IFC4X2_types[1005]));
        ((entity*) IFC4X2_types[746])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4X2_types[50]));defs.push_back(((entity*) IFC4X2_types[255]));defs.push_back(((entity*) IFC4X2_types[315]));defs.push_back(((entity*) IFC4X2_types[407]));defs.push_back(((entity*) IFC4X2_types[607]));defs.push_back(((entity*) IFC4X2_types[664]));defs.push_back(((entity*) IFC4X2_types[766]));defs.push_back(((entity*) IFC4X2_types[890]));defs.push_back(((entity*) IFC4X2_types[891]));
        ((entity*) IFC4X2_types[892])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[51]));defs.push_back(((entity*) IFC4X2_types[52]));defs.push_back(((entity*) IFC4X2_types[191]));defs.push_back(((entity*) IFC4X2_types[286]));defs.push_back(((entity*) IFC4X2_types[672]));
        ((entity*) IFC4X2_types[751])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[53]));
        ((entity*) IFC4X2_types[51])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[59]));defs.push_back(((entity*) IFC4X2_types[522]));defs.push_back(((entity*) IFC4X2_types[1010]));defs.push_back(((entity*) IFC4X2_types[1026]));defs.push_back(((entity*) IFC4X2_types[1067]));
        ((entity*) IFC4X2_types[494])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(11);
        defs.push_back(((entity*) IFC4X2_types[60]));defs.push_back(((entity*) IFC4X2_types[254]));defs.push_back(((entity*) IFC4X2_types[160]));defs.push_back(((entity*) IFC4X2_types[383]));defs.push_back(((entity*) IFC4X2_types[527]));defs.push_back(((entity*) IFC4X2_types[577]));defs.push_back(((entity*) IFC4X2_types[813]));defs.push_back(((entity*) IFC4X2_types[1149]));defs.push_back(((entity*) IFC4X2_types[1143]));defs.push_back(((entity*) IFC4X2_types[1167]));defs.push_back(((entity*) IFC4X2_types[1222]));
        ((entity*) IFC4X2_types[672])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[64]));defs.push_back(((entity*) IFC4X2_types[66]));defs.push_back(((entity*) IFC4X2_types[67]));
        ((entity*) IFC4X2_types[700])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[106]));
        ((entity*) IFC4X2_types[104])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[107]));defs.push_back(((entity*) IFC4X2_types[261]));defs.push_back(((entity*) IFC4X2_types[262]));defs.push_back(((entity*) IFC4X2_types[815]));
        ((entity*) IFC4X2_types[96])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[109]));
        ((entity*) IFC4X2_types[107])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(22);
        defs.push_back(((entity*) IFC4X2_types[68]));defs.push_back(((entity*) IFC4X2_types[72]));defs.push_back(((entity*) IFC4X2_types[115]));defs.push_back(((entity*) IFC4X2_types[155]));defs.push_back(((entity*) IFC4X2_types[177]));defs.push_back(((entity*) IFC4X2_types[245]));defs.push_back(((entity*) IFC4X2_types[256]));defs.push_back(((entity*) IFC4X2_types[282]));defs.push_back(((entity*) IFC4X2_types[319]));defs.push_back(((entity*) IFC4X2_types[467]));defs.push_back(((entity*) IFC4X2_types[618]));defs.push_back(((entity*) IFC4X2_types[706]));defs.push_back(((entity*) IFC4X2_types[799]));defs.push_back(((entity*) IFC4X2_types[802]));defs.push_back(((entity*) IFC4X2_types[803]));defs.push_back(((entity*) IFC4X2_types[901]));defs.push_back(((entity*) IFC4X2_types[928]));defs.push_back(((entity*) IFC4X2_types[946]));defs.push_back(((entity*) IFC4X2_types[985]));defs.push_back(((entity*) IFC4X2_types[986]));defs.push_back(((entity*) IFC4X2_types[1190]));defs.push_back(((entity*) IFC4X2_types[1201]));
        ((entity*) IFC4X2_types[111])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[69]));
        ((entity*) IFC4X2_types[68])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(22);
        defs.push_back(((entity*) IFC4X2_types[70]));defs.push_back(((entity*) IFC4X2_types[73]));defs.push_back(((entity*) IFC4X2_types[116]));defs.push_back(((entity*) IFC4X2_types[156]));defs.push_back(((entity*) IFC4X2_types[179]));defs.push_back(((entity*) IFC4X2_types[246]));defs.push_back(((entity*) IFC4X2_types[257]));defs.push_back(((entity*) IFC4X2_types[283]));defs.push_back(((entity*) IFC4X2_types[328]));defs.push_back(((entity*) IFC4X2_types[468]));defs.push_back(((entity*) IFC4X2_types[620]));defs.push_back(((entity*) IFC4X2_types[708]));defs.push_back(((entity*) IFC4X2_types[800]));defs.push_back(((entity*) IFC4X2_types[804]));defs.push_back(((entity*) IFC4X2_types[806]));defs.push_back(((entity*) IFC4X2_types[902]));defs.push_back(((entity*) IFC4X2_types[929]));defs.push_back(((entity*) IFC4X2_types[949]));defs.push_back(((entity*) IFC4X2_types[987]));defs.push_back(((entity*) IFC4X2_types[989]));defs.push_back(((entity*) IFC4X2_types[1193]));defs.push_back(((entity*) IFC4X2_types[1210]));
        ((entity*) IFC4X2_types[118])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[79]));defs.push_back(((entity*) IFC4X2_types[507]));defs.push_back(((entity*) IFC4X2_types[699]));
        ((entity*) IFC4X2_types[1059])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[80]));defs.push_back(((entity*) IFC4X2_types[814]));defs.push_back(((entity*) IFC4X2_types[898]));defs.push_back(((entity*) IFC4X2_types[899]));defs.push_back(((entity*) IFC4X2_types[980]));
        ((entity*) IFC4X2_types[251])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[85]));
        ((entity*) IFC4X2_types[88])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[90]));
        ((entity*) IFC4X2_types[189])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[91]));defs.push_back(((entity*) IFC4X2_types[92]));defs.push_back(((entity*) IFC4X2_types[93]));
        ((entity*) IFC4X2_types[89])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[94]));
        ((entity*) IFC4X2_types[93])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[95]));defs.push_back(((entity*) IFC4X2_types[199]));defs.push_back(((entity*) IFC4X2_types[563]));defs.push_back(((entity*) IFC4X2_types[655]));defs.push_back(((entity*) IFC4X2_types[675]));defs.push_back(((entity*) IFC4X2_types[1043]));
        ((entity*) IFC4X2_types[260])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[96]));defs.push_back(((entity*) IFC4X2_types[373]));defs.push_back(((entity*) IFC4X2_types[1063]));
        ((entity*) IFC4X2_types[1042])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[99]));defs.push_back(((entity*) IFC4X2_types[714]));
        ((entity*) IFC4X2_types[495])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[100]));defs.push_back(((entity*) IFC4X2_types[110]));
        ((entity*) IFC4X2_types[420])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[101]));defs.push_back(((entity*) IFC4X2_types[119]));
        ((entity*) IFC4X2_types[421])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(10);
        defs.push_back(((entity*) IFC4X2_types[111]));defs.push_back(((entity*) IFC4X2_types[162]));defs.push_back(((entity*) IFC4X2_types[305]));defs.push_back(((entity*) IFC4X2_types[374]));defs.push_back(((entity*) IFC4X2_types[377]));defs.push_back(((entity*) IFC4X2_types[429]));defs.push_back(((entity*) IFC4X2_types[472]));defs.push_back(((entity*) IFC4X2_types[477]));defs.push_back(((entity*) IFC4X2_types[1140]));defs.push_back(((entity*) IFC4X2_types[1184]));
        ((entity*) IFC4X2_types[372])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[112]));defs.push_back(((entity*) IFC4X2_types[295]));defs.push_back(((entity*) IFC4X2_types[426]));defs.push_back(((entity*) IFC4X2_types[612]));defs.push_back(((entity*) IFC4X2_types[830]));defs.push_back(((entity*) IFC4X2_types[1178]));defs.push_back(((entity*) IFC4X2_types[1181]));
        ((entity*) IFC4X2_types[377])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[113]));defs.push_back(((entity*) IFC4X2_types[296]));defs.push_back(((entity*) IFC4X2_types[427]));defs.push_back(((entity*) IFC4X2_types[613]));defs.push_back(((entity*) IFC4X2_types[831]));defs.push_back(((entity*) IFC4X2_types[1179]));defs.push_back(((entity*) IFC4X2_types[1182]));
        ((entity*) IFC4X2_types[378])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4X2_types[118]));defs.push_back(((entity*) IFC4X2_types[163]));defs.push_back(((entity*) IFC4X2_types[306]));defs.push_back(((entity*) IFC4X2_types[375]));defs.push_back(((entity*) IFC4X2_types[378]));defs.push_back(((entity*) IFC4X2_types[473]));defs.push_back(((entity*) IFC4X2_types[478]));defs.push_back(((entity*) IFC4X2_types[1141]));
        ((entity*) IFC4X2_types[381])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[120]));defs.push_back(((entity*) IFC4X2_types[311]));defs.push_back(((entity*) IFC4X2_types[995]));defs.push_back(((entity*) IFC4X2_types[1221]));
        ((entity*) IFC4X2_types[1067])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[125]));defs.push_back(((entity*) IFC4X2_types[131]));defs.push_back(((entity*) IFC4X2_types[334]));defs.push_back(((entity*) IFC4X2_types[529]));defs.push_back(((entity*) IFC4X2_types[693]));
        ((entity*) IFC4X2_types[446])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[126]));defs.push_back(((entity*) IFC4X2_types[132]));defs.push_back(((entity*) IFC4X2_types[335]));defs.push_back(((entity*) IFC4X2_types[530]));defs.push_back(((entity*) IFC4X2_types[694]));
        ((entity*) IFC4X2_types[447])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[128]));defs.push_back(((entity*) IFC4X2_types[134]));defs.push_back(((entity*) IFC4X2_types[337]));defs.push_back(((entity*) IFC4X2_types[696]));
        ((entity*) IFC4X2_types[456])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[129]));defs.push_back(((entity*) IFC4X2_types[135]));defs.push_back(((entity*) IFC4X2_types[338]));defs.push_back(((entity*) IFC4X2_types[697]));
        ((entity*) IFC4X2_types[457])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[137]));defs.push_back(((entity*) IFC4X2_types[689]));
        ((entity*) IFC4X2_types[282])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[138]));defs.push_back(((entity*) IFC4X2_types[691]));
        ((entity*) IFC4X2_types[283])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[141]));defs.push_back(((entity*) IFC4X2_types[711]));defs.push_back(((entity*) IFC4X2_types[712]));
        ((entity*) IFC4X2_types[710])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[143]));defs.push_back(((entity*) IFC4X2_types[144]));
        ((entity*) IFC4X2_types[142])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[146]));defs.push_back(((entity*) IFC4X2_types[148]));
        ((entity*) IFC4X2_types[145])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[147]));
        ((entity*) IFC4X2_types[146])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[149]));
        ((entity*) IFC4X2_types[148])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[150]));
        ((entity*) IFC4X2_types[52])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[158]));defs.push_back(((entity*) IFC4X2_types[382]));
        ((entity*) IFC4X2_types[199])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[159]));
        ((entity*) IFC4X2_types[160])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[161]));defs.push_back(((entity*) IFC4X2_types[571]));defs.push_back(((entity*) IFC4X2_types[1137]));
        ((entity*) IFC4X2_types[267])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[164]));defs.push_back(((entity*) IFC4X2_types[314]));defs.push_back(((entity*) IFC4X2_types[546]));
        ((entity*) IFC4X2_types[402])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[165]));defs.push_back(((entity*) IFC4X2_types[316]));defs.push_back(((entity*) IFC4X2_types[403]));defs.push_back(((entity*) IFC4X2_types[404]));defs.push_back(((entity*) IFC4X2_types[405]));defs.push_back(((entity*) IFC4X2_types[547]));
        ((entity*) IFC4X2_types[406])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[168]));defs.push_back(((entity*) IFC4X2_types[662]));
        ((entity*) IFC4X2_types[200])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[174]));
        ((entity*) IFC4X2_types[176])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(17);
        defs.push_back(((entity*) IFC4X2_types[175]));defs.push_back(((entity*) IFC4X2_types[176]));defs.push_back(((entity*) IFC4X2_types[269]));defs.push_back(((entity*) IFC4X2_types[270]));defs.push_back(((entity*) IFC4X2_types[271]));defs.push_back(((entity*) IFC4X2_types[508]));defs.push_back(((entity*) IFC4X2_types[728]));defs.push_back(((entity*) IFC4X2_types[1054]));defs.push_back(((entity*) IFC4X2_types[1055]));defs.push_back(((entity*) IFC4X2_types[1057]));defs.push_back(((entity*) IFC4X2_types[1058]));defs.push_back(((entity*) IFC4X2_types[1059]));defs.push_back(((entity*) IFC4X2_types[1107]));defs.push_back(((entity*) IFC4X2_types[1108]));defs.push_back(((entity*) IFC4X2_types[1110]));defs.push_back(((entity*) IFC4X2_types[1113]));defs.push_back(((entity*) IFC4X2_types[1114]));
        ((entity*) IFC4X2_types[734])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[178]));
        ((entity*) IFC4X2_types[177])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[185]));defs.push_back(((entity*) IFC4X2_types[937]));
        ((entity*) IFC4X2_types[762])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[186]));defs.push_back(((entity*) IFC4X2_types[938]));
        ((entity*) IFC4X2_types[779])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[189]));
        ((entity*) IFC4X2_types[188])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[193]));defs.push_back(((entity*) IFC4X2_types[423]));defs.push_back(((entity*) IFC4X2_types[788]));
        ((entity*) IFC4X2_types[454])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[194]));defs.push_back(((entity*) IFC4X2_types[424]));defs.push_back(((entity*) IFC4X2_types[789]));
        ((entity*) IFC4X2_types[455])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[200]));defs.push_back(((entity*) IFC4X2_types[345]));defs.push_back(((entity*) IFC4X2_types[413]));defs.push_back(((entity*) IFC4X2_types[415]));defs.push_back(((entity*) IFC4X2_types[576]));defs.push_back(((entity*) IFC4X2_types[674]));defs.push_back(((entity*) IFC4X2_types[1175]));
        ((entity*) IFC4X2_types[1129])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[201]));defs.push_back(((entity*) IFC4X2_types[204]));defs.push_back(((entity*) IFC4X2_types[205]));defs.push_back(((entity*) IFC4X2_types[207]));
        ((entity*) IFC4X2_types[202])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[203]));
        ((entity*) IFC4X2_types[204])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[210]));defs.push_back(((entity*) IFC4X2_types[213]));defs.push_back(((entity*) IFC4X2_types[216]));defs.push_back(((entity*) IFC4X2_types[248]));defs.push_back(((entity*) IFC4X2_types[535]));defs.push_back(((entity*) IFC4X2_types[1038]));
        ((entity*) IFC4X2_types[219])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[211]));defs.push_back(((entity*) IFC4X2_types[214]));defs.push_back(((entity*) IFC4X2_types[217]));defs.push_back(((entity*) IFC4X2_types[249]));defs.push_back(((entity*) IFC4X2_types[536]));defs.push_back(((entity*) IFC4X2_types[1039]));
        ((entity*) IFC4X2_types[220])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[219]));
        ((entity*) IFC4X2_types[889])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[220]));
        ((entity*) IFC4X2_types[1156])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[221]));defs.push_back(((entity*) IFC4X2_types[646]));defs.push_back(((entity*) IFC4X2_types[1153]));
        ((entity*) IFC4X2_types[647])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[223]));defs.push_back(((entity*) IFC4X2_types[228]));defs.push_back(((entity*) IFC4X2_types[943]));
        ((entity*) IFC4X2_types[641])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[229]));
        ((entity*) IFC4X2_types[228])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[243]));
        ((entity*) IFC4X2_types[47])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[253]));defs.push_back(((entity*) IFC4X2_types[583]));defs.push_back(((entity*) IFC4X2_types[916]));defs.push_back(((entity*) IFC4X2_types[1060]));defs.push_back(((entity*) IFC4X2_types[1061]));
        ((entity*) IFC4X2_types[956])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[268]));defs.push_back(((entity*) IFC4X2_types[432]));defs.push_back(((entity*) IFC4X2_types[1052]));defs.push_back(((entity*) IFC4X2_types[1105]));
        ((entity*) IFC4X2_types[737])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[273]));defs.push_back(((entity*) IFC4X2_types[704]));defs.push_back(((entity*) IFC4X2_types[981]));defs.push_back(((entity*) IFC4X2_types[1131]));
        ((entity*) IFC4X2_types[373])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4X2_types[299]));defs.push_back(((entity*) IFC4X2_types[384]));defs.push_back(((entity*) IFC4X2_types[443]));defs.push_back(((entity*) IFC4X2_types[446]));defs.push_back(((entity*) IFC4X2_types[454]));defs.push_back(((entity*) IFC4X2_types[456]));defs.push_back(((entity*) IFC4X2_types[458]));defs.push_back(((entity*) IFC4X2_types[460]));defs.push_back(((entity*) IFC4X2_types[462]));
        ((entity*) IFC4X2_types[307])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4X2_types[300]));defs.push_back(((entity*) IFC4X2_types[385]));defs.push_back(((entity*) IFC4X2_types[444]));defs.push_back(((entity*) IFC4X2_types[447]));defs.push_back(((entity*) IFC4X2_types[455]));defs.push_back(((entity*) IFC4X2_types[457]));defs.push_back(((entity*) IFC4X2_types[459]));defs.push_back(((entity*) IFC4X2_types[461]));defs.push_back(((entity*) IFC4X2_types[463]));
        ((entity*) IFC4X2_types[308])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[302]));
        ((entity*) IFC4X2_types[311])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[303]));defs.push_back(((entity*) IFC4X2_types[307]));
        ((entity*) IFC4X2_types[305])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[304]));defs.push_back(((entity*) IFC4X2_types[308]));
        ((entity*) IFC4X2_types[306])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[309]));
        ((entity*) IFC4X2_types[718])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[320]));defs.push_back(((entity*) IFC4X2_types[323]));defs.push_back(((entity*) IFC4X2_types[679]));defs.push_back(((entity*) IFC4X2_types[824]));defs.push_back(((entity*) IFC4X2_types[1202]));defs.push_back(((entity*) IFC4X2_types[1205]));
        ((entity*) IFC4X2_types[730])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[324]));
        ((entity*) IFC4X2_types[319])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[325]));defs.push_back(((entity*) IFC4X2_types[381]));defs.push_back(((entity*) IFC4X2_types[970]));defs.push_back(((entity*) IFC4X2_types[1207]));
        ((entity*) IFC4X2_types[1155])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[332]));
        ((entity*) IFC4X2_types[726])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[333]));
        ((entity*) IFC4X2_types[727])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[340]));defs.push_back(((entity*) IFC4X2_types[436]));defs.push_back(((entity*) IFC4X2_types[517]));
        ((entity*) IFC4X2_types[462])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[341]));defs.push_back(((entity*) IFC4X2_types[437]));defs.push_back(((entity*) IFC4X2_types[518]));
        ((entity*) IFC4X2_types[463])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[346]));defs.push_back(((entity*) IFC4X2_types[666]));defs.push_back(((entity*) IFC4X2_types[1041]));
        ((entity*) IFC4X2_types[345])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[347]));defs.push_back(((entity*) IFC4X2_types[717]));defs.push_back(((entity*) IFC4X2_types[1176]));
        ((entity*) IFC4X2_types[576])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[358]));defs.push_back(((entity*) IFC4X2_types[1074]));
        ((entity*) IFC4X2_types[458])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[359]));defs.push_back(((entity*) IFC4X2_types[1075]));
        ((entity*) IFC4X2_types[459])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[380]));
        ((entity*) IFC4X2_types[794])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[396]));defs.push_back(((entity*) IFC4X2_types[741]));defs.push_back(((entity*) IFC4X2_types[1077]));
        ((entity*) IFC4X2_types[744])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[397]));defs.push_back(((entity*) IFC4X2_types[538]));defs.push_back(((entity*) IFC4X2_types[895]));defs.push_back(((entity*) IFC4X2_types[1079]));defs.push_back(((entity*) IFC4X2_types[1220]));
        ((entity*) IFC4X2_types[913])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[399]));defs.push_back(((entity*) IFC4X2_types[742]));defs.push_back(((entity*) IFC4X2_types[1081]));
        ((entity*) IFC4X2_types[1154])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[401]));defs.push_back(((entity*) IFC4X2_types[729]));defs.push_back(((entity*) IFC4X2_types[762]));defs.push_back(((entity*) IFC4X2_types[768]));
        ((entity*) IFC4X2_types[763])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[408]));
        ((entity*) IFC4X2_types[410])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[410]));defs.push_back(((entity*) IFC4X2_types[971]));defs.push_back(((entity*) IFC4X2_types[973]));
        ((entity*) IFC4X2_types[969])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[411]));defs.push_back(((entity*) IFC4X2_types[442]));defs.push_back(((entity*) IFC4X2_types[896]));defs.push_back(((entity*) IFC4X2_types[1044]));
        ((entity*) IFC4X2_types[1060])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[412]));
        ((entity*) IFC4X2_types[411])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[416]));
        ((entity*) IFC4X2_types[415])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[417]));
        ((entity*) IFC4X2_types[413])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[419]));
        ((entity*) IFC4X2_types[418])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[420]));defs.push_back(((entity*) IFC4X2_types[421]));defs.push_back(((entity*) IFC4X2_types[942]));defs.push_back(((entity*) IFC4X2_types[962]));
        ((entity*) IFC4X2_types[971])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[422]));defs.push_back(((entity*) IFC4X2_types[951]));
        ((entity*) IFC4X2_types[997])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[430]));defs.push_back(((entity*) IFC4X2_types[431]));defs.push_back(((entity*) IFC4X2_types[1045]));
        ((entity*) IFC4X2_types[429])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[474]));defs.push_back(((entity*) IFC4X2_types[1068]));
        ((entity*) IFC4X2_types[472])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[475]));defs.push_back(((entity*) IFC4X2_types[1069]));
        ((entity*) IFC4X2_types[473])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[480]));
        ((entity*) IFC4X2_types[485])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[482]));
        ((entity*) IFC4X2_types[886])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[483]));defs.push_back(((entity*) IFC4X2_types[585]));defs.push_back(((entity*) IFC4X2_types[1035]));defs.push_back(((entity*) IFC4X2_types[1129]));
        ((entity*) IFC4X2_types[887])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[484]));
        ((entity*) IFC4X2_types[482])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[489]));defs.push_back(((entity*) IFC4X2_types[567]));defs.push_back(((entity*) IFC4X2_types[819]));
        ((entity*) IFC4X2_types[719])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[491]));defs.push_back(((entity*) IFC4X2_types[566]));defs.push_back(((entity*) IFC4X2_types[573]));
        ((entity*) IFC4X2_types[650])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[510]));defs.push_back(((entity*) IFC4X2_types[1095]));
        ((entity*) IFC4X2_types[1096])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[511]));
        ((entity*) IFC4X2_types[510])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[512]));defs.push_back(((entity*) IFC4X2_types[1111]));defs.push_back(((entity*) IFC4X2_types[1112]));
        ((entity*) IFC4X2_types[1110])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[513]));
        ((entity*) IFC4X2_types[512])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[521]));defs.push_back(((entity*) IFC4X2_types[914]));
        ((entity*) IFC4X2_types[1043])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[525]));defs.push_back(((entity*) IFC4X2_types[822]));
        ((entity*) IFC4X2_types[1125])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[558]));defs.push_back(((entity*) IFC4X2_types[559]));defs.push_back(((entity*) IFC4X2_types[560]));defs.push_back(((entity*) IFC4X2_types[561]));
        ((entity*) IFC4X2_types[557])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[562]));
        ((entity*) IFC4X2_types[561])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[584]));
        ((entity*) IFC4X2_types[236])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4X2_types[590]));defs.push_back(((entity*) IFC4X2_types[592]));defs.push_back(((entity*) IFC4X2_types[593]));defs.push_back(((entity*) IFC4X2_types[596]));defs.push_back(((entity*) IFC4X2_types[597]));defs.push_back(((entity*) IFC4X2_types[601]));defs.push_back(((entity*) IFC4X2_types[602]));
        ((entity*) IFC4X2_types[594])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[595]));defs.push_back(((entity*) IFC4X2_types[747]));
        ((entity*) IFC4X2_types[748])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[598]));defs.push_back(((entity*) IFC4X2_types[603]));
        ((entity*) IFC4X2_types[609])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[599]));
        ((entity*) IFC4X2_types[596])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[604]));
        ((entity*) IFC4X2_types[603])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[605]));
        ((entity*) IFC4X2_types[601])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[606]));defs.push_back(((entity*) IFC4X2_types[752]));
        ((entity*) IFC4X2_types[401])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[619]));
        ((entity*) IFC4X2_types[618])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[622]));defs.push_back(((entity*) IFC4X2_types[648]));
        ((entity*) IFC4X2_types[208])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[624]));
        ((entity*) IFC4X2_types[286])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[647]));defs.push_back(((entity*) IFC4X2_types[765]));defs.push_back(((entity*) IFC4X2_types[851]));
        ((entity*) IFC4X2_types[904])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[653]));
        ((entity*) IFC4X2_types[6])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[656]));defs.push_back(((entity*) IFC4X2_types[657]));defs.push_back(((entity*) IFC4X2_types[658]));
        ((entity*) IFC4X2_types[655])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[659]));defs.push_back(((entity*) IFC4X2_types[1186]));
        ((entity*) IFC4X2_types[431])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[661]));
        ((entity*) IFC4X2_types[659])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[667]));
        ((entity*) IFC4X2_types[90])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[685]));defs.push_back(((entity*) IFC4X2_types[688]));
        ((entity*) IFC4X2_types[687])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[701]));
        ((entity*) IFC4X2_types[702])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[707]));
        ((entity*) IFC4X2_types[706])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[715]));defs.push_back(((entity*) IFC4X2_types[1144]));
        ((entity*) IFC4X2_types[1095])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[724]));defs.push_back(((entity*) IFC4X2_types[1083]));
        ((entity*) IFC4X2_types[12])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[726]));defs.push_back(((entity*) IFC4X2_types[727]));defs.push_back(((entity*) IFC4X2_types[731]));
        ((entity*) IFC4X2_types[728])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[730]));defs.push_back(((entity*) IFC4X2_types[771]));defs.push_back(((entity*) IFC4X2_types[794]));
        ((entity*) IFC4X2_types[772])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[736]));
        ((entity*) IFC4X2_types[735])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[754]));defs.push_back(((entity*) IFC4X2_types[759]));
        ((entity*) IFC4X2_types[221])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[755]));
        ((entity*) IFC4X2_types[237])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[757]));
        ((entity*) IFC4X2_types[430])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[764]));defs.push_back(((entity*) IFC4X2_types[767]));defs.push_back(((entity*) IFC4X2_types[769]));defs.push_back(((entity*) IFC4X2_types[770]));defs.push_back(((entity*) IFC4X2_types[777]));defs.push_back(((entity*) IFC4X2_types[778]));
        ((entity*) IFC4X2_types[937])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[772]));defs.push_back(((entity*) IFC4X2_types[780]));
        ((entity*) IFC4X2_types[765])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[775]));defs.push_back(((entity*) IFC4X2_types[779]));
        ((entity*) IFC4X2_types[780])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[791]));defs.push_back(((entity*) IFC4X2_types[792]));defs.push_back(((entity*) IFC4X2_types[793]));defs.push_back(((entity*) IFC4X2_types[795]));defs.push_back(((entity*) IFC4X2_types[796]));defs.push_back(((entity*) IFC4X2_types[797]));
        ((entity*) IFC4X2_types[688])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[809]));
        ((entity*) IFC4X2_types[106])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[810]));
        ((entity*) IFC4X2_types[109])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[812]));defs.push_back(((entity*) IFC4X2_types[909]));
        ((entity*) IFC4X2_types[813])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[823]));defs.push_back(((entity*) IFC4X2_types[920]));defs.push_back(((entity*) IFC4X2_types[921]));
        ((entity*) IFC4X2_types[729])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[825]));defs.push_back(((entity*) IFC4X2_types[832]));defs.push_back(((entity*) IFC4X2_types[1086]));defs.push_back(((entity*) IFC4X2_types[1087]));defs.push_back(((entity*) IFC4X2_types[1090]));
        ((entity*) IFC4X2_types[830])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[828]));defs.push_back(((entity*) IFC4X2_types[833]));defs.push_back(((entity*) IFC4X2_types[1088]));defs.push_back(((entity*) IFC4X2_types[1091]));defs.push_back(((entity*) IFC4X2_types[1093]));
        ((entity*) IFC4X2_types[831])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[835]));defs.push_back(((entity*) IFC4X2_types[874]));defs.push_back(((entity*) IFC4X2_types[876]));defs.push_back(((entity*) IFC4X2_types[883]));
        ((entity*) IFC4X2_types[865])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[836]));defs.push_back(((entity*) IFC4X2_types[844]));defs.push_back(((entity*) IFC4X2_types[852]));defs.push_back(((entity*) IFC4X2_types[864]));defs.push_back(((entity*) IFC4X2_types[865]));defs.push_back(((entity*) IFC4X2_types[866]));
        ((entity*) IFC4X2_types[851])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[837]));defs.push_back(((entity*) IFC4X2_types[838]));defs.push_back(((entity*) IFC4X2_types[839]));defs.push_back(((entity*) IFC4X2_types[841]));defs.push_back(((entity*) IFC4X2_types[842]));defs.push_back(((entity*) IFC4X2_types[843]));
        ((entity*) IFC4X2_types[836])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[840]));
        ((entity*) IFC4X2_types[839])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4X2_types[845]));defs.push_back(((entity*) IFC4X2_types[846]));defs.push_back(((entity*) IFC4X2_types[847]));defs.push_back(((entity*) IFC4X2_types[848]));defs.push_back(((entity*) IFC4X2_types[849]));defs.push_back(((entity*) IFC4X2_types[850]));
        ((entity*) IFC4X2_types[844])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(16);
        defs.push_back(((entity*) IFC4X2_types[853]));defs.push_back(((entity*) IFC4X2_types[856]));defs.push_back(((entity*) IFC4X2_types[855]));defs.push_back(((entity*) IFC4X2_types[857]));defs.push_back(((entity*) IFC4X2_types[858]));defs.push_back(((entity*) IFC4X2_types[861]));defs.push_back(((entity*) IFC4X2_types[862]));defs.push_back(((entity*) IFC4X2_types[863]));defs.push_back(((entity*) IFC4X2_types[871]));defs.push_back(((entity*) IFC4X2_types[872]));defs.push_back(((entity*) IFC4X2_types[873]));defs.push_back(((entity*) IFC4X2_types[875]));defs.push_back(((entity*) IFC4X2_types[877]));defs.push_back(((entity*) IFC4X2_types[878]));defs.push_back(((entity*) IFC4X2_types[879]));defs.push_back(((entity*) IFC4X2_types[880]));
        ((entity*) IFC4X2_types[852])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[854]));defs.push_back(((entity*) IFC4X2_types[860]));
        ((entity*) IFC4X2_types[853])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[859]));
        ((entity*) IFC4X2_types[858])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4X2_types[867]));defs.push_back(((entity*) IFC4X2_types[868]));defs.push_back(((entity*) IFC4X2_types[869]));defs.push_back(((entity*) IFC4X2_types[870]));
        ((entity*) IFC4X2_types[866])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[881]));
        ((entity*) IFC4X2_types[880])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[882]));
        ((entity*) IFC4X2_types[881])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[884]));
        ((entity*) IFC4X2_types[190])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[897]));
        ((entity*) IFC4X2_types[896])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[917]));
        ((entity*) IFC4X2_types[916])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[932]));defs.push_back(((entity*) IFC4X2_types[1037]));
        ((entity*) IFC4X2_types[885])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[933]));defs.push_back(((entity*) IFC4X2_types[1130]));
        ((entity*) IFC4X2_types[932])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[947]));defs.push_back(((entity*) IFC4X2_types[948]));
        ((entity*) IFC4X2_types[946])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[967]));
        ((entity*) IFC4X2_types[972])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[972]));defs.push_back(((entity*) IFC4X2_types[974]));
        ((entity*) IFC4X2_types[970])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[992]));defs.push_back(((entity*) IFC4X2_types[1025]));
        ((entity*) IFC4X2_types[993])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[996]));defs.push_back(((entity*) IFC4X2_types[1020]));
        ((entity*) IFC4X2_types[1005])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[998]));defs.push_back(((entity*) IFC4X2_types[1022]));defs.push_back(((entity*) IFC4X2_types[1027]));
        ((entity*) IFC4X2_types[992])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[1000]));defs.push_back(((entity*) IFC4X2_types[1023]));defs.push_back(((entity*) IFC4X2_types[1029]));
        ((entity*) IFC4X2_types[996])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[1001]));defs.push_back(((entity*) IFC4X2_types[1030]));
        ((entity*) IFC4X2_types[1020])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1003]));
        ((entity*) IFC4X2_types[1001])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[1004]));defs.push_back(((entity*) IFC4X2_types[1024]));defs.push_back(((entity*) IFC4X2_types[1033]));
        ((entity*) IFC4X2_types[1025])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1006]));
        ((entity*) IFC4X2_types[998])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1008]));
        ((entity*) IFC4X2_types[1010])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[1009]));defs.push_back(((entity*) IFC4X2_types[1012]));
        ((entity*) IFC4X2_types[1007])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4X2_types[1011]));defs.push_back(((entity*) IFC4X2_types[1013]));defs.push_back(((entity*) IFC4X2_types[1014]));defs.push_back(((entity*) IFC4X2_types[1016]));defs.push_back(((entity*) IFC4X2_types[1019]));
        ((entity*) IFC4X2_types[1018])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1015]));
        ((entity*) IFC4X2_types[1014])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1017]));
        ((entity*) IFC4X2_types[1016])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[1018]));defs.push_back(((entity*) IFC4X2_types[1050]));
        ((entity*) IFC4X2_types[1012])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1021]));
        ((entity*) IFC4X2_types[1027])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1032]));
        ((entity*) IFC4X2_types[1030])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1036]));
        ((entity*) IFC4X2_types[1037])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[1047]));defs.push_back(((entity*) IFC4X2_types[1048]));
        ((entity*) IFC4X2_types[1063])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1056]));
        ((entity*) IFC4X2_types[1057])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1062]));
        ((entity*) IFC4X2_types[1061])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1080]));
        ((entity*) IFC4X2_types[1079])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1103]));
        ((entity*) IFC4X2_types[1102])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1106]));
        ((entity*) IFC4X2_types[731])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1145]));
        ((entity*) IFC4X2_types[1144])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4X2_types[1154]));defs.push_back(((entity*) IFC4X2_types[1155]));defs.push_back(((entity*) IFC4X2_types[1156]));
        ((entity*) IFC4X2_types[1153])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1177]));
        ((entity*) IFC4X2_types[1175])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[1191]));defs.push_back(((entity*) IFC4X2_types[1192]));
        ((entity*) IFC4X2_types[1190])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4X2_types[1206]));
        ((entity*) IFC4X2_types[1201])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4X2_types[1216]));defs.push_back(((entity*) IFC4X2_types[1218]));
        ((entity*) IFC4X2_types[1215])->set_subtypes(defs);
    }

    std::vector<const declaration*> declarations; declarations.reserve(1223);
    declarations.push_back(IFC4X2_types[0]);
    declarations.push_back(IFC4X2_types[1]);
    declarations.push_back(IFC4X2_types[2]);
    declarations.push_back(IFC4X2_types[3]);
    declarations.push_back(IFC4X2_types[4]);
    declarations.push_back(IFC4X2_types[5]);
    declarations.push_back(IFC4X2_types[6]);
    declarations.push_back(IFC4X2_types[7]);
    declarations.push_back(IFC4X2_types[8]);
    declarations.push_back(IFC4X2_types[9]);
    declarations.push_back(IFC4X2_types[10]);
    declarations.push_back(IFC4X2_types[11]);
    declarations.push_back(IFC4X2_types[12]);
    declarations.push_back(IFC4X2_types[13]);
    declarations.push_back(IFC4X2_types[14]);
    declarations.push_back(IFC4X2_types[15]);
    declarations.push_back(IFC4X2_types[16]);
    declarations.push_back(IFC4X2_types[17]);
    declarations.push_back(IFC4X2_types[18]);
    declarations.push_back(IFC4X2_types[19]);
    declarations.push_back(IFC4X2_types[20]);
    declarations.push_back(IFC4X2_types[21]);
    declarations.push_back(IFC4X2_types[22]);
    declarations.push_back(IFC4X2_types[23]);
    declarations.push_back(IFC4X2_types[24]);
    declarations.push_back(IFC4X2_types[25]);
    declarations.push_back(IFC4X2_types[26]);
    declarations.push_back(IFC4X2_types[27]);
    declarations.push_back(IFC4X2_types[28]);
    declarations.push_back(IFC4X2_types[29]);
    declarations.push_back(IFC4X2_types[30]);
    declarations.push_back(IFC4X2_types[31]);
    declarations.push_back(IFC4X2_types[32]);
    declarations.push_back(IFC4X2_types[33]);
    declarations.push_back(IFC4X2_types[34]);
    declarations.push_back(IFC4X2_types[35]);
    declarations.push_back(IFC4X2_types[36]);
    declarations.push_back(IFC4X2_types[37]);
    declarations.push_back(IFC4X2_types[38]);
    declarations.push_back(IFC4X2_types[39]);
    declarations.push_back(IFC4X2_types[40]);
    declarations.push_back(IFC4X2_types[41]);
    declarations.push_back(IFC4X2_types[42]);
    declarations.push_back(IFC4X2_types[43]);
    declarations.push_back(IFC4X2_types[44]);
    declarations.push_back(IFC4X2_types[45]);
    declarations.push_back(IFC4X2_types[46]);
    declarations.push_back(IFC4X2_types[47]);
    declarations.push_back(IFC4X2_types[48]);
    declarations.push_back(IFC4X2_types[49]);
    declarations.push_back(IFC4X2_types[50]);
    declarations.push_back(IFC4X2_types[51]);
    declarations.push_back(IFC4X2_types[52]);
    declarations.push_back(IFC4X2_types[53]);
    declarations.push_back(IFC4X2_types[54]);
    declarations.push_back(IFC4X2_types[55]);
    declarations.push_back(IFC4X2_types[56]);
    declarations.push_back(IFC4X2_types[57]);
    declarations.push_back(IFC4X2_types[58]);
    declarations.push_back(IFC4X2_types[59]);
    declarations.push_back(IFC4X2_types[60]);
    declarations.push_back(IFC4X2_types[61]);
    declarations.push_back(IFC4X2_types[62]);
    declarations.push_back(IFC4X2_types[63]);
    declarations.push_back(IFC4X2_types[64]);
    declarations.push_back(IFC4X2_types[65]);
    declarations.push_back(IFC4X2_types[66]);
    declarations.push_back(IFC4X2_types[67]);
    declarations.push_back(IFC4X2_types[68]);
    declarations.push_back(IFC4X2_types[69]);
    declarations.push_back(IFC4X2_types[70]);
    declarations.push_back(IFC4X2_types[71]);
    declarations.push_back(IFC4X2_types[72]);
    declarations.push_back(IFC4X2_types[73]);
    declarations.push_back(IFC4X2_types[74]);
    declarations.push_back(IFC4X2_types[75]);
    declarations.push_back(IFC4X2_types[76]);
    declarations.push_back(IFC4X2_types[77]);
    declarations.push_back(IFC4X2_types[78]);
    declarations.push_back(IFC4X2_types[79]);
    declarations.push_back(IFC4X2_types[80]);
    declarations.push_back(IFC4X2_types[81]);
    declarations.push_back(IFC4X2_types[82]);
    declarations.push_back(IFC4X2_types[83]);
    declarations.push_back(IFC4X2_types[84]);
    declarations.push_back(IFC4X2_types[85]);
    declarations.push_back(IFC4X2_types[86]);
    declarations.push_back(IFC4X2_types[87]);
    declarations.push_back(IFC4X2_types[88]);
    declarations.push_back(IFC4X2_types[89]);
    declarations.push_back(IFC4X2_types[90]);
    declarations.push_back(IFC4X2_types[91]);
    declarations.push_back(IFC4X2_types[92]);
    declarations.push_back(IFC4X2_types[93]);
    declarations.push_back(IFC4X2_types[94]);
    declarations.push_back(IFC4X2_types[95]);
    declarations.push_back(IFC4X2_types[96]);
    declarations.push_back(IFC4X2_types[97]);
    declarations.push_back(IFC4X2_types[98]);
    declarations.push_back(IFC4X2_types[99]);
    declarations.push_back(IFC4X2_types[100]);
    declarations.push_back(IFC4X2_types[101]);
    declarations.push_back(IFC4X2_types[102]);
    declarations.push_back(IFC4X2_types[103]);
    declarations.push_back(IFC4X2_types[104]);
    declarations.push_back(IFC4X2_types[105]);
    declarations.push_back(IFC4X2_types[106]);
    declarations.push_back(IFC4X2_types[107]);
    declarations.push_back(IFC4X2_types[108]);
    declarations.push_back(IFC4X2_types[109]);
    declarations.push_back(IFC4X2_types[110]);
    declarations.push_back(IFC4X2_types[111]);
    declarations.push_back(IFC4X2_types[112]);
    declarations.push_back(IFC4X2_types[113]);
    declarations.push_back(IFC4X2_types[114]);
    declarations.push_back(IFC4X2_types[115]);
    declarations.push_back(IFC4X2_types[116]);
    declarations.push_back(IFC4X2_types[117]);
    declarations.push_back(IFC4X2_types[118]);
    declarations.push_back(IFC4X2_types[119]);
    declarations.push_back(IFC4X2_types[120]);
    declarations.push_back(IFC4X2_types[121]);
    declarations.push_back(IFC4X2_types[122]);
    declarations.push_back(IFC4X2_types[123]);
    declarations.push_back(IFC4X2_types[124]);
    declarations.push_back(IFC4X2_types[125]);
    declarations.push_back(IFC4X2_types[126]);
    declarations.push_back(IFC4X2_types[127]);
    declarations.push_back(IFC4X2_types[128]);
    declarations.push_back(IFC4X2_types[129]);
    declarations.push_back(IFC4X2_types[130]);
    declarations.push_back(IFC4X2_types[131]);
    declarations.push_back(IFC4X2_types[132]);
    declarations.push_back(IFC4X2_types[133]);
    declarations.push_back(IFC4X2_types[134]);
    declarations.push_back(IFC4X2_types[135]);
    declarations.push_back(IFC4X2_types[136]);
    declarations.push_back(IFC4X2_types[137]);
    declarations.push_back(IFC4X2_types[138]);
    declarations.push_back(IFC4X2_types[139]);
    declarations.push_back(IFC4X2_types[140]);
    declarations.push_back(IFC4X2_types[141]);
    declarations.push_back(IFC4X2_types[142]);
    declarations.push_back(IFC4X2_types[143]);
    declarations.push_back(IFC4X2_types[144]);
    declarations.push_back(IFC4X2_types[145]);
    declarations.push_back(IFC4X2_types[146]);
    declarations.push_back(IFC4X2_types[147]);
    declarations.push_back(IFC4X2_types[148]);
    declarations.push_back(IFC4X2_types[149]);
    declarations.push_back(IFC4X2_types[150]);
    declarations.push_back(IFC4X2_types[151]);
    declarations.push_back(IFC4X2_types[152]);
    declarations.push_back(IFC4X2_types[153]);
    declarations.push_back(IFC4X2_types[154]);
    declarations.push_back(IFC4X2_types[155]);
    declarations.push_back(IFC4X2_types[156]);
    declarations.push_back(IFC4X2_types[157]);
    declarations.push_back(IFC4X2_types[158]);
    declarations.push_back(IFC4X2_types[159]);
    declarations.push_back(IFC4X2_types[160]);
    declarations.push_back(IFC4X2_types[161]);
    declarations.push_back(IFC4X2_types[162]);
    declarations.push_back(IFC4X2_types[163]);
    declarations.push_back(IFC4X2_types[164]);
    declarations.push_back(IFC4X2_types[165]);
    declarations.push_back(IFC4X2_types[166]);
    declarations.push_back(IFC4X2_types[167]);
    declarations.push_back(IFC4X2_types[168]);
    declarations.push_back(IFC4X2_types[169]);
    declarations.push_back(IFC4X2_types[170]);
    declarations.push_back(IFC4X2_types[171]);
    declarations.push_back(IFC4X2_types[172]);
    declarations.push_back(IFC4X2_types[173]);
    declarations.push_back(IFC4X2_types[174]);
    declarations.push_back(IFC4X2_types[175]);
    declarations.push_back(IFC4X2_types[176]);
    declarations.push_back(IFC4X2_types[177]);
    declarations.push_back(IFC4X2_types[178]);
    declarations.push_back(IFC4X2_types[179]);
    declarations.push_back(IFC4X2_types[180]);
    declarations.push_back(IFC4X2_types[181]);
    declarations.push_back(IFC4X2_types[182]);
    declarations.push_back(IFC4X2_types[183]);
    declarations.push_back(IFC4X2_types[184]);
    declarations.push_back(IFC4X2_types[185]);
    declarations.push_back(IFC4X2_types[186]);
    declarations.push_back(IFC4X2_types[187]);
    declarations.push_back(IFC4X2_types[188]);
    declarations.push_back(IFC4X2_types[189]);
    declarations.push_back(IFC4X2_types[190]);
    declarations.push_back(IFC4X2_types[191]);
    declarations.push_back(IFC4X2_types[192]);
    declarations.push_back(IFC4X2_types[193]);
    declarations.push_back(IFC4X2_types[194]);
    declarations.push_back(IFC4X2_types[195]);
    declarations.push_back(IFC4X2_types[196]);
    declarations.push_back(IFC4X2_types[197]);
    declarations.push_back(IFC4X2_types[198]);
    declarations.push_back(IFC4X2_types[199]);
    declarations.push_back(IFC4X2_types[200]);
    declarations.push_back(IFC4X2_types[201]);
    declarations.push_back(IFC4X2_types[202]);
    declarations.push_back(IFC4X2_types[203]);
    declarations.push_back(IFC4X2_types[204]);
    declarations.push_back(IFC4X2_types[205]);
    declarations.push_back(IFC4X2_types[206]);
    declarations.push_back(IFC4X2_types[207]);
    declarations.push_back(IFC4X2_types[208]);
    declarations.push_back(IFC4X2_types[209]);
    declarations.push_back(IFC4X2_types[210]);
    declarations.push_back(IFC4X2_types[211]);
    declarations.push_back(IFC4X2_types[212]);
    declarations.push_back(IFC4X2_types[213]);
    declarations.push_back(IFC4X2_types[214]);
    declarations.push_back(IFC4X2_types[215]);
    declarations.push_back(IFC4X2_types[216]);
    declarations.push_back(IFC4X2_types[217]);
    declarations.push_back(IFC4X2_types[218]);
    declarations.push_back(IFC4X2_types[219]);
    declarations.push_back(IFC4X2_types[220]);
    declarations.push_back(IFC4X2_types[221]);
    declarations.push_back(IFC4X2_types[222]);
    declarations.push_back(IFC4X2_types[223]);
    declarations.push_back(IFC4X2_types[224]);
    declarations.push_back(IFC4X2_types[225]);
    declarations.push_back(IFC4X2_types[226]);
    declarations.push_back(IFC4X2_types[227]);
    declarations.push_back(IFC4X2_types[228]);
    declarations.push_back(IFC4X2_types[229]);
    declarations.push_back(IFC4X2_types[230]);
    declarations.push_back(IFC4X2_types[231]);
    declarations.push_back(IFC4X2_types[232]);
    declarations.push_back(IFC4X2_types[233]);
    declarations.push_back(IFC4X2_types[234]);
    declarations.push_back(IFC4X2_types[235]);
    declarations.push_back(IFC4X2_types[236]);
    declarations.push_back(IFC4X2_types[237]);
    declarations.push_back(IFC4X2_types[238]);
    declarations.push_back(IFC4X2_types[239]);
    declarations.push_back(IFC4X2_types[240]);
    declarations.push_back(IFC4X2_types[241]);
    declarations.push_back(IFC4X2_types[242]);
    declarations.push_back(IFC4X2_types[243]);
    declarations.push_back(IFC4X2_types[244]);
    declarations.push_back(IFC4X2_types[245]);
    declarations.push_back(IFC4X2_types[246]);
    declarations.push_back(IFC4X2_types[247]);
    declarations.push_back(IFC4X2_types[248]);
    declarations.push_back(IFC4X2_types[249]);
    declarations.push_back(IFC4X2_types[250]);
    declarations.push_back(IFC4X2_types[251]);
    declarations.push_back(IFC4X2_types[252]);
    declarations.push_back(IFC4X2_types[253]);
    declarations.push_back(IFC4X2_types[254]);
    declarations.push_back(IFC4X2_types[255]);
    declarations.push_back(IFC4X2_types[256]);
    declarations.push_back(IFC4X2_types[257]);
    declarations.push_back(IFC4X2_types[258]);
    declarations.push_back(IFC4X2_types[259]);
    declarations.push_back(IFC4X2_types[260]);
    declarations.push_back(IFC4X2_types[261]);
    declarations.push_back(IFC4X2_types[262]);
    declarations.push_back(IFC4X2_types[263]);
    declarations.push_back(IFC4X2_types[264]);
    declarations.push_back(IFC4X2_types[265]);
    declarations.push_back(IFC4X2_types[266]);
    declarations.push_back(IFC4X2_types[267]);
    declarations.push_back(IFC4X2_types[268]);
    declarations.push_back(IFC4X2_types[269]);
    declarations.push_back(IFC4X2_types[270]);
    declarations.push_back(IFC4X2_types[271]);
    declarations.push_back(IFC4X2_types[272]);
    declarations.push_back(IFC4X2_types[273]);
    declarations.push_back(IFC4X2_types[274]);
    declarations.push_back(IFC4X2_types[275]);
    declarations.push_back(IFC4X2_types[276]);
    declarations.push_back(IFC4X2_types[277]);
    declarations.push_back(IFC4X2_types[278]);
    declarations.push_back(IFC4X2_types[279]);
    declarations.push_back(IFC4X2_types[280]);
    declarations.push_back(IFC4X2_types[281]);
    declarations.push_back(IFC4X2_types[282]);
    declarations.push_back(IFC4X2_types[283]);
    declarations.push_back(IFC4X2_types[284]);
    declarations.push_back(IFC4X2_types[285]);
    declarations.push_back(IFC4X2_types[286]);
    declarations.push_back(IFC4X2_types[287]);
    declarations.push_back(IFC4X2_types[288]);
    declarations.push_back(IFC4X2_types[289]);
    declarations.push_back(IFC4X2_types[290]);
    declarations.push_back(IFC4X2_types[291]);
    declarations.push_back(IFC4X2_types[292]);
    declarations.push_back(IFC4X2_types[293]);
    declarations.push_back(IFC4X2_types[294]);
    declarations.push_back(IFC4X2_types[295]);
    declarations.push_back(IFC4X2_types[296]);
    declarations.push_back(IFC4X2_types[297]);
    declarations.push_back(IFC4X2_types[298]);
    declarations.push_back(IFC4X2_types[299]);
    declarations.push_back(IFC4X2_types[300]);
    declarations.push_back(IFC4X2_types[301]);
    declarations.push_back(IFC4X2_types[302]);
    declarations.push_back(IFC4X2_types[303]);
    declarations.push_back(IFC4X2_types[304]);
    declarations.push_back(IFC4X2_types[305]);
    declarations.push_back(IFC4X2_types[306]);
    declarations.push_back(IFC4X2_types[307]);
    declarations.push_back(IFC4X2_types[308]);
    declarations.push_back(IFC4X2_types[309]);
    declarations.push_back(IFC4X2_types[310]);
    declarations.push_back(IFC4X2_types[311]);
    declarations.push_back(IFC4X2_types[312]);
    declarations.push_back(IFC4X2_types[313]);
    declarations.push_back(IFC4X2_types[314]);
    declarations.push_back(IFC4X2_types[315]);
    declarations.push_back(IFC4X2_types[316]);
    declarations.push_back(IFC4X2_types[317]);
    declarations.push_back(IFC4X2_types[318]);
    declarations.push_back(IFC4X2_types[319]);
    declarations.push_back(IFC4X2_types[320]);
    declarations.push_back(IFC4X2_types[321]);
    declarations.push_back(IFC4X2_types[322]);
    declarations.push_back(IFC4X2_types[323]);
    declarations.push_back(IFC4X2_types[324]);
    declarations.push_back(IFC4X2_types[325]);
    declarations.push_back(IFC4X2_types[326]);
    declarations.push_back(IFC4X2_types[327]);
    declarations.push_back(IFC4X2_types[328]);
    declarations.push_back(IFC4X2_types[329]);
    declarations.push_back(IFC4X2_types[330]);
    declarations.push_back(IFC4X2_types[331]);
    declarations.push_back(IFC4X2_types[332]);
    declarations.push_back(IFC4X2_types[333]);
    declarations.push_back(IFC4X2_types[334]);
    declarations.push_back(IFC4X2_types[335]);
    declarations.push_back(IFC4X2_types[336]);
    declarations.push_back(IFC4X2_types[337]);
    declarations.push_back(IFC4X2_types[338]);
    declarations.push_back(IFC4X2_types[339]);
    declarations.push_back(IFC4X2_types[340]);
    declarations.push_back(IFC4X2_types[341]);
    declarations.push_back(IFC4X2_types[342]);
    declarations.push_back(IFC4X2_types[343]);
    declarations.push_back(IFC4X2_types[344]);
    declarations.push_back(IFC4X2_types[345]);
    declarations.push_back(IFC4X2_types[346]);
    declarations.push_back(IFC4X2_types[347]);
    declarations.push_back(IFC4X2_types[348]);
    declarations.push_back(IFC4X2_types[349]);
    declarations.push_back(IFC4X2_types[350]);
    declarations.push_back(IFC4X2_types[351]);
    declarations.push_back(IFC4X2_types[352]);
    declarations.push_back(IFC4X2_types[353]);
    declarations.push_back(IFC4X2_types[354]);
    declarations.push_back(IFC4X2_types[355]);
    declarations.push_back(IFC4X2_types[356]);
    declarations.push_back(IFC4X2_types[357]);
    declarations.push_back(IFC4X2_types[358]);
    declarations.push_back(IFC4X2_types[359]);
    declarations.push_back(IFC4X2_types[360]);
    declarations.push_back(IFC4X2_types[361]);
    declarations.push_back(IFC4X2_types[362]);
    declarations.push_back(IFC4X2_types[363]);
    declarations.push_back(IFC4X2_types[364]);
    declarations.push_back(IFC4X2_types[365]);
    declarations.push_back(IFC4X2_types[366]);
    declarations.push_back(IFC4X2_types[367]);
    declarations.push_back(IFC4X2_types[368]);
    declarations.push_back(IFC4X2_types[369]);
    declarations.push_back(IFC4X2_types[370]);
    declarations.push_back(IFC4X2_types[371]);
    declarations.push_back(IFC4X2_types[372]);
    declarations.push_back(IFC4X2_types[373]);
    declarations.push_back(IFC4X2_types[374]);
    declarations.push_back(IFC4X2_types[375]);
    declarations.push_back(IFC4X2_types[376]);
    declarations.push_back(IFC4X2_types[377]);
    declarations.push_back(IFC4X2_types[378]);
    declarations.push_back(IFC4X2_types[379]);
    declarations.push_back(IFC4X2_types[380]);
    declarations.push_back(IFC4X2_types[381]);
    declarations.push_back(IFC4X2_types[382]);
    declarations.push_back(IFC4X2_types[383]);
    declarations.push_back(IFC4X2_types[384]);
    declarations.push_back(IFC4X2_types[385]);
    declarations.push_back(IFC4X2_types[386]);
    declarations.push_back(IFC4X2_types[387]);
    declarations.push_back(IFC4X2_types[388]);
    declarations.push_back(IFC4X2_types[389]);
    declarations.push_back(IFC4X2_types[390]);
    declarations.push_back(IFC4X2_types[391]);
    declarations.push_back(IFC4X2_types[392]);
    declarations.push_back(IFC4X2_types[393]);
    declarations.push_back(IFC4X2_types[394]);
    declarations.push_back(IFC4X2_types[395]);
    declarations.push_back(IFC4X2_types[396]);
    declarations.push_back(IFC4X2_types[397]);
    declarations.push_back(IFC4X2_types[398]);
    declarations.push_back(IFC4X2_types[399]);
    declarations.push_back(IFC4X2_types[400]);
    declarations.push_back(IFC4X2_types[401]);
    declarations.push_back(IFC4X2_types[402]);
    declarations.push_back(IFC4X2_types[403]);
    declarations.push_back(IFC4X2_types[404]);
    declarations.push_back(IFC4X2_types[405]);
    declarations.push_back(IFC4X2_types[406]);
    declarations.push_back(IFC4X2_types[407]);
    declarations.push_back(IFC4X2_types[408]);
    declarations.push_back(IFC4X2_types[409]);
    declarations.push_back(IFC4X2_types[410]);
    declarations.push_back(IFC4X2_types[411]);
    declarations.push_back(IFC4X2_types[412]);
    declarations.push_back(IFC4X2_types[413]);
    declarations.push_back(IFC4X2_types[414]);
    declarations.push_back(IFC4X2_types[415]);
    declarations.push_back(IFC4X2_types[416]);
    declarations.push_back(IFC4X2_types[417]);
    declarations.push_back(IFC4X2_types[418]);
    declarations.push_back(IFC4X2_types[419]);
    declarations.push_back(IFC4X2_types[420]);
    declarations.push_back(IFC4X2_types[421]);
    declarations.push_back(IFC4X2_types[422]);
    declarations.push_back(IFC4X2_types[423]);
    declarations.push_back(IFC4X2_types[424]);
    declarations.push_back(IFC4X2_types[425]);
    declarations.push_back(IFC4X2_types[426]);
    declarations.push_back(IFC4X2_types[427]);
    declarations.push_back(IFC4X2_types[428]);
    declarations.push_back(IFC4X2_types[429]);
    declarations.push_back(IFC4X2_types[430]);
    declarations.push_back(IFC4X2_types[431]);
    declarations.push_back(IFC4X2_types[432]);
    declarations.push_back(IFC4X2_types[433]);
    declarations.push_back(IFC4X2_types[434]);
    declarations.push_back(IFC4X2_types[435]);
    declarations.push_back(IFC4X2_types[436]);
    declarations.push_back(IFC4X2_types[437]);
    declarations.push_back(IFC4X2_types[438]);
    declarations.push_back(IFC4X2_types[439]);
    declarations.push_back(IFC4X2_types[440]);
    declarations.push_back(IFC4X2_types[441]);
    declarations.push_back(IFC4X2_types[442]);
    declarations.push_back(IFC4X2_types[443]);
    declarations.push_back(IFC4X2_types[444]);
    declarations.push_back(IFC4X2_types[445]);
    declarations.push_back(IFC4X2_types[446]);
    declarations.push_back(IFC4X2_types[447]);
    declarations.push_back(IFC4X2_types[448]);
    declarations.push_back(IFC4X2_types[449]);
    declarations.push_back(IFC4X2_types[450]);
    declarations.push_back(IFC4X2_types[451]);
    declarations.push_back(IFC4X2_types[452]);
    declarations.push_back(IFC4X2_types[453]);
    declarations.push_back(IFC4X2_types[454]);
    declarations.push_back(IFC4X2_types[455]);
    declarations.push_back(IFC4X2_types[456]);
    declarations.push_back(IFC4X2_types[457]);
    declarations.push_back(IFC4X2_types[458]);
    declarations.push_back(IFC4X2_types[459]);
    declarations.push_back(IFC4X2_types[460]);
    declarations.push_back(IFC4X2_types[461]);
    declarations.push_back(IFC4X2_types[462]);
    declarations.push_back(IFC4X2_types[463]);
    declarations.push_back(IFC4X2_types[464]);
    declarations.push_back(IFC4X2_types[465]);
    declarations.push_back(IFC4X2_types[466]);
    declarations.push_back(IFC4X2_types[467]);
    declarations.push_back(IFC4X2_types[468]);
    declarations.push_back(IFC4X2_types[469]);
    declarations.push_back(IFC4X2_types[470]);
    declarations.push_back(IFC4X2_types[471]);
    declarations.push_back(IFC4X2_types[472]);
    declarations.push_back(IFC4X2_types[473]);
    declarations.push_back(IFC4X2_types[474]);
    declarations.push_back(IFC4X2_types[475]);
    declarations.push_back(IFC4X2_types[476]);
    declarations.push_back(IFC4X2_types[477]);
    declarations.push_back(IFC4X2_types[478]);
    declarations.push_back(IFC4X2_types[479]);
    declarations.push_back(IFC4X2_types[480]);
    declarations.push_back(IFC4X2_types[481]);
    declarations.push_back(IFC4X2_types[482]);
    declarations.push_back(IFC4X2_types[483]);
    declarations.push_back(IFC4X2_types[484]);
    declarations.push_back(IFC4X2_types[485]);
    declarations.push_back(IFC4X2_types[486]);
    declarations.push_back(IFC4X2_types[487]);
    declarations.push_back(IFC4X2_types[488]);
    declarations.push_back(IFC4X2_types[489]);
    declarations.push_back(IFC4X2_types[490]);
    declarations.push_back(IFC4X2_types[491]);
    declarations.push_back(IFC4X2_types[492]);
    declarations.push_back(IFC4X2_types[493]);
    declarations.push_back(IFC4X2_types[494]);
    declarations.push_back(IFC4X2_types[495]);
    declarations.push_back(IFC4X2_types[496]);
    declarations.push_back(IFC4X2_types[497]);
    declarations.push_back(IFC4X2_types[498]);
    declarations.push_back(IFC4X2_types[499]);
    declarations.push_back(IFC4X2_types[500]);
    declarations.push_back(IFC4X2_types[501]);
    declarations.push_back(IFC4X2_types[502]);
    declarations.push_back(IFC4X2_types[503]);
    declarations.push_back(IFC4X2_types[504]);
    declarations.push_back(IFC4X2_types[505]);
    declarations.push_back(IFC4X2_types[506]);
    declarations.push_back(IFC4X2_types[507]);
    declarations.push_back(IFC4X2_types[508]);
    declarations.push_back(IFC4X2_types[509]);
    declarations.push_back(IFC4X2_types[510]);
    declarations.push_back(IFC4X2_types[511]);
    declarations.push_back(IFC4X2_types[512]);
    declarations.push_back(IFC4X2_types[513]);
    declarations.push_back(IFC4X2_types[514]);
    declarations.push_back(IFC4X2_types[515]);
    declarations.push_back(IFC4X2_types[516]);
    declarations.push_back(IFC4X2_types[517]);
    declarations.push_back(IFC4X2_types[518]);
    declarations.push_back(IFC4X2_types[519]);
    declarations.push_back(IFC4X2_types[520]);
    declarations.push_back(IFC4X2_types[521]);
    declarations.push_back(IFC4X2_types[522]);
    declarations.push_back(IFC4X2_types[523]);
    declarations.push_back(IFC4X2_types[524]);
    declarations.push_back(IFC4X2_types[525]);
    declarations.push_back(IFC4X2_types[526]);
    declarations.push_back(IFC4X2_types[527]);
    declarations.push_back(IFC4X2_types[528]);
    declarations.push_back(IFC4X2_types[529]);
    declarations.push_back(IFC4X2_types[530]);
    declarations.push_back(IFC4X2_types[531]);
    declarations.push_back(IFC4X2_types[532]);
    declarations.push_back(IFC4X2_types[533]);
    declarations.push_back(IFC4X2_types[534]);
    declarations.push_back(IFC4X2_types[535]);
    declarations.push_back(IFC4X2_types[536]);
    declarations.push_back(IFC4X2_types[537]);
    declarations.push_back(IFC4X2_types[538]);
    declarations.push_back(IFC4X2_types[539]);
    declarations.push_back(IFC4X2_types[540]);
    declarations.push_back(IFC4X2_types[541]);
    declarations.push_back(IFC4X2_types[542]);
    declarations.push_back(IFC4X2_types[543]);
    declarations.push_back(IFC4X2_types[544]);
    declarations.push_back(IFC4X2_types[545]);
    declarations.push_back(IFC4X2_types[546]);
    declarations.push_back(IFC4X2_types[547]);
    declarations.push_back(IFC4X2_types[548]);
    declarations.push_back(IFC4X2_types[549]);
    declarations.push_back(IFC4X2_types[550]);
    declarations.push_back(IFC4X2_types[551]);
    declarations.push_back(IFC4X2_types[552]);
    declarations.push_back(IFC4X2_types[553]);
    declarations.push_back(IFC4X2_types[554]);
    declarations.push_back(IFC4X2_types[555]);
    declarations.push_back(IFC4X2_types[556]);
    declarations.push_back(IFC4X2_types[557]);
    declarations.push_back(IFC4X2_types[558]);
    declarations.push_back(IFC4X2_types[559]);
    declarations.push_back(IFC4X2_types[560]);
    declarations.push_back(IFC4X2_types[561]);
    declarations.push_back(IFC4X2_types[562]);
    declarations.push_back(IFC4X2_types[563]);
    declarations.push_back(IFC4X2_types[564]);
    declarations.push_back(IFC4X2_types[565]);
    declarations.push_back(IFC4X2_types[566]);
    declarations.push_back(IFC4X2_types[567]);
    declarations.push_back(IFC4X2_types[568]);
    declarations.push_back(IFC4X2_types[569]);
    declarations.push_back(IFC4X2_types[570]);
    declarations.push_back(IFC4X2_types[571]);
    declarations.push_back(IFC4X2_types[572]);
    declarations.push_back(IFC4X2_types[573]);
    declarations.push_back(IFC4X2_types[574]);
    declarations.push_back(IFC4X2_types[575]);
    declarations.push_back(IFC4X2_types[576]);
    declarations.push_back(IFC4X2_types[577]);
    declarations.push_back(IFC4X2_types[578]);
    declarations.push_back(IFC4X2_types[579]);
    declarations.push_back(IFC4X2_types[580]);
    declarations.push_back(IFC4X2_types[581]);
    declarations.push_back(IFC4X2_types[582]);
    declarations.push_back(IFC4X2_types[583]);
    declarations.push_back(IFC4X2_types[584]);
    declarations.push_back(IFC4X2_types[585]);
    declarations.push_back(IFC4X2_types[586]);
    declarations.push_back(IFC4X2_types[587]);
    declarations.push_back(IFC4X2_types[588]);
    declarations.push_back(IFC4X2_types[589]);
    declarations.push_back(IFC4X2_types[590]);
    declarations.push_back(IFC4X2_types[591]);
    declarations.push_back(IFC4X2_types[592]);
    declarations.push_back(IFC4X2_types[593]);
    declarations.push_back(IFC4X2_types[594]);
    declarations.push_back(IFC4X2_types[595]);
    declarations.push_back(IFC4X2_types[596]);
    declarations.push_back(IFC4X2_types[597]);
    declarations.push_back(IFC4X2_types[598]);
    declarations.push_back(IFC4X2_types[599]);
    declarations.push_back(IFC4X2_types[600]);
    declarations.push_back(IFC4X2_types[601]);
    declarations.push_back(IFC4X2_types[602]);
    declarations.push_back(IFC4X2_types[603]);
    declarations.push_back(IFC4X2_types[604]);
    declarations.push_back(IFC4X2_types[605]);
    declarations.push_back(IFC4X2_types[606]);
    declarations.push_back(IFC4X2_types[607]);
    declarations.push_back(IFC4X2_types[608]);
    declarations.push_back(IFC4X2_types[609]);
    declarations.push_back(IFC4X2_types[610]);
    declarations.push_back(IFC4X2_types[611]);
    declarations.push_back(IFC4X2_types[612]);
    declarations.push_back(IFC4X2_types[613]);
    declarations.push_back(IFC4X2_types[614]);
    declarations.push_back(IFC4X2_types[615]);
    declarations.push_back(IFC4X2_types[616]);
    declarations.push_back(IFC4X2_types[617]);
    declarations.push_back(IFC4X2_types[618]);
    declarations.push_back(IFC4X2_types[619]);
    declarations.push_back(IFC4X2_types[620]);
    declarations.push_back(IFC4X2_types[621]);
    declarations.push_back(IFC4X2_types[622]);
    declarations.push_back(IFC4X2_types[623]);
    declarations.push_back(IFC4X2_types[624]);
    declarations.push_back(IFC4X2_types[625]);
    declarations.push_back(IFC4X2_types[626]);
    declarations.push_back(IFC4X2_types[627]);
    declarations.push_back(IFC4X2_types[628]);
    declarations.push_back(IFC4X2_types[629]);
    declarations.push_back(IFC4X2_types[630]);
    declarations.push_back(IFC4X2_types[631]);
    declarations.push_back(IFC4X2_types[632]);
    declarations.push_back(IFC4X2_types[633]);
    declarations.push_back(IFC4X2_types[634]);
    declarations.push_back(IFC4X2_types[635]);
    declarations.push_back(IFC4X2_types[636]);
    declarations.push_back(IFC4X2_types[637]);
    declarations.push_back(IFC4X2_types[638]);
    declarations.push_back(IFC4X2_types[639]);
    declarations.push_back(IFC4X2_types[640]);
    declarations.push_back(IFC4X2_types[641]);
    declarations.push_back(IFC4X2_types[642]);
    declarations.push_back(IFC4X2_types[643]);
    declarations.push_back(IFC4X2_types[644]);
    declarations.push_back(IFC4X2_types[645]);
    declarations.push_back(IFC4X2_types[646]);
    declarations.push_back(IFC4X2_types[647]);
    declarations.push_back(IFC4X2_types[648]);
    declarations.push_back(IFC4X2_types[649]);
    declarations.push_back(IFC4X2_types[650]);
    declarations.push_back(IFC4X2_types[651]);
    declarations.push_back(IFC4X2_types[652]);
    declarations.push_back(IFC4X2_types[653]);
    declarations.push_back(IFC4X2_types[654]);
    declarations.push_back(IFC4X2_types[655]);
    declarations.push_back(IFC4X2_types[656]);
    declarations.push_back(IFC4X2_types[657]);
    declarations.push_back(IFC4X2_types[658]);
    declarations.push_back(IFC4X2_types[659]);
    declarations.push_back(IFC4X2_types[660]);
    declarations.push_back(IFC4X2_types[661]);
    declarations.push_back(IFC4X2_types[662]);
    declarations.push_back(IFC4X2_types[663]);
    declarations.push_back(IFC4X2_types[664]);
    declarations.push_back(IFC4X2_types[665]);
    declarations.push_back(IFC4X2_types[666]);
    declarations.push_back(IFC4X2_types[667]);
    declarations.push_back(IFC4X2_types[668]);
    declarations.push_back(IFC4X2_types[669]);
    declarations.push_back(IFC4X2_types[670]);
    declarations.push_back(IFC4X2_types[671]);
    declarations.push_back(IFC4X2_types[672]);
    declarations.push_back(IFC4X2_types[673]);
    declarations.push_back(IFC4X2_types[674]);
    declarations.push_back(IFC4X2_types[675]);
    declarations.push_back(IFC4X2_types[676]);
    declarations.push_back(IFC4X2_types[677]);
    declarations.push_back(IFC4X2_types[678]);
    declarations.push_back(IFC4X2_types[679]);
    declarations.push_back(IFC4X2_types[680]);
    declarations.push_back(IFC4X2_types[681]);
    declarations.push_back(IFC4X2_types[682]);
    declarations.push_back(IFC4X2_types[683]);
    declarations.push_back(IFC4X2_types[684]);
    declarations.push_back(IFC4X2_types[685]);
    declarations.push_back(IFC4X2_types[686]);
    declarations.push_back(IFC4X2_types[687]);
    declarations.push_back(IFC4X2_types[688]);
    declarations.push_back(IFC4X2_types[689]);
    declarations.push_back(IFC4X2_types[690]);
    declarations.push_back(IFC4X2_types[691]);
    declarations.push_back(IFC4X2_types[692]);
    declarations.push_back(IFC4X2_types[693]);
    declarations.push_back(IFC4X2_types[694]);
    declarations.push_back(IFC4X2_types[695]);
    declarations.push_back(IFC4X2_types[696]);
    declarations.push_back(IFC4X2_types[697]);
    declarations.push_back(IFC4X2_types[698]);
    declarations.push_back(IFC4X2_types[699]);
    declarations.push_back(IFC4X2_types[700]);
    declarations.push_back(IFC4X2_types[701]);
    declarations.push_back(IFC4X2_types[702]);
    declarations.push_back(IFC4X2_types[703]);
    declarations.push_back(IFC4X2_types[704]);
    declarations.push_back(IFC4X2_types[705]);
    declarations.push_back(IFC4X2_types[706]);
    declarations.push_back(IFC4X2_types[707]);
    declarations.push_back(IFC4X2_types[708]);
    declarations.push_back(IFC4X2_types[709]);
    declarations.push_back(IFC4X2_types[710]);
    declarations.push_back(IFC4X2_types[711]);
    declarations.push_back(IFC4X2_types[712]);
    declarations.push_back(IFC4X2_types[713]);
    declarations.push_back(IFC4X2_types[714]);
    declarations.push_back(IFC4X2_types[715]);
    declarations.push_back(IFC4X2_types[716]);
    declarations.push_back(IFC4X2_types[717]);
    declarations.push_back(IFC4X2_types[718]);
    declarations.push_back(IFC4X2_types[719]);
    declarations.push_back(IFC4X2_types[720]);
    declarations.push_back(IFC4X2_types[721]);
    declarations.push_back(IFC4X2_types[722]);
    declarations.push_back(IFC4X2_types[723]);
    declarations.push_back(IFC4X2_types[724]);
    declarations.push_back(IFC4X2_types[725]);
    declarations.push_back(IFC4X2_types[726]);
    declarations.push_back(IFC4X2_types[727]);
    declarations.push_back(IFC4X2_types[728]);
    declarations.push_back(IFC4X2_types[729]);
    declarations.push_back(IFC4X2_types[730]);
    declarations.push_back(IFC4X2_types[731]);
    declarations.push_back(IFC4X2_types[732]);
    declarations.push_back(IFC4X2_types[733]);
    declarations.push_back(IFC4X2_types[734]);
    declarations.push_back(IFC4X2_types[735]);
    declarations.push_back(IFC4X2_types[736]);
    declarations.push_back(IFC4X2_types[737]);
    declarations.push_back(IFC4X2_types[738]);
    declarations.push_back(IFC4X2_types[739]);
    declarations.push_back(IFC4X2_types[740]);
    declarations.push_back(IFC4X2_types[741]);
    declarations.push_back(IFC4X2_types[742]);
    declarations.push_back(IFC4X2_types[743]);
    declarations.push_back(IFC4X2_types[744]);
    declarations.push_back(IFC4X2_types[745]);
    declarations.push_back(IFC4X2_types[746]);
    declarations.push_back(IFC4X2_types[747]);
    declarations.push_back(IFC4X2_types[748]);
    declarations.push_back(IFC4X2_types[749]);
    declarations.push_back(IFC4X2_types[750]);
    declarations.push_back(IFC4X2_types[751]);
    declarations.push_back(IFC4X2_types[752]);
    declarations.push_back(IFC4X2_types[753]);
    declarations.push_back(IFC4X2_types[754]);
    declarations.push_back(IFC4X2_types[755]);
    declarations.push_back(IFC4X2_types[756]);
    declarations.push_back(IFC4X2_types[757]);
    declarations.push_back(IFC4X2_types[758]);
    declarations.push_back(IFC4X2_types[759]);
    declarations.push_back(IFC4X2_types[760]);
    declarations.push_back(IFC4X2_types[761]);
    declarations.push_back(IFC4X2_types[762]);
    declarations.push_back(IFC4X2_types[763]);
    declarations.push_back(IFC4X2_types[764]);
    declarations.push_back(IFC4X2_types[765]);
    declarations.push_back(IFC4X2_types[766]);
    declarations.push_back(IFC4X2_types[767]);
    declarations.push_back(IFC4X2_types[768]);
    declarations.push_back(IFC4X2_types[769]);
    declarations.push_back(IFC4X2_types[770]);
    declarations.push_back(IFC4X2_types[771]);
    declarations.push_back(IFC4X2_types[772]);
    declarations.push_back(IFC4X2_types[773]);
    declarations.push_back(IFC4X2_types[774]);
    declarations.push_back(IFC4X2_types[775]);
    declarations.push_back(IFC4X2_types[776]);
    declarations.push_back(IFC4X2_types[777]);
    declarations.push_back(IFC4X2_types[778]);
    declarations.push_back(IFC4X2_types[779]);
    declarations.push_back(IFC4X2_types[780]);
    declarations.push_back(IFC4X2_types[781]);
    declarations.push_back(IFC4X2_types[782]);
    declarations.push_back(IFC4X2_types[783]);
    declarations.push_back(IFC4X2_types[784]);
    declarations.push_back(IFC4X2_types[785]);
    declarations.push_back(IFC4X2_types[786]);
    declarations.push_back(IFC4X2_types[787]);
    declarations.push_back(IFC4X2_types[788]);
    declarations.push_back(IFC4X2_types[789]);
    declarations.push_back(IFC4X2_types[790]);
    declarations.push_back(IFC4X2_types[791]);
    declarations.push_back(IFC4X2_types[792]);
    declarations.push_back(IFC4X2_types[793]);
    declarations.push_back(IFC4X2_types[794]);
    declarations.push_back(IFC4X2_types[795]);
    declarations.push_back(IFC4X2_types[796]);
    declarations.push_back(IFC4X2_types[797]);
    declarations.push_back(IFC4X2_types[798]);
    declarations.push_back(IFC4X2_types[799]);
    declarations.push_back(IFC4X2_types[800]);
    declarations.push_back(IFC4X2_types[801]);
    declarations.push_back(IFC4X2_types[802]);
    declarations.push_back(IFC4X2_types[803]);
    declarations.push_back(IFC4X2_types[804]);
    declarations.push_back(IFC4X2_types[805]);
    declarations.push_back(IFC4X2_types[806]);
    declarations.push_back(IFC4X2_types[807]);
    declarations.push_back(IFC4X2_types[808]);
    declarations.push_back(IFC4X2_types[809]);
    declarations.push_back(IFC4X2_types[810]);
    declarations.push_back(IFC4X2_types[811]);
    declarations.push_back(IFC4X2_types[812]);
    declarations.push_back(IFC4X2_types[813]);
    declarations.push_back(IFC4X2_types[814]);
    declarations.push_back(IFC4X2_types[815]);
    declarations.push_back(IFC4X2_types[816]);
    declarations.push_back(IFC4X2_types[817]);
    declarations.push_back(IFC4X2_types[818]);
    declarations.push_back(IFC4X2_types[819]);
    declarations.push_back(IFC4X2_types[820]);
    declarations.push_back(IFC4X2_types[821]);
    declarations.push_back(IFC4X2_types[822]);
    declarations.push_back(IFC4X2_types[823]);
    declarations.push_back(IFC4X2_types[824]);
    declarations.push_back(IFC4X2_types[825]);
    declarations.push_back(IFC4X2_types[826]);
    declarations.push_back(IFC4X2_types[827]);
    declarations.push_back(IFC4X2_types[828]);
    declarations.push_back(IFC4X2_types[829]);
    declarations.push_back(IFC4X2_types[830]);
    declarations.push_back(IFC4X2_types[831]);
    declarations.push_back(IFC4X2_types[832]);
    declarations.push_back(IFC4X2_types[833]);
    declarations.push_back(IFC4X2_types[834]);
    declarations.push_back(IFC4X2_types[835]);
    declarations.push_back(IFC4X2_types[836]);
    declarations.push_back(IFC4X2_types[837]);
    declarations.push_back(IFC4X2_types[838]);
    declarations.push_back(IFC4X2_types[839]);
    declarations.push_back(IFC4X2_types[840]);
    declarations.push_back(IFC4X2_types[841]);
    declarations.push_back(IFC4X2_types[842]);
    declarations.push_back(IFC4X2_types[843]);
    declarations.push_back(IFC4X2_types[844]);
    declarations.push_back(IFC4X2_types[845]);
    declarations.push_back(IFC4X2_types[846]);
    declarations.push_back(IFC4X2_types[847]);
    declarations.push_back(IFC4X2_types[848]);
    declarations.push_back(IFC4X2_types[849]);
    declarations.push_back(IFC4X2_types[850]);
    declarations.push_back(IFC4X2_types[851]);
    declarations.push_back(IFC4X2_types[852]);
    declarations.push_back(IFC4X2_types[853]);
    declarations.push_back(IFC4X2_types[854]);
    declarations.push_back(IFC4X2_types[855]);
    declarations.push_back(IFC4X2_types[856]);
    declarations.push_back(IFC4X2_types[857]);
    declarations.push_back(IFC4X2_types[858]);
    declarations.push_back(IFC4X2_types[859]);
    declarations.push_back(IFC4X2_types[860]);
    declarations.push_back(IFC4X2_types[861]);
    declarations.push_back(IFC4X2_types[862]);
    declarations.push_back(IFC4X2_types[863]);
    declarations.push_back(IFC4X2_types[864]);
    declarations.push_back(IFC4X2_types[865]);
    declarations.push_back(IFC4X2_types[866]);
    declarations.push_back(IFC4X2_types[867]);
    declarations.push_back(IFC4X2_types[868]);
    declarations.push_back(IFC4X2_types[869]);
    declarations.push_back(IFC4X2_types[870]);
    declarations.push_back(IFC4X2_types[871]);
    declarations.push_back(IFC4X2_types[872]);
    declarations.push_back(IFC4X2_types[873]);
    declarations.push_back(IFC4X2_types[874]);
    declarations.push_back(IFC4X2_types[875]);
    declarations.push_back(IFC4X2_types[876]);
    declarations.push_back(IFC4X2_types[877]);
    declarations.push_back(IFC4X2_types[878]);
    declarations.push_back(IFC4X2_types[879]);
    declarations.push_back(IFC4X2_types[880]);
    declarations.push_back(IFC4X2_types[881]);
    declarations.push_back(IFC4X2_types[882]);
    declarations.push_back(IFC4X2_types[883]);
    declarations.push_back(IFC4X2_types[884]);
    declarations.push_back(IFC4X2_types[885]);
    declarations.push_back(IFC4X2_types[886]);
    declarations.push_back(IFC4X2_types[887]);
    declarations.push_back(IFC4X2_types[888]);
    declarations.push_back(IFC4X2_types[889]);
    declarations.push_back(IFC4X2_types[890]);
    declarations.push_back(IFC4X2_types[891]);
    declarations.push_back(IFC4X2_types[892]);
    declarations.push_back(IFC4X2_types[893]);
    declarations.push_back(IFC4X2_types[894]);
    declarations.push_back(IFC4X2_types[895]);
    declarations.push_back(IFC4X2_types[896]);
    declarations.push_back(IFC4X2_types[897]);
    declarations.push_back(IFC4X2_types[898]);
    declarations.push_back(IFC4X2_types[899]);
    declarations.push_back(IFC4X2_types[900]);
    declarations.push_back(IFC4X2_types[901]);
    declarations.push_back(IFC4X2_types[902]);
    declarations.push_back(IFC4X2_types[903]);
    declarations.push_back(IFC4X2_types[904]);
    declarations.push_back(IFC4X2_types[905]);
    declarations.push_back(IFC4X2_types[906]);
    declarations.push_back(IFC4X2_types[907]);
    declarations.push_back(IFC4X2_types[908]);
    declarations.push_back(IFC4X2_types[909]);
    declarations.push_back(IFC4X2_types[910]);
    declarations.push_back(IFC4X2_types[911]);
    declarations.push_back(IFC4X2_types[912]);
    declarations.push_back(IFC4X2_types[913]);
    declarations.push_back(IFC4X2_types[914]);
    declarations.push_back(IFC4X2_types[915]);
    declarations.push_back(IFC4X2_types[916]);
    declarations.push_back(IFC4X2_types[917]);
    declarations.push_back(IFC4X2_types[918]);
    declarations.push_back(IFC4X2_types[919]);
    declarations.push_back(IFC4X2_types[920]);
    declarations.push_back(IFC4X2_types[921]);
    declarations.push_back(IFC4X2_types[922]);
    declarations.push_back(IFC4X2_types[923]);
    declarations.push_back(IFC4X2_types[924]);
    declarations.push_back(IFC4X2_types[925]);
    declarations.push_back(IFC4X2_types[926]);
    declarations.push_back(IFC4X2_types[927]);
    declarations.push_back(IFC4X2_types[928]);
    declarations.push_back(IFC4X2_types[929]);
    declarations.push_back(IFC4X2_types[930]);
    declarations.push_back(IFC4X2_types[931]);
    declarations.push_back(IFC4X2_types[932]);
    declarations.push_back(IFC4X2_types[933]);
    declarations.push_back(IFC4X2_types[934]);
    declarations.push_back(IFC4X2_types[935]);
    declarations.push_back(IFC4X2_types[936]);
    declarations.push_back(IFC4X2_types[937]);
    declarations.push_back(IFC4X2_types[938]);
    declarations.push_back(IFC4X2_types[939]);
    declarations.push_back(IFC4X2_types[940]);
    declarations.push_back(IFC4X2_types[941]);
    declarations.push_back(IFC4X2_types[942]);
    declarations.push_back(IFC4X2_types[943]);
    declarations.push_back(IFC4X2_types[944]);
    declarations.push_back(IFC4X2_types[945]);
    declarations.push_back(IFC4X2_types[946]);
    declarations.push_back(IFC4X2_types[947]);
    declarations.push_back(IFC4X2_types[948]);
    declarations.push_back(IFC4X2_types[949]);
    declarations.push_back(IFC4X2_types[950]);
    declarations.push_back(IFC4X2_types[951]);
    declarations.push_back(IFC4X2_types[952]);
    declarations.push_back(IFC4X2_types[953]);
    declarations.push_back(IFC4X2_types[954]);
    declarations.push_back(IFC4X2_types[955]);
    declarations.push_back(IFC4X2_types[956]);
    declarations.push_back(IFC4X2_types[957]);
    declarations.push_back(IFC4X2_types[958]);
    declarations.push_back(IFC4X2_types[959]);
    declarations.push_back(IFC4X2_types[960]);
    declarations.push_back(IFC4X2_types[961]);
    declarations.push_back(IFC4X2_types[962]);
    declarations.push_back(IFC4X2_types[963]);
    declarations.push_back(IFC4X2_types[964]);
    declarations.push_back(IFC4X2_types[965]);
    declarations.push_back(IFC4X2_types[966]);
    declarations.push_back(IFC4X2_types[967]);
    declarations.push_back(IFC4X2_types[968]);
    declarations.push_back(IFC4X2_types[969]);
    declarations.push_back(IFC4X2_types[970]);
    declarations.push_back(IFC4X2_types[971]);
    declarations.push_back(IFC4X2_types[972]);
    declarations.push_back(IFC4X2_types[973]);
    declarations.push_back(IFC4X2_types[974]);
    declarations.push_back(IFC4X2_types[975]);
    declarations.push_back(IFC4X2_types[976]);
    declarations.push_back(IFC4X2_types[977]);
    declarations.push_back(IFC4X2_types[978]);
    declarations.push_back(IFC4X2_types[979]);
    declarations.push_back(IFC4X2_types[980]);
    declarations.push_back(IFC4X2_types[981]);
    declarations.push_back(IFC4X2_types[982]);
    declarations.push_back(IFC4X2_types[983]);
    declarations.push_back(IFC4X2_types[984]);
    declarations.push_back(IFC4X2_types[985]);
    declarations.push_back(IFC4X2_types[986]);
    declarations.push_back(IFC4X2_types[987]);
    declarations.push_back(IFC4X2_types[988]);
    declarations.push_back(IFC4X2_types[989]);
    declarations.push_back(IFC4X2_types[990]);
    declarations.push_back(IFC4X2_types[991]);
    declarations.push_back(IFC4X2_types[992]);
    declarations.push_back(IFC4X2_types[993]);
    declarations.push_back(IFC4X2_types[994]);
    declarations.push_back(IFC4X2_types[995]);
    declarations.push_back(IFC4X2_types[996]);
    declarations.push_back(IFC4X2_types[997]);
    declarations.push_back(IFC4X2_types[998]);
    declarations.push_back(IFC4X2_types[999]);
    declarations.push_back(IFC4X2_types[1000]);
    declarations.push_back(IFC4X2_types[1001]);
    declarations.push_back(IFC4X2_types[1002]);
    declarations.push_back(IFC4X2_types[1003]);
    declarations.push_back(IFC4X2_types[1004]);
    declarations.push_back(IFC4X2_types[1005]);
    declarations.push_back(IFC4X2_types[1006]);
    declarations.push_back(IFC4X2_types[1007]);
    declarations.push_back(IFC4X2_types[1008]);
    declarations.push_back(IFC4X2_types[1009]);
    declarations.push_back(IFC4X2_types[1010]);
    declarations.push_back(IFC4X2_types[1011]);
    declarations.push_back(IFC4X2_types[1012]);
    declarations.push_back(IFC4X2_types[1013]);
    declarations.push_back(IFC4X2_types[1014]);
    declarations.push_back(IFC4X2_types[1015]);
    declarations.push_back(IFC4X2_types[1016]);
    declarations.push_back(IFC4X2_types[1017]);
    declarations.push_back(IFC4X2_types[1018]);
    declarations.push_back(IFC4X2_types[1019]);
    declarations.push_back(IFC4X2_types[1020]);
    declarations.push_back(IFC4X2_types[1021]);
    declarations.push_back(IFC4X2_types[1022]);
    declarations.push_back(IFC4X2_types[1023]);
    declarations.push_back(IFC4X2_types[1024]);
    declarations.push_back(IFC4X2_types[1025]);
    declarations.push_back(IFC4X2_types[1026]);
    declarations.push_back(IFC4X2_types[1027]);
    declarations.push_back(IFC4X2_types[1028]);
    declarations.push_back(IFC4X2_types[1029]);
    declarations.push_back(IFC4X2_types[1030]);
    declarations.push_back(IFC4X2_types[1031]);
    declarations.push_back(IFC4X2_types[1032]);
    declarations.push_back(IFC4X2_types[1033]);
    declarations.push_back(IFC4X2_types[1034]);
    declarations.push_back(IFC4X2_types[1035]);
    declarations.push_back(IFC4X2_types[1036]);
    declarations.push_back(IFC4X2_types[1037]);
    declarations.push_back(IFC4X2_types[1038]);
    declarations.push_back(IFC4X2_types[1039]);
    declarations.push_back(IFC4X2_types[1040]);
    declarations.push_back(IFC4X2_types[1041]);
    declarations.push_back(IFC4X2_types[1042]);
    declarations.push_back(IFC4X2_types[1043]);
    declarations.push_back(IFC4X2_types[1044]);
    declarations.push_back(IFC4X2_types[1045]);
    declarations.push_back(IFC4X2_types[1046]);
    declarations.push_back(IFC4X2_types[1047]);
    declarations.push_back(IFC4X2_types[1048]);
    declarations.push_back(IFC4X2_types[1049]);
    declarations.push_back(IFC4X2_types[1050]);
    declarations.push_back(IFC4X2_types[1051]);
    declarations.push_back(IFC4X2_types[1052]);
    declarations.push_back(IFC4X2_types[1053]);
    declarations.push_back(IFC4X2_types[1054]);
    declarations.push_back(IFC4X2_types[1055]);
    declarations.push_back(IFC4X2_types[1056]);
    declarations.push_back(IFC4X2_types[1057]);
    declarations.push_back(IFC4X2_types[1058]);
    declarations.push_back(IFC4X2_types[1059]);
    declarations.push_back(IFC4X2_types[1060]);
    declarations.push_back(IFC4X2_types[1061]);
    declarations.push_back(IFC4X2_types[1062]);
    declarations.push_back(IFC4X2_types[1063]);
    declarations.push_back(IFC4X2_types[1064]);
    declarations.push_back(IFC4X2_types[1065]);
    declarations.push_back(IFC4X2_types[1066]);
    declarations.push_back(IFC4X2_types[1067]);
    declarations.push_back(IFC4X2_types[1068]);
    declarations.push_back(IFC4X2_types[1069]);
    declarations.push_back(IFC4X2_types[1070]);
    declarations.push_back(IFC4X2_types[1071]);
    declarations.push_back(IFC4X2_types[1072]);
    declarations.push_back(IFC4X2_types[1073]);
    declarations.push_back(IFC4X2_types[1074]);
    declarations.push_back(IFC4X2_types[1075]);
    declarations.push_back(IFC4X2_types[1076]);
    declarations.push_back(IFC4X2_types[1077]);
    declarations.push_back(IFC4X2_types[1078]);
    declarations.push_back(IFC4X2_types[1079]);
    declarations.push_back(IFC4X2_types[1080]);
    declarations.push_back(IFC4X2_types[1081]);
    declarations.push_back(IFC4X2_types[1082]);
    declarations.push_back(IFC4X2_types[1083]);
    declarations.push_back(IFC4X2_types[1084]);
    declarations.push_back(IFC4X2_types[1085]);
    declarations.push_back(IFC4X2_types[1086]);
    declarations.push_back(IFC4X2_types[1087]);
    declarations.push_back(IFC4X2_types[1088]);
    declarations.push_back(IFC4X2_types[1089]);
    declarations.push_back(IFC4X2_types[1090]);
    declarations.push_back(IFC4X2_types[1091]);
    declarations.push_back(IFC4X2_types[1092]);
    declarations.push_back(IFC4X2_types[1093]);
    declarations.push_back(IFC4X2_types[1094]);
    declarations.push_back(IFC4X2_types[1095]);
    declarations.push_back(IFC4X2_types[1096]);
    declarations.push_back(IFC4X2_types[1097]);
    declarations.push_back(IFC4X2_types[1098]);
    declarations.push_back(IFC4X2_types[1099]);
    declarations.push_back(IFC4X2_types[1100]);
    declarations.push_back(IFC4X2_types[1101]);
    declarations.push_back(IFC4X2_types[1102]);
    declarations.push_back(IFC4X2_types[1103]);
    declarations.push_back(IFC4X2_types[1104]);
    declarations.push_back(IFC4X2_types[1105]);
    declarations.push_back(IFC4X2_types[1106]);
    declarations.push_back(IFC4X2_types[1107]);
    declarations.push_back(IFC4X2_types[1108]);
    declarations.push_back(IFC4X2_types[1109]);
    declarations.push_back(IFC4X2_types[1110]);
    declarations.push_back(IFC4X2_types[1111]);
    declarations.push_back(IFC4X2_types[1112]);
    declarations.push_back(IFC4X2_types[1113]);
    declarations.push_back(IFC4X2_types[1114]);
    declarations.push_back(IFC4X2_types[1115]);
    declarations.push_back(IFC4X2_types[1116]);
    declarations.push_back(IFC4X2_types[1117]);
    declarations.push_back(IFC4X2_types[1118]);
    declarations.push_back(IFC4X2_types[1119]);
    declarations.push_back(IFC4X2_types[1120]);
    declarations.push_back(IFC4X2_types[1121]);
    declarations.push_back(IFC4X2_types[1122]);
    declarations.push_back(IFC4X2_types[1123]);
    declarations.push_back(IFC4X2_types[1124]);
    declarations.push_back(IFC4X2_types[1125]);
    declarations.push_back(IFC4X2_types[1126]);
    declarations.push_back(IFC4X2_types[1127]);
    declarations.push_back(IFC4X2_types[1128]);
    declarations.push_back(IFC4X2_types[1129]);
    declarations.push_back(IFC4X2_types[1130]);
    declarations.push_back(IFC4X2_types[1131]);
    declarations.push_back(IFC4X2_types[1132]);
    declarations.push_back(IFC4X2_types[1133]);
    declarations.push_back(IFC4X2_types[1134]);
    declarations.push_back(IFC4X2_types[1135]);
    declarations.push_back(IFC4X2_types[1136]);
    declarations.push_back(IFC4X2_types[1137]);
    declarations.push_back(IFC4X2_types[1138]);
    declarations.push_back(IFC4X2_types[1139]);
    declarations.push_back(IFC4X2_types[1140]);
    declarations.push_back(IFC4X2_types[1141]);
    declarations.push_back(IFC4X2_types[1142]);
    declarations.push_back(IFC4X2_types[1143]);
    declarations.push_back(IFC4X2_types[1144]);
    declarations.push_back(IFC4X2_types[1145]);
    declarations.push_back(IFC4X2_types[1146]);
    declarations.push_back(IFC4X2_types[1147]);
    declarations.push_back(IFC4X2_types[1148]);
    declarations.push_back(IFC4X2_types[1149]);
    declarations.push_back(IFC4X2_types[1150]);
    declarations.push_back(IFC4X2_types[1151]);
    declarations.push_back(IFC4X2_types[1152]);
    declarations.push_back(IFC4X2_types[1153]);
    declarations.push_back(IFC4X2_types[1154]);
    declarations.push_back(IFC4X2_types[1155]);
    declarations.push_back(IFC4X2_types[1156]);
    declarations.push_back(IFC4X2_types[1157]);
    declarations.push_back(IFC4X2_types[1158]);
    declarations.push_back(IFC4X2_types[1159]);
    declarations.push_back(IFC4X2_types[1160]);
    declarations.push_back(IFC4X2_types[1161]);
    declarations.push_back(IFC4X2_types[1162]);
    declarations.push_back(IFC4X2_types[1163]);
    declarations.push_back(IFC4X2_types[1164]);
    declarations.push_back(IFC4X2_types[1165]);
    declarations.push_back(IFC4X2_types[1166]);
    declarations.push_back(IFC4X2_types[1167]);
    declarations.push_back(IFC4X2_types[1168]);
    declarations.push_back(IFC4X2_types[1169]);
    declarations.push_back(IFC4X2_types[1170]);
    declarations.push_back(IFC4X2_types[1171]);
    declarations.push_back(IFC4X2_types[1172]);
    declarations.push_back(IFC4X2_types[1173]);
    declarations.push_back(IFC4X2_types[1174]);
    declarations.push_back(IFC4X2_types[1175]);
    declarations.push_back(IFC4X2_types[1176]);
    declarations.push_back(IFC4X2_types[1177]);
    declarations.push_back(IFC4X2_types[1178]);
    declarations.push_back(IFC4X2_types[1179]);
    declarations.push_back(IFC4X2_types[1180]);
    declarations.push_back(IFC4X2_types[1181]);
    declarations.push_back(IFC4X2_types[1182]);
    declarations.push_back(IFC4X2_types[1183]);
    declarations.push_back(IFC4X2_types[1184]);
    declarations.push_back(IFC4X2_types[1185]);
    declarations.push_back(IFC4X2_types[1186]);
    declarations.push_back(IFC4X2_types[1187]);
    declarations.push_back(IFC4X2_types[1188]);
    declarations.push_back(IFC4X2_types[1189]);
    declarations.push_back(IFC4X2_types[1190]);
    declarations.push_back(IFC4X2_types[1191]);
    declarations.push_back(IFC4X2_types[1192]);
    declarations.push_back(IFC4X2_types[1193]);
    declarations.push_back(IFC4X2_types[1194]);
    declarations.push_back(IFC4X2_types[1195]);
    declarations.push_back(IFC4X2_types[1196]);
    declarations.push_back(IFC4X2_types[1197]);
    declarations.push_back(IFC4X2_types[1198]);
    declarations.push_back(IFC4X2_types[1199]);
    declarations.push_back(IFC4X2_types[1200]);
    declarations.push_back(IFC4X2_types[1201]);
    declarations.push_back(IFC4X2_types[1202]);
    declarations.push_back(IFC4X2_types[1203]);
    declarations.push_back(IFC4X2_types[1204]);
    declarations.push_back(IFC4X2_types[1205]);
    declarations.push_back(IFC4X2_types[1206]);
    declarations.push_back(IFC4X2_types[1207]);
    declarations.push_back(IFC4X2_types[1208]);
    declarations.push_back(IFC4X2_types[1209]);
    declarations.push_back(IFC4X2_types[1210]);
    declarations.push_back(IFC4X2_types[1211]);
    declarations.push_back(IFC4X2_types[1212]);
    declarations.push_back(IFC4X2_types[1213]);
    declarations.push_back(IFC4X2_types[1214]);
    declarations.push_back(IFC4X2_types[1215]);
    declarations.push_back(IFC4X2_types[1216]);
    declarations.push_back(IFC4X2_types[1217]);
    declarations.push_back(IFC4X2_types[1218]);
    declarations.push_back(IFC4X2_types[1219]);
    declarations.push_back(IFC4X2_types[1220]);
    declarations.push_back(IFC4X2_types[1221]);
    declarations.push_back(IFC4X2_types[1222]);
    return new schema_definition("IFC4X2", declarations, new IFC4X2_instance_factory());
}


#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        
static std::unique_ptr<schema_definition> schema;

void Ifc4x2::clear_schema() {
    schema.reset();
}

const schema_definition& Ifc4x2::get_schema() {
    if (!schema) {
        schema.reset(IFC4X2_populate_schema());
    }
    return *schema;
}

