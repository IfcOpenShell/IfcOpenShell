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

declaration* IFC4_types[1173] = {nullptr};

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


#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* IFC4_populate_schema() {
    IFC4_types[0] = new type_declaration("IfcAbsorbedDoseMeasure", 0, new simple_type(simple_type::real_type));
    IFC4_types[1] = new type_declaration("IfcAccelerationMeasure", 1, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("EMAIL");
        items.push_back("FAX");
        items.push_back("NOTDEFINED");
        items.push_back("PHONE");
        items.push_back("POST");
        items.push_back("USERDEFINED");
        items.push_back("VERBAL");
        IFC4_types[3] = new enumeration_type("IfcActionRequestTypeEnum", 3, items);
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
        IFC4_types[4] = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IFC4_types[5] = new enumeration_type("IfcActionTypeEnum", 5, items);
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
        IFC4_types[11] = new enumeration_type("IfcActuatorTypeEnum", 11, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4_types[13] = new enumeration_type("IfcAddressTypeEnum", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IFC4_types[20] = new enumeration_type("IfcAirTerminalBoxTypeEnum", 20, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("DIFFUSER");
        items.push_back("GRILLE");
        items.push_back("LOUVRE");
        items.push_back("NOTDEFINED");
        items.push_back("REGISTER");
        items.push_back("USERDEFINED");
        IFC4_types[22] = new enumeration_type("IfcAirTerminalTypeEnum", 22, items);
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
        IFC4_types[25] = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 25, items);
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
        IFC4_types[28] = new enumeration_type("IfcAlarmTypeEnum", 28, items);
    }
    IFC4_types[29] = new type_declaration("IfcAmountOfSubstanceMeasure", 29, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IFC4_types[30] = new enumeration_type("IfcAnalysisModelTypeEnum", 30, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IFC4_types[31] = new enumeration_type("IfcAnalysisTheoryTypeEnum", 31, items);
    }
    IFC4_types[32] = new type_declaration("IfcAngularVelocityMeasure", 32, new simple_type(simple_type::real_type));
    IFC4_types[44] = new type_declaration("IfcAreaDensityMeasure", 44, new simple_type(simple_type::real_type));
    IFC4_types[45] = new type_declaration("IfcAreaMeasure", 45, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IFC4_types[46] = new enumeration_type("IfcArithmeticOperatorEnum", 46, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IFC4_types[47] = new enumeration_type("IfcAssemblyPlaceEnum", 47, items);
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
        IFC4_types[52] = new enumeration_type("IfcAudioVisualApplianceTypeEnum", 52, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IFC4_types[86] = new enumeration_type("IfcBSplineCurveForm", 86, items);
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
        IFC4_types[89] = new enumeration_type("IfcBSplineSurfaceForm", 89, items);
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
        IFC4_types[60] = new enumeration_type("IfcBeamTypeEnum", 60, items);
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
        IFC4_types[61] = new enumeration_type("IfcBenchmarkEnum", 61, items);
    }
    IFC4_types[63] = new type_declaration("IfcBinary", 63, new simple_type(simple_type::binary_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IFC4_types[68] = new enumeration_type("IfcBoilerTypeEnum", 68, items);
    }
    IFC4_types[69] = new type_declaration("IfcBoolean", 69, new simple_type(simple_type::boolean_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IFC4_types[72] = new enumeration_type("IfcBooleanOperator", 72, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("INSULATION");
        items.push_back("NOTDEFINED");
        items.push_back("PRECASTPANEL");
        items.push_back("USERDEFINED");
        IFC4_types[95] = new enumeration_type("IfcBuildingElementPartTypeEnum", 95, items);
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
        IFC4_types[98] = new enumeration_type("IfcBuildingElementProxyTypeEnum", 98, items);
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
        IFC4_types[102] = new enumeration_type("IfcBuildingSystemTypeEnum", 102, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[105] = new enumeration_type("IfcBurnerTypeEnum", 105, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IFC4_types[108] = new enumeration_type("IfcCableCarrierFittingTypeEnum", 108, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[111] = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 111, items);
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
        IFC4_types[114] = new enumeration_type("IfcCableFittingTypeEnum", 114, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BUSBARSEGMENT");
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("CORESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[117] = new enumeration_type("IfcCableSegmentTypeEnum", 117, items);
    }
    IFC4_types[118] = new type_declaration("IfcCardinalPointReference", 118, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("NOCHANGE");
        items.push_back("NOTDEFINED");
        IFC4_types[129] = new enumeration_type("IfcChangeActionEnum", 129, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IFC4_types[132] = new enumeration_type("IfcChillerTypeEnum", 132, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[135] = new enumeration_type("IfcChimneyTypeEnum", 135, items);
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
        IFC4_types[148] = new enumeration_type("IfcCoilTypeEnum", 148, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("PILASTER");
        items.push_back("USERDEFINED");
        IFC4_types[157] = new enumeration_type("IfcColumnTypeEnum", 157, items);
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
        IFC4_types[160] = new enumeration_type("IfcCommunicationsApplianceTypeEnum", 160, items);
    }
    IFC4_types[161] = new type_declaration("IfcComplexNumber", 161, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("P_COMPLEX");
        items.push_back("Q_COMPLEX");
        IFC4_types[164] = new enumeration_type("IfcComplexPropertyTemplateTypeEnum", 164, items);
    }
    IFC4_types[169] = new type_declaration("IfcCompoundPlaneAngleMeasure", 169, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
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
        IFC4_types[172] = new enumeration_type("IfcCompressorTypeEnum", 172, items);
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
        IFC4_types[175] = new enumeration_type("IfcCondenserTypeEnum", 175, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IFC4_types[183] = new enumeration_type("IfcConnectionTypeEnum", 183, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IFC4_types[186] = new enumeration_type("IfcConstraintEnum", 186, items);
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
        IFC4_types[189] = new enumeration_type("IfcConstructionEquipmentResourceTypeEnum", 189, items);
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
        IFC4_types[192] = new enumeration_type("IfcConstructionMaterialResourceTypeEnum", 192, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ASSEMBLY");
        items.push_back("FORMWORK");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[195] = new enumeration_type("IfcConstructionProductResourceTypeEnum", 195, items);
    }
    IFC4_types[199] = new type_declaration("IfcContextDependentMeasure", 199, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("FLOATING");
        items.push_back("MULTIPOSITION");
        items.push_back("NOTDEFINED");
        items.push_back("PROGRAMMABLE");
        items.push_back("PROPORTIONAL");
        items.push_back("TWOPOSITION");
        items.push_back("USERDEFINED");
        IFC4_types[204] = new enumeration_type("IfcControllerTypeEnum", 204, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IFC4_types[209] = new enumeration_type("IfcCooledBeamTypeEnum", 209, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[212] = new enumeration_type("IfcCoolingTowerTypeEnum", 212, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[217] = new enumeration_type("IfcCostItemTypeEnum", 217, items);
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
        IFC4_types[219] = new enumeration_type("IfcCostScheduleTypeEnum", 219, items);
    }
    IFC4_types[221] = new type_declaration("IfcCountMeasure", 221, new simple_type(simple_type::number_type));
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
        IFC4_types[224] = new enumeration_type("IfcCoveringTypeEnum", 224, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IFC4_types[227] = new enumeration_type("IfcCrewResourceTypeEnum", 227, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[235] = new enumeration_type("IfcCurtainWallTypeEnum", 235, items);
    }
    IFC4_types[236] = new type_declaration("IfcCurvatureMeasure", 236, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LINEAR");
        items.push_back("LOG_LINEAR");
        items.push_back("LOG_LOG");
        items.push_back("NOTDEFINED");
        IFC4_types[241] = new enumeration_type("IfcCurveInterpolationEnum", 241, items);
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
        IFC4_types[252] = new enumeration_type("IfcDamperTypeEnum", 252, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IFC4_types[253] = new enumeration_type("IfcDataOriginEnum", 253, items);
    }
    IFC4_types[254] = new type_declaration("IfcDate", 254, new simple_type(simple_type::string_type));
    IFC4_types[255] = new type_declaration("IfcDateTime", 255, new simple_type(simple_type::string_type));
    IFC4_types[256] = new type_declaration("IfcDayInMonthNumber", 256, new simple_type(simple_type::integer_type));
    IFC4_types[257] = new type_declaration("IfcDayInWeekNumber", 257, new simple_type(simple_type::integer_type));
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
        IFC4_types[263] = new enumeration_type("IfcDerivedUnitEnum", 263, items);
    }
    IFC4_types[264] = new type_declaration("IfcDescriptiveMeasure", 264, new simple_type(simple_type::string_type));
    IFC4_types[266] = new type_declaration("IfcDimensionCount", 266, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4_types[268] = new enumeration_type("IfcDirectionSenseEnum", 268, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ANCHORPLATE");
        items.push_back("BRACKET");
        items.push_back("NOTDEFINED");
        items.push_back("SHOE");
        items.push_back("USERDEFINED");
        IFC4_types[271] = new enumeration_type("IfcDiscreteAccessoryTypeEnum", 271, items);
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
        IFC4_types[274] = new enumeration_type("IfcDistributionChamberElementTypeEnum", 274, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLE");
        items.push_back("CABLECARRIER");
        items.push_back("DUCT");
        items.push_back("NOTDEFINED");
        items.push_back("PIPE");
        items.push_back("USERDEFINED");
        IFC4_types[283] = new enumeration_type("IfcDistributionPortTypeEnum", 283, items);
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
        IFC4_types[285] = new enumeration_type("IfcDistributionSystemEnum", 285, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IFC4_types[286] = new enumeration_type("IfcDocumentConfidentialityEnum", 286, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IFC4_types[291] = new enumeration_type("IfcDocumentStatusEnum", 291, items);
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
        IFC4_types[294] = new enumeration_type("IfcDoorPanelOperationEnum", 294, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IFC4_types[295] = new enumeration_type("IfcDoorPanelPositionEnum", 295, items);
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
        IFC4_types[299] = new enumeration_type("IfcDoorStyleConstructionEnum", 299, items);
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
        IFC4_types[300] = new enumeration_type("IfcDoorStyleOperationEnum", 300, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DOOR");
        items.push_back("GATE");
        items.push_back("NOTDEFINED");
        items.push_back("TRAPDOOR");
        items.push_back("USERDEFINED");
        IFC4_types[302] = new enumeration_type("IfcDoorTypeEnum", 302, items);
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
        IFC4_types[303] = new enumeration_type("IfcDoorTypeOperationEnum", 303, items);
    }
    IFC4_types[304] = new type_declaration("IfcDoseEquivalentMeasure", 304, new simple_type(simple_type::real_type));
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
        IFC4_types[309] = new enumeration_type("IfcDuctFittingTypeEnum", 309, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IFC4_types[312] = new enumeration_type("IfcDuctSegmentTypeEnum", 312, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IFC4_types[315] = new enumeration_type("IfcDuctSilencerTypeEnum", 315, items);
    }
    IFC4_types[316] = new type_declaration("IfcDuration", 316, new simple_type(simple_type::string_type));
    IFC4_types[317] = new type_declaration("IfcDynamicViscosityMeasure", 317, new simple_type(simple_type::real_type));
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
        IFC4_types[323] = new enumeration_type("IfcElectricApplianceTypeEnum", 323, items);
    }
    IFC4_types[324] = new type_declaration("IfcElectricCapacitanceMeasure", 324, new simple_type(simple_type::real_type));
    IFC4_types[325] = new type_declaration("IfcElectricChargeMeasure", 325, new simple_type(simple_type::real_type));
    IFC4_types[326] = new type_declaration("IfcElectricConductanceMeasure", 326, new simple_type(simple_type::real_type));
    IFC4_types[327] = new type_declaration("IfcElectricCurrentMeasure", 327, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONSUMERUNIT");
        items.push_back("DISTRIBUTIONBOARD");
        items.push_back("MOTORCONTROLCENTRE");
        items.push_back("NOTDEFINED");
        items.push_back("SWITCHBOARD");
        items.push_back("USERDEFINED");
        IFC4_types[330] = new enumeration_type("IfcElectricDistributionBoardTypeEnum", 330, items);
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
        IFC4_types[333] = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 333, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CHP");
        items.push_back("ENGINEGENERATOR");
        items.push_back("NOTDEFINED");
        items.push_back("STANDALONE");
        items.push_back("USERDEFINED");
        IFC4_types[336] = new enumeration_type("IfcElectricGeneratorTypeEnum", 336, items);
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
        IFC4_types[339] = new enumeration_type("IfcElectricMotorTypeEnum", 339, items);
    }
    IFC4_types[340] = new type_declaration("IfcElectricResistanceMeasure", 340, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IFC4_types[343] = new enumeration_type("IfcElectricTimeControlTypeEnum", 343, items);
    }
    IFC4_types[344] = new type_declaration("IfcElectricVoltageMeasure", 344, new simple_type(simple_type::real_type));
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
        IFC4_types[349] = new enumeration_type("IfcElementAssemblyTypeEnum", 349, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IFC4_types[352] = new enumeration_type("IfcElementCompositionEnum", 352, items);
    }
    IFC4_types[359] = new type_declaration("IfcEnergyMeasure", 359, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("EXTERNALCOMBUSTION");
        items.push_back("INTERNALCOMBUSTION");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[362] = new enumeration_type("IfcEngineTypeEnum", 362, items);
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
        IFC4_types[365] = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 365, items);
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
        IFC4_types[368] = new enumeration_type("IfcEvaporatorTypeEnum", 368, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EVENTCOMPLEX");
        items.push_back("EVENTMESSAGE");
        items.push_back("EVENTRULE");
        items.push_back("EVENTTIME");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[371] = new enumeration_type("IfcEventTriggerTypeEnum", 371, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ENDEVENT");
        items.push_back("INTERMEDIATEEVENT");
        items.push_back("NOTDEFINED");
        items.push_back("STARTEVENT");
        items.push_back("USERDEFINED");
        IFC4_types[373] = new enumeration_type("IfcEventTypeEnum", 373, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[382] = new enumeration_type("IfcExternalSpatialElementTypeEnum", 382, items);
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
        IFC4_types[396] = new enumeration_type("IfcFanTypeEnum", 396, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GLUE");
        items.push_back("MORTAR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WELD");
        IFC4_types[399] = new enumeration_type("IfcFastenerTypeEnum", 399, items);
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
        IFC4_types[409] = new enumeration_type("IfcFilterTypeEnum", 409, items);
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
        IFC4_types[412] = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 412, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IFC4_types[416] = new enumeration_type("IfcFlowDirectionEnum", 416, items);
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
        IFC4_types[421] = new enumeration_type("IfcFlowInstrumentTypeEnum", 421, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ENERGYMETER");
        items.push_back("GASMETER");
        items.push_back("NOTDEFINED");
        items.push_back("OILMETER");
        items.push_back("USERDEFINED");
        items.push_back("WATERMETER");
        IFC4_types[424] = new enumeration_type("IfcFlowMeterTypeEnum", 424, items);
    }
    IFC4_types[435] = new type_declaration("IfcFontStyle", 435, new simple_type(simple_type::string_type));
    IFC4_types[436] = new type_declaration("IfcFontVariant", 436, new simple_type(simple_type::string_type));
    IFC4_types[437] = new type_declaration("IfcFontWeight", 437, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CAISSON_FOUNDATION");
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IFC4_types[440] = new enumeration_type("IfcFootingTypeEnum", 440, items);
    }
    IFC4_types[441] = new type_declaration("IfcForceMeasure", 441, new simple_type(simple_type::real_type));
    IFC4_types[442] = new type_declaration("IfcFrequencyMeasure", 442, new simple_type(simple_type::real_type));
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
        IFC4_types[447] = new enumeration_type("IfcFurnitureTypeEnum", 447, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("TERRAIN");
        items.push_back("USERDEFINED");
        IFC4_types[450] = new enumeration_type("IfcGeographicElementTypeEnum", 450, items);
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
        IFC4_types[452] = new enumeration_type("IfcGeometricProjectionEnum", 452, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IFC4_types[459] = new enumeration_type("IfcGlobalOrLocalEnum", 459, items);
    }
    IFC4_types[458] = new type_declaration("IfcGloballyUniqueId", 458, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("IRREGULAR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIAL");
        items.push_back("RECTANGULAR");
        items.push_back("TRIANGULAR");
        items.push_back("USERDEFINED");
        IFC4_types[464] = new enumeration_type("IfcGridTypeEnum", 464, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IFC4_types[470] = new enumeration_type("IfcHeatExchangerTypeEnum", 470, items);
    }
    IFC4_types[471] = new type_declaration("IfcHeatFluxDensityMeasure", 471, new simple_type(simple_type::real_type));
    IFC4_types[472] = new type_declaration("IfcHeatingValueMeasure", 472, new simple_type(simple_type::real_type));
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
        IFC4_types[475] = new enumeration_type("IfcHumidifierTypeEnum", 475, items);
    }
    IFC4_types[476] = new type_declaration("IfcIdentifier", 476, new simple_type(simple_type::string_type));
    IFC4_types[477] = new type_declaration("IfcIlluminanceMeasure", 477, new simple_type(simple_type::real_type));
    IFC4_types[485] = new type_declaration("IfcInductanceMeasure", 485, new simple_type(simple_type::real_type));
    IFC4_types[486] = new type_declaration("IfcInteger", 486, new simple_type(simple_type::integer_type));
    IFC4_types[487] = new type_declaration("IfcIntegerCountRateMeasure", 487, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CYCLONIC");
        items.push_back("GREASE");
        items.push_back("NOTDEFINED");
        items.push_back("OIL");
        items.push_back("PETROL");
        items.push_back("USERDEFINED");
        IFC4_types[490] = new enumeration_type("IfcInterceptorTypeEnum", 490, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXTERNAL");
        items.push_back("EXTERNAL_EARTH");
        items.push_back("EXTERNAL_FIRE");
        items.push_back("EXTERNAL_WATER");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IFC4_types[491] = new enumeration_type("IfcInternalOrExternalEnum", 491, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IFC4_types[494] = new enumeration_type("IfcInventoryTypeEnum", 494, items);
    }
    IFC4_types[495] = new type_declaration("IfcIonConcentrationMeasure", 495, new simple_type(simple_type::real_type));
    IFC4_types[499] = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 499, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DATA");
        items.push_back("NOTDEFINED");
        items.push_back("POWER");
        items.push_back("USERDEFINED");
        IFC4_types[502] = new enumeration_type("IfcJunctionBoxTypeEnum", 502, items);
    }
    IFC4_types[503] = new type_declaration("IfcKinematicViscosityMeasure", 503, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("PIECEWISE_BEZIER_KNOTS");
        items.push_back("QUASI_UNIFORM_KNOTS");
        items.push_back("UNIFORM_KNOTS");
        items.push_back("UNSPECIFIED");
        IFC4_types[504] = new enumeration_type("IfcKnotType", 504, items);
    }
    IFC4_types[505] = new type_declaration("IfcLabel", 505, new simple_type(simple_type::string_type));
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
        IFC4_types[508] = new enumeration_type("IfcLaborResourceTypeEnum", 508, items);
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
        IFC4_types[512] = new enumeration_type("IfcLampTypeEnum", 512, items);
    }
    IFC4_types[513] = new type_declaration("IfcLanguageId", 513, new named_type(IFC4_types[476]));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IFC4_types[515] = new enumeration_type("IfcLayerSetDirectionEnum", 515, items);
    }
    IFC4_types[516] = new type_declaration("IfcLengthMeasure", 516, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IFC4_types[520] = new enumeration_type("IfcLightDistributionCurveEnum", 520, items);
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
        IFC4_types[523] = new enumeration_type("IfcLightEmissionSourceEnum", 523, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("SECURITYLIGHTING");
        items.push_back("USERDEFINED");
        IFC4_types[526] = new enumeration_type("IfcLightFixtureTypeEnum", 526, items);
    }
    IFC4_types[535] = new type_declaration("IfcLinearForceMeasure", 535, new simple_type(simple_type::real_type));
    IFC4_types[536] = new type_declaration("IfcLinearMomentMeasure", 536, new simple_type(simple_type::real_type));
    IFC4_types[537] = new type_declaration("IfcLinearStiffnessMeasure", 537, new simple_type(simple_type::real_type));
    IFC4_types[538] = new type_declaration("IfcLinearVelocityMeasure", 538, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[540] = new enumeration_type("IfcLoadGroupTypeEnum", 540, items);
    }
    IFC4_types[542] = new type_declaration("IfcLogical", 542, new simple_type(simple_type::logical_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALNOTAND");
        items.push_back("LOGICALNOTOR");
        items.push_back("LOGICALOR");
        items.push_back("LOGICALXOR");
        IFC4_types[543] = new enumeration_type("IfcLogicalOperatorEnum", 543, items);
    }
    IFC4_types[546] = new type_declaration("IfcLuminousFluxMeasure", 546, new simple_type(simple_type::real_type));
    IFC4_types[547] = new type_declaration("IfcLuminousIntensityDistributionMeasure", 547, new simple_type(simple_type::real_type));
    IFC4_types[548] = new type_declaration("IfcLuminousIntensityMeasure", 548, new simple_type(simple_type::real_type));
    IFC4_types[549] = new type_declaration("IfcMagneticFluxDensityMeasure", 549, new simple_type(simple_type::real_type));
    IFC4_types[550] = new type_declaration("IfcMagneticFluxMeasure", 550, new simple_type(simple_type::real_type));
    IFC4_types[554] = new type_declaration("IfcMassDensityMeasure", 554, new simple_type(simple_type::real_type));
    IFC4_types[555] = new type_declaration("IfcMassFlowRateMeasure", 555, new simple_type(simple_type::real_type));
    IFC4_types[556] = new type_declaration("IfcMassMeasure", 556, new simple_type(simple_type::real_type));
    IFC4_types[557] = new type_declaration("IfcMassPerLengthMeasure", 557, new simple_type(simple_type::real_type));
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
        IFC4_types[582] = new enumeration_type("IfcMechanicalFastenerTypeEnum", 582, items);
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
        IFC4_types[585] = new enumeration_type("IfcMedicalDeviceTypeEnum", 585, items);
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
        IFC4_types[589] = new enumeration_type("IfcMemberTypeEnum", 589, items);
    }
    IFC4_types[593] = new type_declaration("IfcModulusOfElasticityMeasure", 593, new simple_type(simple_type::real_type));
    IFC4_types[594] = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 594, new simple_type(simple_type::real_type));
    IFC4_types[595] = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 595, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[595]);
        IFC4_types[596] = new select_type("IfcModulusOfRotationalSubgradeReactionSelect", 596, items);
    }
    IFC4_types[597] = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 597, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[597]);
        IFC4_types[598] = new select_type("IfcModulusOfSubgradeReactionSelect", 598, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[594]);
        IFC4_types[599] = new select_type("IfcModulusOfTranslationalSubgradeReactionSelect", 599, items);
    }
    IFC4_types[600] = new type_declaration("IfcMoistureDiffusivityMeasure", 600, new simple_type(simple_type::real_type));
    IFC4_types[601] = new type_declaration("IfcMolecularWeightMeasure", 601, new simple_type(simple_type::real_type));
    IFC4_types[602] = new type_declaration("IfcMomentOfInertiaMeasure", 602, new simple_type(simple_type::real_type));
    IFC4_types[603] = new type_declaration("IfcMonetaryMeasure", 603, new simple_type(simple_type::real_type));
    IFC4_types[605] = new type_declaration("IfcMonthInYearNumber", 605, new simple_type(simple_type::integer_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[608] = new enumeration_type("IfcMotorConnectionTypeEnum", 608, items);
    }
    IFC4_types[610] = new type_declaration("IfcNonNegativeLengthMeasure", 610, new named_type(IFC4_types[516]));
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IFC4_types[612] = new enumeration_type("IfcNullStyle", 612, items);
    }
    IFC4_types[613] = new type_declaration("IfcNumericMeasure", 613, new simple_type(simple_type::number_type));
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
        IFC4_types[620] = new enumeration_type("IfcObjectTypeEnum", 620, items);
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
        IFC4_types[617] = new enumeration_type("IfcObjectiveEnum", 617, items);
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
        IFC4_types[622] = new enumeration_type("IfcOccupantTypeEnum", 622, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("OPENING");
        items.push_back("RECESS");
        items.push_back("USERDEFINED");
        IFC4_types[626] = new enumeration_type("IfcOpeningElementTypeEnum", 626, items);
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
        IFC4_types[635] = new enumeration_type("IfcOutletTypeEnum", 635, items);
    }
    IFC4_types[649] = new type_declaration("IfcPHMeasure", 649, new simple_type(simple_type::real_type));
    IFC4_types[638] = new type_declaration("IfcParameterValue", 638, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[642] = new enumeration_type("IfcPerformanceHistoryTypeEnum", 642, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IFC4_types[643] = new enumeration_type("IfcPermeableCoveringOperationEnum", 643, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACCESS");
        items.push_back("BUILDING");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4_types[646] = new enumeration_type("IfcPermitTypeEnum", 646, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IFC4_types[651] = new enumeration_type("IfcPhysicalOrVirtualEnum", 651, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IFC4_types[655] = new enumeration_type("IfcPileConstructionEnum", 655, items);
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
        IFC4_types[657] = new enumeration_type("IfcPileTypeEnum", 657, items);
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
        IFC4_types[660] = new enumeration_type("IfcPipeFittingTypeEnum", 660, items);
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
        IFC4_types[663] = new enumeration_type("IfcPipeSegmentTypeEnum", 663, items);
    }
    IFC4_types[668] = new type_declaration("IfcPlanarForceMeasure", 668, new simple_type(simple_type::real_type));
    IFC4_types[670] = new type_declaration("IfcPlaneAngleMeasure", 670, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IFC4_types[674] = new enumeration_type("IfcPlateTypeEnum", 674, items);
    }
    IFC4_types[684] = new type_declaration("IfcPositiveInteger", 684, new named_type(IFC4_types[486]));
    IFC4_types[685] = new type_declaration("IfcPositiveLengthMeasure", 685, new named_type(IFC4_types[516]));
    IFC4_types[686] = new type_declaration("IfcPositivePlaneAngleMeasure", 686, new named_type(IFC4_types[670]));
    IFC4_types[689] = new type_declaration("IfcPowerMeasure", 689, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CURVE3D");
        items.push_back("PCURVE_S1");
        items.push_back("PCURVE_S2");
        IFC4_types[696] = new enumeration_type("IfcPreferredSurfaceCurveRepresentation", 696, items);
    }
    IFC4_types[697] = new type_declaration("IfcPresentableText", 697, new simple_type(simple_type::string_type));
    IFC4_types[704] = new type_declaration("IfcPressureMeasure", 704, new simple_type(simple_type::real_type));
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
        IFC4_types[707] = new enumeration_type("IfcProcedureTypeEnum", 707, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IFC4_types[717] = new enumeration_type("IfcProfileTypeEnum", 717, items);
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
        IFC4_types[725] = new enumeration_type("IfcProjectOrderTypeEnum", 725, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IFC4_types[720] = new enumeration_type("IfcProjectedOrTrueLengthEnum", 720, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[722] = new enumeration_type("IfcProjectionElementTypeEnum", 722, items);
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
        IFC4_types[740] = new enumeration_type("IfcPropertySetTemplateTypeEnum", 740, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ELECTROMAGNETIC");
        items.push_back("ELECTRONIC");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENT");
        items.push_back("THERMAL");
        items.push_back("USERDEFINED");
        IFC4_types[748] = new enumeration_type("IfcProtectiveDeviceTrippingUnitTypeEnum", 748, items);
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
        IFC4_types[750] = new enumeration_type("IfcProtectiveDeviceTypeEnum", 750, items);
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
        IFC4_types[754] = new enumeration_type("IfcPumpTypeEnum", 754, items);
    }
    IFC4_types[762] = new type_declaration("IfcRadioActivityMeasure", 762, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[765] = new enumeration_type("IfcRailingTypeEnum", 765, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IFC4_types[769] = new enumeration_type("IfcRampFlightTypeEnum", 769, items);
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
        IFC4_types[771] = new enumeration_type("IfcRampTypeEnum", 771, items);
    }
    IFC4_types[772] = new type_declaration("IfcRatioMeasure", 772, new simple_type(simple_type::real_type));
    IFC4_types[775] = new type_declaration("IfcReal", 775, new simple_type(simple_type::real_type));
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
        IFC4_types[781] = new enumeration_type("IfcRecurrenceTypeEnum", 781, items);
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
        IFC4_types[783] = new enumeration_type("IfcReflectanceMethodEnum", 783, items);
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
        IFC4_types[788] = new enumeration_type("IfcReinforcingBarRoleEnum", 788, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IFC4_types[789] = new enumeration_type("IfcReinforcingBarSurfaceEnum", 789, items);
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
        IFC4_types[791] = new enumeration_type("IfcReinforcingBarTypeEnum", 791, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[796] = new enumeration_type("IfcReinforcingMeshTypeEnum", 796, items);
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
        IFC4_types[861] = new enumeration_type("IfcRoleEnum", 861, items);
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
        IFC4_types[864] = new enumeration_type("IfcRoofTypeEnum", 864, items);
    }
    IFC4_types[866] = new type_declaration("IfcRotationalFrequencyMeasure", 866, new simple_type(simple_type::real_type));
    IFC4_types[867] = new type_declaration("IfcRotationalMassMeasure", 867, new simple_type(simple_type::real_type));
    IFC4_types[868] = new type_declaration("IfcRotationalStiffnessMeasure", 868, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[868]);
        IFC4_types[869] = new select_type("IfcRotationalStiffnessSelect", 869, items);
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
        IFC4_types[900] = new enumeration_type("IfcSIPrefix", 900, items);
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
        IFC4_types[903] = new enumeration_type("IfcSIUnitName", 903, items);
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
        IFC4_types[873] = new enumeration_type("IfcSanitaryTerminalTypeEnum", 873, items);
    }
    IFC4_types[878] = new type_declaration("IfcSectionModulusMeasure", 878, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IFC4_types[881] = new enumeration_type("IfcSectionTypeEnum", 881, items);
    }
    IFC4_types[876] = new type_declaration("IfcSectionalAreaIntegralMeasure", 876, new simple_type(simple_type::real_type));
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
        IFC4_types[885] = new enumeration_type("IfcSensorTypeEnum", 885, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        items.push_back("USERDEFINED");
        IFC4_types[886] = new enumeration_type("IfcSequenceEnum", 886, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AWNING");
        items.push_back("JALOUSIE");
        items.push_back("NOTDEFINED");
        items.push_back("SHUTTER");
        items.push_back("USERDEFINED");
        IFC4_types[889] = new enumeration_type("IfcShadingDeviceTypeEnum", 889, items);
    }
    IFC4_types[893] = new type_declaration("IfcShearModulusMeasure", 893, new simple_type(simple_type::real_type));
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
        IFC4_types[898] = new enumeration_type("IfcSimplePropertyTemplateTypeEnum", 898, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IFC4_types[909] = new enumeration_type("IfcSlabTypeEnum", 909, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SOLARCOLLECTOR");
        items.push_back("SOLARPANEL");
        items.push_back("USERDEFINED");
        IFC4_types[913] = new enumeration_type("IfcSolarDeviceTypeEnum", 913, items);
    }
    IFC4_types[914] = new type_declaration("IfcSolidAngleMeasure", 914, new simple_type(simple_type::real_type));
    IFC4_types[917] = new type_declaration("IfcSoundPowerLevelMeasure", 917, new simple_type(simple_type::real_type));
    IFC4_types[918] = new type_declaration("IfcSoundPowerMeasure", 918, new simple_type(simple_type::real_type));
    IFC4_types[919] = new type_declaration("IfcSoundPressureLevelMeasure", 919, new simple_type(simple_type::real_type));
    IFC4_types[920] = new type_declaration("IfcSoundPressureMeasure", 920, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONVECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RADIATOR");
        items.push_back("USERDEFINED");
        IFC4_types[925] = new enumeration_type("IfcSpaceHeaterTypeEnum", 925, items);
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
        IFC4_types[927] = new enumeration_type("IfcSpaceTypeEnum", 927, items);
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
        IFC4_types[934] = new enumeration_type("IfcSpatialZoneTypeEnum", 934, items);
    }
    IFC4_types[935] = new type_declaration("IfcSpecificHeatCapacityMeasure", 935, new simple_type(simple_type::real_type));
    IFC4_types[936] = new type_declaration("IfcSpecularExponent", 936, new simple_type(simple_type::real_type));
    IFC4_types[938] = new type_declaration("IfcSpecularRoughness", 938, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IFC4_types[943] = new enumeration_type("IfcStackTerminalTypeEnum", 943, items);
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
        IFC4_types[947] = new enumeration_type("IfcStairFlightTypeEnum", 947, items);
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
        IFC4_types[949] = new enumeration_type("IfcStairTypeEnum", 949, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IFC4_types[950] = new enumeration_type("IfcStateEnum", 950, items);
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
        IFC4_types[958] = new enumeration_type("IfcStructuralCurveActivityTypeEnum", 958, items);
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
        IFC4_types[961] = new enumeration_type("IfcStructuralCurveMemberTypeEnum", 961, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BILINEAR");
        items.push_back("CONST");
        items.push_back("DISCRETE");
        items.push_back("ISOCONTOUR");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[987] = new enumeration_type("IfcStructuralSurfaceActivityTypeEnum", 987, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IFC4_types[990] = new enumeration_type("IfcStructuralSurfaceMemberTypeEnum", 990, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IFC4_types[999] = new enumeration_type("IfcSubContractResourceTypeEnum", 999, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MARK");
        items.push_back("NOTDEFINED");
        items.push_back("TAG");
        items.push_back("TREATMENT");
        items.push_back("USERDEFINED");
        IFC4_types[1005] = new enumeration_type("IfcSurfaceFeatureTypeEnum", 1005, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IFC4_types[1010] = new enumeration_type("IfcSurfaceSide", 1010, items);
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
        IFC4_types[1025] = new enumeration_type("IfcSwitchingDeviceTypeEnum", 1025, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PANEL");
        items.push_back("USERDEFINED");
        items.push_back("WORKSURFACE");
        IFC4_types[1029] = new enumeration_type("IfcSystemFurnitureElementTypeEnum", 1029, items);
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
        IFC4_types[1035] = new enumeration_type("IfcTankTypeEnum", 1035, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ELAPSEDTIME");
        items.push_back("NOTDEFINED");
        items.push_back("WORKTIME");
        IFC4_types[1037] = new enumeration_type("IfcTaskDurationEnum", 1037, items);
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
        IFC4_types[1041] = new enumeration_type("IfcTaskTypeEnum", 1041, items);
    }
    IFC4_types[1043] = new type_declaration("IfcTemperatureGradientMeasure", 1043, new simple_type(simple_type::real_type));
    IFC4_types[1044] = new type_declaration("IfcTemperatureRateOfChangeMeasure", 1044, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COUPLER");
        items.push_back("FIXED_END");
        items.push_back("NOTDEFINED");
        items.push_back("TENSIONING_END");
        items.push_back("USERDEFINED");
        IFC4_types[1048] = new enumeration_type("IfcTendonAnchorTypeEnum", 1048, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IFC4_types[1050] = new enumeration_type("IfcTendonTypeEnum", 1050, items);
    }
    IFC4_types[1053] = new type_declaration("IfcText", 1053, new simple_type(simple_type::string_type));
    IFC4_types[1054] = new type_declaration("IfcTextAlignment", 1054, new simple_type(simple_type::string_type));
    IFC4_types[1055] = new type_declaration("IfcTextDecoration", 1055, new simple_type(simple_type::string_type));
    IFC4_types[1056] = new type_declaration("IfcTextFontName", 1056, new simple_type(simple_type::string_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IFC4_types[1060] = new enumeration_type("IfcTextPath", 1060, items);
    }
    IFC4_types[1065] = new type_declaration("IfcTextTransformation", 1065, new simple_type(simple_type::string_type));
    IFC4_types[1071] = new type_declaration("IfcThermalAdmittanceMeasure", 1071, new simple_type(simple_type::real_type));
    IFC4_types[1072] = new type_declaration("IfcThermalConductivityMeasure", 1072, new simple_type(simple_type::real_type));
    IFC4_types[1073] = new type_declaration("IfcThermalExpansionCoefficientMeasure", 1073, new simple_type(simple_type::real_type));
    IFC4_types[1074] = new type_declaration("IfcThermalResistanceMeasure", 1074, new simple_type(simple_type::real_type));
    IFC4_types[1075] = new type_declaration("IfcThermalTransmittanceMeasure", 1075, new simple_type(simple_type::real_type));
    IFC4_types[1076] = new type_declaration("IfcThermodynamicTemperatureMeasure", 1076, new simple_type(simple_type::real_type));
    IFC4_types[1077] = new type_declaration("IfcTime", 1077, new simple_type(simple_type::string_type));
    IFC4_types[1078] = new type_declaration("IfcTimeMeasure", 1078, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[316]);
        items.push_back(IFC4_types[772]);
        IFC4_types[1079] = new select_type("IfcTimeOrRatioSelect", 1079, items);
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
        IFC4_types[1082] = new enumeration_type("IfcTimeSeriesDataTypeEnum", 1082, items);
    }
    IFC4_types[1084] = new type_declaration("IfcTimeStamp", 1084, new simple_type(simple_type::integer_type));
    IFC4_types[1088] = new type_declaration("IfcTorqueMeasure", 1088, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("INVERTER");
        items.push_back("NOTDEFINED");
        items.push_back("RECTIFIER");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IFC4_types[1091] = new enumeration_type("IfcTransformerTypeEnum", 1091, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IFC4_types[1092] = new enumeration_type("IfcTransitionCode", 1092, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[537]);
        IFC4_types[1093] = new select_type("IfcTranslationalStiffnessSelect", 1093, items);
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
        IFC4_types[1096] = new enumeration_type("IfcTransportElementTypeEnum", 1096, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IFC4_types[1100] = new enumeration_type("IfcTrimmingPreference", 1100, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IFC4_types[1105] = new enumeration_type("IfcTubeBundleTypeEnum", 1105, items);
    }
    IFC4_types[1119] = new type_declaration("IfcURIReference", 1119, new simple_type(simple_type::string_type));
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
        IFC4_types[1118] = new enumeration_type("IfcUnitEnum", 1118, items);
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
        IFC4_types[1113] = new enumeration_type("IfcUnitaryControlElementTypeEnum", 1113, items);
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
        IFC4_types[1116] = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 1116, items);
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
        IFC4_types[1124] = new enumeration_type("IfcValveTypeEnum", 1124, items);
    }
    IFC4_types[1125] = new type_declaration("IfcVaporPermeabilityMeasure", 1125, new simple_type(simple_type::real_type));
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IFC4_types[1133] = new enumeration_type("IfcVibrationIsolatorTypeEnum", 1133, items);
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
        IFC4_types[1137] = new enumeration_type("IfcVoidingFeatureTypeEnum", 1137, items);
    }
    IFC4_types[1138] = new type_declaration("IfcVolumeMeasure", 1138, new simple_type(simple_type::real_type));
    IFC4_types[1139] = new type_declaration("IfcVolumetricFlowRateMeasure", 1139, new simple_type(simple_type::real_type));
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
        IFC4_types[1144] = new enumeration_type("IfcWallTypeEnum", 1144, items);
    }
    IFC4_types[1145] = new type_declaration("IfcWarpingConstantMeasure", 1145, new simple_type(simple_type::real_type));
    IFC4_types[1146] = new type_declaration("IfcWarpingMomentMeasure", 1146, new simple_type(simple_type::real_type));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[1146]);
        IFC4_types[1147] = new select_type("IfcWarpingStiffnessSelect", 1147, items);
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
        IFC4_types[1150] = new enumeration_type("IfcWasteTerminalTypeEnum", 1150, items);
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
        IFC4_types[1153] = new enumeration_type("IfcWindowPanelOperationEnum", 1153, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IFC4_types[1154] = new enumeration_type("IfcWindowPanelPositionEnum", 1154, items);
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
        IFC4_types[1158] = new enumeration_type("IfcWindowStyleConstructionEnum", 1158, items);
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
        IFC4_types[1159] = new enumeration_type("IfcWindowStyleOperationEnum", 1159, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LIGHTDOME");
        items.push_back("NOTDEFINED");
        items.push_back("SKYLIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDOW");
        IFC4_types[1161] = new enumeration_type("IfcWindowTypeEnum", 1161, items);
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
        IFC4_types[1162] = new enumeration_type("IfcWindowTypePartitioningEnum", 1162, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FIRSTSHIFT");
        items.push_back("NOTDEFINED");
        items.push_back("SECONDSHIFT");
        items.push_back("THIRDSHIFT");
        items.push_back("USERDEFINED");
        IFC4_types[1164] = new enumeration_type("IfcWorkCalendarTypeEnum", 1164, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4_types[1167] = new enumeration_type("IfcWorkPlanTypeEnum", 1167, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IFC4_types[1169] = new enumeration_type("IfcWorkScheduleTypeEnum", 1169, items);
    }
    IFC4_types[7] = new entity("IfcActorRole", false, 7, (entity*) 0);
    IFC4_types[12] = new entity("IfcAddress", true, 12, (entity*) 0);
    IFC4_types[35] = new entity("IfcApplication", false, 35, (entity*) 0);
    IFC4_types[36] = new entity("IfcAppliedValue", false, 36, (entity*) 0);
    IFC4_types[38] = new entity("IfcApproval", false, 38, (entity*) 0);
    IFC4_types[74] = new entity("IfcBoundaryCondition", true, 74, (entity*) 0);
    IFC4_types[76] = new entity("IfcBoundaryEdgeCondition", false, 76, (entity*) IFC4_types[74]);
    IFC4_types[77] = new entity("IfcBoundaryFaceCondition", false, 77, (entity*) IFC4_types[74]);
    IFC4_types[78] = new entity("IfcBoundaryNodeCondition", false, 78, (entity*) IFC4_types[74]);
    IFC4_types[79] = new entity("IfcBoundaryNodeConditionWarping", false, 79, (entity*) IFC4_types[78]);
    IFC4_types[179] = new entity("IfcConnectionGeometry", true, 179, (entity*) 0);
    IFC4_types[181] = new entity("IfcConnectionPointGeometry", false, 181, (entity*) IFC4_types[179]);
    IFC4_types[182] = new entity("IfcConnectionSurfaceGeometry", false, 182, (entity*) IFC4_types[179]);
    IFC4_types[184] = new entity("IfcConnectionVolumeGeometry", false, 184, (entity*) IFC4_types[179]);
    IFC4_types[185] = new entity("IfcConstraint", true, 185, (entity*) 0);
    IFC4_types[213] = new entity("IfcCoordinateOperation", true, 213, (entity*) 0);
    IFC4_types[214] = new entity("IfcCoordinateReferenceSystem", true, 214, (entity*) 0);
    IFC4_types[220] = new entity("IfcCostValue", false, 220, (entity*) IFC4_types[36]);
    IFC4_types[261] = new entity("IfcDerivedUnit", false, 261, (entity*) 0);
    IFC4_types[262] = new entity("IfcDerivedUnitElement", false, 262, (entity*) 0);
    IFC4_types[265] = new entity("IfcDimensionalExponents", false, 265, (entity*) 0);
    IFC4_types[375] = new entity("IfcExternalInformation", true, 375, (entity*) 0);
    IFC4_types[379] = new entity("IfcExternalReference", true, 379, (entity*) 0);
    IFC4_types[376] = new entity("IfcExternallyDefinedHatchStyle", false, 376, (entity*) IFC4_types[379]);
    IFC4_types[377] = new entity("IfcExternallyDefinedSurfaceStyle", false, 377, (entity*) IFC4_types[379]);
    IFC4_types[378] = new entity("IfcExternallyDefinedTextFont", false, 378, (entity*) IFC4_types[379]);
    IFC4_types[461] = new entity("IfcGridAxis", false, 461, (entity*) 0);
    IFC4_types[497] = new entity("IfcIrregularTimeSeriesValue", false, 497, (entity*) 0);
    IFC4_types[517] = new entity("IfcLibraryInformation", false, 517, (entity*) IFC4_types[375]);
    IFC4_types[518] = new entity("IfcLibraryReference", false, 518, (entity*) IFC4_types[379]);
    IFC4_types[521] = new entity("IfcLightDistributionData", false, 521, (entity*) 0);
    IFC4_types[527] = new entity("IfcLightIntensityDistribution", false, 527, (entity*) 0);
    IFC4_types[552] = new entity("IfcMapConversion", false, 552, (entity*) IFC4_types[213]);
    IFC4_types[559] = new entity("IfcMaterialClassificationRelationship", false, 559, (entity*) 0);
    IFC4_types[562] = new entity("IfcMaterialDefinition", true, 562, (entity*) 0);
    IFC4_types[564] = new entity("IfcMaterialLayer", false, 564, (entity*) IFC4_types[562]);
    IFC4_types[565] = new entity("IfcMaterialLayerSet", false, 565, (entity*) IFC4_types[562]);
    IFC4_types[567] = new entity("IfcMaterialLayerWithOffsets", false, 567, (entity*) IFC4_types[564]);
    IFC4_types[568] = new entity("IfcMaterialList", false, 568, (entity*) 0);
    IFC4_types[569] = new entity("IfcMaterialProfile", false, 569, (entity*) IFC4_types[562]);
    IFC4_types[570] = new entity("IfcMaterialProfileSet", false, 570, (entity*) IFC4_types[562]);
    IFC4_types[573] = new entity("IfcMaterialProfileWithOffsets", false, 573, (entity*) IFC4_types[569]);
    IFC4_types[577] = new entity("IfcMaterialUsageDefinition", true, 577, (entity*) 0);
    IFC4_types[579] = new entity("IfcMeasureWithUnit", false, 579, (entity*) 0);
    IFC4_types[590] = new entity("IfcMetric", false, 590, (entity*) IFC4_types[185]);
    IFC4_types[604] = new entity("IfcMonetaryUnit", false, 604, (entity*) 0);
    IFC4_types[609] = new entity("IfcNamedUnit", true, 609, (entity*) 0);
    IFC4_types[618] = new entity("IfcObjectPlacement", true, 618, (entity*) 0);
    IFC4_types[616] = new entity("IfcObjective", false, 616, (entity*) IFC4_types[185]);
    IFC4_types[629] = new entity("IfcOrganization", false, 629, (entity*) 0);
    IFC4_types[636] = new entity("IfcOwnerHistory", false, 636, (entity*) 0);
    IFC4_types[647] = new entity("IfcPerson", false, 647, (entity*) 0);
    IFC4_types[648] = new entity("IfcPersonAndOrganization", false, 648, (entity*) 0);
    IFC4_types[652] = new entity("IfcPhysicalQuantity", true, 652, (entity*) 0);
    IFC4_types[653] = new entity("IfcPhysicalSimpleQuantity", true, 653, (entity*) IFC4_types[652]);
    IFC4_types[688] = new entity("IfcPostalAddress", false, 688, (entity*) IFC4_types[12]);
    IFC4_types[698] = new entity("IfcPresentationItem", true, 698, (entity*) 0);
    IFC4_types[699] = new entity("IfcPresentationLayerAssignment", false, 699, (entity*) 0);
    IFC4_types[700] = new entity("IfcPresentationLayerWithStyle", false, 700, (entity*) IFC4_types[699]);
    IFC4_types[701] = new entity("IfcPresentationStyle", true, 701, (entity*) 0);
    IFC4_types[702] = new entity("IfcPresentationStyleAssignment", false, 702, (entity*) 0);
    IFC4_types[712] = new entity("IfcProductRepresentation", true, 712, (entity*) 0);
    IFC4_types[715] = new entity("IfcProfileDef", false, 715, (entity*) 0);
    IFC4_types[719] = new entity("IfcProjectedCRS", false, 719, (entity*) IFC4_types[214]);
    IFC4_types[727] = new entity("IfcPropertyAbstraction", true, 727, (entity*) 0);
    IFC4_types[732] = new entity("IfcPropertyEnumeration", false, 732, (entity*) IFC4_types[727]);
    IFC4_types[755] = new entity("IfcQuantityArea", false, 755, (entity*) IFC4_types[653]);
    IFC4_types[756] = new entity("IfcQuantityCount", false, 756, (entity*) IFC4_types[653]);
    IFC4_types[757] = new entity("IfcQuantityLength", false, 757, (entity*) IFC4_types[653]);
    IFC4_types[759] = new entity("IfcQuantityTime", false, 759, (entity*) IFC4_types[653]);
    IFC4_types[760] = new entity("IfcQuantityVolume", false, 760, (entity*) IFC4_types[653]);
    IFC4_types[761] = new entity("IfcQuantityWeight", false, 761, (entity*) IFC4_types[653]);
    IFC4_types[780] = new entity("IfcRecurrencePattern", false, 780, (entity*) 0);
    IFC4_types[782] = new entity("IfcReference", false, 782, (entity*) 0);
    IFC4_types[846] = new entity("IfcRepresentation", true, 846, (entity*) 0);
    IFC4_types[847] = new entity("IfcRepresentationContext", true, 847, (entity*) 0);
    IFC4_types[848] = new entity("IfcRepresentationItem", true, 848, (entity*) 0);
    IFC4_types[849] = new entity("IfcRepresentationMap", false, 849, (entity*) 0);
    IFC4_types[853] = new entity("IfcResourceLevelRelationship", true, 853, (entity*) 0);
    IFC4_types[865] = new entity("IfcRoot", true, 865, (entity*) 0);
    IFC4_types[902] = new entity("IfcSIUnit", false, 902, (entity*) IFC4_types[609]);
    IFC4_types[874] = new entity("IfcSchedulingTime", true, 874, (entity*) 0);
    IFC4_types[890] = new entity("IfcShapeAspect", false, 890, (entity*) 0);
    IFC4_types[891] = new entity("IfcShapeModel", true, 891, (entity*) IFC4_types[846]);
    IFC4_types[892] = new entity("IfcShapeRepresentation", false, 892, (entity*) IFC4_types[891]);
    IFC4_types[956] = new entity("IfcStructuralConnectionCondition", true, 956, (entity*) 0);
    IFC4_types[966] = new entity("IfcStructuralLoad", true, 966, (entity*) 0);
    IFC4_types[968] = new entity("IfcStructuralLoadConfiguration", false, 968, (entity*) IFC4_types[966]);
    IFC4_types[971] = new entity("IfcStructuralLoadOrResult", true, 971, (entity*) IFC4_types[966]);
    IFC4_types[977] = new entity("IfcStructuralLoadStatic", true, 977, (entity*) IFC4_types[971]);
    IFC4_types[978] = new entity("IfcStructuralLoadTemperature", false, 978, (entity*) IFC4_types[977]);
    IFC4_types[996] = new entity("IfcStyleModel", true, 996, (entity*) IFC4_types[846]);
    IFC4_types[994] = new entity("IfcStyledItem", false, 994, (entity*) IFC4_types[848]);
    IFC4_types[995] = new entity("IfcStyledRepresentation", false, 995, (entity*) IFC4_types[996]);
    IFC4_types[1009] = new entity("IfcSurfaceReinforcementArea", false, 1009, (entity*) IFC4_types[971]);
    IFC4_types[1011] = new entity("IfcSurfaceStyle", false, 1011, (entity*) IFC4_types[701]);
    IFC4_types[1013] = new entity("IfcSurfaceStyleLighting", false, 1013, (entity*) IFC4_types[698]);
    IFC4_types[1014] = new entity("IfcSurfaceStyleRefraction", false, 1014, (entity*) IFC4_types[698]);
    IFC4_types[1016] = new entity("IfcSurfaceStyleShading", false, 1016, (entity*) IFC4_types[698]);
    IFC4_types[1017] = new entity("IfcSurfaceStyleWithTextures", false, 1017, (entity*) IFC4_types[698]);
    IFC4_types[1018] = new entity("IfcSurfaceTexture", true, 1018, (entity*) IFC4_types[698]);
    IFC4_types[1030] = new entity("IfcTable", false, 1030, (entity*) 0);
    IFC4_types[1031] = new entity("IfcTableColumn", false, 1031, (entity*) 0);
    IFC4_types[1032] = new entity("IfcTableRow", false, 1032, (entity*) 0);
    IFC4_types[1038] = new entity("IfcTaskTime", false, 1038, (entity*) IFC4_types[874]);
    IFC4_types[1039] = new entity("IfcTaskTimeRecurring", false, 1039, (entity*) IFC4_types[1038]);
    IFC4_types[1042] = new entity("IfcTelecomAddress", false, 1042, (entity*) IFC4_types[12]);
    IFC4_types[1061] = new entity("IfcTextStyle", false, 1061, (entity*) IFC4_types[701]);
    IFC4_types[1063] = new entity("IfcTextStyleForDefinedFont", false, 1063, (entity*) IFC4_types[698]);
    IFC4_types[1064] = new entity("IfcTextStyleTextModel", false, 1064, (entity*) IFC4_types[698]);
    IFC4_types[1066] = new entity("IfcTextureCoordinate", true, 1066, (entity*) IFC4_types[698]);
    IFC4_types[1067] = new entity("IfcTextureCoordinateGenerator", false, 1067, (entity*) IFC4_types[1066]);
    IFC4_types[1068] = new entity("IfcTextureMap", false, 1068, (entity*) IFC4_types[1066]);
    IFC4_types[1069] = new entity("IfcTextureVertex", false, 1069, (entity*) IFC4_types[698]);
    IFC4_types[1070] = new entity("IfcTextureVertexList", false, 1070, (entity*) IFC4_types[698]);
    IFC4_types[1080] = new entity("IfcTimePeriod", false, 1080, (entity*) 0);
    IFC4_types[1081] = new entity("IfcTimeSeries", true, 1081, (entity*) 0);
    IFC4_types[1083] = new entity("IfcTimeSeriesValue", false, 1083, (entity*) 0);
    IFC4_types[1085] = new entity("IfcTopologicalRepresentationItem", true, 1085, (entity*) IFC4_types[848]);
    IFC4_types[1086] = new entity("IfcTopologyRepresentation", false, 1086, (entity*) IFC4_types[891]);
    IFC4_types[1117] = new entity("IfcUnitAssignment", false, 1117, (entity*) 0);
    IFC4_types[1128] = new entity("IfcVertex", false, 1128, (entity*) IFC4_types[1085]);
    IFC4_types[1130] = new entity("IfcVertexPoint", false, 1130, (entity*) IFC4_types[1128]);
    IFC4_types[1135] = new entity("IfcVirtualGridIntersection", false, 1135, (entity*) 0);
    IFC4_types[1170] = new entity("IfcWorkTime", false, 1170, (entity*) IFC4_types[874]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[629]);
        items.push_back(IFC4_types[647]);
        items.push_back(IFC4_types[648]);
        IFC4_types[8] = new select_type("IfcActorSelect", 8, items);
    }
    IFC4_types[43] = new type_declaration("IfcArcIndex", 43, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[684])));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[516]);
        items.push_back(IFC4_types[670]);
        IFC4_types[62] = new select_type("IfcBendingParameterSelect", 62, items);
    }
    IFC4_types[83] = new type_declaration("IfcBoxAlignment", 83, new named_type(IFC4_types[505]));
    {
        std::vector<const declaration*> items; items.reserve(71);
        items.push_back(IFC4_types[0]);
        items.push_back(IFC4_types[1]);
        items.push_back(IFC4_types[32]);
        items.push_back(IFC4_types[44]);
        items.push_back(IFC4_types[169]);
        items.push_back(IFC4_types[236]);
        items.push_back(IFC4_types[304]);
        items.push_back(IFC4_types[317]);
        items.push_back(IFC4_types[324]);
        items.push_back(IFC4_types[325]);
        items.push_back(IFC4_types[326]);
        items.push_back(IFC4_types[340]);
        items.push_back(IFC4_types[344]);
        items.push_back(IFC4_types[359]);
        items.push_back(IFC4_types[441]);
        items.push_back(IFC4_types[442]);
        items.push_back(IFC4_types[471]);
        items.push_back(IFC4_types[472]);
        items.push_back(IFC4_types[477]);
        items.push_back(IFC4_types[485]);
        items.push_back(IFC4_types[487]);
        items.push_back(IFC4_types[495]);
        items.push_back(IFC4_types[499]);
        items.push_back(IFC4_types[503]);
        items.push_back(IFC4_types[535]);
        items.push_back(IFC4_types[536]);
        items.push_back(IFC4_types[537]);
        items.push_back(IFC4_types[538]);
        items.push_back(IFC4_types[546]);
        items.push_back(IFC4_types[547]);
        items.push_back(IFC4_types[549]);
        items.push_back(IFC4_types[550]);
        items.push_back(IFC4_types[554]);
        items.push_back(IFC4_types[555]);
        items.push_back(IFC4_types[557]);
        items.push_back(IFC4_types[593]);
        items.push_back(IFC4_types[594]);
        items.push_back(IFC4_types[595]);
        items.push_back(IFC4_types[597]);
        items.push_back(IFC4_types[600]);
        items.push_back(IFC4_types[601]);
        items.push_back(IFC4_types[602]);
        items.push_back(IFC4_types[603]);
        items.push_back(IFC4_types[649]);
        items.push_back(IFC4_types[668]);
        items.push_back(IFC4_types[689]);
        items.push_back(IFC4_types[704]);
        items.push_back(IFC4_types[762]);
        items.push_back(IFC4_types[866]);
        items.push_back(IFC4_types[867]);
        items.push_back(IFC4_types[868]);
        items.push_back(IFC4_types[878]);
        items.push_back(IFC4_types[876]);
        items.push_back(IFC4_types[893]);
        items.push_back(IFC4_types[917]);
        items.push_back(IFC4_types[918]);
        items.push_back(IFC4_types[919]);
        items.push_back(IFC4_types[920]);
        items.push_back(IFC4_types[935]);
        items.push_back(IFC4_types[1043]);
        items.push_back(IFC4_types[1044]);
        items.push_back(IFC4_types[1071]);
        items.push_back(IFC4_types[1072]);
        items.push_back(IFC4_types[1073]);
        items.push_back(IFC4_types[1074]);
        items.push_back(IFC4_types[1075]);
        items.push_back(IFC4_types[1088]);
        items.push_back(IFC4_types[1125]);
        items.push_back(IFC4_types[1139]);
        items.push_back(IFC4_types[1145]);
        items.push_back(IFC4_types[1146]);
        IFC4_types[259] = new select_type("IfcDerivedMeasureValue", 259, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[846]);
        items.push_back(IFC4_types[848]);
        IFC4_types[514] = new select_type("IfcLayeredItem", 514, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[517]);
        items.push_back(IFC4_types[518]);
        IFC4_types[519] = new select_type("IfcLibrarySelect", 519, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[379]);
        items.push_back(IFC4_types[527]);
        IFC4_types[522] = new select_type("IfcLightDistributionDataSourceSelect", 522, items);
    }
    IFC4_types[539] = new type_declaration("IfcLineIndex", 539, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[684])));
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[562]);
        items.push_back(IFC4_types[568]);
        items.push_back(IFC4_types[577]);
        IFC4_types[576] = new select_type("IfcMaterialSelect", 576, items);
    }
    IFC4_types[611] = new type_declaration("IfcNormalisedRatioMeasure", 611, new named_type(IFC4_types[772]));
    {
        std::vector<const declaration*> items; items.reserve(9);
        items.push_back(IFC4_types[12]);
        items.push_back(IFC4_types[36]);
        items.push_back(IFC4_types[379]);
        items.push_back(IFC4_types[562]);
        items.push_back(IFC4_types[629]);
        items.push_back(IFC4_types[647]);
        items.push_back(IFC4_types[648]);
        items.push_back(IFC4_types[1030]);
        items.push_back(IFC4_types[1081]);
        IFC4_types[619] = new select_type("IfcObjectReferenceSelect", 619, items);
    }
    IFC4_types[687] = new type_declaration("IfcPositiveRatioMeasure", 687, new named_type(IFC4_types[772]));
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[43]);
        items.push_back(IFC4_types[539]);
        IFC4_types[882] = new select_type("IfcSegmentIndexSelect", 882, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(14);
        items.push_back(IFC4_types[63]);
        items.push_back(IFC4_types[69]);
        items.push_back(IFC4_types[254]);
        items.push_back(IFC4_types[255]);
        items.push_back(IFC4_types[316]);
        items.push_back(IFC4_types[476]);
        items.push_back(IFC4_types[486]);
        items.push_back(IFC4_types[505]);
        items.push_back(IFC4_types[542]);
        items.push_back(IFC4_types[684]);
        items.push_back(IFC4_types[775]);
        items.push_back(IFC4_types[1053]);
        items.push_back(IFC4_types[1077]);
        items.push_back(IFC4_types[1084]);
        IFC4_types[899] = new select_type("IfcSimpleValue", 899, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4_types[264]);
        items.push_back(IFC4_types[516]);
        items.push_back(IFC4_types[611]);
        items.push_back(IFC4_types[685]);
        items.push_back(IFC4_types[687]);
        items.push_back(IFC4_types[772]);
        IFC4_types[904] = new select_type("IfcSizeSelect", 904, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[936]);
        items.push_back(IFC4_types[938]);
        IFC4_types[937] = new select_type("IfcSpecularHighlightSelect", 937, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[701]);
        items.push_back(IFC4_types[702]);
        IFC4_types[993] = new select_type("IfcStyleAssignmentSelect", 993, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4_types[377]);
        items.push_back(IFC4_types[1013]);
        items.push_back(IFC4_types[1014]);
        items.push_back(IFC4_types[1016]);
        items.push_back(IFC4_types[1017]);
        IFC4_types[1012] = new select_type("IfcSurfaceStyleElementSelect", 1012, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[261]);
        items.push_back(IFC4_types[604]);
        items.push_back(IFC4_types[609]);
        IFC4_types[1110] = new select_type("IfcUnit", 1110, items);
    }
    IFC4_types[39] = new entity("IfcApprovalRelationship", false, 39, (entity*) IFC4_types[853]);
    IFC4_types[40] = new entity("IfcArbitraryClosedProfileDef", false, 40, (entity*) IFC4_types[715]);
    IFC4_types[41] = new entity("IfcArbitraryOpenProfileDef", false, 41, (entity*) IFC4_types[715]);
    IFC4_types[42] = new entity("IfcArbitraryProfileDefWithVoids", false, 42, (entity*) IFC4_types[40]);
    IFC4_types[64] = new entity("IfcBlobTexture", false, 64, (entity*) IFC4_types[1018]);
    IFC4_types[128] = new entity("IfcCenterLineProfileDef", false, 128, (entity*) IFC4_types[41]);
    IFC4_types[141] = new entity("IfcClassification", false, 141, (entity*) IFC4_types[375]);
    IFC4_types[142] = new entity("IfcClassificationReference", false, 142, (entity*) IFC4_types[379]);
    IFC4_types[152] = new entity("IfcColourRgbList", false, 152, (entity*) IFC4_types[698]);
    IFC4_types[153] = new entity("IfcColourSpecification", true, 153, (entity*) IFC4_types[698]);
    IFC4_types[168] = new entity("IfcCompositeProfileDef", false, 168, (entity*) IFC4_types[715]);
    IFC4_types[177] = new entity("IfcConnectedFaceSet", false, 177, (entity*) IFC4_types[1085]);
    IFC4_types[178] = new entity("IfcConnectionCurveGeometry", false, 178, (entity*) IFC4_types[179]);
    IFC4_types[180] = new entity("IfcConnectionPointEccentricity", false, 180, (entity*) IFC4_types[181]);
    IFC4_types[200] = new entity("IfcContextDependentUnit", false, 200, (entity*) IFC4_types[609]);
    IFC4_types[205] = new entity("IfcConversionBasedUnit", false, 205, (entity*) IFC4_types[609]);
    IFC4_types[206] = new entity("IfcConversionBasedUnitWithOffset", false, 206, (entity*) IFC4_types[205]);
    IFC4_types[232] = new entity("IfcCurrencyRelationship", false, 232, (entity*) IFC4_types[853]);
    IFC4_types[244] = new entity("IfcCurveStyle", false, 244, (entity*) IFC4_types[701]);
    IFC4_types[245] = new entity("IfcCurveStyleFont", false, 245, (entity*) IFC4_types[698]);
    IFC4_types[246] = new entity("IfcCurveStyleFontAndScaling", false, 246, (entity*) IFC4_types[698]);
    IFC4_types[247] = new entity("IfcCurveStyleFontPattern", false, 247, (entity*) IFC4_types[698]);
    IFC4_types[260] = new entity("IfcDerivedProfileDef", false, 260, (entity*) IFC4_types[715]);
    IFC4_types[287] = new entity("IfcDocumentInformation", false, 287, (entity*) IFC4_types[375]);
    IFC4_types[288] = new entity("IfcDocumentInformationRelationship", false, 288, (entity*) IFC4_types[853]);
    IFC4_types[289] = new entity("IfcDocumentReference", false, 289, (entity*) IFC4_types[379]);
    IFC4_types[318] = new entity("IfcEdge", false, 318, (entity*) IFC4_types[1085]);
    IFC4_types[319] = new entity("IfcEdgeCurve", false, 319, (entity*) IFC4_types[318]);
    IFC4_types[370] = new entity("IfcEventTime", false, 370, (entity*) IFC4_types[874]);
    IFC4_types[374] = new entity("IfcExtendedProperties", true, 374, (entity*) IFC4_types[727]);
    IFC4_types[380] = new entity("IfcExternalReferenceRelationship", false, 380, (entity*) IFC4_types[853]);
    IFC4_types[386] = new entity("IfcFace", false, 386, (entity*) IFC4_types[1085]);
    IFC4_types[388] = new entity("IfcFaceBound", false, 388, (entity*) IFC4_types[1085]);
    IFC4_types[389] = new entity("IfcFaceOuterBound", false, 389, (entity*) IFC4_types[388]);
    IFC4_types[390] = new entity("IfcFaceSurface", false, 390, (entity*) IFC4_types[386]);
    IFC4_types[393] = new entity("IfcFailureConnectionCondition", false, 393, (entity*) IFC4_types[956]);
    IFC4_types[403] = new entity("IfcFillAreaStyle", false, 403, (entity*) IFC4_types[701]);
    IFC4_types[453] = new entity("IfcGeometricRepresentationContext", false, 453, (entity*) IFC4_types[847]);
    IFC4_types[454] = new entity("IfcGeometricRepresentationItem", true, 454, (entity*) IFC4_types[848]);
    IFC4_types[455] = new entity("IfcGeometricRepresentationSubContext", false, 455, (entity*) IFC4_types[453]);
    IFC4_types[456] = new entity("IfcGeometricSet", false, 456, (entity*) IFC4_types[454]);
    IFC4_types[462] = new entity("IfcGridPlacement", false, 462, (entity*) IFC4_types[618]);
    IFC4_types[466] = new entity("IfcHalfSpaceSolid", false, 466, (entity*) IFC4_types[454]);
    IFC4_types[478] = new entity("IfcImageTexture", false, 478, (entity*) IFC4_types[1018]);
    IFC4_types[479] = new entity("IfcIndexedColourMap", false, 479, (entity*) IFC4_types[698]);
    IFC4_types[483] = new entity("IfcIndexedTextureMap", true, 483, (entity*) IFC4_types[1066]);
    IFC4_types[484] = new entity("IfcIndexedTriangleTextureMap", false, 484, (entity*) IFC4_types[483]);
    IFC4_types[496] = new entity("IfcIrregularTimeSeries", false, 496, (entity*) IFC4_types[1081]);
    IFC4_types[509] = new entity("IfcLagTime", false, 509, (entity*) IFC4_types[874]);
    IFC4_types[528] = new entity("IfcLightSource", true, 528, (entity*) IFC4_types[454]);
    IFC4_types[529] = new entity("IfcLightSourceAmbient", false, 529, (entity*) IFC4_types[528]);
    IFC4_types[530] = new entity("IfcLightSourceDirectional", false, 530, (entity*) IFC4_types[528]);
    IFC4_types[531] = new entity("IfcLightSourceGoniometric", false, 531, (entity*) IFC4_types[528]);
    IFC4_types[532] = new entity("IfcLightSourcePositional", false, 532, (entity*) IFC4_types[528]);
    IFC4_types[533] = new entity("IfcLightSourceSpot", false, 533, (entity*) IFC4_types[532]);
    IFC4_types[541] = new entity("IfcLocalPlacement", false, 541, (entity*) IFC4_types[618]);
    IFC4_types[544] = new entity("IfcLoop", false, 544, (entity*) IFC4_types[1085]);
    IFC4_types[553] = new entity("IfcMappedItem", false, 553, (entity*) IFC4_types[848]);
    IFC4_types[558] = new entity("IfcMaterial", false, 558, (entity*) IFC4_types[562]);
    IFC4_types[560] = new entity("IfcMaterialConstituent", false, 560, (entity*) IFC4_types[562]);
    IFC4_types[561] = new entity("IfcMaterialConstituentSet", false, 561, (entity*) IFC4_types[562]);
    IFC4_types[563] = new entity("IfcMaterialDefinitionRepresentation", false, 563, (entity*) IFC4_types[712]);
    IFC4_types[566] = new entity("IfcMaterialLayerSetUsage", false, 566, (entity*) IFC4_types[577]);
    IFC4_types[571] = new entity("IfcMaterialProfileSetUsage", false, 571, (entity*) IFC4_types[577]);
    IFC4_types[572] = new entity("IfcMaterialProfileSetUsageTapering", false, 572, (entity*) IFC4_types[571]);
    IFC4_types[574] = new entity("IfcMaterialProperties", false, 574, (entity*) IFC4_types[374]);
    IFC4_types[575] = new entity("IfcMaterialRelationship", false, 575, (entity*) IFC4_types[853]);
    IFC4_types[592] = new entity("IfcMirroredProfileDef", false, 592, (entity*) IFC4_types[260]);
    IFC4_types[615] = new entity("IfcObjectDefinition", true, 615, (entity*) IFC4_types[865]);
    IFC4_types[628] = new entity("IfcOpenShell", false, 628, (entity*) IFC4_types[177]);
    IFC4_types[630] = new entity("IfcOrganizationRelationship", false, 630, (entity*) IFC4_types[853]);
    IFC4_types[631] = new entity("IfcOrientedEdge", false, 631, (entity*) IFC4_types[318]);
    IFC4_types[637] = new entity("IfcParameterizedProfileDef", true, 637, (entity*) IFC4_types[715]);
    IFC4_types[639] = new entity("IfcPath", false, 639, (entity*) IFC4_types[1085]);
    IFC4_types[650] = new entity("IfcPhysicalComplexQuantity", false, 650, (entity*) IFC4_types[652]);
    IFC4_types[664] = new entity("IfcPixelTexture", false, 664, (entity*) IFC4_types[1018]);
    IFC4_types[665] = new entity("IfcPlacement", true, 665, (entity*) IFC4_types[454]);
    IFC4_types[667] = new entity("IfcPlanarExtent", false, 667, (entity*) IFC4_types[454]);
    IFC4_types[675] = new entity("IfcPoint", true, 675, (entity*) IFC4_types[454]);
    IFC4_types[676] = new entity("IfcPointOnCurve", false, 676, (entity*) IFC4_types[675]);
    IFC4_types[677] = new entity("IfcPointOnSurface", false, 677, (entity*) IFC4_types[675]);
    IFC4_types[682] = new entity("IfcPolyLoop", false, 682, (entity*) IFC4_types[544]);
    IFC4_types[679] = new entity("IfcPolygonalBoundedHalfSpace", false, 679, (entity*) IFC4_types[466]);
    IFC4_types[692] = new entity("IfcPreDefinedItem", true, 692, (entity*) IFC4_types[698]);
    IFC4_types[693] = new entity("IfcPreDefinedProperties", true, 693, (entity*) IFC4_types[727]);
    IFC4_types[695] = new entity("IfcPreDefinedTextFont", true, 695, (entity*) IFC4_types[692]);
    IFC4_types[711] = new entity("IfcProductDefinitionShape", false, 711, (entity*) IFC4_types[712]);
    IFC4_types[716] = new entity("IfcProfileProperties", false, 716, (entity*) IFC4_types[374]);
    IFC4_types[726] = new entity("IfcProperty", true, 726, (entity*) IFC4_types[727]);
    IFC4_types[729] = new entity("IfcPropertyDefinition", true, 729, (entity*) IFC4_types[865]);
    IFC4_types[730] = new entity("IfcPropertyDependencyRelationship", false, 730, (entity*) IFC4_types[853]);
    IFC4_types[736] = new entity("IfcPropertySetDefinition", true, 736, (entity*) IFC4_types[729]);
    IFC4_types[744] = new entity("IfcPropertyTemplateDefinition", true, 744, (entity*) IFC4_types[729]);
    IFC4_types[758] = new entity("IfcQuantitySet", true, 758, (entity*) IFC4_types[736]);
    IFC4_types[777] = new entity("IfcRectangleProfileDef", false, 777, (entity*) IFC4_types[637]);
    IFC4_types[784] = new entity("IfcRegularTimeSeries", false, 784, (entity*) IFC4_types[1081]);
    IFC4_types[785] = new entity("IfcReinforcementBarProperties", false, 785, (entity*) IFC4_types[693]);
    IFC4_types[813] = new entity("IfcRelationship", true, 813, (entity*) IFC4_types[865]);
    IFC4_types[851] = new entity("IfcResourceApprovalRelationship", false, 851, (entity*) IFC4_types[853]);
    IFC4_types[852] = new entity("IfcResourceConstraintRelationship", false, 852, (entity*) IFC4_types[853]);
    IFC4_types[856] = new entity("IfcResourceTime", false, 856, (entity*) IFC4_types[874]);
    IFC4_types[870] = new entity("IfcRoundedRectangleProfileDef", false, 870, (entity*) IFC4_types[777]);
    IFC4_types[879] = new entity("IfcSectionProperties", false, 879, (entity*) IFC4_types[693]);
    IFC4_types[880] = new entity("IfcSectionReinforcementProperties", false, 880, (entity*) IFC4_types[693]);
    IFC4_types[877] = new entity("IfcSectionedSpine", false, 877, (entity*) IFC4_types[454]);
    IFC4_types[895] = new entity("IfcShellBasedSurfaceModel", false, 895, (entity*) IFC4_types[454]);
    IFC4_types[896] = new entity("IfcSimpleProperty", true, 896, (entity*) IFC4_types[726]);
    IFC4_types[910] = new entity("IfcSlippageConnectionCondition", false, 910, (entity*) IFC4_types[956]);
    IFC4_types[915] = new entity("IfcSolidModel", true, 915, (entity*) IFC4_types[454]);
    IFC4_types[970] = new entity("IfcStructuralLoadLinearForce", false, 970, (entity*) IFC4_types[977]);
    IFC4_types[972] = new entity("IfcStructuralLoadPlanarForce", false, 972, (entity*) IFC4_types[977]);
    IFC4_types[973] = new entity("IfcStructuralLoadSingleDisplacement", false, 973, (entity*) IFC4_types[977]);
    IFC4_types[974] = new entity("IfcStructuralLoadSingleDisplacementDistortion", false, 974, (entity*) IFC4_types[973]);
    IFC4_types[975] = new entity("IfcStructuralLoadSingleForce", false, 975, (entity*) IFC4_types[977]);
    IFC4_types[976] = new entity("IfcStructuralLoadSingleForceWarping", false, 976, (entity*) IFC4_types[975]);
    IFC4_types[1000] = new entity("IfcSubedge", false, 1000, (entity*) IFC4_types[318]);
    IFC4_types[1001] = new entity("IfcSurface", true, 1001, (entity*) IFC4_types[454]);
    IFC4_types[1015] = new entity("IfcSurfaceStyleRendering", false, 1015, (entity*) IFC4_types[1016]);
    IFC4_types[1019] = new entity("IfcSweptAreaSolid", true, 1019, (entity*) IFC4_types[915]);
    IFC4_types[1020] = new entity("IfcSweptDiskSolid", false, 1020, (entity*) IFC4_types[915]);
    IFC4_types[1021] = new entity("IfcSweptDiskSolidPolygonal", false, 1021, (entity*) IFC4_types[1020]);
    IFC4_types[1022] = new entity("IfcSweptSurface", true, 1022, (entity*) IFC4_types[1001]);
    IFC4_types[1102] = new entity("IfcTShapeProfileDef", false, 1102, (entity*) IFC4_types[637]);
    IFC4_types[1052] = new entity("IfcTessellatedItem", true, 1052, (entity*) IFC4_types[454]);
    IFC4_types[1058] = new entity("IfcTextLiteral", false, 1058, (entity*) IFC4_types[454]);
    IFC4_types[1059] = new entity("IfcTextLiteralWithExtent", false, 1059, (entity*) IFC4_types[1058]);
    IFC4_types[1062] = new entity("IfcTextStyleFontModel", false, 1062, (entity*) IFC4_types[695]);
    IFC4_types[1097] = new entity("IfcTrapeziumProfileDef", false, 1097, (entity*) IFC4_types[637]);
    IFC4_types[1106] = new entity("IfcTypeObject", false, 1106, (entity*) IFC4_types[615]);
    IFC4_types[1107] = new entity("IfcTypeProcess", true, 1107, (entity*) IFC4_types[1106]);
    IFC4_types[1108] = new entity("IfcTypeProduct", false, 1108, (entity*) IFC4_types[1106]);
    IFC4_types[1109] = new entity("IfcTypeResource", true, 1109, (entity*) IFC4_types[1106]);
    IFC4_types[1120] = new entity("IfcUShapeProfileDef", false, 1120, (entity*) IFC4_types[637]);
    IFC4_types[1126] = new entity("IfcVector", false, 1126, (entity*) IFC4_types[454]);
    IFC4_types[1129] = new entity("IfcVertexLoop", false, 1129, (entity*) IFC4_types[544]);
    IFC4_types[1157] = new entity("IfcWindowStyle", false, 1157, (entity*) IFC4_types[1108]);
    IFC4_types[1172] = new entity("IfcZShapeProfileDef", false, 1172, (entity*) IFC4_types[637]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[141]);
        items.push_back(IFC4_types[142]);
        IFC4_types[143] = new select_type("IfcClassificationReferenceSelect", 143, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[141]);
        items.push_back(IFC4_types[142]);
        IFC4_types[144] = new select_type("IfcClassificationSelect", 144, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[214]);
        items.push_back(IFC4_types[453]);
        IFC4_types[215] = new select_type("IfcCoordinateReferenceSystemSelect", 215, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[615]);
        items.push_back(IFC4_types[729]);
        IFC4_types[258] = new select_type("IfcDefinitionSelect", 258, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[287]);
        items.push_back(IFC4_types[289]);
        IFC4_types[290] = new select_type("IfcDocumentSelect", 290, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[685]);
        items.push_back(IFC4_types[1126]);
        IFC4_types[467] = new select_type("IfcHatchLineDistanceSelect", 467, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(23);
        items.push_back(IFC4_types[29]);
        items.push_back(IFC4_types[45]);
        items.push_back(IFC4_types[161]);
        items.push_back(IFC4_types[199]);
        items.push_back(IFC4_types[221]);
        items.push_back(IFC4_types[264]);
        items.push_back(IFC4_types[327]);
        items.push_back(IFC4_types[516]);
        items.push_back(IFC4_types[548]);
        items.push_back(IFC4_types[556]);
        items.push_back(IFC4_types[610]);
        items.push_back(IFC4_types[611]);
        items.push_back(IFC4_types[613]);
        items.push_back(IFC4_types[638]);
        items.push_back(IFC4_types[670]);
        items.push_back(IFC4_types[685]);
        items.push_back(IFC4_types[686]);
        items.push_back(IFC4_types[687]);
        items.push_back(IFC4_types[772]);
        items.push_back(IFC4_types[914]);
        items.push_back(IFC4_types[1076]);
        items.push_back(IFC4_types[1078]);
        items.push_back(IFC4_types[1138]);
        IFC4_types[578] = new select_type("IfcMeasureValue", 578, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[675]);
        items.push_back(IFC4_types[1130]);
        IFC4_types[678] = new select_type("IfcPointOrVertexPoint", 678, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4_types[244]);
        items.push_back(IFC4_types[403]);
        items.push_back(IFC4_types[612]);
        items.push_back(IFC4_types[1011]);
        items.push_back(IFC4_types[1061]);
        IFC4_types[703] = new select_type("IfcPresentationStyleSelect", 703, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[711]);
        items.push_back(IFC4_types[849]);
        IFC4_types[713] = new select_type("IfcProductRepresentationSelect", 713, items);
    }
    IFC4_types[738] = new type_declaration("IfcPropertySetDefinitionSet", 738, new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[736])));
    {
        std::vector<const declaration*> items; items.reserve(16);
        items.push_back(IFC4_types[7]);
        items.push_back(IFC4_types[36]);
        items.push_back(IFC4_types[38]);
        items.push_back(IFC4_types[185]);
        items.push_back(IFC4_types[200]);
        items.push_back(IFC4_types[205]);
        items.push_back(IFC4_types[375]);
        items.push_back(IFC4_types[379]);
        items.push_back(IFC4_types[562]);
        items.push_back(IFC4_types[629]);
        items.push_back(IFC4_types[647]);
        items.push_back(IFC4_types[648]);
        items.push_back(IFC4_types[652]);
        items.push_back(IFC4_types[715]);
        items.push_back(IFC4_types[727]);
        items.push_back(IFC4_types[1081]);
        IFC4_types[854] = new select_type("IfcResourceObjectSelect", 854, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[378]);
        items.push_back(IFC4_types[695]);
        IFC4_types[1057] = new select_type("IfcTextFontSelect", 1057, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[259]);
        items.push_back(IFC4_types[578]);
        items.push_back(IFC4_types[899]);
        IFC4_types[1121] = new select_type("IfcValue", 1121, items);
    }
    IFC4_types[16] = new entity("IfcAdvancedFace", false, 16, (entity*) IFC4_types[390]);
    IFC4_types[34] = new entity("IfcAnnotationFillArea", false, 34, (entity*) IFC4_types[454]);
    IFC4_types[49] = new entity("IfcAsymmetricIShapeProfileDef", false, 49, (entity*) IFC4_types[637]);
    IFC4_types[53] = new entity("IfcAxis1Placement", false, 53, (entity*) IFC4_types[665]);
    IFC4_types[55] = new entity("IfcAxis2Placement2D", false, 55, (entity*) IFC4_types[665]);
    IFC4_types[56] = new entity("IfcAxis2Placement3D", false, 56, (entity*) IFC4_types[665]);
    IFC4_types[73] = new entity("IfcBooleanResult", false, 73, (entity*) IFC4_types[454]);
    IFC4_types[81] = new entity("IfcBoundedSurface", true, 81, (entity*) IFC4_types[1001]);
    IFC4_types[82] = new entity("IfcBoundingBox", false, 82, (entity*) IFC4_types[454]);
    IFC4_types[84] = new entity("IfcBoxedHalfSpace", false, 84, (entity*) IFC4_types[466]);
    IFC4_types[231] = new entity("IfcCShapeProfileDef", false, 231, (entity*) IFC4_types[637]);
    IFC4_types[119] = new entity("IfcCartesianPoint", false, 119, (entity*) IFC4_types[675]);
    IFC4_types[120] = new entity("IfcCartesianPointList", true, 120, (entity*) IFC4_types[454]);
    IFC4_types[121] = new entity("IfcCartesianPointList2D", false, 121, (entity*) IFC4_types[120]);
    IFC4_types[122] = new entity("IfcCartesianPointList3D", false, 122, (entity*) IFC4_types[120]);
    IFC4_types[123] = new entity("IfcCartesianTransformationOperator", true, 123, (entity*) IFC4_types[454]);
    IFC4_types[124] = new entity("IfcCartesianTransformationOperator2D", false, 124, (entity*) IFC4_types[123]);
    IFC4_types[125] = new entity("IfcCartesianTransformationOperator2DnonUniform", false, 125, (entity*) IFC4_types[124]);
    IFC4_types[126] = new entity("IfcCartesianTransformationOperator3D", false, 126, (entity*) IFC4_types[123]);
    IFC4_types[127] = new entity("IfcCartesianTransformationOperator3DnonUniform", false, 127, (entity*) IFC4_types[126]);
    IFC4_types[138] = new entity("IfcCircleProfileDef", false, 138, (entity*) IFC4_types[637]);
    IFC4_types[145] = new entity("IfcClosedShell", false, 145, (entity*) IFC4_types[177]);
    IFC4_types[151] = new entity("IfcColourRgb", false, 151, (entity*) IFC4_types[153]);
    IFC4_types[162] = new entity("IfcComplexProperty", false, 162, (entity*) IFC4_types[726]);
    IFC4_types[167] = new entity("IfcCompositeCurveSegment", false, 167, (entity*) IFC4_types[454]);
    IFC4_types[197] = new entity("IfcConstructionResourceType", true, 197, (entity*) IFC4_types[1109]);
    IFC4_types[198] = new entity("IfcContext", true, 198, (entity*) IFC4_types[615]);
    IFC4_types[226] = new entity("IfcCrewResourceType", false, 226, (entity*) IFC4_types[197]);
    IFC4_types[228] = new entity("IfcCsgPrimitive3D", true, 228, (entity*) IFC4_types[454]);
    IFC4_types[230] = new entity("IfcCsgSolid", false, 230, (entity*) IFC4_types[915]);
    IFC4_types[237] = new entity("IfcCurve", true, 237, (entity*) IFC4_types[454]);
    IFC4_types[238] = new entity("IfcCurveBoundedPlane", false, 238, (entity*) IFC4_types[81]);
    IFC4_types[239] = new entity("IfcCurveBoundedSurface", false, 239, (entity*) IFC4_types[81]);
    IFC4_types[267] = new entity("IfcDirection", false, 267, (entity*) IFC4_types[454]);
    IFC4_types[298] = new entity("IfcDoorStyle", false, 298, (entity*) IFC4_types[1108]);
    IFC4_types[320] = new entity("IfcEdgeLoop", false, 320, (entity*) IFC4_types[544]);
    IFC4_types[353] = new entity("IfcElementQuantity", false, 353, (entity*) IFC4_types[758]);
    IFC4_types[354] = new entity("IfcElementType", true, 354, (entity*) IFC4_types[1108]);
    IFC4_types[346] = new entity("IfcElementarySurface", true, 346, (entity*) IFC4_types[1001]);
    IFC4_types[356] = new entity("IfcEllipseProfileDef", false, 356, (entity*) IFC4_types[637]);
    IFC4_types[372] = new entity("IfcEventType", false, 372, (entity*) IFC4_types[1107]);
    IFC4_types[384] = new entity("IfcExtrudedAreaSolid", false, 384, (entity*) IFC4_types[1019]);
    IFC4_types[385] = new entity("IfcExtrudedAreaSolidTapered", false, 385, (entity*) IFC4_types[384]);
    IFC4_types[387] = new entity("IfcFaceBasedSurfaceModel", false, 387, (entity*) IFC4_types[454]);
    IFC4_types[404] = new entity("IfcFillAreaStyleHatching", false, 404, (entity*) IFC4_types[454]);
    IFC4_types[405] = new entity("IfcFillAreaStyleTiles", false, 405, (entity*) IFC4_types[454]);
    IFC4_types[413] = new entity("IfcFixedReferenceSweptAreaSolid", false, 413, (entity*) IFC4_types[1019]);
    IFC4_types[444] = new entity("IfcFurnishingElementType", false, 444, (entity*) IFC4_types[354]);
    IFC4_types[446] = new entity("IfcFurnitureType", false, 446, (entity*) IFC4_types[444]);
    IFC4_types[449] = new entity("IfcGeographicElementType", false, 449, (entity*) IFC4_types[354]);
    IFC4_types[451] = new entity("IfcGeometricCurveSet", false, 451, (entity*) IFC4_types[456]);
    IFC4_types[498] = new entity("IfcIShapeProfileDef", false, 498, (entity*) IFC4_types[637]);
    IFC4_types[481] = new entity("IfcIndexedPolygonalFace", false, 481, (entity*) IFC4_types[1052]);
    IFC4_types[482] = new entity("IfcIndexedPolygonalFaceWithVoids", false, 482, (entity*) IFC4_types[481]);
    IFC4_types[545] = new entity("IfcLShapeProfileDef", false, 545, (entity*) IFC4_types[637]);
    IFC4_types[507] = new entity("IfcLaborResourceType", false, 507, (entity*) IFC4_types[197]);
    IFC4_types[534] = new entity("IfcLine", false, 534, (entity*) IFC4_types[237]);
    IFC4_types[551] = new entity("IfcManifoldSolidBrep", true, 551, (entity*) IFC4_types[915]);
    IFC4_types[614] = new entity("IfcObject", true, 614, (entity*) IFC4_types[615]);
    IFC4_types[623] = new entity("IfcOffsetCurve2D", false, 623, (entity*) IFC4_types[237]);
    IFC4_types[624] = new entity("IfcOffsetCurve3D", false, 624, (entity*) IFC4_types[237]);
    IFC4_types[640] = new entity("IfcPcurve", false, 640, (entity*) IFC4_types[237]);
    IFC4_types[666] = new entity("IfcPlanarBox", false, 666, (entity*) IFC4_types[667]);
    IFC4_types[669] = new entity("IfcPlane", false, 669, (entity*) IFC4_types[346]);
    IFC4_types[690] = new entity("IfcPreDefinedColour", true, 690, (entity*) IFC4_types[692]);
    IFC4_types[691] = new entity("IfcPreDefinedCurveFont", true, 691, (entity*) IFC4_types[692]);
    IFC4_types[694] = new entity("IfcPreDefinedPropertySet", true, 694, (entity*) IFC4_types[736]);
    IFC4_types[706] = new entity("IfcProcedureType", false, 706, (entity*) IFC4_types[1107]);
    IFC4_types[708] = new entity("IfcProcess", true, 708, (entity*) IFC4_types[614]);
    IFC4_types[710] = new entity("IfcProduct", true, 710, (entity*) IFC4_types[614]);
    IFC4_types[718] = new entity("IfcProject", false, 718, (entity*) IFC4_types[198]);
    IFC4_types[723] = new entity("IfcProjectLibrary", false, 723, (entity*) IFC4_types[198]);
    IFC4_types[728] = new entity("IfcPropertyBoundedValue", false, 728, (entity*) IFC4_types[896]);
    IFC4_types[731] = new entity("IfcPropertyEnumeratedValue", false, 731, (entity*) IFC4_types[896]);
    IFC4_types[733] = new entity("IfcPropertyListValue", false, 733, (entity*) IFC4_types[896]);
    IFC4_types[734] = new entity("IfcPropertyReferenceValue", false, 734, (entity*) IFC4_types[896]);
    IFC4_types[735] = new entity("IfcPropertySet", false, 735, (entity*) IFC4_types[736]);
    IFC4_types[739] = new entity("IfcPropertySetTemplate", false, 739, (entity*) IFC4_types[744]);
    IFC4_types[741] = new entity("IfcPropertySingleValue", false, 741, (entity*) IFC4_types[896]);
    IFC4_types[742] = new entity("IfcPropertyTableValue", false, 742, (entity*) IFC4_types[896]);
    IFC4_types[743] = new entity("IfcPropertyTemplate", true, 743, (entity*) IFC4_types[744]);
    IFC4_types[751] = new entity("IfcProxy", false, 751, (entity*) IFC4_types[710]);
    IFC4_types[776] = new entity("IfcRectangleHollowProfileDef", false, 776, (entity*) IFC4_types[777]);
    IFC4_types[778] = new entity("IfcRectangularPyramid", false, 778, (entity*) IFC4_types[228]);
    IFC4_types[779] = new entity("IfcRectangularTrimmedSurface", false, 779, (entity*) IFC4_types[81]);
    IFC4_types[786] = new entity("IfcReinforcementDefinitionProperties", false, 786, (entity*) IFC4_types[694]);
    IFC4_types[798] = new entity("IfcRelAssigns", true, 798, (entity*) IFC4_types[813]);
    IFC4_types[799] = new entity("IfcRelAssignsToActor", false, 799, (entity*) IFC4_types[798]);
    IFC4_types[800] = new entity("IfcRelAssignsToControl", false, 800, (entity*) IFC4_types[798]);
    IFC4_types[801] = new entity("IfcRelAssignsToGroup", false, 801, (entity*) IFC4_types[798]);
    IFC4_types[802] = new entity("IfcRelAssignsToGroupByFactor", false, 802, (entity*) IFC4_types[801]);
    IFC4_types[803] = new entity("IfcRelAssignsToProcess", false, 803, (entity*) IFC4_types[798]);
    IFC4_types[804] = new entity("IfcRelAssignsToProduct", false, 804, (entity*) IFC4_types[798]);
    IFC4_types[805] = new entity("IfcRelAssignsToResource", false, 805, (entity*) IFC4_types[798]);
    IFC4_types[806] = new entity("IfcRelAssociates", true, 806, (entity*) IFC4_types[813]);
    IFC4_types[807] = new entity("IfcRelAssociatesApproval", false, 807, (entity*) IFC4_types[806]);
    IFC4_types[808] = new entity("IfcRelAssociatesClassification", false, 808, (entity*) IFC4_types[806]);
    IFC4_types[809] = new entity("IfcRelAssociatesConstraint", false, 809, (entity*) IFC4_types[806]);
    IFC4_types[810] = new entity("IfcRelAssociatesDocument", false, 810, (entity*) IFC4_types[806]);
    IFC4_types[811] = new entity("IfcRelAssociatesLibrary", false, 811, (entity*) IFC4_types[806]);
    IFC4_types[812] = new entity("IfcRelAssociatesMaterial", false, 812, (entity*) IFC4_types[806]);
    IFC4_types[814] = new entity("IfcRelConnects", true, 814, (entity*) IFC4_types[813]);
    IFC4_types[815] = new entity("IfcRelConnectsElements", false, 815, (entity*) IFC4_types[814]);
    IFC4_types[816] = new entity("IfcRelConnectsPathElements", false, 816, (entity*) IFC4_types[815]);
    IFC4_types[818] = new entity("IfcRelConnectsPortToElement", false, 818, (entity*) IFC4_types[814]);
    IFC4_types[817] = new entity("IfcRelConnectsPorts", false, 817, (entity*) IFC4_types[814]);
    IFC4_types[819] = new entity("IfcRelConnectsStructuralActivity", false, 819, (entity*) IFC4_types[814]);
    IFC4_types[820] = new entity("IfcRelConnectsStructuralMember", false, 820, (entity*) IFC4_types[814]);
    IFC4_types[821] = new entity("IfcRelConnectsWithEccentricity", false, 821, (entity*) IFC4_types[820]);
    IFC4_types[822] = new entity("IfcRelConnectsWithRealizingElements", false, 822, (entity*) IFC4_types[815]);
    IFC4_types[823] = new entity("IfcRelContainedInSpatialStructure", false, 823, (entity*) IFC4_types[814]);
    IFC4_types[824] = new entity("IfcRelCoversBldgElements", false, 824, (entity*) IFC4_types[814]);
    IFC4_types[825] = new entity("IfcRelCoversSpaces", false, 825, (entity*) IFC4_types[814]);
    IFC4_types[826] = new entity("IfcRelDeclares", false, 826, (entity*) IFC4_types[813]);
    IFC4_types[827] = new entity("IfcRelDecomposes", true, 827, (entity*) IFC4_types[813]);
    IFC4_types[828] = new entity("IfcRelDefines", true, 828, (entity*) IFC4_types[813]);
    IFC4_types[829] = new entity("IfcRelDefinesByObject", false, 829, (entity*) IFC4_types[828]);
    IFC4_types[830] = new entity("IfcRelDefinesByProperties", false, 830, (entity*) IFC4_types[828]);
    IFC4_types[831] = new entity("IfcRelDefinesByTemplate", false, 831, (entity*) IFC4_types[828]);
    IFC4_types[832] = new entity("IfcRelDefinesByType", false, 832, (entity*) IFC4_types[828]);
    IFC4_types[833] = new entity("IfcRelFillsElement", false, 833, (entity*) IFC4_types[814]);
    IFC4_types[834] = new entity("IfcRelFlowControlElements", false, 834, (entity*) IFC4_types[814]);
    IFC4_types[835] = new entity("IfcRelInterferesElements", false, 835, (entity*) IFC4_types[814]);
    IFC4_types[836] = new entity("IfcRelNests", false, 836, (entity*) IFC4_types[827]);
    IFC4_types[837] = new entity("IfcRelProjectsElement", false, 837, (entity*) IFC4_types[827]);
    IFC4_types[838] = new entity("IfcRelReferencedInSpatialStructure", false, 838, (entity*) IFC4_types[814]);
    IFC4_types[839] = new entity("IfcRelSequence", false, 839, (entity*) IFC4_types[814]);
    IFC4_types[840] = new entity("IfcRelServicesBuildings", false, 840, (entity*) IFC4_types[814]);
    IFC4_types[841] = new entity("IfcRelSpaceBoundary", false, 841, (entity*) IFC4_types[814]);
    IFC4_types[842] = new entity("IfcRelSpaceBoundary1stLevel", false, 842, (entity*) IFC4_types[841]);
    IFC4_types[843] = new entity("IfcRelSpaceBoundary2ndLevel", false, 843, (entity*) IFC4_types[842]);
    IFC4_types[844] = new entity("IfcRelVoidsElement", false, 844, (entity*) IFC4_types[827]);
    IFC4_types[845] = new entity("IfcReparametrisedCompositeCurveSegment", false, 845, (entity*) IFC4_types[167]);
    IFC4_types[850] = new entity("IfcResource", true, 850, (entity*) IFC4_types[614]);
    IFC4_types[857] = new entity("IfcRevolvedAreaSolid", false, 857, (entity*) IFC4_types[1019]);
    IFC4_types[858] = new entity("IfcRevolvedAreaSolidTapered", false, 858, (entity*) IFC4_types[857]);
    IFC4_types[859] = new entity("IfcRightCircularCone", false, 859, (entity*) IFC4_types[228]);
    IFC4_types[860] = new entity("IfcRightCircularCylinder", false, 860, (entity*) IFC4_types[228]);
    IFC4_types[897] = new entity("IfcSimplePropertyTemplate", false, 897, (entity*) IFC4_types[743]);
    IFC4_types[928] = new entity("IfcSpatialElement", true, 928, (entity*) IFC4_types[710]);
    IFC4_types[929] = new entity("IfcSpatialElementType", true, 929, (entity*) IFC4_types[1108]);
    IFC4_types[930] = new entity("IfcSpatialStructureElement", true, 930, (entity*) IFC4_types[928]);
    IFC4_types[931] = new entity("IfcSpatialStructureElementType", true, 931, (entity*) IFC4_types[929]);
    IFC4_types[932] = new entity("IfcSpatialZone", false, 932, (entity*) IFC4_types[928]);
    IFC4_types[933] = new entity("IfcSpatialZoneType", false, 933, (entity*) IFC4_types[929]);
    IFC4_types[939] = new entity("IfcSphere", false, 939, (entity*) IFC4_types[228]);
    IFC4_types[940] = new entity("IfcSphericalSurface", false, 940, (entity*) IFC4_types[346]);
    IFC4_types[952] = new entity("IfcStructuralActivity", true, 952, (entity*) IFC4_types[710]);
    IFC4_types[964] = new entity("IfcStructuralItem", true, 964, (entity*) IFC4_types[710]);
    IFC4_types[979] = new entity("IfcStructuralMember", true, 979, (entity*) IFC4_types[964]);
    IFC4_types[984] = new entity("IfcStructuralReaction", true, 984, (entity*) IFC4_types[952]);
    IFC4_types[989] = new entity("IfcStructuralSurfaceMember", false, 989, (entity*) IFC4_types[979]);
    IFC4_types[991] = new entity("IfcStructuralSurfaceMemberVarying", false, 991, (entity*) IFC4_types[989]);
    IFC4_types[992] = new entity("IfcStructuralSurfaceReaction", false, 992, (entity*) IFC4_types[984]);
    IFC4_types[998] = new entity("IfcSubContractResourceType", false, 998, (entity*) IFC4_types[197]);
    IFC4_types[1002] = new entity("IfcSurfaceCurve", false, 1002, (entity*) IFC4_types[237]);
    IFC4_types[1003] = new entity("IfcSurfaceCurveSweptAreaSolid", false, 1003, (entity*) IFC4_types[1019]);
    IFC4_types[1006] = new entity("IfcSurfaceOfLinearExtrusion", false, 1006, (entity*) IFC4_types[1022]);
    IFC4_types[1007] = new entity("IfcSurfaceOfRevolution", false, 1007, (entity*) IFC4_types[1022]);
    IFC4_types[1028] = new entity("IfcSystemFurnitureElementType", false, 1028, (entity*) IFC4_types[444]);
    IFC4_types[1036] = new entity("IfcTask", false, 1036, (entity*) IFC4_types[708]);
    IFC4_types[1040] = new entity("IfcTaskType", false, 1040, (entity*) IFC4_types[1107]);
    IFC4_types[1051] = new entity("IfcTessellatedFaceSet", true, 1051, (entity*) IFC4_types[1052]);
    IFC4_types[1087] = new entity("IfcToroidalSurface", false, 1087, (entity*) IFC4_types[346]);
    IFC4_types[1095] = new entity("IfcTransportElementType", false, 1095, (entity*) IFC4_types[354]);
    IFC4_types[1098] = new entity("IfcTriangulatedFaceSet", false, 1098, (entity*) IFC4_types[1051]);
    IFC4_types[1152] = new entity("IfcWindowLiningProperties", false, 1152, (entity*) IFC4_types[694]);
    IFC4_types[1155] = new entity("IfcWindowPanelProperties", false, 1155, (entity*) IFC4_types[694]);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[579]);
        items.push_back(IFC4_types[782]);
        items.push_back(IFC4_types[1121]);
        IFC4_types[37] = new select_type("IfcAppliedValueSelect", 37, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[55]);
        items.push_back(IFC4_types[56]);
        IFC4_types[54] = new select_type("IfcAxis2Placement", 54, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IFC4_types[73]);
        items.push_back(IFC4_types[228]);
        items.push_back(IFC4_types[466]);
        items.push_back(IFC4_types[915]);
        items.push_back(IFC4_types[1051]);
        IFC4_types[71] = new select_type("IfcBooleanOperand", 71, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[153]);
        items.push_back(IFC4_types[690]);
        IFC4_types[149] = new select_type("IfcColour", 149, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[151]);
        items.push_back(IFC4_types[611]);
        IFC4_types[150] = new select_type("IfcColourOrFactor", 150, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[73]);
        items.push_back(IFC4_types[228]);
        IFC4_types[229] = new select_type("IfcCsgSelect", 229, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[245]);
        items.push_back(IFC4_types[691]);
        IFC4_types[248] = new select_type("IfcCurveStyleFontSelect", 248, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IFC4_types[149]);
        items.push_back(IFC4_types[376]);
        items.push_back(IFC4_types[404]);
        items.push_back(IFC4_types[405]);
        IFC4_types[406] = new select_type("IfcFillStyleSelect", 406, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[237]);
        items.push_back(IFC4_types[675]);
        items.push_back(IFC4_types[1001]);
        IFC4_types[457] = new select_type("IfcGeometricSetSelect", 457, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[267]);
        items.push_back(IFC4_types[1135]);
        IFC4_types[463] = new select_type("IfcGridPlacementDirectionSelect", 463, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IFC4_types[36]);
        items.push_back(IFC4_types[579]);
        items.push_back(IFC4_types[782]);
        items.push_back(IFC4_types[1030]);
        items.push_back(IFC4_types[1081]);
        items.push_back(IFC4_types[1121]);
        IFC4_types[591] = new select_type("IfcMetricValueSelect", 591, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[708]);
        items.push_back(IFC4_types[1107]);
        IFC4_types[709] = new select_type("IfcProcessSelect", 709, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[710]);
        items.push_back(IFC4_types[1108]);
        IFC4_types[714] = new select_type("IfcProductSelect", 714, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[736]);
        items.push_back(IFC4_types[738]);
        IFC4_types[737] = new select_type("IfcPropertySetDefinitionSelect", 737, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[850]);
        items.push_back(IFC4_types[1109]);
        IFC4_types[855] = new select_type("IfcResourceSelect", 855, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[145]);
        items.push_back(IFC4_types[628]);
        IFC4_types[894] = new select_type("IfcShell", 894, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[145]);
        items.push_back(IFC4_types[915]);
        IFC4_types[916] = new select_type("IfcSolidOrShell", 916, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[387]);
        items.push_back(IFC4_types[390]);
        items.push_back(IFC4_types[1001]);
        IFC4_types[1008] = new select_type("IfcSurfaceOrFaceSurface", 1008, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[119]);
        items.push_back(IFC4_types[638]);
        IFC4_types[1101] = new select_type("IfcTrimmingSelect", 1101, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[267]);
        items.push_back(IFC4_types[1126]);
        IFC4_types[1127] = new select_type("IfcVectorOrDirection", 1127, items);
    }
    IFC4_types[6] = new entity("IfcActor", false, 6, (entity*) IFC4_types[614]);
    IFC4_types[14] = new entity("IfcAdvancedBrep", false, 14, (entity*) IFC4_types[551]);
    IFC4_types[15] = new entity("IfcAdvancedBrepWithVoids", false, 15, (entity*) IFC4_types[14]);
    IFC4_types[33] = new entity("IfcAnnotation", false, 33, (entity*) IFC4_types[710]);
    IFC4_types[88] = new entity("IfcBSplineSurface", true, 88, (entity*) IFC4_types[81]);
    IFC4_types[90] = new entity("IfcBSplineSurfaceWithKnots", false, 90, (entity*) IFC4_types[88]);
    IFC4_types[65] = new entity("IfcBlock", false, 65, (entity*) IFC4_types[228]);
    IFC4_types[70] = new entity("IfcBooleanClippingResult", false, 70, (entity*) IFC4_types[73]);
    IFC4_types[80] = new entity("IfcBoundedCurve", true, 80, (entity*) IFC4_types[237]);
    IFC4_types[91] = new entity("IfcBuilding", false, 91, (entity*) IFC4_types[930]);
    IFC4_types[99] = new entity("IfcBuildingElementType", true, 99, (entity*) IFC4_types[354]);
    IFC4_types[100] = new entity("IfcBuildingStorey", false, 100, (entity*) IFC4_types[930]);
    IFC4_types[134] = new entity("IfcChimneyType", false, 134, (entity*) IFC4_types[99]);
    IFC4_types[137] = new entity("IfcCircleHollowProfileDef", false, 137, (entity*) IFC4_types[138]);
    IFC4_types[140] = new entity("IfcCivilElementType", false, 140, (entity*) IFC4_types[354]);
    IFC4_types[156] = new entity("IfcColumnType", false, 156, (entity*) IFC4_types[99]);
    IFC4_types[163] = new entity("IfcComplexPropertyTemplate", false, 163, (entity*) IFC4_types[743]);
    IFC4_types[165] = new entity("IfcCompositeCurve", false, 165, (entity*) IFC4_types[80]);
    IFC4_types[166] = new entity("IfcCompositeCurveOnSurface", false, 166, (entity*) IFC4_types[165]);
    IFC4_types[176] = new entity("IfcConic", true, 176, (entity*) IFC4_types[237]);
    IFC4_types[188] = new entity("IfcConstructionEquipmentResourceType", false, 188, (entity*) IFC4_types[197]);
    IFC4_types[191] = new entity("IfcConstructionMaterialResourceType", false, 191, (entity*) IFC4_types[197]);
    IFC4_types[194] = new entity("IfcConstructionProductResourceType", false, 194, (entity*) IFC4_types[197]);
    IFC4_types[196] = new entity("IfcConstructionResource", true, 196, (entity*) IFC4_types[850]);
    IFC4_types[201] = new entity("IfcControl", true, 201, (entity*) IFC4_types[614]);
    IFC4_types[216] = new entity("IfcCostItem", false, 216, (entity*) IFC4_types[201]);
    IFC4_types[218] = new entity("IfcCostSchedule", false, 218, (entity*) IFC4_types[201]);
    IFC4_types[223] = new entity("IfcCoveringType", false, 223, (entity*) IFC4_types[99]);
    IFC4_types[225] = new entity("IfcCrewResource", false, 225, (entity*) IFC4_types[196]);
    IFC4_types[234] = new entity("IfcCurtainWallType", false, 234, (entity*) IFC4_types[99]);
    IFC4_types[249] = new entity("IfcCylindricalSurface", false, 249, (entity*) IFC4_types[346]);
    IFC4_types[279] = new entity("IfcDistributionElementType", false, 279, (entity*) IFC4_types[354]);
    IFC4_types[281] = new entity("IfcDistributionFlowElementType", true, 281, (entity*) IFC4_types[279]);
    IFC4_types[293] = new entity("IfcDoorLiningProperties", false, 293, (entity*) IFC4_types[694]);
    IFC4_types[296] = new entity("IfcDoorPanelProperties", false, 296, (entity*) IFC4_types[694]);
    IFC4_types[301] = new entity("IfcDoorType", false, 301, (entity*) IFC4_types[99]);
    IFC4_types[305] = new entity("IfcDraughtingPreDefinedColour", false, 305, (entity*) IFC4_types[690]);
    IFC4_types[306] = new entity("IfcDraughtingPreDefinedCurveFont", false, 306, (entity*) IFC4_types[691]);
    IFC4_types[345] = new entity("IfcElement", true, 345, (entity*) IFC4_types[710]);
    IFC4_types[347] = new entity("IfcElementAssembly", false, 347, (entity*) IFC4_types[345]);
    IFC4_types[348] = new entity("IfcElementAssemblyType", false, 348, (entity*) IFC4_types[354]);
    IFC4_types[350] = new entity("IfcElementComponent", true, 350, (entity*) IFC4_types[345]);
    IFC4_types[351] = new entity("IfcElementComponentType", true, 351, (entity*) IFC4_types[354]);
    IFC4_types[355] = new entity("IfcEllipse", false, 355, (entity*) IFC4_types[176]);
    IFC4_types[358] = new entity("IfcEnergyConversionDeviceType", true, 358, (entity*) IFC4_types[281]);
    IFC4_types[361] = new entity("IfcEngineType", false, 361, (entity*) IFC4_types[358]);
    IFC4_types[364] = new entity("IfcEvaporativeCoolerType", false, 364, (entity*) IFC4_types[358]);
    IFC4_types[367] = new entity("IfcEvaporatorType", false, 367, (entity*) IFC4_types[358]);
    IFC4_types[369] = new entity("IfcEvent", false, 369, (entity*) IFC4_types[708]);
    IFC4_types[383] = new entity("IfcExternalSpatialStructureElement", true, 383, (entity*) IFC4_types[928]);
    IFC4_types[391] = new entity("IfcFacetedBrep", false, 391, (entity*) IFC4_types[551]);
    IFC4_types[392] = new entity("IfcFacetedBrepWithVoids", false, 392, (entity*) IFC4_types[391]);
    IFC4_types[397] = new entity("IfcFastener", false, 397, (entity*) IFC4_types[350]);
    IFC4_types[398] = new entity("IfcFastenerType", false, 398, (entity*) IFC4_types[351]);
    IFC4_types[400] = new entity("IfcFeatureElement", true, 400, (entity*) IFC4_types[345]);
    IFC4_types[401] = new entity("IfcFeatureElementAddition", true, 401, (entity*) IFC4_types[400]);
    IFC4_types[402] = new entity("IfcFeatureElementSubtraction", true, 402, (entity*) IFC4_types[400]);
    IFC4_types[415] = new entity("IfcFlowControllerType", true, 415, (entity*) IFC4_types[281]);
    IFC4_types[418] = new entity("IfcFlowFittingType", true, 418, (entity*) IFC4_types[281]);
    IFC4_types[423] = new entity("IfcFlowMeterType", false, 423, (entity*) IFC4_types[415]);
    IFC4_types[426] = new entity("IfcFlowMovingDeviceType", true, 426, (entity*) IFC4_types[281]);
    IFC4_types[428] = new entity("IfcFlowSegmentType", true, 428, (entity*) IFC4_types[281]);
    IFC4_types[430] = new entity("IfcFlowStorageDeviceType", true, 430, (entity*) IFC4_types[281]);
    IFC4_types[432] = new entity("IfcFlowTerminalType", true, 432, (entity*) IFC4_types[281]);
    IFC4_types[434] = new entity("IfcFlowTreatmentDeviceType", true, 434, (entity*) IFC4_types[281]);
    IFC4_types[439] = new entity("IfcFootingType", false, 439, (entity*) IFC4_types[99]);
    IFC4_types[443] = new entity("IfcFurnishingElement", false, 443, (entity*) IFC4_types[345]);
    IFC4_types[445] = new entity("IfcFurniture", false, 445, (entity*) IFC4_types[443]);
    IFC4_types[448] = new entity("IfcGeographicElement", false, 448, (entity*) IFC4_types[345]);
    IFC4_types[460] = new entity("IfcGrid", false, 460, (entity*) IFC4_types[710]);
    IFC4_types[465] = new entity("IfcGroup", false, 465, (entity*) IFC4_types[614]);
    IFC4_types[469] = new entity("IfcHeatExchangerType", false, 469, (entity*) IFC4_types[358]);
    IFC4_types[474] = new entity("IfcHumidifierType", false, 474, (entity*) IFC4_types[358]);
    IFC4_types[480] = new entity("IfcIndexedPolyCurve", false, 480, (entity*) IFC4_types[80]);
    IFC4_types[489] = new entity("IfcInterceptorType", false, 489, (entity*) IFC4_types[434]);
    IFC4_types[492] = new entity("IfcIntersectionCurve", false, 492, (entity*) IFC4_types[1002]);
    IFC4_types[493] = new entity("IfcInventory", false, 493, (entity*) IFC4_types[465]);
    IFC4_types[501] = new entity("IfcJunctionBoxType", false, 501, (entity*) IFC4_types[418]);
    IFC4_types[506] = new entity("IfcLaborResource", false, 506, (entity*) IFC4_types[196]);
    IFC4_types[511] = new entity("IfcLampType", false, 511, (entity*) IFC4_types[432]);
    IFC4_types[525] = new entity("IfcLightFixtureType", false, 525, (entity*) IFC4_types[432]);
    IFC4_types[580] = new entity("IfcMechanicalFastener", false, 580, (entity*) IFC4_types[350]);
    IFC4_types[581] = new entity("IfcMechanicalFastenerType", false, 581, (entity*) IFC4_types[351]);
    IFC4_types[584] = new entity("IfcMedicalDeviceType", false, 584, (entity*) IFC4_types[432]);
    IFC4_types[588] = new entity("IfcMemberType", false, 588, (entity*) IFC4_types[99]);
    IFC4_types[607] = new entity("IfcMotorConnectionType", false, 607, (entity*) IFC4_types[358]);
    IFC4_types[621] = new entity("IfcOccupant", false, 621, (entity*) IFC4_types[6]);
    IFC4_types[625] = new entity("IfcOpeningElement", false, 625, (entity*) IFC4_types[402]);
    IFC4_types[627] = new entity("IfcOpeningStandardCase", false, 627, (entity*) IFC4_types[625]);
    IFC4_types[634] = new entity("IfcOutletType", false, 634, (entity*) IFC4_types[432]);
    IFC4_types[641] = new entity("IfcPerformanceHistory", false, 641, (entity*) IFC4_types[201]);
    IFC4_types[644] = new entity("IfcPermeableCoveringProperties", false, 644, (entity*) IFC4_types[694]);
    IFC4_types[645] = new entity("IfcPermit", false, 645, (entity*) IFC4_types[201]);
    IFC4_types[656] = new entity("IfcPileType", false, 656, (entity*) IFC4_types[99]);
    IFC4_types[659] = new entity("IfcPipeFittingType", false, 659, (entity*) IFC4_types[418]);
    IFC4_types[662] = new entity("IfcPipeSegmentType", false, 662, (entity*) IFC4_types[428]);
    IFC4_types[673] = new entity("IfcPlateType", false, 673, (entity*) IFC4_types[99]);
    IFC4_types[680] = new entity("IfcPolygonalFaceSet", false, 680, (entity*) IFC4_types[1051]);
    IFC4_types[681] = new entity("IfcPolyline", false, 681, (entity*) IFC4_types[80]);
    IFC4_types[683] = new entity("IfcPort", true, 683, (entity*) IFC4_types[710]);
    IFC4_types[705] = new entity("IfcProcedure", false, 705, (entity*) IFC4_types[708]);
    IFC4_types[724] = new entity("IfcProjectOrder", false, 724, (entity*) IFC4_types[201]);
    IFC4_types[721] = new entity("IfcProjectionElement", false, 721, (entity*) IFC4_types[401]);
    IFC4_types[749] = new entity("IfcProtectiveDeviceType", false, 749, (entity*) IFC4_types[415]);
    IFC4_types[753] = new entity("IfcPumpType", false, 753, (entity*) IFC4_types[426]);
    IFC4_types[764] = new entity("IfcRailingType", false, 764, (entity*) IFC4_types[99]);
    IFC4_types[768] = new entity("IfcRampFlightType", false, 768, (entity*) IFC4_types[99]);
    IFC4_types[770] = new entity("IfcRampType", false, 770, (entity*) IFC4_types[99]);
    IFC4_types[774] = new entity("IfcRationalBSplineSurfaceWithKnots", false, 774, (entity*) IFC4_types[90]);
    IFC4_types[792] = new entity("IfcReinforcingElement", true, 792, (entity*) IFC4_types[350]);
    IFC4_types[793] = new entity("IfcReinforcingElementType", true, 793, (entity*) IFC4_types[351]);
    IFC4_types[794] = new entity("IfcReinforcingMesh", false, 794, (entity*) IFC4_types[792]);
    IFC4_types[795] = new entity("IfcReinforcingMeshType", false, 795, (entity*) IFC4_types[793]);
    IFC4_types[797] = new entity("IfcRelAggregates", false, 797, (entity*) IFC4_types[827]);
    IFC4_types[863] = new entity("IfcRoofType", false, 863, (entity*) IFC4_types[99]);
    IFC4_types[872] = new entity("IfcSanitaryTerminalType", false, 872, (entity*) IFC4_types[432]);
    IFC4_types[875] = new entity("IfcSeamCurve", false, 875, (entity*) IFC4_types[1002]);
    IFC4_types[888] = new entity("IfcShadingDeviceType", false, 888, (entity*) IFC4_types[99]);
    IFC4_types[901] = new entity("IfcSite", false, 901, (entity*) IFC4_types[930]);
    IFC4_types[908] = new entity("IfcSlabType", false, 908, (entity*) IFC4_types[99]);
    IFC4_types[912] = new entity("IfcSolarDeviceType", false, 912, (entity*) IFC4_types[358]);
    IFC4_types[921] = new entity("IfcSpace", false, 921, (entity*) IFC4_types[930]);
    IFC4_types[924] = new entity("IfcSpaceHeaterType", false, 924, (entity*) IFC4_types[432]);
    IFC4_types[926] = new entity("IfcSpaceType", false, 926, (entity*) IFC4_types[931]);
    IFC4_types[942] = new entity("IfcStackTerminalType", false, 942, (entity*) IFC4_types[432]);
    IFC4_types[946] = new entity("IfcStairFlightType", false, 946, (entity*) IFC4_types[99]);
    IFC4_types[948] = new entity("IfcStairType", false, 948, (entity*) IFC4_types[99]);
    IFC4_types[951] = new entity("IfcStructuralAction", true, 951, (entity*) IFC4_types[952]);
    IFC4_types[955] = new entity("IfcStructuralConnection", true, 955, (entity*) IFC4_types[964]);
    IFC4_types[957] = new entity("IfcStructuralCurveAction", false, 957, (entity*) IFC4_types[951]);
    IFC4_types[959] = new entity("IfcStructuralCurveConnection", false, 959, (entity*) IFC4_types[955]);
    IFC4_types[960] = new entity("IfcStructuralCurveMember", false, 960, (entity*) IFC4_types[979]);
    IFC4_types[962] = new entity("IfcStructuralCurveMemberVarying", false, 962, (entity*) IFC4_types[960]);
    IFC4_types[963] = new entity("IfcStructuralCurveReaction", false, 963, (entity*) IFC4_types[984]);
    IFC4_types[965] = new entity("IfcStructuralLinearAction", false, 965, (entity*) IFC4_types[957]);
    IFC4_types[969] = new entity("IfcStructuralLoadGroup", false, 969, (entity*) IFC4_types[465]);
    IFC4_types[981] = new entity("IfcStructuralPointAction", false, 981, (entity*) IFC4_types[951]);
    IFC4_types[982] = new entity("IfcStructuralPointConnection", false, 982, (entity*) IFC4_types[955]);
    IFC4_types[983] = new entity("IfcStructuralPointReaction", false, 983, (entity*) IFC4_types[984]);
    IFC4_types[985] = new entity("IfcStructuralResultGroup", false, 985, (entity*) IFC4_types[465]);
    IFC4_types[986] = new entity("IfcStructuralSurfaceAction", false, 986, (entity*) IFC4_types[951]);
    IFC4_types[988] = new entity("IfcStructuralSurfaceConnection", false, 988, (entity*) IFC4_types[955]);
    IFC4_types[997] = new entity("IfcSubContractResource", false, 997, (entity*) IFC4_types[196]);
    IFC4_types[1004] = new entity("IfcSurfaceFeature", false, 1004, (entity*) IFC4_types[400]);
    IFC4_types[1024] = new entity("IfcSwitchingDeviceType", false, 1024, (entity*) IFC4_types[415]);
    IFC4_types[1026] = new entity("IfcSystem", false, 1026, (entity*) IFC4_types[465]);
    IFC4_types[1027] = new entity("IfcSystemFurnitureElement", false, 1027, (entity*) IFC4_types[443]);
    IFC4_types[1034] = new entity("IfcTankType", false, 1034, (entity*) IFC4_types[430]);
    IFC4_types[1045] = new entity("IfcTendon", false, 1045, (entity*) IFC4_types[792]);
    IFC4_types[1046] = new entity("IfcTendonAnchor", false, 1046, (entity*) IFC4_types[792]);
    IFC4_types[1047] = new entity("IfcTendonAnchorType", false, 1047, (entity*) IFC4_types[793]);
    IFC4_types[1049] = new entity("IfcTendonType", false, 1049, (entity*) IFC4_types[793]);
    IFC4_types[1090] = new entity("IfcTransformerType", false, 1090, (entity*) IFC4_types[358]);
    IFC4_types[1094] = new entity("IfcTransportElement", false, 1094, (entity*) IFC4_types[345]);
    IFC4_types[1099] = new entity("IfcTrimmedCurve", false, 1099, (entity*) IFC4_types[80]);
    IFC4_types[1104] = new entity("IfcTubeBundleType", false, 1104, (entity*) IFC4_types[358]);
    IFC4_types[1115] = new entity("IfcUnitaryEquipmentType", false, 1115, (entity*) IFC4_types[358]);
    IFC4_types[1123] = new entity("IfcValveType", false, 1123, (entity*) IFC4_types[415]);
    IFC4_types[1131] = new entity("IfcVibrationIsolator", false, 1131, (entity*) IFC4_types[350]);
    IFC4_types[1132] = new entity("IfcVibrationIsolatorType", false, 1132, (entity*) IFC4_types[351]);
    IFC4_types[1134] = new entity("IfcVirtualElement", false, 1134, (entity*) IFC4_types[345]);
    IFC4_types[1136] = new entity("IfcVoidingFeature", false, 1136, (entity*) IFC4_types[402]);
    IFC4_types[1143] = new entity("IfcWallType", false, 1143, (entity*) IFC4_types[99]);
    IFC4_types[1149] = new entity("IfcWasteTerminalType", false, 1149, (entity*) IFC4_types[432]);
    IFC4_types[1160] = new entity("IfcWindowType", false, 1160, (entity*) IFC4_types[99]);
    IFC4_types[1163] = new entity("IfcWorkCalendar", false, 1163, (entity*) IFC4_types[201]);
    IFC4_types[1165] = new entity("IfcWorkControl", true, 1165, (entity*) IFC4_types[201]);
    IFC4_types[1166] = new entity("IfcWorkPlan", false, 1166, (entity*) IFC4_types[1165]);
    IFC4_types[1168] = new entity("IfcWorkSchedule", false, 1168, (entity*) IFC4_types[1165]);
    IFC4_types[1171] = new entity("IfcZone", false, 1171, (entity*) IFC4_types[1026]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[246]);
        items.push_back(IFC4_types[248]);
        IFC4_types[240] = new select_type("IfcCurveFontOrScaledCurveFontSelect", 240, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IFC4_types[166]);
        items.push_back(IFC4_types[640]);
        items.push_back(IFC4_types[1002]);
        IFC4_types[242] = new select_type("IfcCurveOnSurface", 242, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[80]);
        items.push_back(IFC4_types[319]);
        IFC4_types[243] = new select_type("IfcCurveOrEdgeCurve", 243, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[345]);
        items.push_back(IFC4_types[964]);
        IFC4_types[953] = new select_type("IfcStructuralActivityAssignmentSelect", 953, items);
    }
    IFC4_types[2] = new entity("IfcActionRequest", false, 2, (entity*) IFC4_types[201]);
    IFC4_types[19] = new entity("IfcAirTerminalBoxType", false, 19, (entity*) IFC4_types[415]);
    IFC4_types[21] = new entity("IfcAirTerminalType", false, 21, (entity*) IFC4_types[432]);
    IFC4_types[24] = new entity("IfcAirToAirHeatRecoveryType", false, 24, (entity*) IFC4_types[358]);
    IFC4_types[48] = new entity("IfcAsset", false, 48, (entity*) IFC4_types[465]);
    IFC4_types[51] = new entity("IfcAudioVisualApplianceType", false, 51, (entity*) IFC4_types[432]);
    IFC4_types[85] = new entity("IfcBSplineCurve", true, 85, (entity*) IFC4_types[80]);
    IFC4_types[87] = new entity("IfcBSplineCurveWithKnots", false, 87, (entity*) IFC4_types[85]);
    IFC4_types[59] = new entity("IfcBeamType", false, 59, (entity*) IFC4_types[99]);
    IFC4_types[67] = new entity("IfcBoilerType", false, 67, (entity*) IFC4_types[358]);
    IFC4_types[75] = new entity("IfcBoundaryCurve", false, 75, (entity*) IFC4_types[166]);
    IFC4_types[92] = new entity("IfcBuildingElement", true, 92, (entity*) IFC4_types[345]);
    IFC4_types[93] = new entity("IfcBuildingElementPart", false, 93, (entity*) IFC4_types[350]);
    IFC4_types[94] = new entity("IfcBuildingElementPartType", false, 94, (entity*) IFC4_types[351]);
    IFC4_types[96] = new entity("IfcBuildingElementProxy", false, 96, (entity*) IFC4_types[92]);
    IFC4_types[97] = new entity("IfcBuildingElementProxyType", false, 97, (entity*) IFC4_types[99]);
    IFC4_types[101] = new entity("IfcBuildingSystem", false, 101, (entity*) IFC4_types[1026]);
    IFC4_types[104] = new entity("IfcBurnerType", false, 104, (entity*) IFC4_types[358]);
    IFC4_types[107] = new entity("IfcCableCarrierFittingType", false, 107, (entity*) IFC4_types[418]);
    IFC4_types[110] = new entity("IfcCableCarrierSegmentType", false, 110, (entity*) IFC4_types[428]);
    IFC4_types[113] = new entity("IfcCableFittingType", false, 113, (entity*) IFC4_types[418]);
    IFC4_types[116] = new entity("IfcCableSegmentType", false, 116, (entity*) IFC4_types[428]);
    IFC4_types[131] = new entity("IfcChillerType", false, 131, (entity*) IFC4_types[358]);
    IFC4_types[133] = new entity("IfcChimney", false, 133, (entity*) IFC4_types[92]);
    IFC4_types[136] = new entity("IfcCircle", false, 136, (entity*) IFC4_types[176]);
    IFC4_types[139] = new entity("IfcCivilElement", false, 139, (entity*) IFC4_types[345]);
    IFC4_types[147] = new entity("IfcCoilType", false, 147, (entity*) IFC4_types[358]);
    IFC4_types[154] = new entity("IfcColumn", false, 154, (entity*) IFC4_types[92]);
    IFC4_types[155] = new entity("IfcColumnStandardCase", false, 155, (entity*) IFC4_types[154]);
    IFC4_types[159] = new entity("IfcCommunicationsApplianceType", false, 159, (entity*) IFC4_types[432]);
    IFC4_types[171] = new entity("IfcCompressorType", false, 171, (entity*) IFC4_types[426]);
    IFC4_types[174] = new entity("IfcCondenserType", false, 174, (entity*) IFC4_types[358]);
    IFC4_types[187] = new entity("IfcConstructionEquipmentResource", false, 187, (entity*) IFC4_types[196]);
    IFC4_types[190] = new entity("IfcConstructionMaterialResource", false, 190, (entity*) IFC4_types[196]);
    IFC4_types[193] = new entity("IfcConstructionProductResource", false, 193, (entity*) IFC4_types[196]);
    IFC4_types[208] = new entity("IfcCooledBeamType", false, 208, (entity*) IFC4_types[358]);
    IFC4_types[211] = new entity("IfcCoolingTowerType", false, 211, (entity*) IFC4_types[358]);
    IFC4_types[222] = new entity("IfcCovering", false, 222, (entity*) IFC4_types[92]);
    IFC4_types[233] = new entity("IfcCurtainWall", false, 233, (entity*) IFC4_types[92]);
    IFC4_types[251] = new entity("IfcDamperType", false, 251, (entity*) IFC4_types[415]);
    IFC4_types[269] = new entity("IfcDiscreteAccessory", false, 269, (entity*) IFC4_types[350]);
    IFC4_types[270] = new entity("IfcDiscreteAccessoryType", false, 270, (entity*) IFC4_types[351]);
    IFC4_types[273] = new entity("IfcDistributionChamberElementType", false, 273, (entity*) IFC4_types[281]);
    IFC4_types[277] = new entity("IfcDistributionControlElementType", true, 277, (entity*) IFC4_types[279]);
    IFC4_types[278] = new entity("IfcDistributionElement", false, 278, (entity*) IFC4_types[345]);
    IFC4_types[280] = new entity("IfcDistributionFlowElement", false, 280, (entity*) IFC4_types[278]);
    IFC4_types[282] = new entity("IfcDistributionPort", false, 282, (entity*) IFC4_types[683]);
    IFC4_types[284] = new entity("IfcDistributionSystem", false, 284, (entity*) IFC4_types[1026]);
    IFC4_types[292] = new entity("IfcDoor", false, 292, (entity*) IFC4_types[92]);
    IFC4_types[297] = new entity("IfcDoorStandardCase", false, 297, (entity*) IFC4_types[292]);
    IFC4_types[308] = new entity("IfcDuctFittingType", false, 308, (entity*) IFC4_types[418]);
    IFC4_types[311] = new entity("IfcDuctSegmentType", false, 311, (entity*) IFC4_types[428]);
    IFC4_types[314] = new entity("IfcDuctSilencerType", false, 314, (entity*) IFC4_types[434]);
    IFC4_types[322] = new entity("IfcElectricApplianceType", false, 322, (entity*) IFC4_types[432]);
    IFC4_types[329] = new entity("IfcElectricDistributionBoardType", false, 329, (entity*) IFC4_types[415]);
    IFC4_types[332] = new entity("IfcElectricFlowStorageDeviceType", false, 332, (entity*) IFC4_types[430]);
    IFC4_types[335] = new entity("IfcElectricGeneratorType", false, 335, (entity*) IFC4_types[358]);
    IFC4_types[338] = new entity("IfcElectricMotorType", false, 338, (entity*) IFC4_types[358]);
    IFC4_types[342] = new entity("IfcElectricTimeControlType", false, 342, (entity*) IFC4_types[415]);
    IFC4_types[357] = new entity("IfcEnergyConversionDevice", false, 357, (entity*) IFC4_types[280]);
    IFC4_types[360] = new entity("IfcEngine", false, 360, (entity*) IFC4_types[357]);
    IFC4_types[363] = new entity("IfcEvaporativeCooler", false, 363, (entity*) IFC4_types[357]);
    IFC4_types[366] = new entity("IfcEvaporator", false, 366, (entity*) IFC4_types[357]);
    IFC4_types[381] = new entity("IfcExternalSpatialElement", false, 381, (entity*) IFC4_types[383]);
    IFC4_types[395] = new entity("IfcFanType", false, 395, (entity*) IFC4_types[426]);
    IFC4_types[408] = new entity("IfcFilterType", false, 408, (entity*) IFC4_types[434]);
    IFC4_types[411] = new entity("IfcFireSuppressionTerminalType", false, 411, (entity*) IFC4_types[432]);
    IFC4_types[414] = new entity("IfcFlowController", false, 414, (entity*) IFC4_types[280]);
    IFC4_types[417] = new entity("IfcFlowFitting", false, 417, (entity*) IFC4_types[280]);
    IFC4_types[420] = new entity("IfcFlowInstrumentType", false, 420, (entity*) IFC4_types[277]);
    IFC4_types[422] = new entity("IfcFlowMeter", false, 422, (entity*) IFC4_types[414]);
    IFC4_types[425] = new entity("IfcFlowMovingDevice", false, 425, (entity*) IFC4_types[280]);
    IFC4_types[427] = new entity("IfcFlowSegment", false, 427, (entity*) IFC4_types[280]);
    IFC4_types[429] = new entity("IfcFlowStorageDevice", false, 429, (entity*) IFC4_types[280]);
    IFC4_types[431] = new entity("IfcFlowTerminal", false, 431, (entity*) IFC4_types[280]);
    IFC4_types[433] = new entity("IfcFlowTreatmentDevice", false, 433, (entity*) IFC4_types[280]);
    IFC4_types[438] = new entity("IfcFooting", false, 438, (entity*) IFC4_types[92]);
    IFC4_types[468] = new entity("IfcHeatExchanger", false, 468, (entity*) IFC4_types[357]);
    IFC4_types[473] = new entity("IfcHumidifier", false, 473, (entity*) IFC4_types[357]);
    IFC4_types[488] = new entity("IfcInterceptor", false, 488, (entity*) IFC4_types[433]);
    IFC4_types[500] = new entity("IfcJunctionBox", false, 500, (entity*) IFC4_types[417]);
    IFC4_types[510] = new entity("IfcLamp", false, 510, (entity*) IFC4_types[431]);
    IFC4_types[524] = new entity("IfcLightFixture", false, 524, (entity*) IFC4_types[431]);
    IFC4_types[583] = new entity("IfcMedicalDevice", false, 583, (entity*) IFC4_types[431]);
    IFC4_types[586] = new entity("IfcMember", false, 586, (entity*) IFC4_types[92]);
    IFC4_types[587] = new entity("IfcMemberStandardCase", false, 587, (entity*) IFC4_types[586]);
    IFC4_types[606] = new entity("IfcMotorConnection", false, 606, (entity*) IFC4_types[357]);
    IFC4_types[632] = new entity("IfcOuterBoundaryCurve", false, 632, (entity*) IFC4_types[75]);
    IFC4_types[633] = new entity("IfcOutlet", false, 633, (entity*) IFC4_types[431]);
    IFC4_types[654] = new entity("IfcPile", false, 654, (entity*) IFC4_types[92]);
    IFC4_types[658] = new entity("IfcPipeFitting", false, 658, (entity*) IFC4_types[417]);
    IFC4_types[661] = new entity("IfcPipeSegment", false, 661, (entity*) IFC4_types[427]);
    IFC4_types[671] = new entity("IfcPlate", false, 671, (entity*) IFC4_types[92]);
    IFC4_types[672] = new entity("IfcPlateStandardCase", false, 672, (entity*) IFC4_types[671]);
    IFC4_types[745] = new entity("IfcProtectiveDevice", false, 745, (entity*) IFC4_types[414]);
    IFC4_types[747] = new entity("IfcProtectiveDeviceTrippingUnitType", false, 747, (entity*) IFC4_types[277]);
    IFC4_types[752] = new entity("IfcPump", false, 752, (entity*) IFC4_types[425]);
    IFC4_types[763] = new entity("IfcRailing", false, 763, (entity*) IFC4_types[92]);
    IFC4_types[766] = new entity("IfcRamp", false, 766, (entity*) IFC4_types[92]);
    IFC4_types[767] = new entity("IfcRampFlight", false, 767, (entity*) IFC4_types[92]);
    IFC4_types[773] = new entity("IfcRationalBSplineCurveWithKnots", false, 773, (entity*) IFC4_types[87]);
    IFC4_types[787] = new entity("IfcReinforcingBar", false, 787, (entity*) IFC4_types[792]);
    IFC4_types[790] = new entity("IfcReinforcingBarType", false, 790, (entity*) IFC4_types[793]);
    IFC4_types[862] = new entity("IfcRoof", false, 862, (entity*) IFC4_types[92]);
    IFC4_types[871] = new entity("IfcSanitaryTerminal", false, 871, (entity*) IFC4_types[431]);
    IFC4_types[884] = new entity("IfcSensorType", false, 884, (entity*) IFC4_types[277]);
    IFC4_types[887] = new entity("IfcShadingDevice", false, 887, (entity*) IFC4_types[92]);
    IFC4_types[905] = new entity("IfcSlab", false, 905, (entity*) IFC4_types[92]);
    IFC4_types[906] = new entity("IfcSlabElementedCase", false, 906, (entity*) IFC4_types[905]);
    IFC4_types[907] = new entity("IfcSlabStandardCase", false, 907, (entity*) IFC4_types[905]);
    IFC4_types[911] = new entity("IfcSolarDevice", false, 911, (entity*) IFC4_types[357]);
    IFC4_types[923] = new entity("IfcSpaceHeater", false, 923, (entity*) IFC4_types[431]);
    IFC4_types[941] = new entity("IfcStackTerminal", false, 941, (entity*) IFC4_types[431]);
    IFC4_types[944] = new entity("IfcStair", false, 944, (entity*) IFC4_types[92]);
    IFC4_types[945] = new entity("IfcStairFlight", false, 945, (entity*) IFC4_types[92]);
    IFC4_types[954] = new entity("IfcStructuralAnalysisModel", false, 954, (entity*) IFC4_types[1026]);
    IFC4_types[967] = new entity("IfcStructuralLoadCase", false, 967, (entity*) IFC4_types[969]);
    IFC4_types[980] = new entity("IfcStructuralPlanarAction", false, 980, (entity*) IFC4_types[986]);
    IFC4_types[1023] = new entity("IfcSwitchingDevice", false, 1023, (entity*) IFC4_types[414]);
    IFC4_types[1033] = new entity("IfcTank", false, 1033, (entity*) IFC4_types[429]);
    IFC4_types[1089] = new entity("IfcTransformer", false, 1089, (entity*) IFC4_types[357]);
    IFC4_types[1103] = new entity("IfcTubeBundle", false, 1103, (entity*) IFC4_types[357]);
    IFC4_types[1112] = new entity("IfcUnitaryControlElementType", false, 1112, (entity*) IFC4_types[277]);
    IFC4_types[1114] = new entity("IfcUnitaryEquipment", false, 1114, (entity*) IFC4_types[357]);
    IFC4_types[1122] = new entity("IfcValve", false, 1122, (entity*) IFC4_types[414]);
    IFC4_types[1140] = new entity("IfcWall", false, 1140, (entity*) IFC4_types[92]);
    IFC4_types[1141] = new entity("IfcWallElementedCase", false, 1141, (entity*) IFC4_types[1140]);
    IFC4_types[1142] = new entity("IfcWallStandardCase", false, 1142, (entity*) IFC4_types[1140]);
    IFC4_types[1148] = new entity("IfcWasteTerminal", false, 1148, (entity*) IFC4_types[431]);
    IFC4_types[1151] = new entity("IfcWindow", false, 1151, (entity*) IFC4_types[92]);
    IFC4_types[1156] = new entity("IfcWindowStandardCase", false, 1156, (entity*) IFC4_types[1151]);
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IFC4_types[381]);
        items.push_back(IFC4_types[921]);
        IFC4_types[922] = new select_type("IfcSpaceBoundarySelect", 922, items);
    }
    IFC4_types[10] = new entity("IfcActuatorType", false, 10, (entity*) IFC4_types[277]);
    IFC4_types[17] = new entity("IfcAirTerminal", false, 17, (entity*) IFC4_types[431]);
    IFC4_types[18] = new entity("IfcAirTerminalBox", false, 18, (entity*) IFC4_types[414]);
    IFC4_types[23] = new entity("IfcAirToAirHeatRecovery", false, 23, (entity*) IFC4_types[357]);
    IFC4_types[27] = new entity("IfcAlarmType", false, 27, (entity*) IFC4_types[277]);
    IFC4_types[50] = new entity("IfcAudioVisualAppliance", false, 50, (entity*) IFC4_types[431]);
    IFC4_types[57] = new entity("IfcBeam", false, 57, (entity*) IFC4_types[92]);
    IFC4_types[58] = new entity("IfcBeamStandardCase", false, 58, (entity*) IFC4_types[57]);
    IFC4_types[66] = new entity("IfcBoiler", false, 66, (entity*) IFC4_types[357]);
    IFC4_types[103] = new entity("IfcBurner", false, 103, (entity*) IFC4_types[357]);
    IFC4_types[106] = new entity("IfcCableCarrierFitting", false, 106, (entity*) IFC4_types[417]);
    IFC4_types[109] = new entity("IfcCableCarrierSegment", false, 109, (entity*) IFC4_types[427]);
    IFC4_types[112] = new entity("IfcCableFitting", false, 112, (entity*) IFC4_types[417]);
    IFC4_types[115] = new entity("IfcCableSegment", false, 115, (entity*) IFC4_types[427]);
    IFC4_types[130] = new entity("IfcChiller", false, 130, (entity*) IFC4_types[357]);
    IFC4_types[146] = new entity("IfcCoil", false, 146, (entity*) IFC4_types[357]);
    IFC4_types[158] = new entity("IfcCommunicationsAppliance", false, 158, (entity*) IFC4_types[431]);
    IFC4_types[170] = new entity("IfcCompressor", false, 170, (entity*) IFC4_types[425]);
    IFC4_types[173] = new entity("IfcCondenser", false, 173, (entity*) IFC4_types[357]);
    IFC4_types[203] = new entity("IfcControllerType", false, 203, (entity*) IFC4_types[277]);
    IFC4_types[207] = new entity("IfcCooledBeam", false, 207, (entity*) IFC4_types[357]);
    IFC4_types[210] = new entity("IfcCoolingTower", false, 210, (entity*) IFC4_types[357]);
    IFC4_types[250] = new entity("IfcDamper", false, 250, (entity*) IFC4_types[414]);
    IFC4_types[272] = new entity("IfcDistributionChamberElement", false, 272, (entity*) IFC4_types[280]);
    IFC4_types[275] = new entity("IfcDistributionCircuit", false, 275, (entity*) IFC4_types[284]);
    IFC4_types[276] = new entity("IfcDistributionControlElement", false, 276, (entity*) IFC4_types[278]);
    IFC4_types[307] = new entity("IfcDuctFitting", false, 307, (entity*) IFC4_types[417]);
    IFC4_types[310] = new entity("IfcDuctSegment", false, 310, (entity*) IFC4_types[427]);
    IFC4_types[313] = new entity("IfcDuctSilencer", false, 313, (entity*) IFC4_types[433]);
    IFC4_types[321] = new entity("IfcElectricAppliance", false, 321, (entity*) IFC4_types[431]);
    IFC4_types[328] = new entity("IfcElectricDistributionBoard", false, 328, (entity*) IFC4_types[414]);
    IFC4_types[331] = new entity("IfcElectricFlowStorageDevice", false, 331, (entity*) IFC4_types[429]);
    IFC4_types[334] = new entity("IfcElectricGenerator", false, 334, (entity*) IFC4_types[357]);
    IFC4_types[337] = new entity("IfcElectricMotor", false, 337, (entity*) IFC4_types[357]);
    IFC4_types[341] = new entity("IfcElectricTimeControl", false, 341, (entity*) IFC4_types[414]);
    IFC4_types[394] = new entity("IfcFan", false, 394, (entity*) IFC4_types[425]);
    IFC4_types[407] = new entity("IfcFilter", false, 407, (entity*) IFC4_types[433]);
    IFC4_types[410] = new entity("IfcFireSuppressionTerminal", false, 410, (entity*) IFC4_types[431]);
    IFC4_types[419] = new entity("IfcFlowInstrument", false, 419, (entity*) IFC4_types[276]);
    IFC4_types[746] = new entity("IfcProtectiveDeviceTrippingUnit", false, 746, (entity*) IFC4_types[276]);
    IFC4_types[883] = new entity("IfcSensor", false, 883, (entity*) IFC4_types[276]);
    IFC4_types[1111] = new entity("IfcUnitaryControlElement", false, 1111, (entity*) IFC4_types[276]);
    IFC4_types[9] = new entity("IfcActuator", false, 9, (entity*) IFC4_types[276]);
    IFC4_types[26] = new entity("IfcAlarm", false, 26, (entity*) IFC4_types[276]);
    IFC4_types[202] = new entity("IfcController", false, 202, (entity*) IFC4_types[276]);
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[3]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[2])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TheActor", new named_type(IFC4_types[8]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[6])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Role", new named_type(IFC4_types[861]), false));
        attributes.push_back(new attribute("UserDefinedRole", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[7])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[11]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[9])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[11]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[10])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Purpose", new named_type(IFC4_types[13]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("UserDefinedPurpose", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[12])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[14])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[145])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[15])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[16])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[22]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[17])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[20]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[18])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[20]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[19])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[22]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[21])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[25]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[23])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[25]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[24])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[28]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[26])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[28]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[27])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[33])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[237])), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[34])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ApplicationDeveloper", new named_type(IFC4_types[629]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("ApplicationFullName", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("ApplicationIdentifier", new named_type(IFC4_types[476]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[35])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("AppliedValue", new named_type(IFC4_types[37]), true));
        attributes.push_back(new attribute("UnitBasis", new named_type(IFC4_types[579]), true));
        attributes.push_back(new attribute("ApplicableDate", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("FixedUntilDate", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Condition", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("ArithmeticOperator", new named_type(IFC4_types[46]), true));
        attributes.push_back(new attribute("Components", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[36])), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[36])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Identifier", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("TimeOfApproval", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Level", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Qualifier", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("RequestingApproval", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("GivingApproval", new named_type(IFC4_types[8]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[38])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4_types[38]), false));
        attributes.push_back(new attribute("RelatedApprovals", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[38])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[39])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OuterCurve", new named_type(IFC4_types[237]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[40])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Curve", new named_type(IFC4_types[80]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[41])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[237])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[42])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC4_types[220]), true));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC4_types[220]), true));
        attributes.push_back(new attribute("TotalReplacementCost", new named_type(IFC4_types[220]), true));
        attributes.push_back(new attribute("Owner", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("User", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("ResponsiblePerson", new named_type(IFC4_types[647]), true));
        attributes.push_back(new attribute("IncorporationDate", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("DepreciatedValue", new named_type(IFC4_types[220]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[48])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("BottomFlangeWidth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("BottomFlangeThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("BottomFlangeFilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("TopFlangeWidth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("TopFlangeThickness", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("TopFlangeFilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("BottomFlangeEdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("BottomFlangeSlope", new named_type(IFC4_types[670]), true));
        attributes.push_back(new attribute("TopFlangeEdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("TopFlangeSlope", new named_type(IFC4_types[670]), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[49])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[52]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[50])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[52]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[51])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4_types[267]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[53])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4_types[267]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[55])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC4_types[267]), true));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4_types[267]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[56])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Degree", new named_type(IFC4_types[486]), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[119])), false));
        attributes.push_back(new attribute("CurveForm", new named_type(IFC4_types[86]), false));
        attributes.push_back(new attribute("ClosedCurve", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4_types[542]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[85])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("KnotMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[486])), false));
        attributes.push_back(new attribute("Knots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[638])), false));
        attributes.push_back(new attribute("KnotSpec", new named_type(IFC4_types[504]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[87])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("UDegree", new named_type(IFC4_types[486]), false));
        attributes.push_back(new attribute("VDegree", new named_type(IFC4_types[486]), false));
        attributes.push_back(new attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[119]))), false));
        attributes.push_back(new attribute("SurfaceForm", new named_type(IFC4_types[89]), false));
        attributes.push_back(new attribute("UClosed", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("VClosed", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4_types[542]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[88])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("UMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[486])), false));
        attributes.push_back(new attribute("VMultiplicities", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[486])), false));
        attributes.push_back(new attribute("UKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[638])), false));
        attributes.push_back(new attribute("VKnots", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[638])), false));
        attributes.push_back(new attribute("KnotSpec", new named_type(IFC4_types[504]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[90])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[60]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[57])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[58])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[60]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[59])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RasterFormat", new named_type(IFC4_types[476]), false));
        attributes.push_back(new attribute("RasterCode", new named_type(IFC4_types[63]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[64])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("ZLength", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[65])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[68]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[66])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[68]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[67])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[70])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Operator", new named_type(IFC4_types[72]), false));
        attributes.push_back(new attribute("FirstOperand", new named_type(IFC4_types[71]), false));
        attributes.push_back(new attribute("SecondOperand", new named_type(IFC4_types[71]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[73])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[74])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[75])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TranslationalStiffnessByLengthX", new named_type(IFC4_types[599]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByLengthY", new named_type(IFC4_types[599]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByLengthZ", new named_type(IFC4_types[599]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthX", new named_type(IFC4_types[596]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthY", new named_type(IFC4_types[596]), true));
        attributes.push_back(new attribute("RotationalStiffnessByLengthZ", new named_type(IFC4_types[596]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[76])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TranslationalStiffnessByAreaX", new named_type(IFC4_types[598]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByAreaY", new named_type(IFC4_types[598]), true));
        attributes.push_back(new attribute("TranslationalStiffnessByAreaZ", new named_type(IFC4_types[598]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[77])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TranslationalStiffnessX", new named_type(IFC4_types[1093]), true));
        attributes.push_back(new attribute("TranslationalStiffnessY", new named_type(IFC4_types[1093]), true));
        attributes.push_back(new attribute("TranslationalStiffnessZ", new named_type(IFC4_types[1093]), true));
        attributes.push_back(new attribute("RotationalStiffnessX", new named_type(IFC4_types[869]), true));
        attributes.push_back(new attribute("RotationalStiffnessY", new named_type(IFC4_types[869]), true));
        attributes.push_back(new attribute("RotationalStiffnessZ", new named_type(IFC4_types[869]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[78])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingStiffness", new named_type(IFC4_types[1147]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[79])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[80])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[81])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Corner", new named_type(IFC4_types[119]), false));
        attributes.push_back(new attribute("XDim", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("ZDim", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[82])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Enclosure", new named_type(IFC4_types[82]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[84])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ElevationOfRefHeight", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("ElevationOfTerrain", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("BuildingAddress", new named_type(IFC4_types[688]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[91])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[92])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[95]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[93])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[95]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[94])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[98]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[96])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[98]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[97])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[99])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elevation", new named_type(IFC4_types[516]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[100])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[102]), true));
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[101])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[105]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[103])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[105]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[104])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("Girth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("InternalFilletRadius", new named_type(IFC4_types[610]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[231])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[108]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[106])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[108]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[107])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[111]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[109])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[111]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[110])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[114]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[114]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[113])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[117]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[115])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[117]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[116])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IFC4_types[516])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[119])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[120])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_types[516]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[121])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CoordList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[516]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[122])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Axis1", new named_type(IFC4_types[267]), true));
        attributes.push_back(new attribute("Axis2", new named_type(IFC4_types[267]), true));
        attributes.push_back(new attribute("LocalOrigin", new named_type(IFC4_types[119]), false));
        attributes.push_back(new attribute("Scale", new named_type(IFC4_types[775]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[123])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[124])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Scale2", new named_type(IFC4_types[775]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[125])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis3", new named_type(IFC4_types[267]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[126])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Scale2", new named_type(IFC4_types[775]), true));
        attributes.push_back(new attribute("Scale3", new named_type(IFC4_types[775]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[127])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Thickness", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[128])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[132]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[130])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[132]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[135]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[133])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[135]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[136])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[137])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[138])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[139])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[140])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Source", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Edition", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("EditionDate", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4_types[1119]), true));
        attributes.push_back(new attribute("ReferenceTokens", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[476])), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[141])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ReferencedSource", new named_type(IFC4_types[143]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Sort", new named_type(IFC4_types[476]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[142])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[145])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[148]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[146])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[148]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[147])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Red", new named_type(IFC4_types[611]), false));
        attributes.push_back(new attribute("Green", new named_type(IFC4_types[611]), false));
        attributes.push_back(new attribute("Blue", new named_type(IFC4_types[611]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[151])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ColourList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[611]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[152])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[153])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[157]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[154])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[155])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[157]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[156])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[160]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[158])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[160]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[159])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4_types[476]), false));
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[726])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[162])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4_types[164]), true));
        attributes.push_back(new attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[743])), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[163])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[167])), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4_types[542]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[165])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[166])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Transition", new named_type(IFC4_types[1092]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("ParentCurve", new named_type(IFC4_types[237]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[167])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IFC4_types[715])), false));
        attributes.push_back(new attribute("Label", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[168])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[172]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[170])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[172]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[171])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[175]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[173])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[175]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[174])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[54]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[176])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[386])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[177])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CurveOnRelatingElement", new named_type(IFC4_types[243]), false));
        attributes.push_back(new attribute("CurveOnRelatedElement", new named_type(IFC4_types[243]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[178])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[179])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("EccentricityInX", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("EccentricityInY", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("EccentricityInZ", new named_type(IFC4_types[516]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[180])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PointOnRelatingElement", new named_type(IFC4_types[678]), false));
        attributes.push_back(new attribute("PointOnRelatedElement", new named_type(IFC4_types[678]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[181])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceOnRelatingElement", new named_type(IFC4_types[1008]), false));
        attributes.push_back(new attribute("SurfaceOnRelatedElement", new named_type(IFC4_types[1008]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[182])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VolumeOnRelatingElement", new named_type(IFC4_types[916]), false));
        attributes.push_back(new attribute("VolumeOnRelatedElement", new named_type(IFC4_types[916]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[184])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("ConstraintGrade", new named_type(IFC4_types[186]), false));
        attributes.push_back(new attribute("ConstraintSource", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("CreatingActor", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("UserDefinedGrade", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[185])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[189]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[187])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[189]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[188])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[192]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[190])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[192]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[191])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[195]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[193])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[195]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[194])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Usage", new named_type(IFC4_types[856]), true));
        attributes.push_back(new attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[36])), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC4_types[652]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[196])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseCosts", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[36])), true));
        attributes.push_back(new attribute("BaseQuantity", new named_type(IFC4_types[652]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[197])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Phase", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[847])), true));
        attributes.push_back(new attribute("UnitsInContext", new named_type(IFC4_types[1117]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[198])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[200])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[201])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[204]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[202])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[204]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[203])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("ConversionFactor", new named_type(IFC4_types[579]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[205])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConversionOffset", new named_type(IFC4_types[775]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[206])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[209]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[207])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[209]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[208])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[212]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[210])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[212]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[211])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SourceCRS", new named_type(IFC4_types[215]), false));
        attributes.push_back(new attribute("TargetCRS", new named_type(IFC4_types[214]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[213])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("GeodeticDatum", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("VerticalDatum", new named_type(IFC4_types[476]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[214])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[217]), true));
        attributes.push_back(new attribute("CostValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[220])), true));
        attributes.push_back(new attribute("CostQuantities", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[652])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[216])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[219]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("SubmittedOn", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("UpdateDate", new named_type(IFC4_types[255]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[218])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[220])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[224]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[222])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[224]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[223])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[227]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[225])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[227]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[226])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[56]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[228])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TreeRootExpression", new named_type(IFC4_types[229]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[230])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingMonetaryUnit", new named_type(IFC4_types[604]), false));
        attributes.push_back(new attribute("RelatedMonetaryUnit", new named_type(IFC4_types[604]), false));
        attributes.push_back(new attribute("ExchangeRate", new named_type(IFC4_types[687]), false));
        attributes.push_back(new attribute("RateDateTime", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("RateSource", new named_type(IFC4_types[517]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[232])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[235]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[233])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[235]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[234])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[237])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4_types[669]), false));
        attributes.push_back(new attribute("OuterBoundary", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4_types[237])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[238])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4_types[1001]), false));
        attributes.push_back(new attribute("Boundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[75])), false));
        attributes.push_back(new attribute("ImplicitOuter", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[239])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CurveFont", new named_type(IFC4_types[240]), true));
        attributes.push_back(new attribute("CurveWidth", new named_type(IFC4_types[904]), true));
        attributes.push_back(new attribute("CurveColour", new named_type(IFC4_types[149]), true));
        attributes.push_back(new attribute("ModelOrDraughting", new named_type(IFC4_types[69]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[244])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[247])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[245])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("CurveFont", new named_type(IFC4_types[248]), false));
        attributes.push_back(new attribute("CurveFontScaling", new named_type(IFC4_types[687]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[246])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VisibleSegmentLength", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("InvisibleSegmentLength", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[247])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[249])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[252]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[250])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[252]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[251])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ParentProfile", new named_type(IFC4_types[715]), false));
        attributes.push_back(new attribute("Operator", new named_type(IFC4_types[124]), false));
        attributes.push_back(new attribute("Label", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[260])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[262])), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC4_types[263]), false));
        attributes.push_back(new attribute("UserDefinedType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[261])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[609]), false));
        attributes.push_back(new attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[262])->set_attributes(attributes, derived);
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
        ((entity*)IFC4_types[265])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_types[775])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[267])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[271]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[269])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[271]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[270])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[274]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[272])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[274]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[273])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[275])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[276])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[277])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[278])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[279])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[280])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[281])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("FlowDirection", new named_type(IFC4_types[416]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[283]), true));
        attributes.push_back(new attribute("SystemType", new named_type(IFC4_types[285]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[282])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[285]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[284])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4_types[1119]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("IntendedUse", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Scope", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Revision", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("DocumentOwner", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[8])), true));
        attributes.push_back(new attribute("CreationTime", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("LastRevisionTime", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ElectronicFormat", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("ValidFrom", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("ValidUntil", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("Confidentiality", new named_type(IFC4_types[286]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[291]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[287])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC4_types[287]), false));
        attributes.push_back(new attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[287])), false));
        attributes.push_back(new attribute("RelationshipType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[288])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("ReferencedDocument", new named_type(IFC4_types[287]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[289])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[302]), true));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4_types[303]), true));
        attributes.push_back(new attribute("UserDefinedOperationType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[292])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(13);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("ThresholdDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("ThresholdThickness", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("TransomOffset", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("ThresholdOffset", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("CasingThickness", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("CasingDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4_types[890]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetX", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetY", new named_type(IFC4_types[516]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[293])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PanelDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PanelOperation", new named_type(IFC4_types[294]), false));
        attributes.push_back(new attribute("PanelWidth", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4_types[295]), false));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4_types[890]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[296])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[297])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4_types[300]), false));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4_types[299]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("Sizeable", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[298])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[302]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4_types[303]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4_types[69]), true));
        attributes.push_back(new attribute("UserDefinedOperationType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[301])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[305])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[306])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[309]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[307])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[309]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[308])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[312]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[310])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[312]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[311])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[315]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[313])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[315]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[314])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeStart", new named_type(IFC4_types[1128]), false));
        attributes.push_back(new attribute("EdgeEnd", new named_type(IFC4_types[1128]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[318])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeGeometry", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[319])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[631])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[320])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[323]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[321])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[323]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[322])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[330]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[328])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[330]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[329])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[333]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[331])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[333]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[332])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[336]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[334])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[336]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[335])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[339]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[337])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[339]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[338])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[343]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[341])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[343]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[342])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Tag", new named_type(IFC4_types[476]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[345])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC4_types[47]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[349]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[347])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[349]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[348])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[350])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[351])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MethodOfMeasurement", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[652])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[353])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[354])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[56]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[346])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[355])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SemiAxis1", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("SemiAxis2", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[356])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[357])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[358])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[362]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[360])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[362]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[361])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[365]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[363])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[365]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[364])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[368]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[366])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[368]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[367])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[373]), true));
        attributes.push_back(new attribute("EventTriggerType", new named_type(IFC4_types[371]), true));
        attributes.push_back(new attribute("UserDefinedEventTriggerType", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("EventOccurenceTime", new named_type(IFC4_types[370]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[369])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ActualDate", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("EarlyDate", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("LateDate", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ScheduleDate", new named_type(IFC4_types[255]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[370])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[373]), false));
        attributes.push_back(new attribute("EventTriggerType", new named_type(IFC4_types[371]), false));
        attributes.push_back(new attribute("UserDefinedEventTriggerType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[372])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Properties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[726])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[374])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[375])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Location", new named_type(IFC4_types[1119]), true));
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[379])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingReference", new named_type(IFC4_types[379]), false));
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[854])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[380])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[382]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[381])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[383])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[376])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[377])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[378])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC4_types[267]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[384])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EndSweptArea", new named_type(IFC4_types[715]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[385])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[388])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[386])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[177])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[387])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Bound", new named_type(IFC4_types[544]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[388])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[389])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FaceSurface", new named_type(IFC4_types[1001]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[390])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[391])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[145])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[392])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TensionFailureX", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("TensionFailureY", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("TensionFailureZ", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("CompressionFailureX", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("CompressionFailureY", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("CompressionFailureZ", new named_type(IFC4_types[441]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[393])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[396]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[394])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[396]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[395])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[399]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[397])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[399]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[398])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[400])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[401])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[402])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[406])), false));
        attributes.push_back(new attribute("ModelorDraughting", new named_type(IFC4_types[69]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[403])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("HatchLineAppearance", new named_type(IFC4_types[244]), false));
        attributes.push_back(new attribute("StartOfNextHatchLine", new named_type(IFC4_types[467]), false));
        attributes.push_back(new attribute("PointOfReferenceHatchLine", new named_type(IFC4_types[119]), true));
        attributes.push_back(new attribute("PatternStart", new named_type(IFC4_types[119]), true));
        attributes.push_back(new attribute("HatchLineAngle", new named_type(IFC4_types[670]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[404])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TilingPattern", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_types[1126])), false));
        attributes.push_back(new attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[994])), false));
        attributes.push_back(new attribute("TilingScale", new named_type(IFC4_types[687]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[405])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[409]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[407])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[409]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[408])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[412]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[410])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[412]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[411])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4_types[638]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4_types[638]), true));
        attributes.push_back(new attribute("FixedReference", new named_type(IFC4_types[267]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[413])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[414])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[415])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[417])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[418])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[421]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[419])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[421]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[420])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[424]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[422])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[424]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[423])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[425])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[426])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[427])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[428])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[429])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[430])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[431])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[432])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[433])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[434])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[440]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[438])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[440]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[439])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[443])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[444])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[447]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[445])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AssemblyPlace", new named_type(IFC4_types[47]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[447]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[446])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[450]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[448])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[450]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[449])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[451])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("CoordinateSpaceDimension", new named_type(IFC4_types[266]), false));
        attributes.push_back(new attribute("Precision", new named_type(IFC4_types[775]), true));
        attributes.push_back(new attribute("WorldCoordinateSystem", new named_type(IFC4_types[54]), false));
        attributes.push_back(new attribute("TrueNorth", new named_type(IFC4_types[267]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[453])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[454])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ParentContext", new named_type(IFC4_types[453]), false));
        attributes.push_back(new attribute("TargetScale", new named_type(IFC4_types[687]), true));
        attributes.push_back(new attribute("TargetView", new named_type(IFC4_types[452]), false));
        attributes.push_back(new attribute("UserDefinedTargetView", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[455])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[457])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[456])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[461])), false));
        attributes.push_back(new attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[461])), false));
        attributes.push_back(new attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[461])), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[464]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[460])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("AxisTag", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("AxisCurve", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("SameSense", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[461])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementLocation", new named_type(IFC4_types[1135]), false));
        attributes.push_back(new attribute("PlacementRefDirection", new named_type(IFC4_types[463]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[462])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[465])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BaseSurface", new named_type(IFC4_types[1001]), false));
        attributes.push_back(new attribute("AgreementFlag", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[466])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[470]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[468])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[470]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[469])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[475]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[473])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[475]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[474])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("OverallDepth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4_types[670]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[498])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("URLReference", new named_type(IFC4_types[1119]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[478])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4_types[1051]), false));
        attributes.push_back(new attribute("Opacity", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("Colours", new named_type(IFC4_types[152]), false));
        attributes.push_back(new attribute("ColourIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[684])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[479])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Points", new named_type(IFC4_types[120]), false));
        attributes.push_back(new attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[882])), true));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4_types[69]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[480])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_types[684])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[481])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("InnerCoordIndices", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_types[684]))), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[482])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4_types[1051]), false));
        attributes.push_back(new attribute("TexCoords", new named_type(IFC4_types[1070]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[483])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TexCoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[684]))), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[484])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[490]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[488])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[490]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[489])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[492])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[494]), true));
        attributes.push_back(new attribute("Jurisdiction", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[647])), true));
        attributes.push_back(new attribute("LastUpdateDate", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("CurrentValue", new named_type(IFC4_types[220]), true));
        attributes.push_back(new attribute("OriginalValue", new named_type(IFC4_types[220]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[493])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[497])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[496])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStamp", new named_type(IFC4_types[255]), false));
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[497])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[502]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[500])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[502]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[501])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("Width", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("Thickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("LegSlope", new named_type(IFC4_types[670]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[545])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[508]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[506])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[508]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[507])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LagValue", new named_type(IFC4_types[1079]), false));
        attributes.push_back(new attribute("DurationType", new named_type(IFC4_types[1037]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[509])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[512]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[510])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[512]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[511])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Version", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Publisher", new named_type(IFC4_types[8]), true));
        attributes.push_back(new attribute("VersionDate", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("Location", new named_type(IFC4_types[1119]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[517])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Language", new named_type(IFC4_types[513]), true));
        attributes.push_back(new attribute("ReferencedLibrary", new named_type(IFC4_types[517]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[518])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MainPlaneAngle", new named_type(IFC4_types[670]), false));
        attributes.push_back(new attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[670])), false));
        attributes.push_back(new attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[547])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[521])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[526]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[524])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[526]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[525])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LightDistributionCurve", new named_type(IFC4_types[520]), false));
        attributes.push_back(new attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[521])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[527])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("LightColour", new named_type(IFC4_types[151]), false));
        attributes.push_back(new attribute("AmbientIntensity", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("Intensity", new named_type(IFC4_types[611]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[528])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[529])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4_types[267]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[530])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[56]), false));
        attributes.push_back(new attribute("ColourAppearance", new named_type(IFC4_types[151]), true));
        attributes.push_back(new attribute("ColourTemperature", new named_type(IFC4_types[1076]), false));
        attributes.push_back(new attribute("LuminousFlux", new named_type(IFC4_types[546]), false));
        attributes.push_back(new attribute("LightEmissionSource", new named_type(IFC4_types[523]), false));
        attributes.push_back(new attribute("LightDistributionDataSource", new named_type(IFC4_types[522]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[531])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[119]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("ConstantAttenuation", new named_type(IFC4_types[775]), false));
        attributes.push_back(new attribute("DistanceAttenuation", new named_type(IFC4_types[775]), false));
        attributes.push_back(new attribute("QuadricAttenuation", new named_type(IFC4_types[775]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[532])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4_types[267]), false));
        attributes.push_back(new attribute("ConcentrationExponent", new named_type(IFC4_types[775]), true));
        attributes.push_back(new attribute("SpreadAngle", new named_type(IFC4_types[686]), false));
        attributes.push_back(new attribute("BeamWidthAngle", new named_type(IFC4_types[686]), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[533])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Pnt", new named_type(IFC4_types[119]), false));
        attributes.push_back(new attribute("Dir", new named_type(IFC4_types[1126]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[534])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PlacementRelTo", new named_type(IFC4_types[618]), true));
        attributes.push_back(new attribute("RelativePlacement", new named_type(IFC4_types[54]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[541])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[544])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Outer", new named_type(IFC4_types[145]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[551])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Eastings", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("Northings", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("OrthogonalHeight", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("XAxisAbscissa", new named_type(IFC4_types[775]), true));
        attributes.push_back(new attribute("XAxisOrdinate", new named_type(IFC4_types[775]), true));
        attributes.push_back(new attribute("Scale", new named_type(IFC4_types[775]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[552])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingSource", new named_type(IFC4_types[849]), false));
        attributes.push_back(new attribute("MappingTarget", new named_type(IFC4_types[123]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[553])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[558])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[144])), false));
        attributes.push_back(new attribute("ClassifiedMaterial", new named_type(IFC4_types[558]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[559])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Material", new named_type(IFC4_types[558]), false));
        attributes.push_back(new attribute("Fraction", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[560])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("MaterialConstituents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[560])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[561])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[562])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RepresentedMaterial", new named_type(IFC4_types[558]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[563])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Material", new named_type(IFC4_types[558]), true));
        attributes.push_back(new attribute("LayerThickness", new named_type(IFC4_types[610]), false));
        attributes.push_back(new attribute("IsVentilated", new named_type(IFC4_types[542]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Priority", new named_type(IFC4_types[486]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[564])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[564])), false));
        attributes.push_back(new attribute("LayerSetName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[565])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ForLayerSet", new named_type(IFC4_types[565]), false));
        attributes.push_back(new attribute("LayerSetDirection", new named_type(IFC4_types[515]), false));
        attributes.push_back(new attribute("DirectionSense", new named_type(IFC4_types[268]), false));
        attributes.push_back(new attribute("OffsetFromReferenceLine", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("ReferenceExtent", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[566])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("OffsetDirection", new named_type(IFC4_types[515]), false));
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4_types[516])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[567])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[558])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[568])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Material", new named_type(IFC4_types[558]), true));
        attributes.push_back(new attribute("Profile", new named_type(IFC4_types[715]), false));
        attributes.push_back(new attribute("Priority", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("Category", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[569])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("MaterialProfiles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[569])), false));
        attributes.push_back(new attribute("CompositeProfile", new named_type(IFC4_types[168]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[570])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ForProfileSet", new named_type(IFC4_types[570]), false));
        attributes.push_back(new attribute("CardinalPoint", new named_type(IFC4_types[118]), true));
        attributes.push_back(new attribute("ReferenceExtent", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[571])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ForProfileEndSet", new named_type(IFC4_types[570]), false));
        attributes.push_back(new attribute("CardinalEndPoint", new named_type(IFC4_types[118]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[572])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("OffsetValues", new aggregation_type(aggregation_type::array_type, 1, 2, new named_type(IFC4_types[516])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[573])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Material", new named_type(IFC4_types[562]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[574])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC4_types[558]), false));
        attributes.push_back(new attribute("RelatedMaterials", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[558])), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[575])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[577])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ValueComponent", new named_type(IFC4_types[1121]), false));
        attributes.push_back(new attribute("UnitComponent", new named_type(IFC4_types[1110]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[579])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[582]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[580])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[582]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("NominalLength", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[581])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[585]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[583])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[585]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[584])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[589]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[586])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[587])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[589]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[588])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Benchmark", new named_type(IFC4_types[61]), false));
        attributes.push_back(new attribute("ValueSource", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("DataValue", new named_type(IFC4_types[591]), true));
        attributes.push_back(new attribute("ReferencePath", new named_type(IFC4_types[782]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[590])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(false);
        ((entity*)IFC4_types[592])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Currency", new named_type(IFC4_types[505]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[604])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[608]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[606])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[608]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[607])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Dimensions", new named_type(IFC4_types[265]), false));
        attributes.push_back(new attribute("UnitType", new named_type(IFC4_types[1118]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[609])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ObjectType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[614])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[615])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[618])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BenchmarkValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[185])), true));
        attributes.push_back(new attribute("LogicalAggregator", new named_type(IFC4_types[543]), true));
        attributes.push_back(new attribute("ObjectiveQualifier", new named_type(IFC4_types[617]), false));
        attributes.push_back(new attribute("UserDefinedQualifier", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[616])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[622]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[621])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("Distance", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4_types[542]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[623])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("Distance", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("SelfIntersect", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("RefDirection", new named_type(IFC4_types[267]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[624])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[628])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[626]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[625])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[627])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[12])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[629])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOrganization", new named_type(IFC4_types[629]), false));
        attributes.push_back(new attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[629])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[630])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EdgeElement", new named_type(IFC4_types[318]), false));
        attributes.push_back(new attribute("Orientation", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[631])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[632])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[635]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[633])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[635]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[634])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("OwningUser", new named_type(IFC4_types[648]), false));
        attributes.push_back(new attribute("OwningApplication", new named_type(IFC4_types[35]), false));
        attributes.push_back(new attribute("State", new named_type(IFC4_types[950]), true));
        attributes.push_back(new attribute("ChangeAction", new named_type(IFC4_types[129]), true));
        attributes.push_back(new attribute("LastModifiedDate", new named_type(IFC4_types[1084]), true));
        attributes.push_back(new attribute("LastModifyingUser", new named_type(IFC4_types[648]), true));
        attributes.push_back(new attribute("LastModifyingApplication", new named_type(IFC4_types[35]), true));
        attributes.push_back(new attribute("CreationDate", new named_type(IFC4_types[1084]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[636])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[55]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[637])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[631])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[639])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4_types[1001]), false));
        attributes.push_back(new attribute("ReferenceCurve", new named_type(IFC4_types[237]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[640])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LifeCyclePhase", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[642]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[641])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4_types[643]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4_types[1154]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4_types[890]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[644])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[646]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[645])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("FamilyName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("GivenName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[7])), true));
        attributes.push_back(new attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[12])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[647])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ThePerson", new named_type(IFC4_types[647]), false));
        attributes.push_back(new attribute("TheOrganization", new named_type(IFC4_types[629]), false));
        attributes.push_back(new attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[7])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[648])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[652])), false));
        attributes.push_back(new attribute("Discrimination", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Quality", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Usage", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[650])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[652])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[609]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[653])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[657]), true));
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4_types[655]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[654])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[657]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[656])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[660]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[658])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[660]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[659])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[663]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[661])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[663]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[662])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Width", new named_type(IFC4_types[486]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC4_types[486]), false));
        attributes.push_back(new attribute("ColourComponents", new named_type(IFC4_types[486]), false));
        attributes.push_back(new attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[63])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[664])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Location", new named_type(IFC4_types[119]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[665])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Placement", new named_type(IFC4_types[54]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[666])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SizeInX", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("SizeInY", new named_type(IFC4_types[516]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[667])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[669])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[674]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[671])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[672])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[674]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[673])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[675])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("PointParameter", new named_type(IFC4_types[638]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[676])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4_types[1001]), false));
        attributes.push_back(new attribute("PointParameterU", new named_type(IFC4_types[638]), false));
        attributes.push_back(new attribute("PointParameterV", new named_type(IFC4_types[638]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[677])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_types[119])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[682])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[56]), false));
        attributes.push_back(new attribute("PolygonalBoundary", new named_type(IFC4_types[80]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[679])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Closed", new named_type(IFC4_types[69]), true));
        attributes.push_back(new attribute("Faces", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[481])), false));
        attributes.push_back(new attribute("PnIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[684])), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[680])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[119])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[681])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[683])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("InternalLocation", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("PostalBox", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Town", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Region", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("PostalCode", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Country", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[688])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[690])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[691])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[692])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[693])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[694])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[695])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[698])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[514])), false));
        attributes.push_back(new attribute("Identifier", new named_type(IFC4_types[476]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[699])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("LayerOn", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("LayerFrozen", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("LayerBlocked", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IFC4_types[701])), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[700])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[701])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[703])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[702])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[707]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[705])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[707]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[706])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[708])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ObjectPlacement", new named_type(IFC4_types[618]), true));
        attributes.push_back(new attribute("Representation", new named_type(IFC4_types[712]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[710])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[711])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[846])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[712])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProfileType", new named_type(IFC4_types[717]), false));
        attributes.push_back(new attribute("ProfileName", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[715])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ProfileDefinition", new named_type(IFC4_types[715]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[716])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[718])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[723])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[725]), true));
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[724])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("MapProjection", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("MapZone", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("MapUnit", new named_type(IFC4_types[609]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[719])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[722]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[721])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[476]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[726])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[727])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("UpperBoundValue", new named_type(IFC4_types[1121]), true));
        attributes.push_back(new attribute("LowerBoundValue", new named_type(IFC4_types[1121]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[1110]), true));
        attributes.push_back(new attribute("SetPointValue", new named_type(IFC4_types[1121]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[728])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[729])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DependingProperty", new named_type(IFC4_types[726]), false));
        attributes.push_back(new attribute("DependantProperty", new named_type(IFC4_types[726]), false));
        attributes.push_back(new attribute("Expression", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[730])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), true));
        attributes.push_back(new attribute("EnumerationReference", new named_type(IFC4_types[732]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[731])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), false));
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[1110]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[732])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[1110]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[733])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("UsageName", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("PropertyReference", new named_type(IFC4_types[619]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[734])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[726])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[735])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[736])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4_types[740]), true));
        attributes.push_back(new attribute("ApplicableEntity", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("HasPropertyTemplates", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[743])), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[739])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("NominalValue", new named_type(IFC4_types[1121]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[1110]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[741])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), true));
        attributes.push_back(new attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("DefiningUnit", new named_type(IFC4_types[1110]), true));
        attributes.push_back(new attribute("DefinedUnit", new named_type(IFC4_types[1110]), true));
        attributes.push_back(new attribute("CurveInterpolation", new named_type(IFC4_types[241]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[742])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[743])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[744])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[750]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[745])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[748]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[746])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[748]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[747])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[750]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[749])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProxyType", new named_type(IFC4_types[620]), false));
        attributes.push_back(new attribute("Tag", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[751])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[754]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[752])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[754]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[753])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AreaValue", new named_type(IFC4_types[45]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[755])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("CountValue", new named_type(IFC4_types[221]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[756])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("LengthValue", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[757])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[758])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeValue", new named_type(IFC4_types[1078]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[759])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("VolumeValue", new named_type(IFC4_types[1138]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[760])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("WeightValue", new named_type(IFC4_types[556]), false));
        attributes.push_back(new attribute("Formula", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[761])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[765]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[763])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[765]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[764])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[771]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[766])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[769]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[767])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[769]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[768])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[771]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[770])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[775])), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[773])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[775]))), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[774])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WallThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("InnerFilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("OuterFilletRadius", new named_type(IFC4_types[610]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[776])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("XDim", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[777])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("XLength", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("YLength", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("Height", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[778])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("BasisSurface", new named_type(IFC4_types[1001]), false));
        attributes.push_back(new attribute("U1", new named_type(IFC4_types[638]), false));
        attributes.push_back(new attribute("V1", new named_type(IFC4_types[638]), false));
        attributes.push_back(new attribute("U2", new named_type(IFC4_types[638]), false));
        attributes.push_back(new attribute("V2", new named_type(IFC4_types[638]), false));
        attributes.push_back(new attribute("Usense", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("Vsense", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[779])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("RecurrenceType", new named_type(IFC4_types[781]), false));
        attributes.push_back(new attribute("DayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[256])), true));
        attributes.push_back(new attribute("WeekdayComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[257])), true));
        attributes.push_back(new attribute("MonthComponent", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[605])), true));
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("Interval", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("Occurrences", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("TimePeriods", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1080])), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[780])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("TypeIdentifier", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("AttributeIdentifier", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("InstanceName", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("ListPositions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[486])), true));
        attributes.push_back(new attribute("InnerReference", new named_type(IFC4_types[782]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[782])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("TimeStep", new named_type(IFC4_types[1078]), false));
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1083])), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[784])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TotalCrossSectionArea", new named_type(IFC4_types[45]), false));
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4_types[789]), true));
        attributes.push_back(new attribute("EffectiveDepth", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("NominalBarDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("BarCount", new named_type(IFC4_types[221]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[785])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("DefinitionType", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[880])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[786])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("BarLength", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[791]), true));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4_types[789]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[787])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[791]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("BarLength", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("BarSurface", new named_type(IFC4_types[789]), true));
        attributes.push_back(new attribute("BendingShapeCode", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[62])), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[790])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SteelGrade", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[792])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[793])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("MeshLength", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[796]), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[794])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[796]), false));
        attributes.push_back(new attribute("MeshLength", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("MeshWidth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("LongitudinalBarNominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("TransverseBarNominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("LongitudinalBarCrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("TransverseBarCrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("LongitudinalBarSpacing", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("TransverseBarSpacing", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("BendingShapeCode", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("BendingParameters", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[62])), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[795])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4_types[615]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[615])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[797])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[615])), false));
        attributes.push_back(new attribute("RelatedObjectsType", new named_type(IFC4_types[620]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[798])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingActor", new named_type(IFC4_types[6]), false));
        attributes.push_back(new attribute("ActingRole", new named_type(IFC4_types[7]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[799])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingControl", new named_type(IFC4_types[201]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[800])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingGroup", new named_type(IFC4_types[465]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[801])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Factor", new named_type(IFC4_types[772]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[802])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC4_types[709]), false));
        attributes.push_back(new attribute("QuantityInProcess", new named_type(IFC4_types[579]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[803])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingProduct", new named_type(IFC4_types[714]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[804])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingResource", new named_type(IFC4_types[855]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[805])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[258])), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[806])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4_types[38]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[807])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingClassification", new named_type(IFC4_types[144]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[808])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Intent", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC4_types[185]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[809])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingDocument", new named_type(IFC4_types[290]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[810])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingLibrary", new named_type(IFC4_types[519]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[811])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RelatingMaterial", new named_type(IFC4_types[576]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[812])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[814])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC4_types[179]), true));
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4_types[345]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[815])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4_types[486])), false));
        attributes.push_back(new attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new named_type(IFC4_types[486])), false));
        attributes.push_back(new attribute("RelatedConnectionType", new named_type(IFC4_types[183]), false));
        attributes.push_back(new attribute("RelatingConnectionType", new named_type(IFC4_types[183]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[816])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC4_types[683]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4_types[278]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[818])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RelatingPort", new named_type(IFC4_types[683]), false));
        attributes.push_back(new attribute("RelatedPort", new named_type(IFC4_types[683]), false));
        attributes.push_back(new attribute("RealizingElement", new named_type(IFC4_types[345]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[817])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4_types[953]), false));
        attributes.push_back(new attribute("RelatedStructuralActivity", new named_type(IFC4_types[952]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[819])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("RelatingStructuralMember", new named_type(IFC4_types[979]), false));
        attributes.push_back(new attribute("RelatedStructuralConnection", new named_type(IFC4_types[955]), false));
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC4_types[74]), true));
        attributes.push_back(new attribute("AdditionalConditions", new named_type(IFC4_types[956]), true));
        attributes.push_back(new attribute("SupportedLength", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC4_types[56]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[820])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConnectionConstraint", new named_type(IFC4_types[179]), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[821])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[345])), false));
        attributes.push_back(new attribute("ConnectionType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[822])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[710])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC4_types[928]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[823])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[222])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[824])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC4_types[921]), false));
        attributes.push_back(new attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[222])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[825])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingContext", new named_type(IFC4_types[198]), false));
        attributes.push_back(new attribute("RelatedDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[258])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[826])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[827])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[828])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[614])), false));
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4_types[614]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[829])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[615])), false));
        attributes.push_back(new attribute("RelatingPropertyDefinition", new named_type(IFC4_types[737]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[830])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[736])), false));
        attributes.push_back(new attribute("RelatingTemplate", new named_type(IFC4_types[739]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[831])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[614])), false));
        attributes.push_back(new attribute("RelatingType", new named_type(IFC4_types[1106]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[832])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingOpeningElement", new named_type(IFC4_types[625]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC4_types[345]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[833])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[276])), false));
        attributes.push_back(new attribute("RelatingFlowElement", new named_type(IFC4_types[280]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[834])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("RelatedElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("InterferenceGeometry", new named_type(IFC4_types[179]), true));
        attributes.push_back(new attribute("InterferenceType", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("ImpliedOrder", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[835])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingObject", new named_type(IFC4_types[615]), false));
        attributes.push_back(new attribute("RelatedObjects", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[615])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[836])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("RelatedFeatureElement", new named_type(IFC4_types[401]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[837])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[710])), false));
        attributes.push_back(new attribute("RelatingStructure", new named_type(IFC4_types[928]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[838])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingProcess", new named_type(IFC4_types[708]), false));
        attributes.push_back(new attribute("RelatedProcess", new named_type(IFC4_types[708]), false));
        attributes.push_back(new attribute("TimeLag", new named_type(IFC4_types[509]), true));
        attributes.push_back(new attribute("SequenceType", new named_type(IFC4_types[886]), true));
        attributes.push_back(new attribute("UserDefinedSequenceType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[839])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingSystem", new named_type(IFC4_types[1026]), false));
        attributes.push_back(new attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[928])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[840])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RelatingSpace", new named_type(IFC4_types[922]), false));
        attributes.push_back(new attribute("RelatedBuildingElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("ConnectionGeometry", new named_type(IFC4_types[179]), true));
        attributes.push_back(new attribute("PhysicalOrVirtualBoundary", new named_type(IFC4_types[651]), false));
        attributes.push_back(new attribute("InternalOrExternalBoundary", new named_type(IFC4_types[491]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[841])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentBoundary", new named_type(IFC4_types[842]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[842])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CorrespondingBoundary", new named_type(IFC4_types[843]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[843])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingBuildingElement", new named_type(IFC4_types[345]), false));
        attributes.push_back(new attribute("RelatedOpeningElement", new named_type(IFC4_types[402]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[844])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[813])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParamLength", new named_type(IFC4_types[638]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[845])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ContextOfItems", new named_type(IFC4_types[847]), false));
        attributes.push_back(new attribute("RepresentationIdentifier", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("RepresentationType", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[848])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[846])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ContextIdentifier", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("ContextType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[847])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[848])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MappingOrigin", new named_type(IFC4_types[54]), false));
        attributes.push_back(new attribute("MappedRepresentation", new named_type(IFC4_types[846]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[849])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[850])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[854])), false));
        attributes.push_back(new attribute("RelatingApproval", new named_type(IFC4_types[38]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[851])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RelatingConstraint", new named_type(IFC4_types[185]), false));
        attributes.push_back(new attribute("RelatedResourceObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[854])), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[852])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[853])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new attribute("ScheduleWork", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("ScheduleUsage", new named_type(IFC4_types[687]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ScheduleContour", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("LevelingDelay", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("IsOverAllocated", new named_type(IFC4_types[69]), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ActualWork", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("ActualUsage", new named_type(IFC4_types[687]), true));
        attributes.push_back(new attribute("ActualStart", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("RemainingWork", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("RemainingUsage", new named_type(IFC4_types[687]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC4_types[687]), true));
        std::vector<bool> derived; derived.reserve(18);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[856])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Axis", new named_type(IFC4_types[53]), false));
        attributes.push_back(new attribute("Angle", new named_type(IFC4_types[670]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[857])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("EndSweptArea", new named_type(IFC4_types[715]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[858])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("BottomRadius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[859])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Height", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[860])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[864]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[862])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[864]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[863])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("GlobalId", new named_type(IFC4_types[458]), false));
        attributes.push_back(new attribute("OwnerHistory", new named_type(IFC4_types[636]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[865])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("RoundingRadius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[870])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Prefix", new named_type(IFC4_types[900]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[903]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[902])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[873]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[871])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[873]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[872])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC4_types[253]), true));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[874])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[875])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SectionType", new named_type(IFC4_types[881]), false));
        attributes.push_back(new attribute("StartProfile", new named_type(IFC4_types[715]), false));
        attributes.push_back(new attribute("EndProfile", new named_type(IFC4_types[715]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[879])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LongitudinalStartPosition", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("LongitudinalEndPosition", new named_type(IFC4_types[516]), false));
        attributes.push_back(new attribute("TransversePosition", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("ReinforcementRole", new named_type(IFC4_types[788]), false));
        attributes.push_back(new attribute("SectionDefinition", new named_type(IFC4_types[879]), false));
        attributes.push_back(new attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[785])), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[880])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SpineCurve", new named_type(IFC4_types[165]), false));
        attributes.push_back(new attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[715])), false));
        attributes.push_back(new attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IFC4_types[56])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[877])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[885]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[883])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[885]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[884])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[889]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[887])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[889]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[888])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[891])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("ProductDefinitional", new named_type(IFC4_types[542]), false));
        attributes.push_back(new attribute("PartOfProductDefinitionShape", new named_type(IFC4_types[713]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[890])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[891])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[892])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[894])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[895])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[896])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("TemplateType", new named_type(IFC4_types[898]), true));
        attributes.push_back(new attribute("PrimaryMeasureType", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("SecondaryMeasureType", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Enumerators", new named_type(IFC4_types[732]), true));
        attributes.push_back(new attribute("PrimaryUnit", new named_type(IFC4_types[1110]), true));
        attributes.push_back(new attribute("SecondaryUnit", new named_type(IFC4_types[1110]), true));
        attributes.push_back(new attribute("Expression", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("AccessState", new named_type(IFC4_types[950]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[897])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RefLatitude", new named_type(IFC4_types[169]), true));
        attributes.push_back(new attribute("RefLongitude", new named_type(IFC4_types[169]), true));
        attributes.push_back(new attribute("RefElevation", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("LandTitleNumber", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("SiteAddress", new named_type(IFC4_types[688]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[901])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[909]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[905])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[906])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[907])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[909]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[908])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SlippageX", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("SlippageY", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("SlippageZ", new named_type(IFC4_types[516]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[910])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[913]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[911])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[913]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[912])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[915])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[927]), true));
        attributes.push_back(new attribute("ElevationWithFlooring", new named_type(IFC4_types[516]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[921])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[925]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[923])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[925]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[924])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[927]), false));
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[926])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[928])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ElementType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[929])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("CompositionType", new named_type(IFC4_types[352]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[930])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[931])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[934]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[932])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[934]), false));
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[933])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[939])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[940])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[943]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[941])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[943]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[942])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[949]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[944])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("NumberOfRisers", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("NumberOfTreads", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("RiserHeight", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("TreadLength", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[947]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[945])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[947]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[946])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[949]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[948])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("DestabilizingLoad", new named_type(IFC4_types[69]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[951])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("AppliedLoad", new named_type(IFC4_types[966]), false));
        attributes.push_back(new attribute("GlobalOrLocal", new named_type(IFC4_types[459]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[952])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[30]), false));
        attributes.push_back(new attribute("OrientationOf2DPlane", new named_type(IFC4_types[56]), true));
        attributes.push_back(new attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[969])), true));
        attributes.push_back(new attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[985])), true));
        attributes.push_back(new attribute("SharedPlacement", new named_type(IFC4_types[618]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[954])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AppliedCondition", new named_type(IFC4_types[74]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[955])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[956])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC4_types[720]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[958]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[957])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Axis", new named_type(IFC4_types[267]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[959])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[961]), false));
        attributes.push_back(new attribute("Axis", new named_type(IFC4_types[267]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[960])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[962])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[958]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[963])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[964])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[965])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[966])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("SelfWeightCoefficients", new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[772])), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[967])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[971])), false));
        attributes.push_back(new attribute("Locations", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4_types[516]))), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[968])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[540]), false));
        attributes.push_back(new attribute("ActionType", new named_type(IFC4_types[5]), false));
        attributes.push_back(new attribute("ActionSource", new named_type(IFC4_types[4]), false));
        attributes.push_back(new attribute("Coefficient", new named_type(IFC4_types[772]), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[969])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("LinearForceX", new named_type(IFC4_types[535]), true));
        attributes.push_back(new attribute("LinearForceY", new named_type(IFC4_types[535]), true));
        attributes.push_back(new attribute("LinearForceZ", new named_type(IFC4_types[535]), true));
        attributes.push_back(new attribute("LinearMomentX", new named_type(IFC4_types[536]), true));
        attributes.push_back(new attribute("LinearMomentY", new named_type(IFC4_types[536]), true));
        attributes.push_back(new attribute("LinearMomentZ", new named_type(IFC4_types[536]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[970])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[971])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("PlanarForceX", new named_type(IFC4_types[668]), true));
        attributes.push_back(new attribute("PlanarForceY", new named_type(IFC4_types[668]), true));
        attributes.push_back(new attribute("PlanarForceZ", new named_type(IFC4_types[668]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[972])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("DisplacementX", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("DisplacementY", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("DisplacementZ", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("RotationalDisplacementRX", new named_type(IFC4_types[670]), true));
        attributes.push_back(new attribute("RotationalDisplacementRY", new named_type(IFC4_types[670]), true));
        attributes.push_back(new attribute("RotationalDisplacementRZ", new named_type(IFC4_types[670]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[973])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Distortion", new named_type(IFC4_types[236]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[974])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("ForceX", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("ForceY", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("ForceZ", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("MomentX", new named_type(IFC4_types[1088]), true));
        attributes.push_back(new attribute("MomentY", new named_type(IFC4_types[1088]), true));
        attributes.push_back(new attribute("MomentZ", new named_type(IFC4_types[1088]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[975])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("WarpingMoment", new named_type(IFC4_types[1146]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[976])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[977])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("DeltaTConstant", new named_type(IFC4_types[1076]), true));
        attributes.push_back(new attribute("DeltaTY", new named_type(IFC4_types[1076]), true));
        attributes.push_back(new attribute("DeltaTZ", new named_type(IFC4_types[1076]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[978])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[979])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[980])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[981])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ConditionCoordinateSystem", new named_type(IFC4_types[56]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[982])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[983])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[984])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("TheoryType", new named_type(IFC4_types[31]), false));
        attributes.push_back(new attribute("ResultForLoadGroup", new named_type(IFC4_types[969]), true));
        attributes.push_back(new attribute("IsLinear", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[985])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ProjectedOrTrue", new named_type(IFC4_types[720]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[987]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[986])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[988])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[990]), false));
        attributes.push_back(new attribute("Thickness", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[989])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[991])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[987]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[992])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[996])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Item", new named_type(IFC4_types[848]), true));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[993])), false));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[994])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[995])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[999]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[997])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[999]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[998])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ParentEdge", new named_type(IFC4_types[318]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1000])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[1001])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Curve3D", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("AssociatedGeometry", new aggregation_type(aggregation_type::list_type, 1, 2, new named_type(IFC4_types[640])), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC4_types[696]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1002])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4_types[638]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4_types[638]), true));
        attributes.push_back(new attribute("ReferenceSurface", new named_type(IFC4_types[1001]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1003])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1005]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1004])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ExtrudedDirection", new named_type(IFC4_types[267]), false));
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[516]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1006])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("AxisPosition", new named_type(IFC4_types[53]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1007])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("SurfaceReinforcement1", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_types[516])), true));
        attributes.push_back(new attribute("SurfaceReinforcement2", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_types[516])), true));
        attributes.push_back(new attribute("ShearReinforcement", new named_type(IFC4_types[772]), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1009])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Side", new named_type(IFC4_types[1010]), false));
        attributes.push_back(new attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IFC4_types[1012])), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1011])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC4_types[151]), false));
        attributes.push_back(new attribute("DiffuseReflectionColour", new named_type(IFC4_types[151]), false));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC4_types[151]), false));
        attributes.push_back(new attribute("ReflectanceColour", new named_type(IFC4_types[151]), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1013])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RefractionIndex", new named_type(IFC4_types[775]), true));
        attributes.push_back(new attribute("DispersionFactor", new named_type(IFC4_types[775]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1014])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("DiffuseColour", new named_type(IFC4_types[150]), true));
        attributes.push_back(new attribute("TransmissionColour", new named_type(IFC4_types[150]), true));
        attributes.push_back(new attribute("DiffuseTransmissionColour", new named_type(IFC4_types[150]), true));
        attributes.push_back(new attribute("ReflectionColour", new named_type(IFC4_types[150]), true));
        attributes.push_back(new attribute("SpecularColour", new named_type(IFC4_types[150]), true));
        attributes.push_back(new attribute("SpecularHighlight", new named_type(IFC4_types[937]), true));
        attributes.push_back(new attribute("ReflectanceMethod", new named_type(IFC4_types[783]), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1015])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SurfaceColour", new named_type(IFC4_types[151]), false));
        attributes.push_back(new attribute("Transparency", new named_type(IFC4_types[611]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1016])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1018])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1017])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("RepeatS", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("RepeatT", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("Mode", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("TextureTransform", new named_type(IFC4_types[124]), true));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[476])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1018])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptArea", new named_type(IFC4_types[715]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[56]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1019])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Directrix", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("Radius", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("InnerRadius", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("StartParam", new named_type(IFC4_types[638]), true));
        attributes.push_back(new attribute("EndParam", new named_type(IFC4_types[638]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1020])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1021])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("SweptCurve", new named_type(IFC4_types[715]), false));
        attributes.push_back(new attribute("Position", new named_type(IFC4_types[56]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1022])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1025]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1023])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1025]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1024])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1026])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1029]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1027])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1029]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1028])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("FlangeEdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("WebEdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("WebSlope", new named_type(IFC4_types[670]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4_types[670]), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1102])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1032])), true));
        attributes.push_back(new attribute("Columns", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1031])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1030])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("Identifier", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[1110]), true));
        attributes.push_back(new attribute("ReferencePath", new named_type(IFC4_types[782]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1031])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), true));
        attributes.push_back(new attribute("IsHeading", new named_type(IFC4_types[69]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1032])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1035]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1033])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1035]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1034])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Status", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("IsMilestone", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("Priority", new named_type(IFC4_types[486]), true));
        attributes.push_back(new attribute("TaskTime", new named_type(IFC4_types[1038]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1041]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1036])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new attribute("DurationType", new named_type(IFC4_types[1037]), true));
        attributes.push_back(new attribute("ScheduleDuration", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("ScheduleStart", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ScheduleFinish", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("EarlyStart", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("EarlyFinish", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("LateStart", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("LateFinish", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("FreeFloat", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("IsCritical", new named_type(IFC4_types[69]), true));
        attributes.push_back(new attribute("StatusTime", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ActualDuration", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("ActualStart", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("ActualFinish", new named_type(IFC4_types[255]), true));
        attributes.push_back(new attribute("RemainingTime", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("Completion", new named_type(IFC4_types[687]), true));
        std::vector<bool> derived; derived.reserve(20);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1038])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Recurrence", new named_type(IFC4_types[780]), false));
        std::vector<bool> derived; derived.reserve(21);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1039])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1041]), false));
        attributes.push_back(new attribute("WorkMethod", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1040])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("PagerNumber", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[505])), true));
        attributes.push_back(new attribute("WWWHomePageURL", new named_type(IFC4_types[1119]), true));
        attributes.push_back(new attribute("MessagingIDs", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1119])), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1042])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1050]), true));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("TensionForce", new named_type(IFC4_types[441]), true));
        attributes.push_back(new attribute("PreStress", new named_type(IFC4_types[704]), true));
        attributes.push_back(new attribute("FrictionCoefficient", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("AnchorageSlip", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("MinCurvatureRadius", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1045])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1048]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1046])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1048]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1047])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1050]), false));
        attributes.push_back(new attribute("NominalDiameter", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("CrossSectionArea", new named_type(IFC4_types[45]), true));
        attributes.push_back(new attribute("SheathDiameter", new named_type(IFC4_types[685]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1049])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new named_type(IFC4_types[122]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1051])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[1052])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Literal", new named_type(IFC4_types[697]), false));
        attributes.push_back(new attribute("Placement", new named_type(IFC4_types[54]), false));
        attributes.push_back(new attribute("Path", new named_type(IFC4_types[1060]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1058])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Extent", new named_type(IFC4_types[667]), false));
        attributes.push_back(new attribute("BoxAlignment", new named_type(IFC4_types[83]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1059])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("TextCharacterAppearance", new named_type(IFC4_types[1063]), true));
        attributes.push_back(new attribute("TextStyle", new named_type(IFC4_types[1064]), true));
        attributes.push_back(new attribute("TextFontStyle", new named_type(IFC4_types[1057]), false));
        attributes.push_back(new attribute("ModelOrDraughting", new named_type(IFC4_types[69]), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1061])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1056])), false));
        attributes.push_back(new attribute("FontStyle", new named_type(IFC4_types[435]), true));
        attributes.push_back(new attribute("FontVariant", new named_type(IFC4_types[436]), true));
        attributes.push_back(new attribute("FontWeight", new named_type(IFC4_types[437]), true));
        attributes.push_back(new attribute("FontSize", new named_type(IFC4_types[904]), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1062])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Colour", new named_type(IFC4_types[149]), false));
        attributes.push_back(new attribute("BackgroundColour", new named_type(IFC4_types[149]), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1063])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("TextIndent", new named_type(IFC4_types[904]), true));
        attributes.push_back(new attribute("TextAlign", new named_type(IFC4_types[1054]), true));
        attributes.push_back(new attribute("TextDecoration", new named_type(IFC4_types[1055]), true));
        attributes.push_back(new attribute("LetterSpacing", new named_type(IFC4_types[904]), true));
        attributes.push_back(new attribute("WordSpacing", new named_type(IFC4_types[904]), true));
        attributes.push_back(new attribute("TextTransform", new named_type(IFC4_types[1065]), true));
        attributes.push_back(new attribute("LineHeight", new named_type(IFC4_types[904]), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1064])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Maps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1018])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1066])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Mode", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[775])), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1067])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Vertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IFC4_types[1069])), false));
        attributes.push_back(new attribute("MappedTo", new named_type(IFC4_types[386]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1068])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_types[638])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1069])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("TexCoordsList", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_types[638]))), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1070])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("StartTime", new named_type(IFC4_types[1077]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC4_types[1077]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1080])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new attribute("Name", new named_type(IFC4_types[505]), false));
        attributes.push_back(new attribute("Description", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC4_types[255]), false));
        attributes.push_back(new attribute("EndTime", new named_type(IFC4_types[255]), false));
        attributes.push_back(new attribute("TimeSeriesDataType", new named_type(IFC4_types[1082]), false));
        attributes.push_back(new attribute("DataOrigin", new named_type(IFC4_types[253]), false));
        attributes.push_back(new attribute("UserDefinedDataOrigin", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Unit", new named_type(IFC4_types[1110]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1081])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[1121])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1083])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[1085])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1086])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("MajorRadius", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("MinorRadius", new named_type(IFC4_types[685]), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1087])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1091]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1089])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1091]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1090])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1096]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1094])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1096]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1095])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("BottomXDim", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("TopXDim", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("YDim", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("TopXOffset", new named_type(IFC4_types[516]), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1097])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("Normals", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[638]))), true));
        attributes.push_back(new attribute("Closed", new named_type(IFC4_types[69]), true));
        attributes.push_back(new attribute("CoordIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new aggregation_type(aggregation_type::list_type, 3, 3, new named_type(IFC4_types[684]))), false));
        attributes.push_back(new attribute("PnIndex", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[684])), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1098])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("BasisCurve", new named_type(IFC4_types[237]), false));
        attributes.push_back(new attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4_types[1101])), false));
        attributes.push_back(new attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IFC4_types[1101])), false));
        attributes.push_back(new attribute("SenseAgreement", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("MasterRepresentation", new named_type(IFC4_types[1100]), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1099])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1105]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1103])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1105]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1104])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("ApplicableOccurrence", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[736])), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1106])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("ProcessType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1107])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IFC4_types[849])), true));
        attributes.push_back(new attribute("Tag", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1108])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("Identification", new named_type(IFC4_types[476]), true));
        attributes.push_back(new attribute("LongDescription", new named_type(IFC4_types[1053]), true));
        attributes.push_back(new attribute("ResourceType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1109])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("FlangeSlope", new named_type(IFC4_types[670]), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1120])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[1110])), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1117])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1113]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1111])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1113]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1112])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1116]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1114])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1116]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1115])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1124]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1122])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1124]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1123])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("Orientation", new named_type(IFC4_types[267]), false));
        attributes.push_back(new attribute("Magnitude", new named_type(IFC4_types[516]), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1126])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        ((entity*)IFC4_types[1128])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LoopVertex", new named_type(IFC4_types[1128]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1129])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("VertexGeometry", new named_type(IFC4_types[675]), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        ((entity*)IFC4_types[1130])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1133]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1131])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1133]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1132])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1134])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IFC4_types[461])), false));
        attributes.push_back(new attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IFC4_types[516])), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1135])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1137]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1136])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1144]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1140])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1141])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1142])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1144]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1143])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1150]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1148])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1150]), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1149])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OverallHeight", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("OverallWidth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1161]), true));
        attributes.push_back(new attribute("PartitioningType", new named_type(IFC4_types[1162]), true));
        attributes.push_back(new attribute("UserDefinedPartitioningType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1151])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new attribute("LiningDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("LiningThickness", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("TransomThickness", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("MullionThickness", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("FirstTransomOffset", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("SecondTransomOffset", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("FirstMullionOffset", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("SecondMullionOffset", new named_type(IFC4_types[611]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4_types[890]), true));
        attributes.push_back(new attribute("LiningOffset", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetX", new named_type(IFC4_types[516]), true));
        attributes.push_back(new attribute("LiningToPanelOffsetY", new named_type(IFC4_types[516]), true));
        std::vector<bool> derived; derived.reserve(16);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1152])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new attribute("OperationType", new named_type(IFC4_types[1153]), false));
        attributes.push_back(new attribute("PanelPosition", new named_type(IFC4_types[1154]), false));
        attributes.push_back(new attribute("FrameDepth", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("FrameThickness", new named_type(IFC4_types[685]), true));
        attributes.push_back(new attribute("ShapeAspectStyle", new named_type(IFC4_types[890]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1155])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1156])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("ConstructionType", new named_type(IFC4_types[1158]), false));
        attributes.push_back(new attribute("OperationType", new named_type(IFC4_types[1159]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4_types[69]), false));
        attributes.push_back(new attribute("Sizeable", new named_type(IFC4_types[69]), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1157])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1161]), false));
        attributes.push_back(new attribute("PartitioningType", new named_type(IFC4_types[1162]), false));
        attributes.push_back(new attribute("ParameterTakesPrecedence", new named_type(IFC4_types[69]), true));
        attributes.push_back(new attribute("UserDefinedPartitioningType", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1160])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("WorkingTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[1170])), true));
        attributes.push_back(new attribute("ExceptionTimes", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[1170])), true));
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1164]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1163])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new attribute("CreationDate", new named_type(IFC4_types[255]), false));
        attributes.push_back(new attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IFC4_types[647])), true));
        attributes.push_back(new attribute("Purpose", new named_type(IFC4_types[505]), true));
        attributes.push_back(new attribute("Duration", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("TotalFloat", new named_type(IFC4_types[316]), true));
        attributes.push_back(new attribute("StartTime", new named_type(IFC4_types[255]), false));
        attributes.push_back(new attribute("FinishTime", new named_type(IFC4_types[255]), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1165])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1167]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1166])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("PredefinedType", new named_type(IFC4_types[1169]), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1168])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new attribute("RecurrencePattern", new named_type(IFC4_types[780]), true));
        attributes.push_back(new attribute("Start", new named_type(IFC4_types[254]), true));
        attributes.push_back(new attribute("Finish", new named_type(IFC4_types[254]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1170])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new attribute("Depth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeWidth", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("WebThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FlangeThickness", new named_type(IFC4_types[685]), false));
        attributes.push_back(new attribute("FilletRadius", new named_type(IFC4_types[610]), true));
        attributes.push_back(new attribute("EdgeRadius", new named_type(IFC4_types[610]), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1172])->set_attributes(attributes, derived);
    }
    {
        std::vector<const attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new attribute("LongName", new named_type(IFC4_types[505]), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        ((entity*)IFC4_types[1171])->set_attributes(attributes, derived);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsActingUpon", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[799]), ((entity*) IFC4_types[799])->attributes()[0]));
        ((entity*) IFC4_types[6])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        ((entity*) IFC4_types[7])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("OfPerson", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[647]), ((entity*) IFC4_types[647])->attributes()[7]));
        attributes.push_back(new inverse_attribute("OfOrganization", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[629]), ((entity*) IFC4_types[629])->attributes()[4]));
        ((entity*) IFC4_types[12])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[823]), ((entity*) IFC4_types[823])->attributes()[0]));
        ((entity*) IFC4_types[33])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        ((entity*) IFC4_types[36])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ApprovedObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[807]), ((entity*) IFC4_types[807])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ApprovedResources", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[851]), ((entity*) IFC4_types[851])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[39]), ((entity*) IFC4_types[39])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[39]), ((entity*) IFC4_types[39])->attributes()[0]));
        ((entity*) IFC4_types[38])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ClassificationForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[808]), ((entity*) IFC4_types[808])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[142]), ((entity*) IFC4_types[142])->attributes()[0]));
        ((entity*) IFC4_types[141])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ClassificationRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[808]), ((entity*) IFC4_types[808])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[142]), ((entity*) IFC4_types[142])->attributes()[0]));
        ((entity*) IFC4_types[142])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("UsingCurves", inverse_attribute::set_type, 1, -1, ((entity*) IFC4_types[165]), ((entity*) IFC4_types[165])->attributes()[0]));
        ((entity*) IFC4_types[167])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PropertiesForConstraint", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[852]), ((entity*) IFC4_types[852])->attributes()[0]));
        ((entity*) IFC4_types[185])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[830]), ((entity*) IFC4_types[830])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Declares", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[826]), ((entity*) IFC4_types[826])->attributes()[0]));
        ((entity*) IFC4_types[198])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        ((entity*) IFC4_types[200])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Controls", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[800]), ((entity*) IFC4_types[800])->attributes()[0]));
        ((entity*) IFC4_types[201])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        ((entity*) IFC4_types[205])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasCoordinateOperation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[213]), ((entity*) IFC4_types[213])->attributes()[0]));
        ((entity*) IFC4_types[214])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("CoversSpaces", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[825]), ((entity*) IFC4_types[825])->attributes()[1]));
        attributes.push_back(new inverse_attribute("CoversElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[824]), ((entity*) IFC4_types[824])->attributes()[1]));
        ((entity*) IFC4_types[222])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToFlowElement", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[834]), ((entity*) IFC4_types[834])->attributes()[0]));
        ((entity*) IFC4_types[276])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasPorts", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[818]), ((entity*) IFC4_types[818])->attributes()[1]));
        ((entity*) IFC4_types[278])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasControlElements", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[834]), ((entity*) IFC4_types[834])->attributes()[1]));
        ((entity*) IFC4_types[280])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("DocumentInfoForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[810]), ((entity*) IFC4_types[810])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasDocumentReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[289]), ((entity*) IFC4_types[289])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[288]), ((entity*) IFC4_types[288])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsPointer", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[288]), ((entity*) IFC4_types[288])->attributes()[0]));
        ((entity*) IFC4_types[287])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("DocumentRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[810]), ((entity*) IFC4_types[810])->attributes()[0]));
        ((entity*) IFC4_types[289])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new inverse_attribute("FillsVoids", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[833]), ((entity*) IFC4_types[833])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[815]), ((entity*) IFC4_types[815])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsInterferedByElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[835]), ((entity*) IFC4_types[835])->attributes()[1]));
        attributes.push_back(new inverse_attribute("InterferesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[835]), ((entity*) IFC4_types[835])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasProjections", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[837]), ((entity*) IFC4_types[837])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedInStructures", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[838]), ((entity*) IFC4_types[838])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasOpenings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[844]), ((entity*) IFC4_types[844])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsConnectionRealization", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[822]), ((entity*) IFC4_types[822])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ProvidesBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[841]), ((entity*) IFC4_types[841])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[815]), ((entity*) IFC4_types[815])->attributes()[2]));
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[823]), ((entity*) IFC4_types[823])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[824]), ((entity*) IFC4_types[824])->attributes()[0]));
        ((entity*) IFC4_types[345])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ExternalReferenceForResources", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[0]));
        ((entity*) IFC4_types[379])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[841]), ((entity*) IFC4_types[841])->attributes()[0]));
        ((entity*) IFC4_types[381])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasTextureMaps", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[1068]), ((entity*) IFC4_types[1068])->attributes()[1]));
        ((entity*) IFC4_types[386])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ProjectsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4_types[837]), ((entity*) IFC4_types[837])->attributes()[1]));
        ((entity*) IFC4_types[401])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("VoidsElements", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4_types[844]), ((entity*) IFC4_types[844])->attributes()[1]));
        ((entity*) IFC4_types[402])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasSubContexts", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[455]), ((entity*) IFC4_types[455])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasCoordinateOperation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[213]), ((entity*) IFC4_types[213])->attributes()[0]));
        ((entity*) IFC4_types[453])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ContainedInStructure", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[823]), ((entity*) IFC4_types[823])->attributes()[0]));
        ((entity*) IFC4_types[460])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("PartOfW", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[460]), ((entity*) IFC4_types[460])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfV", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[460]), ((entity*) IFC4_types[460])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfU", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[460]), ((entity*) IFC4_types[460])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasIntersections", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[1135]), ((entity*) IFC4_types[1135])->attributes()[0]));
        ((entity*) IFC4_types[461])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("IsGroupedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[801]), ((entity*) IFC4_types[801])->attributes()[0]));
        ((entity*) IFC4_types[465])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToFaceSet", inverse_attribute::set_type, 1, -1, ((entity*) IFC4_types[680]), ((entity*) IFC4_types[680])->attributes()[1]));
        ((entity*) IFC4_types[481])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LibraryInfoForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[811]), ((entity*) IFC4_types[811])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasLibraryReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[518]), ((entity*) IFC4_types[518])->attributes()[2]));
        ((entity*) IFC4_types[517])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("LibraryRefForObjects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[811]), ((entity*) IFC4_types[811])->attributes()[0]));
        ((entity*) IFC4_types[518])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("HasRepresentation", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[563]), ((entity*) IFC4_types[563])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsRelatedWith", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[575]), ((entity*) IFC4_types[575])->attributes()[1]));
        attributes.push_back(new inverse_attribute("RelatesTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[575]), ((entity*) IFC4_types[575])->attributes()[0]));
        ((entity*) IFC4_types[558])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialConstituentSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4_types[561]), ((entity*) IFC4_types[561])->attributes()[2]));
        ((entity*) IFC4_types[560])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("AssociatedTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[812]), ((entity*) IFC4_types[812])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasProperties", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[574]), ((entity*) IFC4_types[574])->attributes()[0]));
        ((entity*) IFC4_types[562])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialLayerSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4_types[565]), ((entity*) IFC4_types[565])->attributes()[0]));
        ((entity*) IFC4_types[564])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ToMaterialProfileSet", inverse_attribute::unspecified_type, -1, -1, ((entity*) IFC4_types[570]), ((entity*) IFC4_types[570])->attributes()[2]));
        ((entity*) IFC4_types[569])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssociatedTo", inverse_attribute::set_type, 1, -1, ((entity*) IFC4_types[812]), ((entity*) IFC4_types[812])->attributes()[0]));
        ((entity*) IFC4_types[577])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new inverse_attribute("IsDeclaredBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[829]), ((entity*) IFC4_types[829])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Declares", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[829]), ((entity*) IFC4_types[829])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsTypedBy", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[832]), ((entity*) IFC4_types[832])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[830]), ((entity*) IFC4_types[830])->attributes()[0]));
        ((entity*) IFC4_types[614])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new inverse_attribute("HasAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[798]), ((entity*) IFC4_types[798])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Nests", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[836]), ((entity*) IFC4_types[836])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsNestedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[836]), ((entity*) IFC4_types[836])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasContext", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[826]), ((entity*) IFC4_types[826])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsDecomposedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[797]), ((entity*) IFC4_types[797])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Decomposes", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[797]), ((entity*) IFC4_types[797])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[806]), ((entity*) IFC4_types[806])->attributes()[0]));
        ((entity*) IFC4_types[615])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PlacesObject", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[710]), ((entity*) IFC4_types[710])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ReferencedByPlacements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[541]), ((entity*) IFC4_types[541])->attributes()[0]));
        ((entity*) IFC4_types[618])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasFillings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[833]), ((entity*) IFC4_types[833])->attributes()[0]));
        ((entity*) IFC4_types[625])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsRelatedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[630]), ((entity*) IFC4_types[630])->attributes()[1]));
        attributes.push_back(new inverse_attribute("Relates", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[630]), ((entity*) IFC4_types[630])->attributes()[0]));
        attributes.push_back(new inverse_attribute("Engages", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[648]), ((entity*) IFC4_types[648])->attributes()[1]));
        ((entity*) IFC4_types[629])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("EngagedIn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[648]), ((entity*) IFC4_types[648])->attributes()[0]));
        ((entity*) IFC4_types[647])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[650]), ((entity*) IFC4_types[650])->attributes()[0]));
        ((entity*) IFC4_types[652])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainedIn", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[818]), ((entity*) IFC4_types[818])->attributes()[0]));
        attributes.push_back(new inverse_attribute("ConnectedFrom", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[817]), ((entity*) IFC4_types[817])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ConnectedTo", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[817]), ((entity*) IFC4_types[817])->attributes()[0]));
        ((entity*) IFC4_types[683])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("IsPredecessorTo", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[839]), ((entity*) IFC4_types[839])->attributes()[0]));
        attributes.push_back(new inverse_attribute("IsSuccessorFrom", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[839]), ((entity*) IFC4_types[839])->attributes()[1]));
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[803]), ((entity*) IFC4_types[803])->attributes()[0]));
        ((entity*) IFC4_types[708])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[804]), ((entity*) IFC4_types[804])->attributes()[0]));
        ((entity*) IFC4_types[710])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("ShapeOfProduct", inverse_attribute::set_type, 1, -1, ((entity*) IFC4_types[710]), ((entity*) IFC4_types[710])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[890]), ((entity*) IFC4_types[890])->attributes()[4]));
        ((entity*) IFC4_types[711])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasProperties", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[716]), ((entity*) IFC4_types[716])->attributes()[0]));
        ((entity*) IFC4_types[715])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new inverse_attribute("PartOfPset", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[735]), ((entity*) IFC4_types[735])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyForDependance", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[730]), ((entity*) IFC4_types[730])->attributes()[0]));
        attributes.push_back(new inverse_attribute("PropertyDependsOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[730]), ((entity*) IFC4_types[730])->attributes()[1]));
        attributes.push_back(new inverse_attribute("PartOfComplex", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[162]), ((entity*) IFC4_types[162])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasConstraints", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[852]), ((entity*) IFC4_types[852])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasApprovals", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[851]), ((entity*) IFC4_types[851])->attributes()[0]));
        ((entity*) IFC4_types[726])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReferences", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        ((entity*) IFC4_types[727])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasContext", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[826]), ((entity*) IFC4_types[826])->attributes()[1]));
        attributes.push_back(new inverse_attribute("HasAssociations", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[806]), ((entity*) IFC4_types[806])->attributes()[0]));
        ((entity*) IFC4_types[729])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("DefinesType", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[1106]), ((entity*) IFC4_types[1106])->attributes()[1]));
        attributes.push_back(new inverse_attribute("IsDefinedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[831]), ((entity*) IFC4_types[831])->attributes()[0]));
        attributes.push_back(new inverse_attribute("DefinesOccurrence", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[830]), ((entity*) IFC4_types[830])->attributes()[1]));
        ((entity*) IFC4_types[736])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Defines", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[831]), ((entity*) IFC4_types[831])->attributes()[1]));
        ((entity*) IFC4_types[739])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("PartOfComplexTemplate", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[163]), ((entity*) IFC4_types[163])->attributes()[2]));
        attributes.push_back(new inverse_attribute("PartOfPsetTemplate", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[739]), ((entity*) IFC4_types[739])->attributes()[2]));
        ((entity*) IFC4_types[743])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("InnerBoundaries", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[842]), ((entity*) IFC4_types[842])->attributes()[0]));
        ((entity*) IFC4_types[842])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Corresponds", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[843]), ((entity*) IFC4_types[843])->attributes()[0]));
        ((entity*) IFC4_types[843])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("RepresentationMap", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[849]), ((entity*) IFC4_types[849])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LayerAssignments", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[699]), ((entity*) IFC4_types[699])->attributes()[2]));
        attributes.push_back(new inverse_attribute("OfProductRepresentation", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[712]), ((entity*) IFC4_types[712])->attributes()[2]));
        ((entity*) IFC4_types[846])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("RepresentationsInContext", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[846]), ((entity*) IFC4_types[846])->attributes()[0]));
        ((entity*) IFC4_types[847])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("LayerAssignment", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[699]), ((entity*) IFC4_types[699])->attributes()[2]));
        attributes.push_back(new inverse_attribute("StyledByItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[994]), ((entity*) IFC4_types[994])->attributes()[0]));
        ((entity*) IFC4_types[848])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasShapeAspects", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[890]), ((entity*) IFC4_types[890])->attributes()[4]));
        attributes.push_back(new inverse_attribute("MapUsage", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[553]), ((entity*) IFC4_types[553])->attributes()[0]));
        ((entity*) IFC4_types[849])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[805]), ((entity*) IFC4_types[805])->attributes()[0]));
        ((entity*) IFC4_types[850])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OfShapeAspect", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[890]), ((entity*) IFC4_types[890])->attributes()[0]));
        ((entity*) IFC4_types[891])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasCoverings", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[825]), ((entity*) IFC4_types[825])->attributes()[0]));
        attributes.push_back(new inverse_attribute("BoundedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[841]), ((entity*) IFC4_types[841])->attributes()[0]));
        ((entity*) IFC4_types[921])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new inverse_attribute("ContainsElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[823]), ((entity*) IFC4_types[823])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ServicedBySystems", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[840]), ((entity*) IFC4_types[840])->attributes()[1]));
        attributes.push_back(new inverse_attribute("ReferencesElements", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[838]), ((entity*) IFC4_types[838])->attributes()[1]));
        ((entity*) IFC4_types[928])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedToStructuralItem", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[819]), ((entity*) IFC4_types[819])->attributes()[1]));
        ((entity*) IFC4_types[952])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectsStructuralMembers", inverse_attribute::set_type, 1, -1, ((entity*) IFC4_types[820]), ((entity*) IFC4_types[820])->attributes()[1]));
        ((entity*) IFC4_types[955])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("AssignedStructuralActivity", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[819]), ((entity*) IFC4_types[819])->attributes()[0]));
        ((entity*) IFC4_types[964])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("SourceOfResultGroup", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[985]), ((entity*) IFC4_types[985])->attributes()[1]));
        attributes.push_back(new inverse_attribute("LoadGroupFor", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[954]), ((entity*) IFC4_types[954])->attributes()[2]));
        ((entity*) IFC4_types[969])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ConnectedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[820]), ((entity*) IFC4_types[820])->attributes()[0]));
        ((entity*) IFC4_types[979])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResultGroupFor", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[954]), ((entity*) IFC4_types[954])->attributes()[3]));
        ((entity*) IFC4_types[985])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("IsMappedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[1066]), ((entity*) IFC4_types[1066])->attributes()[0]));
        attributes.push_back(new inverse_attribute("UsedInStyles", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[1017]), ((entity*) IFC4_types[1017])->attributes()[0]));
        ((entity*) IFC4_types[1018])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ServicesBuildings", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[840]), ((entity*) IFC4_types[840])->attributes()[0]));
        ((entity*) IFC4_types[1026])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new inverse_attribute("HasColours", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[479]), ((entity*) IFC4_types[479])->attributes()[0]));
        attributes.push_back(new inverse_attribute("HasTextures", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[483]), ((entity*) IFC4_types[483])->attributes()[0]));
        ((entity*) IFC4_types[1051])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("HasExternalReference", inverse_attribute::set_type, 1, -1, ((entity*) IFC4_types[380]), ((entity*) IFC4_types[380])->attributes()[1]));
        ((entity*) IFC4_types[1081])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("Types", inverse_attribute::set_type, 0, 1, ((entity*) IFC4_types[832]), ((entity*) IFC4_types[832])->attributes()[1]));
        ((entity*) IFC4_types[1106])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("OperatesOn", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[803]), ((entity*) IFC4_types[803])->attributes()[0]));
        ((entity*) IFC4_types[1107])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ReferencedBy", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[804]), ((entity*) IFC4_types[804])->attributes()[0]));
        ((entity*) IFC4_types[1108])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new inverse_attribute("ResourceOf", inverse_attribute::set_type, 0, -1, ((entity*) IFC4_types[805]), ((entity*) IFC4_types[805])->attributes()[0]));
        ((entity*) IFC4_types[1109])->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4_types[2]));defs.push_back(((entity*) IFC4_types[216]));defs.push_back(((entity*) IFC4_types[218]));defs.push_back(((entity*) IFC4_types[641]));defs.push_back(((entity*) IFC4_types[645]));defs.push_back(((entity*) IFC4_types[724]));defs.push_back(((entity*) IFC4_types[1163]));defs.push_back(((entity*) IFC4_types[1165]));
        ((entity*) IFC4_types[201])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[6]));defs.push_back(((entity*) IFC4_types[201]));defs.push_back(((entity*) IFC4_types[465]));defs.push_back(((entity*) IFC4_types[708]));defs.push_back(((entity*) IFC4_types[710]));defs.push_back(((entity*) IFC4_types[850]));
        ((entity*) IFC4_types[614])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4_types[9]));defs.push_back(((entity*) IFC4_types[26]));defs.push_back(((entity*) IFC4_types[202]));defs.push_back(((entity*) IFC4_types[419]));defs.push_back(((entity*) IFC4_types[746]));defs.push_back(((entity*) IFC4_types[883]));defs.push_back(((entity*) IFC4_types[1111]));
        ((entity*) IFC4_types[276])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4_types[10]));defs.push_back(((entity*) IFC4_types[27]));defs.push_back(((entity*) IFC4_types[203]));defs.push_back(((entity*) IFC4_types[420]));defs.push_back(((entity*) IFC4_types[747]));defs.push_back(((entity*) IFC4_types[884]));defs.push_back(((entity*) IFC4_types[1112]));
        ((entity*) IFC4_types[277])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[14]));defs.push_back(((entity*) IFC4_types[391]));
        ((entity*) IFC4_types[551])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[15]));
        ((entity*) IFC4_types[14])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[16]));
        ((entity*) IFC4_types[390])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(13);
        defs.push_back(((entity*) IFC4_types[17]));defs.push_back(((entity*) IFC4_types[50]));defs.push_back(((entity*) IFC4_types[158]));defs.push_back(((entity*) IFC4_types[321]));defs.push_back(((entity*) IFC4_types[410]));defs.push_back(((entity*) IFC4_types[510]));defs.push_back(((entity*) IFC4_types[524]));defs.push_back(((entity*) IFC4_types[583]));defs.push_back(((entity*) IFC4_types[633]));defs.push_back(((entity*) IFC4_types[871]));defs.push_back(((entity*) IFC4_types[923]));defs.push_back(((entity*) IFC4_types[941]));defs.push_back(((entity*) IFC4_types[1148]));
        ((entity*) IFC4_types[431])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4_types[18]));defs.push_back(((entity*) IFC4_types[250]));defs.push_back(((entity*) IFC4_types[328]));defs.push_back(((entity*) IFC4_types[341]));defs.push_back(((entity*) IFC4_types[422]));defs.push_back(((entity*) IFC4_types[745]));defs.push_back(((entity*) IFC4_types[1023]));defs.push_back(((entity*) IFC4_types[1122]));
        ((entity*) IFC4_types[414])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4_types[19]));defs.push_back(((entity*) IFC4_types[251]));defs.push_back(((entity*) IFC4_types[329]));defs.push_back(((entity*) IFC4_types[342]));defs.push_back(((entity*) IFC4_types[423]));defs.push_back(((entity*) IFC4_types[749]));defs.push_back(((entity*) IFC4_types[1024]));defs.push_back(((entity*) IFC4_types[1123]));
        ((entity*) IFC4_types[415])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(13);
        defs.push_back(((entity*) IFC4_types[21]));defs.push_back(((entity*) IFC4_types[51]));defs.push_back(((entity*) IFC4_types[159]));defs.push_back(((entity*) IFC4_types[322]));defs.push_back(((entity*) IFC4_types[411]));defs.push_back(((entity*) IFC4_types[511]));defs.push_back(((entity*) IFC4_types[525]));defs.push_back(((entity*) IFC4_types[584]));defs.push_back(((entity*) IFC4_types[634]));defs.push_back(((entity*) IFC4_types[872]));defs.push_back(((entity*) IFC4_types[924]));defs.push_back(((entity*) IFC4_types[942]));defs.push_back(((entity*) IFC4_types[1149]));
        ((entity*) IFC4_types[432])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC4_types[23]));defs.push_back(((entity*) IFC4_types[66]));defs.push_back(((entity*) IFC4_types[103]));defs.push_back(((entity*) IFC4_types[130]));defs.push_back(((entity*) IFC4_types[146]));defs.push_back(((entity*) IFC4_types[173]));defs.push_back(((entity*) IFC4_types[207]));defs.push_back(((entity*) IFC4_types[210]));defs.push_back(((entity*) IFC4_types[334]));defs.push_back(((entity*) IFC4_types[337]));defs.push_back(((entity*) IFC4_types[360]));defs.push_back(((entity*) IFC4_types[363]));defs.push_back(((entity*) IFC4_types[366]));defs.push_back(((entity*) IFC4_types[468]));defs.push_back(((entity*) IFC4_types[473]));defs.push_back(((entity*) IFC4_types[606]));defs.push_back(((entity*) IFC4_types[911]));defs.push_back(((entity*) IFC4_types[1089]));defs.push_back(((entity*) IFC4_types[1103]));defs.push_back(((entity*) IFC4_types[1114]));
        ((entity*) IFC4_types[357])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(20);
        defs.push_back(((entity*) IFC4_types[24]));defs.push_back(((entity*) IFC4_types[67]));defs.push_back(((entity*) IFC4_types[104]));defs.push_back(((entity*) IFC4_types[131]));defs.push_back(((entity*) IFC4_types[147]));defs.push_back(((entity*) IFC4_types[174]));defs.push_back(((entity*) IFC4_types[208]));defs.push_back(((entity*) IFC4_types[211]));defs.push_back(((entity*) IFC4_types[335]));defs.push_back(((entity*) IFC4_types[338]));defs.push_back(((entity*) IFC4_types[361]));defs.push_back(((entity*) IFC4_types[364]));defs.push_back(((entity*) IFC4_types[367]));defs.push_back(((entity*) IFC4_types[469]));defs.push_back(((entity*) IFC4_types[474]));defs.push_back(((entity*) IFC4_types[607]));defs.push_back(((entity*) IFC4_types[912]));defs.push_back(((entity*) IFC4_types[1090]));defs.push_back(((entity*) IFC4_types[1104]));defs.push_back(((entity*) IFC4_types[1115]));
        ((entity*) IFC4_types[358])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4_types[33]));defs.push_back(((entity*) IFC4_types[345]));defs.push_back(((entity*) IFC4_types[460]));defs.push_back(((entity*) IFC4_types[683]));defs.push_back(((entity*) IFC4_types[751]));defs.push_back(((entity*) IFC4_types[928]));defs.push_back(((entity*) IFC4_types[952]));defs.push_back(((entity*) IFC4_types[964]));
        ((entity*) IFC4_types[710])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(25);
        defs.push_back(((entity*) IFC4_types[34]));defs.push_back(((entity*) IFC4_types[73]));defs.push_back(((entity*) IFC4_types[82]));defs.push_back(((entity*) IFC4_types[120]));defs.push_back(((entity*) IFC4_types[123]));defs.push_back(((entity*) IFC4_types[167]));defs.push_back(((entity*) IFC4_types[228]));defs.push_back(((entity*) IFC4_types[237]));defs.push_back(((entity*) IFC4_types[267]));defs.push_back(((entity*) IFC4_types[387]));defs.push_back(((entity*) IFC4_types[404]));defs.push_back(((entity*) IFC4_types[405]));defs.push_back(((entity*) IFC4_types[456]));defs.push_back(((entity*) IFC4_types[466]));defs.push_back(((entity*) IFC4_types[528]));defs.push_back(((entity*) IFC4_types[665]));defs.push_back(((entity*) IFC4_types[667]));defs.push_back(((entity*) IFC4_types[675]));defs.push_back(((entity*) IFC4_types[877]));defs.push_back(((entity*) IFC4_types[895]));defs.push_back(((entity*) IFC4_types[915]));defs.push_back(((entity*) IFC4_types[1001]));defs.push_back(((entity*) IFC4_types[1052]));defs.push_back(((entity*) IFC4_types[1058]));defs.push_back(((entity*) IFC4_types[1126]));
        ((entity*) IFC4_types[454])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4_types[39]));defs.push_back(((entity*) IFC4_types[232]));defs.push_back(((entity*) IFC4_types[288]));defs.push_back(((entity*) IFC4_types[380]));defs.push_back(((entity*) IFC4_types[575]));defs.push_back(((entity*) IFC4_types[630]));defs.push_back(((entity*) IFC4_types[730]));defs.push_back(((entity*) IFC4_types[851]));defs.push_back(((entity*) IFC4_types[852]));
        ((entity*) IFC4_types[853])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[40]));defs.push_back(((entity*) IFC4_types[41]));defs.push_back(((entity*) IFC4_types[168]));defs.push_back(((entity*) IFC4_types[260]));defs.push_back(((entity*) IFC4_types[637]));
        ((entity*) IFC4_types[715])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[42]));
        ((entity*) IFC4_types[40])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[48]));defs.push_back(((entity*) IFC4_types[493]));defs.push_back(((entity*) IFC4_types[969]));defs.push_back(((entity*) IFC4_types[985]));defs.push_back(((entity*) IFC4_types[1026]));
        ((entity*) IFC4_types[465])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(11);
        defs.push_back(((entity*) IFC4_types[49]));defs.push_back(((entity*) IFC4_types[231]));defs.push_back(((entity*) IFC4_types[138]));defs.push_back(((entity*) IFC4_types[356]));defs.push_back(((entity*) IFC4_types[498]));defs.push_back(((entity*) IFC4_types[545]));defs.push_back(((entity*) IFC4_types[777]));defs.push_back(((entity*) IFC4_types[1102]));defs.push_back(((entity*) IFC4_types[1097]));defs.push_back(((entity*) IFC4_types[1120]));defs.push_back(((entity*) IFC4_types[1172]));
        ((entity*) IFC4_types[637])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[53]));defs.push_back(((entity*) IFC4_types[55]));defs.push_back(((entity*) IFC4_types[56]));
        ((entity*) IFC4_types[665])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[85]));defs.push_back(((entity*) IFC4_types[165]));defs.push_back(((entity*) IFC4_types[480]));defs.push_back(((entity*) IFC4_types[681]));defs.push_back(((entity*) IFC4_types[1099]));
        ((entity*) IFC4_types[80])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[87]));
        ((entity*) IFC4_types[85])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[88]));defs.push_back(((entity*) IFC4_types[238]));defs.push_back(((entity*) IFC4_types[239]));defs.push_back(((entity*) IFC4_types[779]));
        ((entity*) IFC4_types[81])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[90]));
        ((entity*) IFC4_types[88])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(21);
        defs.push_back(((entity*) IFC4_types[57]));defs.push_back(((entity*) IFC4_types[96]));defs.push_back(((entity*) IFC4_types[133]));defs.push_back(((entity*) IFC4_types[154]));defs.push_back(((entity*) IFC4_types[222]));defs.push_back(((entity*) IFC4_types[233]));defs.push_back(((entity*) IFC4_types[292]));defs.push_back(((entity*) IFC4_types[438]));defs.push_back(((entity*) IFC4_types[586]));defs.push_back(((entity*) IFC4_types[654]));defs.push_back(((entity*) IFC4_types[671]));defs.push_back(((entity*) IFC4_types[763]));defs.push_back(((entity*) IFC4_types[766]));defs.push_back(((entity*) IFC4_types[767]));defs.push_back(((entity*) IFC4_types[862]));defs.push_back(((entity*) IFC4_types[887]));defs.push_back(((entity*) IFC4_types[905]));defs.push_back(((entity*) IFC4_types[944]));defs.push_back(((entity*) IFC4_types[945]));defs.push_back(((entity*) IFC4_types[1140]));defs.push_back(((entity*) IFC4_types[1151]));
        ((entity*) IFC4_types[92])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[58]));
        ((entity*) IFC4_types[57])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(21);
        defs.push_back(((entity*) IFC4_types[59]));defs.push_back(((entity*) IFC4_types[97]));defs.push_back(((entity*) IFC4_types[134]));defs.push_back(((entity*) IFC4_types[156]));defs.push_back(((entity*) IFC4_types[223]));defs.push_back(((entity*) IFC4_types[234]));defs.push_back(((entity*) IFC4_types[301]));defs.push_back(((entity*) IFC4_types[439]));defs.push_back(((entity*) IFC4_types[588]));defs.push_back(((entity*) IFC4_types[656]));defs.push_back(((entity*) IFC4_types[673]));defs.push_back(((entity*) IFC4_types[764]));defs.push_back(((entity*) IFC4_types[768]));defs.push_back(((entity*) IFC4_types[770]));defs.push_back(((entity*) IFC4_types[863]));defs.push_back(((entity*) IFC4_types[888]));defs.push_back(((entity*) IFC4_types[908]));defs.push_back(((entity*) IFC4_types[946]));defs.push_back(((entity*) IFC4_types[948]));defs.push_back(((entity*) IFC4_types[1143]));defs.push_back(((entity*) IFC4_types[1160]));
        ((entity*) IFC4_types[99])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[64]));defs.push_back(((entity*) IFC4_types[478]));defs.push_back(((entity*) IFC4_types[664]));
        ((entity*) IFC4_types[1018])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[65]));defs.push_back(((entity*) IFC4_types[778]));defs.push_back(((entity*) IFC4_types[859]));defs.push_back(((entity*) IFC4_types[860]));defs.push_back(((entity*) IFC4_types[939]));
        ((entity*) IFC4_types[228])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[70]));
        ((entity*) IFC4_types[73])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[75]));
        ((entity*) IFC4_types[166])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[76]));defs.push_back(((entity*) IFC4_types[77]));defs.push_back(((entity*) IFC4_types[78]));
        ((entity*) IFC4_types[74])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[79]));
        ((entity*) IFC4_types[78])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4_types[80]));defs.push_back(((entity*) IFC4_types[176]));defs.push_back(((entity*) IFC4_types[534]));defs.push_back(((entity*) IFC4_types[623]));defs.push_back(((entity*) IFC4_types[624]));defs.push_back(((entity*) IFC4_types[640]));defs.push_back(((entity*) IFC4_types[1002]));
        ((entity*) IFC4_types[237])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[81]));defs.push_back(((entity*) IFC4_types[346]));defs.push_back(((entity*) IFC4_types[1022]));
        ((entity*) IFC4_types[1001])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[84]));defs.push_back(((entity*) IFC4_types[679]));
        ((entity*) IFC4_types[466])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[91]));defs.push_back(((entity*) IFC4_types[100]));defs.push_back(((entity*) IFC4_types[901]));defs.push_back(((entity*) IFC4_types[921]));
        ((entity*) IFC4_types[930])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(10);
        defs.push_back(((entity*) IFC4_types[92]));defs.push_back(((entity*) IFC4_types[139]));defs.push_back(((entity*) IFC4_types[278]));defs.push_back(((entity*) IFC4_types[347]));defs.push_back(((entity*) IFC4_types[350]));defs.push_back(((entity*) IFC4_types[400]));defs.push_back(((entity*) IFC4_types[443]));defs.push_back(((entity*) IFC4_types[448]));defs.push_back(((entity*) IFC4_types[1094]));defs.push_back(((entity*) IFC4_types[1134]));
        ((entity*) IFC4_types[345])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[93]));defs.push_back(((entity*) IFC4_types[269]));defs.push_back(((entity*) IFC4_types[397]));defs.push_back(((entity*) IFC4_types[580]));defs.push_back(((entity*) IFC4_types[792]));defs.push_back(((entity*) IFC4_types[1131]));
        ((entity*) IFC4_types[350])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[94]));defs.push_back(((entity*) IFC4_types[270]));defs.push_back(((entity*) IFC4_types[398]));defs.push_back(((entity*) IFC4_types[581]));defs.push_back(((entity*) IFC4_types[793]));defs.push_back(((entity*) IFC4_types[1132]));
        ((entity*) IFC4_types[351])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(8);
        defs.push_back(((entity*) IFC4_types[99]));defs.push_back(((entity*) IFC4_types[140]));defs.push_back(((entity*) IFC4_types[279]));defs.push_back(((entity*) IFC4_types[348]));defs.push_back(((entity*) IFC4_types[351]));defs.push_back(((entity*) IFC4_types[444]));defs.push_back(((entity*) IFC4_types[449]));defs.push_back(((entity*) IFC4_types[1095]));
        ((entity*) IFC4_types[354])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[101]));defs.push_back(((entity*) IFC4_types[284]));defs.push_back(((entity*) IFC4_types[954]));defs.push_back(((entity*) IFC4_types[1171]));
        ((entity*) IFC4_types[1026])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[106]));defs.push_back(((entity*) IFC4_types[112]));defs.push_back(((entity*) IFC4_types[307]));defs.push_back(((entity*) IFC4_types[500]));defs.push_back(((entity*) IFC4_types[658]));
        ((entity*) IFC4_types[417])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[107]));defs.push_back(((entity*) IFC4_types[113]));defs.push_back(((entity*) IFC4_types[308]));defs.push_back(((entity*) IFC4_types[501]));defs.push_back(((entity*) IFC4_types[659]));
        ((entity*) IFC4_types[418])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[109]));defs.push_back(((entity*) IFC4_types[115]));defs.push_back(((entity*) IFC4_types[310]));defs.push_back(((entity*) IFC4_types[661]));
        ((entity*) IFC4_types[427])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[110]));defs.push_back(((entity*) IFC4_types[116]));defs.push_back(((entity*) IFC4_types[311]));defs.push_back(((entity*) IFC4_types[662]));
        ((entity*) IFC4_types[428])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[119]));defs.push_back(((entity*) IFC4_types[676]));defs.push_back(((entity*) IFC4_types[677]));
        ((entity*) IFC4_types[675])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[121]));defs.push_back(((entity*) IFC4_types[122]));
        ((entity*) IFC4_types[120])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[124]));defs.push_back(((entity*) IFC4_types[126]));
        ((entity*) IFC4_types[123])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[125]));
        ((entity*) IFC4_types[124])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[127]));
        ((entity*) IFC4_types[126])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[128]));
        ((entity*) IFC4_types[41])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[136]));defs.push_back(((entity*) IFC4_types[355]));
        ((entity*) IFC4_types[176])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[137]));
        ((entity*) IFC4_types[138])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[141]));defs.push_back(((entity*) IFC4_types[287]));defs.push_back(((entity*) IFC4_types[517]));
        ((entity*) IFC4_types[375])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[142]));defs.push_back(((entity*) IFC4_types[289]));defs.push_back(((entity*) IFC4_types[376]));defs.push_back(((entity*) IFC4_types[377]));defs.push_back(((entity*) IFC4_types[378]));defs.push_back(((entity*) IFC4_types[518]));
        ((entity*) IFC4_types[379])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[145]));defs.push_back(((entity*) IFC4_types[628]));
        ((entity*) IFC4_types[177])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[151]));
        ((entity*) IFC4_types[153])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(17);
        defs.push_back(((entity*) IFC4_types[152]));defs.push_back(((entity*) IFC4_types[153]));defs.push_back(((entity*) IFC4_types[245]));defs.push_back(((entity*) IFC4_types[246]));defs.push_back(((entity*) IFC4_types[247]));defs.push_back(((entity*) IFC4_types[479]));defs.push_back(((entity*) IFC4_types[692]));defs.push_back(((entity*) IFC4_types[1013]));defs.push_back(((entity*) IFC4_types[1014]));defs.push_back(((entity*) IFC4_types[1016]));defs.push_back(((entity*) IFC4_types[1017]));defs.push_back(((entity*) IFC4_types[1018]));defs.push_back(((entity*) IFC4_types[1063]));defs.push_back(((entity*) IFC4_types[1064]));defs.push_back(((entity*) IFC4_types[1066]));defs.push_back(((entity*) IFC4_types[1069]));defs.push_back(((entity*) IFC4_types[1070]));
        ((entity*) IFC4_types[698])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[155]));
        ((entity*) IFC4_types[154])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[162]));defs.push_back(((entity*) IFC4_types[896]));
        ((entity*) IFC4_types[726])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[163]));defs.push_back(((entity*) IFC4_types[897]));
        ((entity*) IFC4_types[743])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[166]));
        ((entity*) IFC4_types[165])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[170]));defs.push_back(((entity*) IFC4_types[394]));defs.push_back(((entity*) IFC4_types[752]));
        ((entity*) IFC4_types[425])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[171]));defs.push_back(((entity*) IFC4_types[395]));defs.push_back(((entity*) IFC4_types[753]));
        ((entity*) IFC4_types[426])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4_types[177]));defs.push_back(((entity*) IFC4_types[318]));defs.push_back(((entity*) IFC4_types[386]));defs.push_back(((entity*) IFC4_types[388]));defs.push_back(((entity*) IFC4_types[544]));defs.push_back(((entity*) IFC4_types[639]));defs.push_back(((entity*) IFC4_types[1128]));
        ((entity*) IFC4_types[1085])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[178]));defs.push_back(((entity*) IFC4_types[181]));defs.push_back(((entity*) IFC4_types[182]));defs.push_back(((entity*) IFC4_types[184]));
        ((entity*) IFC4_types[179])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[180]));
        ((entity*) IFC4_types[181])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[187]));defs.push_back(((entity*) IFC4_types[190]));defs.push_back(((entity*) IFC4_types[193]));defs.push_back(((entity*) IFC4_types[225]));defs.push_back(((entity*) IFC4_types[506]));defs.push_back(((entity*) IFC4_types[997]));
        ((entity*) IFC4_types[196])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[188]));defs.push_back(((entity*) IFC4_types[191]));defs.push_back(((entity*) IFC4_types[194]));defs.push_back(((entity*) IFC4_types[226]));defs.push_back(((entity*) IFC4_types[507]));defs.push_back(((entity*) IFC4_types[998]));
        ((entity*) IFC4_types[197])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[196]));
        ((entity*) IFC4_types[850])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[197]));
        ((entity*) IFC4_types[1109])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[198]));defs.push_back(((entity*) IFC4_types[614]));defs.push_back(((entity*) IFC4_types[1106]));
        ((entity*) IFC4_types[615])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[200]));defs.push_back(((entity*) IFC4_types[205]));defs.push_back(((entity*) IFC4_types[902]));
        ((entity*) IFC4_types[609])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[206]));
        ((entity*) IFC4_types[205])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[220]));
        ((entity*) IFC4_types[36])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[230]));defs.push_back(((entity*) IFC4_types[551]));defs.push_back(((entity*) IFC4_types[1019]));defs.push_back(((entity*) IFC4_types[1020]));
        ((entity*) IFC4_types[915])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[244]));defs.push_back(((entity*) IFC4_types[403]));defs.push_back(((entity*) IFC4_types[1011]));defs.push_back(((entity*) IFC4_types[1061]));
        ((entity*) IFC4_types[701])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[249]));defs.push_back(((entity*) IFC4_types[669]));defs.push_back(((entity*) IFC4_types[940]));defs.push_back(((entity*) IFC4_types[1087]));
        ((entity*) IFC4_types[346])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4_types[272]));defs.push_back(((entity*) IFC4_types[357]));defs.push_back(((entity*) IFC4_types[414]));defs.push_back(((entity*) IFC4_types[417]));defs.push_back(((entity*) IFC4_types[425]));defs.push_back(((entity*) IFC4_types[427]));defs.push_back(((entity*) IFC4_types[429]));defs.push_back(((entity*) IFC4_types[431]));defs.push_back(((entity*) IFC4_types[433]));
        ((entity*) IFC4_types[280])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(9);
        defs.push_back(((entity*) IFC4_types[273]));defs.push_back(((entity*) IFC4_types[358]));defs.push_back(((entity*) IFC4_types[415]));defs.push_back(((entity*) IFC4_types[418]));defs.push_back(((entity*) IFC4_types[426]));defs.push_back(((entity*) IFC4_types[428]));defs.push_back(((entity*) IFC4_types[430]));defs.push_back(((entity*) IFC4_types[432]));defs.push_back(((entity*) IFC4_types[434]));
        ((entity*) IFC4_types[281])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[275]));
        ((entity*) IFC4_types[284])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[276]));defs.push_back(((entity*) IFC4_types[280]));
        ((entity*) IFC4_types[278])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[277]));defs.push_back(((entity*) IFC4_types[281]));
        ((entity*) IFC4_types[279])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[282]));
        ((entity*) IFC4_types[683])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[293]));defs.push_back(((entity*) IFC4_types[296]));defs.push_back(((entity*) IFC4_types[644]));defs.push_back(((entity*) IFC4_types[786]));defs.push_back(((entity*) IFC4_types[1152]));defs.push_back(((entity*) IFC4_types[1155]));
        ((entity*) IFC4_types[694])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[297]));
        ((entity*) IFC4_types[292])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[298]));defs.push_back(((entity*) IFC4_types[354]));defs.push_back(((entity*) IFC4_types[929]));defs.push_back(((entity*) IFC4_types[1157]));
        ((entity*) IFC4_types[1108])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[305]));
        ((entity*) IFC4_types[690])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[306]));
        ((entity*) IFC4_types[691])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[313]));defs.push_back(((entity*) IFC4_types[407]));defs.push_back(((entity*) IFC4_types[488]));
        ((entity*) IFC4_types[433])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[314]));defs.push_back(((entity*) IFC4_types[408]));defs.push_back(((entity*) IFC4_types[489]));
        ((entity*) IFC4_types[434])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[319]));defs.push_back(((entity*) IFC4_types[631]));defs.push_back(((entity*) IFC4_types[1000]));
        ((entity*) IFC4_types[318])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[320]));defs.push_back(((entity*) IFC4_types[682]));defs.push_back(((entity*) IFC4_types[1129]));
        ((entity*) IFC4_types[544])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[331]));defs.push_back(((entity*) IFC4_types[1033]));
        ((entity*) IFC4_types[429])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[332]));defs.push_back(((entity*) IFC4_types[1034]));
        ((entity*) IFC4_types[430])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[353]));
        ((entity*) IFC4_types[758])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[369]));defs.push_back(((entity*) IFC4_types[705]));defs.push_back(((entity*) IFC4_types[1036]));
        ((entity*) IFC4_types[708])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[370]));defs.push_back(((entity*) IFC4_types[509]));defs.push_back(((entity*) IFC4_types[856]));defs.push_back(((entity*) IFC4_types[1038]));defs.push_back(((entity*) IFC4_types[1170]));
        ((entity*) IFC4_types[874])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[372]));defs.push_back(((entity*) IFC4_types[706]));defs.push_back(((entity*) IFC4_types[1040]));
        ((entity*) IFC4_types[1107])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[374]));defs.push_back(((entity*) IFC4_types[693]));defs.push_back(((entity*) IFC4_types[726]));defs.push_back(((entity*) IFC4_types[732]));
        ((entity*) IFC4_types[727])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[381]));
        ((entity*) IFC4_types[383])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[383]));defs.push_back(((entity*) IFC4_types[930]));defs.push_back(((entity*) IFC4_types[932]));
        ((entity*) IFC4_types[928])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[384]));defs.push_back(((entity*) IFC4_types[413]));defs.push_back(((entity*) IFC4_types[857]));defs.push_back(((entity*) IFC4_types[1003]));
        ((entity*) IFC4_types[1019])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[385]));
        ((entity*) IFC4_types[384])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[389]));
        ((entity*) IFC4_types[388])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[390]));
        ((entity*) IFC4_types[386])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[392]));
        ((entity*) IFC4_types[391])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[393]));defs.push_back(((entity*) IFC4_types[910]));
        ((entity*) IFC4_types[956])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[401]));defs.push_back(((entity*) IFC4_types[402]));defs.push_back(((entity*) IFC4_types[1004]));
        ((entity*) IFC4_types[400])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[445]));defs.push_back(((entity*) IFC4_types[1027]));
        ((entity*) IFC4_types[443])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[446]));defs.push_back(((entity*) IFC4_types[1028]));
        ((entity*) IFC4_types[444])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[451]));
        ((entity*) IFC4_types[456])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[453]));
        ((entity*) IFC4_types[847])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[454]));defs.push_back(((entity*) IFC4_types[553]));defs.push_back(((entity*) IFC4_types[994]));defs.push_back(((entity*) IFC4_types[1085]));
        ((entity*) IFC4_types[848])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[455]));
        ((entity*) IFC4_types[453])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[462]));defs.push_back(((entity*) IFC4_types[541]));
        ((entity*) IFC4_types[618])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[481]));defs.push_back(((entity*) IFC4_types[1051]));
        ((entity*) IFC4_types[1052])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[482]));
        ((entity*) IFC4_types[481])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[483]));defs.push_back(((entity*) IFC4_types[1067]));defs.push_back(((entity*) IFC4_types[1068]));
        ((entity*) IFC4_types[1066])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[484]));
        ((entity*) IFC4_types[483])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[492]));defs.push_back(((entity*) IFC4_types[875]));
        ((entity*) IFC4_types[1002])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[496]));defs.push_back(((entity*) IFC4_types[784]));
        ((entity*) IFC4_types[1081])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[529]));defs.push_back(((entity*) IFC4_types[530]));defs.push_back(((entity*) IFC4_types[531]));defs.push_back(((entity*) IFC4_types[532]));
        ((entity*) IFC4_types[528])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[533]));
        ((entity*) IFC4_types[532])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[552]));
        ((entity*) IFC4_types[213])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(7);
        defs.push_back(((entity*) IFC4_types[558]));defs.push_back(((entity*) IFC4_types[560]));defs.push_back(((entity*) IFC4_types[561]));defs.push_back(((entity*) IFC4_types[564]));defs.push_back(((entity*) IFC4_types[565]));defs.push_back(((entity*) IFC4_types[569]));defs.push_back(((entity*) IFC4_types[570]));
        ((entity*) IFC4_types[562])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[563]));defs.push_back(((entity*) IFC4_types[711]));
        ((entity*) IFC4_types[712])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[566]));defs.push_back(((entity*) IFC4_types[571]));
        ((entity*) IFC4_types[577])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[567]));
        ((entity*) IFC4_types[564])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[572]));
        ((entity*) IFC4_types[571])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[573]));
        ((entity*) IFC4_types[569])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[574]));defs.push_back(((entity*) IFC4_types[716]));
        ((entity*) IFC4_types[374])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[587]));
        ((entity*) IFC4_types[586])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[590]));defs.push_back(((entity*) IFC4_types[616]));
        ((entity*) IFC4_types[185])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[592]));
        ((entity*) IFC4_types[260])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[615]));defs.push_back(((entity*) IFC4_types[729]));defs.push_back(((entity*) IFC4_types[813]));
        ((entity*) IFC4_types[865])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[621]));
        ((entity*) IFC4_types[6])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[625]));defs.push_back(((entity*) IFC4_types[1136]));
        ((entity*) IFC4_types[402])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[627]));
        ((entity*) IFC4_types[625])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[632]));
        ((entity*) IFC4_types[75])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[650]));defs.push_back(((entity*) IFC4_types[653]));
        ((entity*) IFC4_types[652])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[666]));
        ((entity*) IFC4_types[667])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[672]));
        ((entity*) IFC4_types[671])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[680]));defs.push_back(((entity*) IFC4_types[1098]));
        ((entity*) IFC4_types[1051])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[688]));defs.push_back(((entity*) IFC4_types[1042]));
        ((entity*) IFC4_types[12])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[690]));defs.push_back(((entity*) IFC4_types[691]));defs.push_back(((entity*) IFC4_types[695]));
        ((entity*) IFC4_types[692])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[694]));defs.push_back(((entity*) IFC4_types[735]));defs.push_back(((entity*) IFC4_types[758]));
        ((entity*) IFC4_types[736])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[700]));
        ((entity*) IFC4_types[699])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[718]));defs.push_back(((entity*) IFC4_types[723]));
        ((entity*) IFC4_types[198])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[719]));
        ((entity*) IFC4_types[214])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[721]));
        ((entity*) IFC4_types[401])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[728]));defs.push_back(((entity*) IFC4_types[731]));defs.push_back(((entity*) IFC4_types[733]));defs.push_back(((entity*) IFC4_types[734]));defs.push_back(((entity*) IFC4_types[741]));defs.push_back(((entity*) IFC4_types[742]));
        ((entity*) IFC4_types[896])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[736]));defs.push_back(((entity*) IFC4_types[744]));
        ((entity*) IFC4_types[729])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[739]));defs.push_back(((entity*) IFC4_types[743]));
        ((entity*) IFC4_types[744])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[755]));defs.push_back(((entity*) IFC4_types[756]));defs.push_back(((entity*) IFC4_types[757]));defs.push_back(((entity*) IFC4_types[759]));defs.push_back(((entity*) IFC4_types[760]));defs.push_back(((entity*) IFC4_types[761]));
        ((entity*) IFC4_types[653])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[773]));
        ((entity*) IFC4_types[87])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[774]));
        ((entity*) IFC4_types[90])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[776]));defs.push_back(((entity*) IFC4_types[870]));
        ((entity*) IFC4_types[777])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[785]));defs.push_back(((entity*) IFC4_types[879]));defs.push_back(((entity*) IFC4_types[880]));
        ((entity*) IFC4_types[693])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[787]));defs.push_back(((entity*) IFC4_types[794]));defs.push_back(((entity*) IFC4_types[1045]));defs.push_back(((entity*) IFC4_types[1046]));
        ((entity*) IFC4_types[792])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[790]));defs.push_back(((entity*) IFC4_types[795]));defs.push_back(((entity*) IFC4_types[1047]));defs.push_back(((entity*) IFC4_types[1049]));
        ((entity*) IFC4_types[793])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[797]));defs.push_back(((entity*) IFC4_types[836]));defs.push_back(((entity*) IFC4_types[837]));defs.push_back(((entity*) IFC4_types[844]));
        ((entity*) IFC4_types[827])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[798]));defs.push_back(((entity*) IFC4_types[806]));defs.push_back(((entity*) IFC4_types[814]));defs.push_back(((entity*) IFC4_types[826]));defs.push_back(((entity*) IFC4_types[827]));defs.push_back(((entity*) IFC4_types[828]));
        ((entity*) IFC4_types[813])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[799]));defs.push_back(((entity*) IFC4_types[800]));defs.push_back(((entity*) IFC4_types[801]));defs.push_back(((entity*) IFC4_types[803]));defs.push_back(((entity*) IFC4_types[804]));defs.push_back(((entity*) IFC4_types[805]));
        ((entity*) IFC4_types[798])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[802]));
        ((entity*) IFC4_types[801])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(6);
        defs.push_back(((entity*) IFC4_types[807]));defs.push_back(((entity*) IFC4_types[808]));defs.push_back(((entity*) IFC4_types[809]));defs.push_back(((entity*) IFC4_types[810]));defs.push_back(((entity*) IFC4_types[811]));defs.push_back(((entity*) IFC4_types[812]));
        ((entity*) IFC4_types[806])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(15);
        defs.push_back(((entity*) IFC4_types[815]));defs.push_back(((entity*) IFC4_types[818]));defs.push_back(((entity*) IFC4_types[817]));defs.push_back(((entity*) IFC4_types[819]));defs.push_back(((entity*) IFC4_types[820]));defs.push_back(((entity*) IFC4_types[823]));defs.push_back(((entity*) IFC4_types[824]));defs.push_back(((entity*) IFC4_types[825]));defs.push_back(((entity*) IFC4_types[833]));defs.push_back(((entity*) IFC4_types[834]));defs.push_back(((entity*) IFC4_types[835]));defs.push_back(((entity*) IFC4_types[838]));defs.push_back(((entity*) IFC4_types[839]));defs.push_back(((entity*) IFC4_types[840]));defs.push_back(((entity*) IFC4_types[841]));
        ((entity*) IFC4_types[814])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[816]));defs.push_back(((entity*) IFC4_types[822]));
        ((entity*) IFC4_types[815])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[821]));
        ((entity*) IFC4_types[820])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(4);
        defs.push_back(((entity*) IFC4_types[829]));defs.push_back(((entity*) IFC4_types[830]));defs.push_back(((entity*) IFC4_types[831]));defs.push_back(((entity*) IFC4_types[832]));
        ((entity*) IFC4_types[828])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[842]));
        ((entity*) IFC4_types[841])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[843]));
        ((entity*) IFC4_types[842])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[845]));
        ((entity*) IFC4_types[167])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[858]));
        ((entity*) IFC4_types[857])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[891]));defs.push_back(((entity*) IFC4_types[996]));
        ((entity*) IFC4_types[846])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[892]));defs.push_back(((entity*) IFC4_types[1086]));
        ((entity*) IFC4_types[891])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[906]));defs.push_back(((entity*) IFC4_types[907]));
        ((entity*) IFC4_types[905])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[926]));
        ((entity*) IFC4_types[931])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[931]));defs.push_back(((entity*) IFC4_types[933]));
        ((entity*) IFC4_types[929])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[951]));defs.push_back(((entity*) IFC4_types[984]));
        ((entity*) IFC4_types[952])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[955]));defs.push_back(((entity*) IFC4_types[979]));
        ((entity*) IFC4_types[964])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[957]));defs.push_back(((entity*) IFC4_types[981]));defs.push_back(((entity*) IFC4_types[986]));
        ((entity*) IFC4_types[951])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[959]));defs.push_back(((entity*) IFC4_types[982]));defs.push_back(((entity*) IFC4_types[988]));
        ((entity*) IFC4_types[955])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[960]));defs.push_back(((entity*) IFC4_types[989]));
        ((entity*) IFC4_types[979])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[962]));
        ((entity*) IFC4_types[960])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[963]));defs.push_back(((entity*) IFC4_types[983]));defs.push_back(((entity*) IFC4_types[992]));
        ((entity*) IFC4_types[984])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[965]));
        ((entity*) IFC4_types[957])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[967]));
        ((entity*) IFC4_types[969])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[968]));defs.push_back(((entity*) IFC4_types[971]));
        ((entity*) IFC4_types[966])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(5);
        defs.push_back(((entity*) IFC4_types[970]));defs.push_back(((entity*) IFC4_types[972]));defs.push_back(((entity*) IFC4_types[973]));defs.push_back(((entity*) IFC4_types[975]));defs.push_back(((entity*) IFC4_types[978]));
        ((entity*) IFC4_types[977])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[974]));
        ((entity*) IFC4_types[973])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[976]));
        ((entity*) IFC4_types[975])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[977]));defs.push_back(((entity*) IFC4_types[1009]));
        ((entity*) IFC4_types[971])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[980]));
        ((entity*) IFC4_types[986])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[991]));
        ((entity*) IFC4_types[989])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[995]));
        ((entity*) IFC4_types[996])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[1006]));defs.push_back(((entity*) IFC4_types[1007]));
        ((entity*) IFC4_types[1022])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1015]));
        ((entity*) IFC4_types[1016])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1021]));
        ((entity*) IFC4_types[1020])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1039]));
        ((entity*) IFC4_types[1038])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1059]));
        ((entity*) IFC4_types[1058])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1062]));
        ((entity*) IFC4_types[695])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(3);
        defs.push_back(((entity*) IFC4_types[1107]));defs.push_back(((entity*) IFC4_types[1108]));defs.push_back(((entity*) IFC4_types[1109]));
        ((entity*) IFC4_types[1106])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1130]));
        ((entity*) IFC4_types[1128])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[1141]));defs.push_back(((entity*) IFC4_types[1142]));
        ((entity*) IFC4_types[1140])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(1);
        defs.push_back(((entity*) IFC4_types[1156]));
        ((entity*) IFC4_types[1151])->set_subtypes(defs);
    }
    {
        std::vector<const entity*> defs; defs.reserve(2);
        defs.push_back(((entity*) IFC4_types[1166]));defs.push_back(((entity*) IFC4_types[1168]));
        ((entity*) IFC4_types[1165])->set_subtypes(defs);
    }

    std::vector<const declaration*> declarations; declarations.reserve(1173);
    declarations.push_back(IFC4_types[0]);
    declarations.push_back(IFC4_types[1]);
    declarations.push_back(IFC4_types[2]);
    declarations.push_back(IFC4_types[3]);
    declarations.push_back(IFC4_types[4]);
    declarations.push_back(IFC4_types[5]);
    declarations.push_back(IFC4_types[6]);
    declarations.push_back(IFC4_types[7]);
    declarations.push_back(IFC4_types[8]);
    declarations.push_back(IFC4_types[9]);
    declarations.push_back(IFC4_types[10]);
    declarations.push_back(IFC4_types[11]);
    declarations.push_back(IFC4_types[12]);
    declarations.push_back(IFC4_types[13]);
    declarations.push_back(IFC4_types[14]);
    declarations.push_back(IFC4_types[15]);
    declarations.push_back(IFC4_types[16]);
    declarations.push_back(IFC4_types[17]);
    declarations.push_back(IFC4_types[18]);
    declarations.push_back(IFC4_types[19]);
    declarations.push_back(IFC4_types[20]);
    declarations.push_back(IFC4_types[21]);
    declarations.push_back(IFC4_types[22]);
    declarations.push_back(IFC4_types[23]);
    declarations.push_back(IFC4_types[24]);
    declarations.push_back(IFC4_types[25]);
    declarations.push_back(IFC4_types[26]);
    declarations.push_back(IFC4_types[27]);
    declarations.push_back(IFC4_types[28]);
    declarations.push_back(IFC4_types[29]);
    declarations.push_back(IFC4_types[30]);
    declarations.push_back(IFC4_types[31]);
    declarations.push_back(IFC4_types[32]);
    declarations.push_back(IFC4_types[33]);
    declarations.push_back(IFC4_types[34]);
    declarations.push_back(IFC4_types[35]);
    declarations.push_back(IFC4_types[36]);
    declarations.push_back(IFC4_types[37]);
    declarations.push_back(IFC4_types[38]);
    declarations.push_back(IFC4_types[39]);
    declarations.push_back(IFC4_types[40]);
    declarations.push_back(IFC4_types[41]);
    declarations.push_back(IFC4_types[42]);
    declarations.push_back(IFC4_types[43]);
    declarations.push_back(IFC4_types[44]);
    declarations.push_back(IFC4_types[45]);
    declarations.push_back(IFC4_types[46]);
    declarations.push_back(IFC4_types[47]);
    declarations.push_back(IFC4_types[48]);
    declarations.push_back(IFC4_types[49]);
    declarations.push_back(IFC4_types[50]);
    declarations.push_back(IFC4_types[51]);
    declarations.push_back(IFC4_types[52]);
    declarations.push_back(IFC4_types[53]);
    declarations.push_back(IFC4_types[54]);
    declarations.push_back(IFC4_types[55]);
    declarations.push_back(IFC4_types[56]);
    declarations.push_back(IFC4_types[57]);
    declarations.push_back(IFC4_types[58]);
    declarations.push_back(IFC4_types[59]);
    declarations.push_back(IFC4_types[60]);
    declarations.push_back(IFC4_types[61]);
    declarations.push_back(IFC4_types[62]);
    declarations.push_back(IFC4_types[63]);
    declarations.push_back(IFC4_types[64]);
    declarations.push_back(IFC4_types[65]);
    declarations.push_back(IFC4_types[66]);
    declarations.push_back(IFC4_types[67]);
    declarations.push_back(IFC4_types[68]);
    declarations.push_back(IFC4_types[69]);
    declarations.push_back(IFC4_types[70]);
    declarations.push_back(IFC4_types[71]);
    declarations.push_back(IFC4_types[72]);
    declarations.push_back(IFC4_types[73]);
    declarations.push_back(IFC4_types[74]);
    declarations.push_back(IFC4_types[75]);
    declarations.push_back(IFC4_types[76]);
    declarations.push_back(IFC4_types[77]);
    declarations.push_back(IFC4_types[78]);
    declarations.push_back(IFC4_types[79]);
    declarations.push_back(IFC4_types[80]);
    declarations.push_back(IFC4_types[81]);
    declarations.push_back(IFC4_types[82]);
    declarations.push_back(IFC4_types[83]);
    declarations.push_back(IFC4_types[84]);
    declarations.push_back(IFC4_types[85]);
    declarations.push_back(IFC4_types[86]);
    declarations.push_back(IFC4_types[87]);
    declarations.push_back(IFC4_types[88]);
    declarations.push_back(IFC4_types[89]);
    declarations.push_back(IFC4_types[90]);
    declarations.push_back(IFC4_types[91]);
    declarations.push_back(IFC4_types[92]);
    declarations.push_back(IFC4_types[93]);
    declarations.push_back(IFC4_types[94]);
    declarations.push_back(IFC4_types[95]);
    declarations.push_back(IFC4_types[96]);
    declarations.push_back(IFC4_types[97]);
    declarations.push_back(IFC4_types[98]);
    declarations.push_back(IFC4_types[99]);
    declarations.push_back(IFC4_types[100]);
    declarations.push_back(IFC4_types[101]);
    declarations.push_back(IFC4_types[102]);
    declarations.push_back(IFC4_types[103]);
    declarations.push_back(IFC4_types[104]);
    declarations.push_back(IFC4_types[105]);
    declarations.push_back(IFC4_types[106]);
    declarations.push_back(IFC4_types[107]);
    declarations.push_back(IFC4_types[108]);
    declarations.push_back(IFC4_types[109]);
    declarations.push_back(IFC4_types[110]);
    declarations.push_back(IFC4_types[111]);
    declarations.push_back(IFC4_types[112]);
    declarations.push_back(IFC4_types[113]);
    declarations.push_back(IFC4_types[114]);
    declarations.push_back(IFC4_types[115]);
    declarations.push_back(IFC4_types[116]);
    declarations.push_back(IFC4_types[117]);
    declarations.push_back(IFC4_types[118]);
    declarations.push_back(IFC4_types[119]);
    declarations.push_back(IFC4_types[120]);
    declarations.push_back(IFC4_types[121]);
    declarations.push_back(IFC4_types[122]);
    declarations.push_back(IFC4_types[123]);
    declarations.push_back(IFC4_types[124]);
    declarations.push_back(IFC4_types[125]);
    declarations.push_back(IFC4_types[126]);
    declarations.push_back(IFC4_types[127]);
    declarations.push_back(IFC4_types[128]);
    declarations.push_back(IFC4_types[129]);
    declarations.push_back(IFC4_types[130]);
    declarations.push_back(IFC4_types[131]);
    declarations.push_back(IFC4_types[132]);
    declarations.push_back(IFC4_types[133]);
    declarations.push_back(IFC4_types[134]);
    declarations.push_back(IFC4_types[135]);
    declarations.push_back(IFC4_types[136]);
    declarations.push_back(IFC4_types[137]);
    declarations.push_back(IFC4_types[138]);
    declarations.push_back(IFC4_types[139]);
    declarations.push_back(IFC4_types[140]);
    declarations.push_back(IFC4_types[141]);
    declarations.push_back(IFC4_types[142]);
    declarations.push_back(IFC4_types[143]);
    declarations.push_back(IFC4_types[144]);
    declarations.push_back(IFC4_types[145]);
    declarations.push_back(IFC4_types[146]);
    declarations.push_back(IFC4_types[147]);
    declarations.push_back(IFC4_types[148]);
    declarations.push_back(IFC4_types[149]);
    declarations.push_back(IFC4_types[150]);
    declarations.push_back(IFC4_types[151]);
    declarations.push_back(IFC4_types[152]);
    declarations.push_back(IFC4_types[153]);
    declarations.push_back(IFC4_types[154]);
    declarations.push_back(IFC4_types[155]);
    declarations.push_back(IFC4_types[156]);
    declarations.push_back(IFC4_types[157]);
    declarations.push_back(IFC4_types[158]);
    declarations.push_back(IFC4_types[159]);
    declarations.push_back(IFC4_types[160]);
    declarations.push_back(IFC4_types[161]);
    declarations.push_back(IFC4_types[162]);
    declarations.push_back(IFC4_types[163]);
    declarations.push_back(IFC4_types[164]);
    declarations.push_back(IFC4_types[165]);
    declarations.push_back(IFC4_types[166]);
    declarations.push_back(IFC4_types[167]);
    declarations.push_back(IFC4_types[168]);
    declarations.push_back(IFC4_types[169]);
    declarations.push_back(IFC4_types[170]);
    declarations.push_back(IFC4_types[171]);
    declarations.push_back(IFC4_types[172]);
    declarations.push_back(IFC4_types[173]);
    declarations.push_back(IFC4_types[174]);
    declarations.push_back(IFC4_types[175]);
    declarations.push_back(IFC4_types[176]);
    declarations.push_back(IFC4_types[177]);
    declarations.push_back(IFC4_types[178]);
    declarations.push_back(IFC4_types[179]);
    declarations.push_back(IFC4_types[180]);
    declarations.push_back(IFC4_types[181]);
    declarations.push_back(IFC4_types[182]);
    declarations.push_back(IFC4_types[183]);
    declarations.push_back(IFC4_types[184]);
    declarations.push_back(IFC4_types[185]);
    declarations.push_back(IFC4_types[186]);
    declarations.push_back(IFC4_types[187]);
    declarations.push_back(IFC4_types[188]);
    declarations.push_back(IFC4_types[189]);
    declarations.push_back(IFC4_types[190]);
    declarations.push_back(IFC4_types[191]);
    declarations.push_back(IFC4_types[192]);
    declarations.push_back(IFC4_types[193]);
    declarations.push_back(IFC4_types[194]);
    declarations.push_back(IFC4_types[195]);
    declarations.push_back(IFC4_types[196]);
    declarations.push_back(IFC4_types[197]);
    declarations.push_back(IFC4_types[198]);
    declarations.push_back(IFC4_types[199]);
    declarations.push_back(IFC4_types[200]);
    declarations.push_back(IFC4_types[201]);
    declarations.push_back(IFC4_types[202]);
    declarations.push_back(IFC4_types[203]);
    declarations.push_back(IFC4_types[204]);
    declarations.push_back(IFC4_types[205]);
    declarations.push_back(IFC4_types[206]);
    declarations.push_back(IFC4_types[207]);
    declarations.push_back(IFC4_types[208]);
    declarations.push_back(IFC4_types[209]);
    declarations.push_back(IFC4_types[210]);
    declarations.push_back(IFC4_types[211]);
    declarations.push_back(IFC4_types[212]);
    declarations.push_back(IFC4_types[213]);
    declarations.push_back(IFC4_types[214]);
    declarations.push_back(IFC4_types[215]);
    declarations.push_back(IFC4_types[216]);
    declarations.push_back(IFC4_types[217]);
    declarations.push_back(IFC4_types[218]);
    declarations.push_back(IFC4_types[219]);
    declarations.push_back(IFC4_types[220]);
    declarations.push_back(IFC4_types[221]);
    declarations.push_back(IFC4_types[222]);
    declarations.push_back(IFC4_types[223]);
    declarations.push_back(IFC4_types[224]);
    declarations.push_back(IFC4_types[225]);
    declarations.push_back(IFC4_types[226]);
    declarations.push_back(IFC4_types[227]);
    declarations.push_back(IFC4_types[228]);
    declarations.push_back(IFC4_types[229]);
    declarations.push_back(IFC4_types[230]);
    declarations.push_back(IFC4_types[231]);
    declarations.push_back(IFC4_types[232]);
    declarations.push_back(IFC4_types[233]);
    declarations.push_back(IFC4_types[234]);
    declarations.push_back(IFC4_types[235]);
    declarations.push_back(IFC4_types[236]);
    declarations.push_back(IFC4_types[237]);
    declarations.push_back(IFC4_types[238]);
    declarations.push_back(IFC4_types[239]);
    declarations.push_back(IFC4_types[240]);
    declarations.push_back(IFC4_types[241]);
    declarations.push_back(IFC4_types[242]);
    declarations.push_back(IFC4_types[243]);
    declarations.push_back(IFC4_types[244]);
    declarations.push_back(IFC4_types[245]);
    declarations.push_back(IFC4_types[246]);
    declarations.push_back(IFC4_types[247]);
    declarations.push_back(IFC4_types[248]);
    declarations.push_back(IFC4_types[249]);
    declarations.push_back(IFC4_types[250]);
    declarations.push_back(IFC4_types[251]);
    declarations.push_back(IFC4_types[252]);
    declarations.push_back(IFC4_types[253]);
    declarations.push_back(IFC4_types[254]);
    declarations.push_back(IFC4_types[255]);
    declarations.push_back(IFC4_types[256]);
    declarations.push_back(IFC4_types[257]);
    declarations.push_back(IFC4_types[258]);
    declarations.push_back(IFC4_types[259]);
    declarations.push_back(IFC4_types[260]);
    declarations.push_back(IFC4_types[261]);
    declarations.push_back(IFC4_types[262]);
    declarations.push_back(IFC4_types[263]);
    declarations.push_back(IFC4_types[264]);
    declarations.push_back(IFC4_types[265]);
    declarations.push_back(IFC4_types[266]);
    declarations.push_back(IFC4_types[267]);
    declarations.push_back(IFC4_types[268]);
    declarations.push_back(IFC4_types[269]);
    declarations.push_back(IFC4_types[270]);
    declarations.push_back(IFC4_types[271]);
    declarations.push_back(IFC4_types[272]);
    declarations.push_back(IFC4_types[273]);
    declarations.push_back(IFC4_types[274]);
    declarations.push_back(IFC4_types[275]);
    declarations.push_back(IFC4_types[276]);
    declarations.push_back(IFC4_types[277]);
    declarations.push_back(IFC4_types[278]);
    declarations.push_back(IFC4_types[279]);
    declarations.push_back(IFC4_types[280]);
    declarations.push_back(IFC4_types[281]);
    declarations.push_back(IFC4_types[282]);
    declarations.push_back(IFC4_types[283]);
    declarations.push_back(IFC4_types[284]);
    declarations.push_back(IFC4_types[285]);
    declarations.push_back(IFC4_types[286]);
    declarations.push_back(IFC4_types[287]);
    declarations.push_back(IFC4_types[288]);
    declarations.push_back(IFC4_types[289]);
    declarations.push_back(IFC4_types[290]);
    declarations.push_back(IFC4_types[291]);
    declarations.push_back(IFC4_types[292]);
    declarations.push_back(IFC4_types[293]);
    declarations.push_back(IFC4_types[294]);
    declarations.push_back(IFC4_types[295]);
    declarations.push_back(IFC4_types[296]);
    declarations.push_back(IFC4_types[297]);
    declarations.push_back(IFC4_types[298]);
    declarations.push_back(IFC4_types[299]);
    declarations.push_back(IFC4_types[300]);
    declarations.push_back(IFC4_types[301]);
    declarations.push_back(IFC4_types[302]);
    declarations.push_back(IFC4_types[303]);
    declarations.push_back(IFC4_types[304]);
    declarations.push_back(IFC4_types[305]);
    declarations.push_back(IFC4_types[306]);
    declarations.push_back(IFC4_types[307]);
    declarations.push_back(IFC4_types[308]);
    declarations.push_back(IFC4_types[309]);
    declarations.push_back(IFC4_types[310]);
    declarations.push_back(IFC4_types[311]);
    declarations.push_back(IFC4_types[312]);
    declarations.push_back(IFC4_types[313]);
    declarations.push_back(IFC4_types[314]);
    declarations.push_back(IFC4_types[315]);
    declarations.push_back(IFC4_types[316]);
    declarations.push_back(IFC4_types[317]);
    declarations.push_back(IFC4_types[318]);
    declarations.push_back(IFC4_types[319]);
    declarations.push_back(IFC4_types[320]);
    declarations.push_back(IFC4_types[321]);
    declarations.push_back(IFC4_types[322]);
    declarations.push_back(IFC4_types[323]);
    declarations.push_back(IFC4_types[324]);
    declarations.push_back(IFC4_types[325]);
    declarations.push_back(IFC4_types[326]);
    declarations.push_back(IFC4_types[327]);
    declarations.push_back(IFC4_types[328]);
    declarations.push_back(IFC4_types[329]);
    declarations.push_back(IFC4_types[330]);
    declarations.push_back(IFC4_types[331]);
    declarations.push_back(IFC4_types[332]);
    declarations.push_back(IFC4_types[333]);
    declarations.push_back(IFC4_types[334]);
    declarations.push_back(IFC4_types[335]);
    declarations.push_back(IFC4_types[336]);
    declarations.push_back(IFC4_types[337]);
    declarations.push_back(IFC4_types[338]);
    declarations.push_back(IFC4_types[339]);
    declarations.push_back(IFC4_types[340]);
    declarations.push_back(IFC4_types[341]);
    declarations.push_back(IFC4_types[342]);
    declarations.push_back(IFC4_types[343]);
    declarations.push_back(IFC4_types[344]);
    declarations.push_back(IFC4_types[345]);
    declarations.push_back(IFC4_types[346]);
    declarations.push_back(IFC4_types[347]);
    declarations.push_back(IFC4_types[348]);
    declarations.push_back(IFC4_types[349]);
    declarations.push_back(IFC4_types[350]);
    declarations.push_back(IFC4_types[351]);
    declarations.push_back(IFC4_types[352]);
    declarations.push_back(IFC4_types[353]);
    declarations.push_back(IFC4_types[354]);
    declarations.push_back(IFC4_types[355]);
    declarations.push_back(IFC4_types[356]);
    declarations.push_back(IFC4_types[357]);
    declarations.push_back(IFC4_types[358]);
    declarations.push_back(IFC4_types[359]);
    declarations.push_back(IFC4_types[360]);
    declarations.push_back(IFC4_types[361]);
    declarations.push_back(IFC4_types[362]);
    declarations.push_back(IFC4_types[363]);
    declarations.push_back(IFC4_types[364]);
    declarations.push_back(IFC4_types[365]);
    declarations.push_back(IFC4_types[366]);
    declarations.push_back(IFC4_types[367]);
    declarations.push_back(IFC4_types[368]);
    declarations.push_back(IFC4_types[369]);
    declarations.push_back(IFC4_types[370]);
    declarations.push_back(IFC4_types[371]);
    declarations.push_back(IFC4_types[372]);
    declarations.push_back(IFC4_types[373]);
    declarations.push_back(IFC4_types[374]);
    declarations.push_back(IFC4_types[375]);
    declarations.push_back(IFC4_types[376]);
    declarations.push_back(IFC4_types[377]);
    declarations.push_back(IFC4_types[378]);
    declarations.push_back(IFC4_types[379]);
    declarations.push_back(IFC4_types[380]);
    declarations.push_back(IFC4_types[381]);
    declarations.push_back(IFC4_types[382]);
    declarations.push_back(IFC4_types[383]);
    declarations.push_back(IFC4_types[384]);
    declarations.push_back(IFC4_types[385]);
    declarations.push_back(IFC4_types[386]);
    declarations.push_back(IFC4_types[387]);
    declarations.push_back(IFC4_types[388]);
    declarations.push_back(IFC4_types[389]);
    declarations.push_back(IFC4_types[390]);
    declarations.push_back(IFC4_types[391]);
    declarations.push_back(IFC4_types[392]);
    declarations.push_back(IFC4_types[393]);
    declarations.push_back(IFC4_types[394]);
    declarations.push_back(IFC4_types[395]);
    declarations.push_back(IFC4_types[396]);
    declarations.push_back(IFC4_types[397]);
    declarations.push_back(IFC4_types[398]);
    declarations.push_back(IFC4_types[399]);
    declarations.push_back(IFC4_types[400]);
    declarations.push_back(IFC4_types[401]);
    declarations.push_back(IFC4_types[402]);
    declarations.push_back(IFC4_types[403]);
    declarations.push_back(IFC4_types[404]);
    declarations.push_back(IFC4_types[405]);
    declarations.push_back(IFC4_types[406]);
    declarations.push_back(IFC4_types[407]);
    declarations.push_back(IFC4_types[408]);
    declarations.push_back(IFC4_types[409]);
    declarations.push_back(IFC4_types[410]);
    declarations.push_back(IFC4_types[411]);
    declarations.push_back(IFC4_types[412]);
    declarations.push_back(IFC4_types[413]);
    declarations.push_back(IFC4_types[414]);
    declarations.push_back(IFC4_types[415]);
    declarations.push_back(IFC4_types[416]);
    declarations.push_back(IFC4_types[417]);
    declarations.push_back(IFC4_types[418]);
    declarations.push_back(IFC4_types[419]);
    declarations.push_back(IFC4_types[420]);
    declarations.push_back(IFC4_types[421]);
    declarations.push_back(IFC4_types[422]);
    declarations.push_back(IFC4_types[423]);
    declarations.push_back(IFC4_types[424]);
    declarations.push_back(IFC4_types[425]);
    declarations.push_back(IFC4_types[426]);
    declarations.push_back(IFC4_types[427]);
    declarations.push_back(IFC4_types[428]);
    declarations.push_back(IFC4_types[429]);
    declarations.push_back(IFC4_types[430]);
    declarations.push_back(IFC4_types[431]);
    declarations.push_back(IFC4_types[432]);
    declarations.push_back(IFC4_types[433]);
    declarations.push_back(IFC4_types[434]);
    declarations.push_back(IFC4_types[435]);
    declarations.push_back(IFC4_types[436]);
    declarations.push_back(IFC4_types[437]);
    declarations.push_back(IFC4_types[438]);
    declarations.push_back(IFC4_types[439]);
    declarations.push_back(IFC4_types[440]);
    declarations.push_back(IFC4_types[441]);
    declarations.push_back(IFC4_types[442]);
    declarations.push_back(IFC4_types[443]);
    declarations.push_back(IFC4_types[444]);
    declarations.push_back(IFC4_types[445]);
    declarations.push_back(IFC4_types[446]);
    declarations.push_back(IFC4_types[447]);
    declarations.push_back(IFC4_types[448]);
    declarations.push_back(IFC4_types[449]);
    declarations.push_back(IFC4_types[450]);
    declarations.push_back(IFC4_types[451]);
    declarations.push_back(IFC4_types[452]);
    declarations.push_back(IFC4_types[453]);
    declarations.push_back(IFC4_types[454]);
    declarations.push_back(IFC4_types[455]);
    declarations.push_back(IFC4_types[456]);
    declarations.push_back(IFC4_types[457]);
    declarations.push_back(IFC4_types[458]);
    declarations.push_back(IFC4_types[459]);
    declarations.push_back(IFC4_types[460]);
    declarations.push_back(IFC4_types[461]);
    declarations.push_back(IFC4_types[462]);
    declarations.push_back(IFC4_types[463]);
    declarations.push_back(IFC4_types[464]);
    declarations.push_back(IFC4_types[465]);
    declarations.push_back(IFC4_types[466]);
    declarations.push_back(IFC4_types[467]);
    declarations.push_back(IFC4_types[468]);
    declarations.push_back(IFC4_types[469]);
    declarations.push_back(IFC4_types[470]);
    declarations.push_back(IFC4_types[471]);
    declarations.push_back(IFC4_types[472]);
    declarations.push_back(IFC4_types[473]);
    declarations.push_back(IFC4_types[474]);
    declarations.push_back(IFC4_types[475]);
    declarations.push_back(IFC4_types[476]);
    declarations.push_back(IFC4_types[477]);
    declarations.push_back(IFC4_types[478]);
    declarations.push_back(IFC4_types[479]);
    declarations.push_back(IFC4_types[480]);
    declarations.push_back(IFC4_types[481]);
    declarations.push_back(IFC4_types[482]);
    declarations.push_back(IFC4_types[483]);
    declarations.push_back(IFC4_types[484]);
    declarations.push_back(IFC4_types[485]);
    declarations.push_back(IFC4_types[486]);
    declarations.push_back(IFC4_types[487]);
    declarations.push_back(IFC4_types[488]);
    declarations.push_back(IFC4_types[489]);
    declarations.push_back(IFC4_types[490]);
    declarations.push_back(IFC4_types[491]);
    declarations.push_back(IFC4_types[492]);
    declarations.push_back(IFC4_types[493]);
    declarations.push_back(IFC4_types[494]);
    declarations.push_back(IFC4_types[495]);
    declarations.push_back(IFC4_types[496]);
    declarations.push_back(IFC4_types[497]);
    declarations.push_back(IFC4_types[498]);
    declarations.push_back(IFC4_types[499]);
    declarations.push_back(IFC4_types[500]);
    declarations.push_back(IFC4_types[501]);
    declarations.push_back(IFC4_types[502]);
    declarations.push_back(IFC4_types[503]);
    declarations.push_back(IFC4_types[504]);
    declarations.push_back(IFC4_types[505]);
    declarations.push_back(IFC4_types[506]);
    declarations.push_back(IFC4_types[507]);
    declarations.push_back(IFC4_types[508]);
    declarations.push_back(IFC4_types[509]);
    declarations.push_back(IFC4_types[510]);
    declarations.push_back(IFC4_types[511]);
    declarations.push_back(IFC4_types[512]);
    declarations.push_back(IFC4_types[513]);
    declarations.push_back(IFC4_types[514]);
    declarations.push_back(IFC4_types[515]);
    declarations.push_back(IFC4_types[516]);
    declarations.push_back(IFC4_types[517]);
    declarations.push_back(IFC4_types[518]);
    declarations.push_back(IFC4_types[519]);
    declarations.push_back(IFC4_types[520]);
    declarations.push_back(IFC4_types[521]);
    declarations.push_back(IFC4_types[522]);
    declarations.push_back(IFC4_types[523]);
    declarations.push_back(IFC4_types[524]);
    declarations.push_back(IFC4_types[525]);
    declarations.push_back(IFC4_types[526]);
    declarations.push_back(IFC4_types[527]);
    declarations.push_back(IFC4_types[528]);
    declarations.push_back(IFC4_types[529]);
    declarations.push_back(IFC4_types[530]);
    declarations.push_back(IFC4_types[531]);
    declarations.push_back(IFC4_types[532]);
    declarations.push_back(IFC4_types[533]);
    declarations.push_back(IFC4_types[534]);
    declarations.push_back(IFC4_types[535]);
    declarations.push_back(IFC4_types[536]);
    declarations.push_back(IFC4_types[537]);
    declarations.push_back(IFC4_types[538]);
    declarations.push_back(IFC4_types[539]);
    declarations.push_back(IFC4_types[540]);
    declarations.push_back(IFC4_types[541]);
    declarations.push_back(IFC4_types[542]);
    declarations.push_back(IFC4_types[543]);
    declarations.push_back(IFC4_types[544]);
    declarations.push_back(IFC4_types[545]);
    declarations.push_back(IFC4_types[546]);
    declarations.push_back(IFC4_types[547]);
    declarations.push_back(IFC4_types[548]);
    declarations.push_back(IFC4_types[549]);
    declarations.push_back(IFC4_types[550]);
    declarations.push_back(IFC4_types[551]);
    declarations.push_back(IFC4_types[552]);
    declarations.push_back(IFC4_types[553]);
    declarations.push_back(IFC4_types[554]);
    declarations.push_back(IFC4_types[555]);
    declarations.push_back(IFC4_types[556]);
    declarations.push_back(IFC4_types[557]);
    declarations.push_back(IFC4_types[558]);
    declarations.push_back(IFC4_types[559]);
    declarations.push_back(IFC4_types[560]);
    declarations.push_back(IFC4_types[561]);
    declarations.push_back(IFC4_types[562]);
    declarations.push_back(IFC4_types[563]);
    declarations.push_back(IFC4_types[564]);
    declarations.push_back(IFC4_types[565]);
    declarations.push_back(IFC4_types[566]);
    declarations.push_back(IFC4_types[567]);
    declarations.push_back(IFC4_types[568]);
    declarations.push_back(IFC4_types[569]);
    declarations.push_back(IFC4_types[570]);
    declarations.push_back(IFC4_types[571]);
    declarations.push_back(IFC4_types[572]);
    declarations.push_back(IFC4_types[573]);
    declarations.push_back(IFC4_types[574]);
    declarations.push_back(IFC4_types[575]);
    declarations.push_back(IFC4_types[576]);
    declarations.push_back(IFC4_types[577]);
    declarations.push_back(IFC4_types[578]);
    declarations.push_back(IFC4_types[579]);
    declarations.push_back(IFC4_types[580]);
    declarations.push_back(IFC4_types[581]);
    declarations.push_back(IFC4_types[582]);
    declarations.push_back(IFC4_types[583]);
    declarations.push_back(IFC4_types[584]);
    declarations.push_back(IFC4_types[585]);
    declarations.push_back(IFC4_types[586]);
    declarations.push_back(IFC4_types[587]);
    declarations.push_back(IFC4_types[588]);
    declarations.push_back(IFC4_types[589]);
    declarations.push_back(IFC4_types[590]);
    declarations.push_back(IFC4_types[591]);
    declarations.push_back(IFC4_types[592]);
    declarations.push_back(IFC4_types[593]);
    declarations.push_back(IFC4_types[594]);
    declarations.push_back(IFC4_types[595]);
    declarations.push_back(IFC4_types[596]);
    declarations.push_back(IFC4_types[597]);
    declarations.push_back(IFC4_types[598]);
    declarations.push_back(IFC4_types[599]);
    declarations.push_back(IFC4_types[600]);
    declarations.push_back(IFC4_types[601]);
    declarations.push_back(IFC4_types[602]);
    declarations.push_back(IFC4_types[603]);
    declarations.push_back(IFC4_types[604]);
    declarations.push_back(IFC4_types[605]);
    declarations.push_back(IFC4_types[606]);
    declarations.push_back(IFC4_types[607]);
    declarations.push_back(IFC4_types[608]);
    declarations.push_back(IFC4_types[609]);
    declarations.push_back(IFC4_types[610]);
    declarations.push_back(IFC4_types[611]);
    declarations.push_back(IFC4_types[612]);
    declarations.push_back(IFC4_types[613]);
    declarations.push_back(IFC4_types[614]);
    declarations.push_back(IFC4_types[615]);
    declarations.push_back(IFC4_types[616]);
    declarations.push_back(IFC4_types[617]);
    declarations.push_back(IFC4_types[618]);
    declarations.push_back(IFC4_types[619]);
    declarations.push_back(IFC4_types[620]);
    declarations.push_back(IFC4_types[621]);
    declarations.push_back(IFC4_types[622]);
    declarations.push_back(IFC4_types[623]);
    declarations.push_back(IFC4_types[624]);
    declarations.push_back(IFC4_types[625]);
    declarations.push_back(IFC4_types[626]);
    declarations.push_back(IFC4_types[627]);
    declarations.push_back(IFC4_types[628]);
    declarations.push_back(IFC4_types[629]);
    declarations.push_back(IFC4_types[630]);
    declarations.push_back(IFC4_types[631]);
    declarations.push_back(IFC4_types[632]);
    declarations.push_back(IFC4_types[633]);
    declarations.push_back(IFC4_types[634]);
    declarations.push_back(IFC4_types[635]);
    declarations.push_back(IFC4_types[636]);
    declarations.push_back(IFC4_types[637]);
    declarations.push_back(IFC4_types[638]);
    declarations.push_back(IFC4_types[639]);
    declarations.push_back(IFC4_types[640]);
    declarations.push_back(IFC4_types[641]);
    declarations.push_back(IFC4_types[642]);
    declarations.push_back(IFC4_types[643]);
    declarations.push_back(IFC4_types[644]);
    declarations.push_back(IFC4_types[645]);
    declarations.push_back(IFC4_types[646]);
    declarations.push_back(IFC4_types[647]);
    declarations.push_back(IFC4_types[648]);
    declarations.push_back(IFC4_types[649]);
    declarations.push_back(IFC4_types[650]);
    declarations.push_back(IFC4_types[651]);
    declarations.push_back(IFC4_types[652]);
    declarations.push_back(IFC4_types[653]);
    declarations.push_back(IFC4_types[654]);
    declarations.push_back(IFC4_types[655]);
    declarations.push_back(IFC4_types[656]);
    declarations.push_back(IFC4_types[657]);
    declarations.push_back(IFC4_types[658]);
    declarations.push_back(IFC4_types[659]);
    declarations.push_back(IFC4_types[660]);
    declarations.push_back(IFC4_types[661]);
    declarations.push_back(IFC4_types[662]);
    declarations.push_back(IFC4_types[663]);
    declarations.push_back(IFC4_types[664]);
    declarations.push_back(IFC4_types[665]);
    declarations.push_back(IFC4_types[666]);
    declarations.push_back(IFC4_types[667]);
    declarations.push_back(IFC4_types[668]);
    declarations.push_back(IFC4_types[669]);
    declarations.push_back(IFC4_types[670]);
    declarations.push_back(IFC4_types[671]);
    declarations.push_back(IFC4_types[672]);
    declarations.push_back(IFC4_types[673]);
    declarations.push_back(IFC4_types[674]);
    declarations.push_back(IFC4_types[675]);
    declarations.push_back(IFC4_types[676]);
    declarations.push_back(IFC4_types[677]);
    declarations.push_back(IFC4_types[678]);
    declarations.push_back(IFC4_types[679]);
    declarations.push_back(IFC4_types[680]);
    declarations.push_back(IFC4_types[681]);
    declarations.push_back(IFC4_types[682]);
    declarations.push_back(IFC4_types[683]);
    declarations.push_back(IFC4_types[684]);
    declarations.push_back(IFC4_types[685]);
    declarations.push_back(IFC4_types[686]);
    declarations.push_back(IFC4_types[687]);
    declarations.push_back(IFC4_types[688]);
    declarations.push_back(IFC4_types[689]);
    declarations.push_back(IFC4_types[690]);
    declarations.push_back(IFC4_types[691]);
    declarations.push_back(IFC4_types[692]);
    declarations.push_back(IFC4_types[693]);
    declarations.push_back(IFC4_types[694]);
    declarations.push_back(IFC4_types[695]);
    declarations.push_back(IFC4_types[696]);
    declarations.push_back(IFC4_types[697]);
    declarations.push_back(IFC4_types[698]);
    declarations.push_back(IFC4_types[699]);
    declarations.push_back(IFC4_types[700]);
    declarations.push_back(IFC4_types[701]);
    declarations.push_back(IFC4_types[702]);
    declarations.push_back(IFC4_types[703]);
    declarations.push_back(IFC4_types[704]);
    declarations.push_back(IFC4_types[705]);
    declarations.push_back(IFC4_types[706]);
    declarations.push_back(IFC4_types[707]);
    declarations.push_back(IFC4_types[708]);
    declarations.push_back(IFC4_types[709]);
    declarations.push_back(IFC4_types[710]);
    declarations.push_back(IFC4_types[711]);
    declarations.push_back(IFC4_types[712]);
    declarations.push_back(IFC4_types[713]);
    declarations.push_back(IFC4_types[714]);
    declarations.push_back(IFC4_types[715]);
    declarations.push_back(IFC4_types[716]);
    declarations.push_back(IFC4_types[717]);
    declarations.push_back(IFC4_types[718]);
    declarations.push_back(IFC4_types[719]);
    declarations.push_back(IFC4_types[720]);
    declarations.push_back(IFC4_types[721]);
    declarations.push_back(IFC4_types[722]);
    declarations.push_back(IFC4_types[723]);
    declarations.push_back(IFC4_types[724]);
    declarations.push_back(IFC4_types[725]);
    declarations.push_back(IFC4_types[726]);
    declarations.push_back(IFC4_types[727]);
    declarations.push_back(IFC4_types[728]);
    declarations.push_back(IFC4_types[729]);
    declarations.push_back(IFC4_types[730]);
    declarations.push_back(IFC4_types[731]);
    declarations.push_back(IFC4_types[732]);
    declarations.push_back(IFC4_types[733]);
    declarations.push_back(IFC4_types[734]);
    declarations.push_back(IFC4_types[735]);
    declarations.push_back(IFC4_types[736]);
    declarations.push_back(IFC4_types[737]);
    declarations.push_back(IFC4_types[738]);
    declarations.push_back(IFC4_types[739]);
    declarations.push_back(IFC4_types[740]);
    declarations.push_back(IFC4_types[741]);
    declarations.push_back(IFC4_types[742]);
    declarations.push_back(IFC4_types[743]);
    declarations.push_back(IFC4_types[744]);
    declarations.push_back(IFC4_types[745]);
    declarations.push_back(IFC4_types[746]);
    declarations.push_back(IFC4_types[747]);
    declarations.push_back(IFC4_types[748]);
    declarations.push_back(IFC4_types[749]);
    declarations.push_back(IFC4_types[750]);
    declarations.push_back(IFC4_types[751]);
    declarations.push_back(IFC4_types[752]);
    declarations.push_back(IFC4_types[753]);
    declarations.push_back(IFC4_types[754]);
    declarations.push_back(IFC4_types[755]);
    declarations.push_back(IFC4_types[756]);
    declarations.push_back(IFC4_types[757]);
    declarations.push_back(IFC4_types[758]);
    declarations.push_back(IFC4_types[759]);
    declarations.push_back(IFC4_types[760]);
    declarations.push_back(IFC4_types[761]);
    declarations.push_back(IFC4_types[762]);
    declarations.push_back(IFC4_types[763]);
    declarations.push_back(IFC4_types[764]);
    declarations.push_back(IFC4_types[765]);
    declarations.push_back(IFC4_types[766]);
    declarations.push_back(IFC4_types[767]);
    declarations.push_back(IFC4_types[768]);
    declarations.push_back(IFC4_types[769]);
    declarations.push_back(IFC4_types[770]);
    declarations.push_back(IFC4_types[771]);
    declarations.push_back(IFC4_types[772]);
    declarations.push_back(IFC4_types[773]);
    declarations.push_back(IFC4_types[774]);
    declarations.push_back(IFC4_types[775]);
    declarations.push_back(IFC4_types[776]);
    declarations.push_back(IFC4_types[777]);
    declarations.push_back(IFC4_types[778]);
    declarations.push_back(IFC4_types[779]);
    declarations.push_back(IFC4_types[780]);
    declarations.push_back(IFC4_types[781]);
    declarations.push_back(IFC4_types[782]);
    declarations.push_back(IFC4_types[783]);
    declarations.push_back(IFC4_types[784]);
    declarations.push_back(IFC4_types[785]);
    declarations.push_back(IFC4_types[786]);
    declarations.push_back(IFC4_types[787]);
    declarations.push_back(IFC4_types[788]);
    declarations.push_back(IFC4_types[789]);
    declarations.push_back(IFC4_types[790]);
    declarations.push_back(IFC4_types[791]);
    declarations.push_back(IFC4_types[792]);
    declarations.push_back(IFC4_types[793]);
    declarations.push_back(IFC4_types[794]);
    declarations.push_back(IFC4_types[795]);
    declarations.push_back(IFC4_types[796]);
    declarations.push_back(IFC4_types[797]);
    declarations.push_back(IFC4_types[798]);
    declarations.push_back(IFC4_types[799]);
    declarations.push_back(IFC4_types[800]);
    declarations.push_back(IFC4_types[801]);
    declarations.push_back(IFC4_types[802]);
    declarations.push_back(IFC4_types[803]);
    declarations.push_back(IFC4_types[804]);
    declarations.push_back(IFC4_types[805]);
    declarations.push_back(IFC4_types[806]);
    declarations.push_back(IFC4_types[807]);
    declarations.push_back(IFC4_types[808]);
    declarations.push_back(IFC4_types[809]);
    declarations.push_back(IFC4_types[810]);
    declarations.push_back(IFC4_types[811]);
    declarations.push_back(IFC4_types[812]);
    declarations.push_back(IFC4_types[813]);
    declarations.push_back(IFC4_types[814]);
    declarations.push_back(IFC4_types[815]);
    declarations.push_back(IFC4_types[816]);
    declarations.push_back(IFC4_types[817]);
    declarations.push_back(IFC4_types[818]);
    declarations.push_back(IFC4_types[819]);
    declarations.push_back(IFC4_types[820]);
    declarations.push_back(IFC4_types[821]);
    declarations.push_back(IFC4_types[822]);
    declarations.push_back(IFC4_types[823]);
    declarations.push_back(IFC4_types[824]);
    declarations.push_back(IFC4_types[825]);
    declarations.push_back(IFC4_types[826]);
    declarations.push_back(IFC4_types[827]);
    declarations.push_back(IFC4_types[828]);
    declarations.push_back(IFC4_types[829]);
    declarations.push_back(IFC4_types[830]);
    declarations.push_back(IFC4_types[831]);
    declarations.push_back(IFC4_types[832]);
    declarations.push_back(IFC4_types[833]);
    declarations.push_back(IFC4_types[834]);
    declarations.push_back(IFC4_types[835]);
    declarations.push_back(IFC4_types[836]);
    declarations.push_back(IFC4_types[837]);
    declarations.push_back(IFC4_types[838]);
    declarations.push_back(IFC4_types[839]);
    declarations.push_back(IFC4_types[840]);
    declarations.push_back(IFC4_types[841]);
    declarations.push_back(IFC4_types[842]);
    declarations.push_back(IFC4_types[843]);
    declarations.push_back(IFC4_types[844]);
    declarations.push_back(IFC4_types[845]);
    declarations.push_back(IFC4_types[846]);
    declarations.push_back(IFC4_types[847]);
    declarations.push_back(IFC4_types[848]);
    declarations.push_back(IFC4_types[849]);
    declarations.push_back(IFC4_types[850]);
    declarations.push_back(IFC4_types[851]);
    declarations.push_back(IFC4_types[852]);
    declarations.push_back(IFC4_types[853]);
    declarations.push_back(IFC4_types[854]);
    declarations.push_back(IFC4_types[855]);
    declarations.push_back(IFC4_types[856]);
    declarations.push_back(IFC4_types[857]);
    declarations.push_back(IFC4_types[858]);
    declarations.push_back(IFC4_types[859]);
    declarations.push_back(IFC4_types[860]);
    declarations.push_back(IFC4_types[861]);
    declarations.push_back(IFC4_types[862]);
    declarations.push_back(IFC4_types[863]);
    declarations.push_back(IFC4_types[864]);
    declarations.push_back(IFC4_types[865]);
    declarations.push_back(IFC4_types[866]);
    declarations.push_back(IFC4_types[867]);
    declarations.push_back(IFC4_types[868]);
    declarations.push_back(IFC4_types[869]);
    declarations.push_back(IFC4_types[870]);
    declarations.push_back(IFC4_types[871]);
    declarations.push_back(IFC4_types[872]);
    declarations.push_back(IFC4_types[873]);
    declarations.push_back(IFC4_types[874]);
    declarations.push_back(IFC4_types[875]);
    declarations.push_back(IFC4_types[876]);
    declarations.push_back(IFC4_types[877]);
    declarations.push_back(IFC4_types[878]);
    declarations.push_back(IFC4_types[879]);
    declarations.push_back(IFC4_types[880]);
    declarations.push_back(IFC4_types[881]);
    declarations.push_back(IFC4_types[882]);
    declarations.push_back(IFC4_types[883]);
    declarations.push_back(IFC4_types[884]);
    declarations.push_back(IFC4_types[885]);
    declarations.push_back(IFC4_types[886]);
    declarations.push_back(IFC4_types[887]);
    declarations.push_back(IFC4_types[888]);
    declarations.push_back(IFC4_types[889]);
    declarations.push_back(IFC4_types[890]);
    declarations.push_back(IFC4_types[891]);
    declarations.push_back(IFC4_types[892]);
    declarations.push_back(IFC4_types[893]);
    declarations.push_back(IFC4_types[894]);
    declarations.push_back(IFC4_types[895]);
    declarations.push_back(IFC4_types[896]);
    declarations.push_back(IFC4_types[897]);
    declarations.push_back(IFC4_types[898]);
    declarations.push_back(IFC4_types[899]);
    declarations.push_back(IFC4_types[900]);
    declarations.push_back(IFC4_types[901]);
    declarations.push_back(IFC4_types[902]);
    declarations.push_back(IFC4_types[903]);
    declarations.push_back(IFC4_types[904]);
    declarations.push_back(IFC4_types[905]);
    declarations.push_back(IFC4_types[906]);
    declarations.push_back(IFC4_types[907]);
    declarations.push_back(IFC4_types[908]);
    declarations.push_back(IFC4_types[909]);
    declarations.push_back(IFC4_types[910]);
    declarations.push_back(IFC4_types[911]);
    declarations.push_back(IFC4_types[912]);
    declarations.push_back(IFC4_types[913]);
    declarations.push_back(IFC4_types[914]);
    declarations.push_back(IFC4_types[915]);
    declarations.push_back(IFC4_types[916]);
    declarations.push_back(IFC4_types[917]);
    declarations.push_back(IFC4_types[918]);
    declarations.push_back(IFC4_types[919]);
    declarations.push_back(IFC4_types[920]);
    declarations.push_back(IFC4_types[921]);
    declarations.push_back(IFC4_types[922]);
    declarations.push_back(IFC4_types[923]);
    declarations.push_back(IFC4_types[924]);
    declarations.push_back(IFC4_types[925]);
    declarations.push_back(IFC4_types[926]);
    declarations.push_back(IFC4_types[927]);
    declarations.push_back(IFC4_types[928]);
    declarations.push_back(IFC4_types[929]);
    declarations.push_back(IFC4_types[930]);
    declarations.push_back(IFC4_types[931]);
    declarations.push_back(IFC4_types[932]);
    declarations.push_back(IFC4_types[933]);
    declarations.push_back(IFC4_types[934]);
    declarations.push_back(IFC4_types[935]);
    declarations.push_back(IFC4_types[936]);
    declarations.push_back(IFC4_types[937]);
    declarations.push_back(IFC4_types[938]);
    declarations.push_back(IFC4_types[939]);
    declarations.push_back(IFC4_types[940]);
    declarations.push_back(IFC4_types[941]);
    declarations.push_back(IFC4_types[942]);
    declarations.push_back(IFC4_types[943]);
    declarations.push_back(IFC4_types[944]);
    declarations.push_back(IFC4_types[945]);
    declarations.push_back(IFC4_types[946]);
    declarations.push_back(IFC4_types[947]);
    declarations.push_back(IFC4_types[948]);
    declarations.push_back(IFC4_types[949]);
    declarations.push_back(IFC4_types[950]);
    declarations.push_back(IFC4_types[951]);
    declarations.push_back(IFC4_types[952]);
    declarations.push_back(IFC4_types[953]);
    declarations.push_back(IFC4_types[954]);
    declarations.push_back(IFC4_types[955]);
    declarations.push_back(IFC4_types[956]);
    declarations.push_back(IFC4_types[957]);
    declarations.push_back(IFC4_types[958]);
    declarations.push_back(IFC4_types[959]);
    declarations.push_back(IFC4_types[960]);
    declarations.push_back(IFC4_types[961]);
    declarations.push_back(IFC4_types[962]);
    declarations.push_back(IFC4_types[963]);
    declarations.push_back(IFC4_types[964]);
    declarations.push_back(IFC4_types[965]);
    declarations.push_back(IFC4_types[966]);
    declarations.push_back(IFC4_types[967]);
    declarations.push_back(IFC4_types[968]);
    declarations.push_back(IFC4_types[969]);
    declarations.push_back(IFC4_types[970]);
    declarations.push_back(IFC4_types[971]);
    declarations.push_back(IFC4_types[972]);
    declarations.push_back(IFC4_types[973]);
    declarations.push_back(IFC4_types[974]);
    declarations.push_back(IFC4_types[975]);
    declarations.push_back(IFC4_types[976]);
    declarations.push_back(IFC4_types[977]);
    declarations.push_back(IFC4_types[978]);
    declarations.push_back(IFC4_types[979]);
    declarations.push_back(IFC4_types[980]);
    declarations.push_back(IFC4_types[981]);
    declarations.push_back(IFC4_types[982]);
    declarations.push_back(IFC4_types[983]);
    declarations.push_back(IFC4_types[984]);
    declarations.push_back(IFC4_types[985]);
    declarations.push_back(IFC4_types[986]);
    declarations.push_back(IFC4_types[987]);
    declarations.push_back(IFC4_types[988]);
    declarations.push_back(IFC4_types[989]);
    declarations.push_back(IFC4_types[990]);
    declarations.push_back(IFC4_types[991]);
    declarations.push_back(IFC4_types[992]);
    declarations.push_back(IFC4_types[993]);
    declarations.push_back(IFC4_types[994]);
    declarations.push_back(IFC4_types[995]);
    declarations.push_back(IFC4_types[996]);
    declarations.push_back(IFC4_types[997]);
    declarations.push_back(IFC4_types[998]);
    declarations.push_back(IFC4_types[999]);
    declarations.push_back(IFC4_types[1000]);
    declarations.push_back(IFC4_types[1001]);
    declarations.push_back(IFC4_types[1002]);
    declarations.push_back(IFC4_types[1003]);
    declarations.push_back(IFC4_types[1004]);
    declarations.push_back(IFC4_types[1005]);
    declarations.push_back(IFC4_types[1006]);
    declarations.push_back(IFC4_types[1007]);
    declarations.push_back(IFC4_types[1008]);
    declarations.push_back(IFC4_types[1009]);
    declarations.push_back(IFC4_types[1010]);
    declarations.push_back(IFC4_types[1011]);
    declarations.push_back(IFC4_types[1012]);
    declarations.push_back(IFC4_types[1013]);
    declarations.push_back(IFC4_types[1014]);
    declarations.push_back(IFC4_types[1015]);
    declarations.push_back(IFC4_types[1016]);
    declarations.push_back(IFC4_types[1017]);
    declarations.push_back(IFC4_types[1018]);
    declarations.push_back(IFC4_types[1019]);
    declarations.push_back(IFC4_types[1020]);
    declarations.push_back(IFC4_types[1021]);
    declarations.push_back(IFC4_types[1022]);
    declarations.push_back(IFC4_types[1023]);
    declarations.push_back(IFC4_types[1024]);
    declarations.push_back(IFC4_types[1025]);
    declarations.push_back(IFC4_types[1026]);
    declarations.push_back(IFC4_types[1027]);
    declarations.push_back(IFC4_types[1028]);
    declarations.push_back(IFC4_types[1029]);
    declarations.push_back(IFC4_types[1030]);
    declarations.push_back(IFC4_types[1031]);
    declarations.push_back(IFC4_types[1032]);
    declarations.push_back(IFC4_types[1033]);
    declarations.push_back(IFC4_types[1034]);
    declarations.push_back(IFC4_types[1035]);
    declarations.push_back(IFC4_types[1036]);
    declarations.push_back(IFC4_types[1037]);
    declarations.push_back(IFC4_types[1038]);
    declarations.push_back(IFC4_types[1039]);
    declarations.push_back(IFC4_types[1040]);
    declarations.push_back(IFC4_types[1041]);
    declarations.push_back(IFC4_types[1042]);
    declarations.push_back(IFC4_types[1043]);
    declarations.push_back(IFC4_types[1044]);
    declarations.push_back(IFC4_types[1045]);
    declarations.push_back(IFC4_types[1046]);
    declarations.push_back(IFC4_types[1047]);
    declarations.push_back(IFC4_types[1048]);
    declarations.push_back(IFC4_types[1049]);
    declarations.push_back(IFC4_types[1050]);
    declarations.push_back(IFC4_types[1051]);
    declarations.push_back(IFC4_types[1052]);
    declarations.push_back(IFC4_types[1053]);
    declarations.push_back(IFC4_types[1054]);
    declarations.push_back(IFC4_types[1055]);
    declarations.push_back(IFC4_types[1056]);
    declarations.push_back(IFC4_types[1057]);
    declarations.push_back(IFC4_types[1058]);
    declarations.push_back(IFC4_types[1059]);
    declarations.push_back(IFC4_types[1060]);
    declarations.push_back(IFC4_types[1061]);
    declarations.push_back(IFC4_types[1062]);
    declarations.push_back(IFC4_types[1063]);
    declarations.push_back(IFC4_types[1064]);
    declarations.push_back(IFC4_types[1065]);
    declarations.push_back(IFC4_types[1066]);
    declarations.push_back(IFC4_types[1067]);
    declarations.push_back(IFC4_types[1068]);
    declarations.push_back(IFC4_types[1069]);
    declarations.push_back(IFC4_types[1070]);
    declarations.push_back(IFC4_types[1071]);
    declarations.push_back(IFC4_types[1072]);
    declarations.push_back(IFC4_types[1073]);
    declarations.push_back(IFC4_types[1074]);
    declarations.push_back(IFC4_types[1075]);
    declarations.push_back(IFC4_types[1076]);
    declarations.push_back(IFC4_types[1077]);
    declarations.push_back(IFC4_types[1078]);
    declarations.push_back(IFC4_types[1079]);
    declarations.push_back(IFC4_types[1080]);
    declarations.push_back(IFC4_types[1081]);
    declarations.push_back(IFC4_types[1082]);
    declarations.push_back(IFC4_types[1083]);
    declarations.push_back(IFC4_types[1084]);
    declarations.push_back(IFC4_types[1085]);
    declarations.push_back(IFC4_types[1086]);
    declarations.push_back(IFC4_types[1087]);
    declarations.push_back(IFC4_types[1088]);
    declarations.push_back(IFC4_types[1089]);
    declarations.push_back(IFC4_types[1090]);
    declarations.push_back(IFC4_types[1091]);
    declarations.push_back(IFC4_types[1092]);
    declarations.push_back(IFC4_types[1093]);
    declarations.push_back(IFC4_types[1094]);
    declarations.push_back(IFC4_types[1095]);
    declarations.push_back(IFC4_types[1096]);
    declarations.push_back(IFC4_types[1097]);
    declarations.push_back(IFC4_types[1098]);
    declarations.push_back(IFC4_types[1099]);
    declarations.push_back(IFC4_types[1100]);
    declarations.push_back(IFC4_types[1101]);
    declarations.push_back(IFC4_types[1102]);
    declarations.push_back(IFC4_types[1103]);
    declarations.push_back(IFC4_types[1104]);
    declarations.push_back(IFC4_types[1105]);
    declarations.push_back(IFC4_types[1106]);
    declarations.push_back(IFC4_types[1107]);
    declarations.push_back(IFC4_types[1108]);
    declarations.push_back(IFC4_types[1109]);
    declarations.push_back(IFC4_types[1110]);
    declarations.push_back(IFC4_types[1111]);
    declarations.push_back(IFC4_types[1112]);
    declarations.push_back(IFC4_types[1113]);
    declarations.push_back(IFC4_types[1114]);
    declarations.push_back(IFC4_types[1115]);
    declarations.push_back(IFC4_types[1116]);
    declarations.push_back(IFC4_types[1117]);
    declarations.push_back(IFC4_types[1118]);
    declarations.push_back(IFC4_types[1119]);
    declarations.push_back(IFC4_types[1120]);
    declarations.push_back(IFC4_types[1121]);
    declarations.push_back(IFC4_types[1122]);
    declarations.push_back(IFC4_types[1123]);
    declarations.push_back(IFC4_types[1124]);
    declarations.push_back(IFC4_types[1125]);
    declarations.push_back(IFC4_types[1126]);
    declarations.push_back(IFC4_types[1127]);
    declarations.push_back(IFC4_types[1128]);
    declarations.push_back(IFC4_types[1129]);
    declarations.push_back(IFC4_types[1130]);
    declarations.push_back(IFC4_types[1131]);
    declarations.push_back(IFC4_types[1132]);
    declarations.push_back(IFC4_types[1133]);
    declarations.push_back(IFC4_types[1134]);
    declarations.push_back(IFC4_types[1135]);
    declarations.push_back(IFC4_types[1136]);
    declarations.push_back(IFC4_types[1137]);
    declarations.push_back(IFC4_types[1138]);
    declarations.push_back(IFC4_types[1139]);
    declarations.push_back(IFC4_types[1140]);
    declarations.push_back(IFC4_types[1141]);
    declarations.push_back(IFC4_types[1142]);
    declarations.push_back(IFC4_types[1143]);
    declarations.push_back(IFC4_types[1144]);
    declarations.push_back(IFC4_types[1145]);
    declarations.push_back(IFC4_types[1146]);
    declarations.push_back(IFC4_types[1147]);
    declarations.push_back(IFC4_types[1148]);
    declarations.push_back(IFC4_types[1149]);
    declarations.push_back(IFC4_types[1150]);
    declarations.push_back(IFC4_types[1151]);
    declarations.push_back(IFC4_types[1152]);
    declarations.push_back(IFC4_types[1153]);
    declarations.push_back(IFC4_types[1154]);
    declarations.push_back(IFC4_types[1155]);
    declarations.push_back(IFC4_types[1156]);
    declarations.push_back(IFC4_types[1157]);
    declarations.push_back(IFC4_types[1158]);
    declarations.push_back(IFC4_types[1159]);
    declarations.push_back(IFC4_types[1160]);
    declarations.push_back(IFC4_types[1161]);
    declarations.push_back(IFC4_types[1162]);
    declarations.push_back(IFC4_types[1163]);
    declarations.push_back(IFC4_types[1164]);
    declarations.push_back(IFC4_types[1165]);
    declarations.push_back(IFC4_types[1166]);
    declarations.push_back(IFC4_types[1167]);
    declarations.push_back(IFC4_types[1168]);
    declarations.push_back(IFC4_types[1169]);
    declarations.push_back(IFC4_types[1170]);
    declarations.push_back(IFC4_types[1171]);
    declarations.push_back(IFC4_types[1172]);
    return new schema_definition("IFC4", declarations, new IFC4_instance_factory());
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

