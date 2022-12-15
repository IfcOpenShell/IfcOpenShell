import ifcopenshell
def exists(v): return v is not None


sizeof = len
hiindex = len
class enum_namespace:
    def __getattr__(self, k):
        return k



class rmult_set(set):
    def __rmul__(self, other):
        return rmult_set(set(other) & self)
    def __repr__(self):
        return repr(set(self))


def typeof(inst):
    schema_name = inst.wrapped_data.file.schema.lower()
    def inner():
        decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(inst.is_a())
        while decl:
            yield '.'.join((schema_name, decl.name().lower()))
            decl = decl.supertype()
    return rmult_set(inner())

IfcActionSourceTypeEnum = enum_namespace()


IfcActionTypeEnum = enum_namespace()


IfcActuatorTypeEnum = enum_namespace()


IfcAddressTypeEnum = enum_namespace()


IfcAheadOrBehind = enum_namespace()


IfcAirTerminalBoxTypeEnum = enum_namespace()


IfcAirTerminalTypeEnum = enum_namespace()


IfcAirToAirHeatRecoveryTypeEnum = enum_namespace()


IfcAlarmTypeEnum = enum_namespace()


IfcAnalysisModelTypeEnum = enum_namespace()


IfcAnalysisTheoryTypeEnum = enum_namespace()


IfcArithmeticOperatorEnum = enum_namespace()


IfcAssemblyPlaceEnum = enum_namespace()


IfcBSplineCurveForm = enum_namespace()


IfcBeamTypeEnum = enum_namespace()


IfcBenchmarkEnum = enum_namespace()


IfcBoilerTypeEnum = enum_namespace()


IfcBooleanOperator = enum_namespace()


IfcBuildingElementProxyTypeEnum = enum_namespace()


IfcCableCarrierFittingTypeEnum = enum_namespace()


IfcCableCarrierSegmentTypeEnum = enum_namespace()


IfcCableSegmentTypeEnum = enum_namespace()


IfcChangeActionEnum = enum_namespace()


IfcChillerTypeEnum = enum_namespace()


IfcCoilTypeEnum = enum_namespace()


IfcColumnTypeEnum = enum_namespace()


IfcCompressorTypeEnum = enum_namespace()


IfcCondenserTypeEnum = enum_namespace()


IfcConnectionTypeEnum = enum_namespace()


IfcConstraintEnum = enum_namespace()


IfcControllerTypeEnum = enum_namespace()


IfcCooledBeamTypeEnum = enum_namespace()


IfcCoolingTowerTypeEnum = enum_namespace()


IfcCostScheduleTypeEnum = enum_namespace()


IfcCoveringTypeEnum = enum_namespace()


IfcCurrencyEnum = enum_namespace()


IfcCurtainWallTypeEnum = enum_namespace()


IfcDamperTypeEnum = enum_namespace()


IfcDataOriginEnum = enum_namespace()


IfcDerivedUnitEnum = enum_namespace()


IfcDimensionExtentUsage = enum_namespace()


IfcDirectionSenseEnum = enum_namespace()


IfcDistributionChamberElementTypeEnum = enum_namespace()


IfcDocumentConfidentialityEnum = enum_namespace()


IfcDocumentStatusEnum = enum_namespace()


IfcDoorPanelOperationEnum = enum_namespace()


IfcDoorPanelPositionEnum = enum_namespace()


IfcDoorStyleConstructionEnum = enum_namespace()


IfcDoorStyleOperationEnum = enum_namespace()


IfcDuctFittingTypeEnum = enum_namespace()


IfcDuctSegmentTypeEnum = enum_namespace()


IfcDuctSilencerTypeEnum = enum_namespace()


IfcElectricApplianceTypeEnum = enum_namespace()


IfcElectricCurrentEnum = enum_namespace()


IfcElectricDistributionPointFunctionEnum = enum_namespace()


IfcElectricFlowStorageDeviceTypeEnum = enum_namespace()


IfcElectricGeneratorTypeEnum = enum_namespace()


IfcElectricHeaterTypeEnum = enum_namespace()


IfcElectricMotorTypeEnum = enum_namespace()


IfcElectricTimeControlTypeEnum = enum_namespace()


IfcElementAssemblyTypeEnum = enum_namespace()


IfcElementCompositionEnum = enum_namespace()


IfcEnergySequenceEnum = enum_namespace()


IfcEnvironmentalImpactCategoryEnum = enum_namespace()


IfcEvaporativeCoolerTypeEnum = enum_namespace()


IfcEvaporatorTypeEnum = enum_namespace()


IfcFanTypeEnum = enum_namespace()


IfcFilterTypeEnum = enum_namespace()


IfcFireSuppressionTerminalTypeEnum = enum_namespace()


IfcFlowDirectionEnum = enum_namespace()


IfcFlowInstrumentTypeEnum = enum_namespace()


IfcFlowMeterTypeEnum = enum_namespace()


IfcFootingTypeEnum = enum_namespace()


IfcGasTerminalTypeEnum = enum_namespace()


IfcGeometricProjectionEnum = enum_namespace()


IfcGlobalOrLocalEnum = enum_namespace()


IfcHeatExchangerTypeEnum = enum_namespace()


IfcHumidifierTypeEnum = enum_namespace()


IfcInternalOrExternalEnum = enum_namespace()


IfcInventoryTypeEnum = enum_namespace()


IfcJunctionBoxTypeEnum = enum_namespace()


IfcLampTypeEnum = enum_namespace()


IfcLayerSetDirectionEnum = enum_namespace()


IfcLightDistributionCurveEnum = enum_namespace()


IfcLightEmissionSourceEnum = enum_namespace()


IfcLightFixtureTypeEnum = enum_namespace()


IfcLoadGroupTypeEnum = enum_namespace()


IfcLogicalOperatorEnum = enum_namespace()


IfcMemberTypeEnum = enum_namespace()


IfcMotorConnectionTypeEnum = enum_namespace()


IfcNullStyle = enum_namespace()


IfcObjectTypeEnum = enum_namespace()


IfcObjectiveEnum = enum_namespace()


IfcOccupantTypeEnum = enum_namespace()


IfcOutletTypeEnum = enum_namespace()


IfcPermeableCoveringOperationEnum = enum_namespace()


IfcPhysicalOrVirtualEnum = enum_namespace()


IfcPileConstructionEnum = enum_namespace()


IfcPileTypeEnum = enum_namespace()


IfcPipeFittingTypeEnum = enum_namespace()


IfcPipeSegmentTypeEnum = enum_namespace()


IfcPlateTypeEnum = enum_namespace()


IfcProcedureTypeEnum = enum_namespace()


IfcProfileTypeEnum = enum_namespace()


IfcProjectOrderRecordTypeEnum = enum_namespace()


IfcProjectOrderTypeEnum = enum_namespace()


IfcProjectedOrTrueLengthEnum = enum_namespace()


IfcPropertySourceEnum = enum_namespace()


IfcProtectiveDeviceTypeEnum = enum_namespace()


IfcPumpTypeEnum = enum_namespace()


IfcRailingTypeEnum = enum_namespace()


IfcRampFlightTypeEnum = enum_namespace()


IfcRampTypeEnum = enum_namespace()


IfcReflectanceMethodEnum = enum_namespace()


IfcReinforcingBarRoleEnum = enum_namespace()


IfcReinforcingBarSurfaceEnum = enum_namespace()


IfcResourceConsumptionEnum = enum_namespace()


IfcRibPlateDirectionEnum = enum_namespace()


IfcRoleEnum = enum_namespace()


IfcRoofTypeEnum = enum_namespace()


IfcSIPrefix = enum_namespace()


IfcSIUnitName = enum_namespace()


IfcSanitaryTerminalTypeEnum = enum_namespace()


IfcSectionTypeEnum = enum_namespace()


IfcSensorTypeEnum = enum_namespace()


IfcSequenceEnum = enum_namespace()


IfcServiceLifeFactorTypeEnum = enum_namespace()


IfcServiceLifeTypeEnum = enum_namespace()


IfcSlabTypeEnum = enum_namespace()


IfcSoundScaleEnum = enum_namespace()


IfcSpaceHeaterTypeEnum = enum_namespace()


IfcSpaceTypeEnum = enum_namespace()


IfcStackTerminalTypeEnum = enum_namespace()


IfcStairFlightTypeEnum = enum_namespace()


IfcStairTypeEnum = enum_namespace()


IfcStateEnum = enum_namespace()


IfcStructuralCurveTypeEnum = enum_namespace()


IfcStructuralSurfaceTypeEnum = enum_namespace()


IfcSurfaceSide = enum_namespace()


IfcSurfaceTextureEnum = enum_namespace()


IfcSwitchingDeviceTypeEnum = enum_namespace()


IfcTankTypeEnum = enum_namespace()


IfcTendonTypeEnum = enum_namespace()


IfcTextPath = enum_namespace()


IfcThermalLoadSourceEnum = enum_namespace()


IfcThermalLoadTypeEnum = enum_namespace()


IfcTimeSeriesDataTypeEnum = enum_namespace()


IfcTimeSeriesScheduleTypeEnum = enum_namespace()


IfcTransformerTypeEnum = enum_namespace()


IfcTransitionCode = enum_namespace()


IfcTransportElementTypeEnum = enum_namespace()


IfcTrimmingPreference = enum_namespace()


IfcTubeBundleTypeEnum = enum_namespace()


IfcUnitEnum = enum_namespace()


IfcUnitaryEquipmentTypeEnum = enum_namespace()


IfcValveTypeEnum = enum_namespace()


IfcVibrationIsolatorTypeEnum = enum_namespace()


IfcWallTypeEnum = enum_namespace()


IfcWasteTerminalTypeEnum = enum_namespace()


IfcWindowPanelOperationEnum = enum_namespace()


IfcWindowPanelPositionEnum = enum_namespace()


IfcWindowStyleConstructionEnum = enum_namespace()


IfcWindowStyleOperationEnum = enum_namespace()


IfcWorkControlTypeEnum = enum_namespace()



class IfcBSplineCurve_WR41:
    SCOPE = "entity"
    TYPE_NAME = "IfcBSplineCurve"
    RULE_NAME = "WR41"

    @staticmethod    
    def __call__(self):
        Degree = self.Degree
        ControlPointsList = self.ControlPointsList
        CurveForm = self.CurveForm
        ClosedCurve = self.ClosedCurve
        SelfIntersect = self.SelfIntersect
        
        assert sizeof([Temp for Temp in ControlPointsList if Temp.Dim != ControlPointsList[0].Dim]) == 0
        



def calc_IfcBSplineCurve_ControlPoints(self):
    Degree = self.Degree
    ControlPointsList = self.ControlPointsList
    CurveForm = self.CurveForm
    ClosedCurve = self.ClosedCurve
    SelfIntersect = self.SelfIntersect
    return \
    IfcListToArray(UpperIndexOnControlPoints)



def calc_IfcBSplineCurve_UpperIndexOnControlPoints(self):
    Degree = self.Degree
    ControlPointsList = self.ControlPointsList
    CurveForm = self.CurveForm
    ClosedCurve = self.ClosedCurve
    SelfIntersect = self.SelfIntersect
    return \
    (sizeof(ControlPointsList)) - (1)




class IfcCartesianPoint_WR1:
    SCOPE = "entity"
    TYPE_NAME = "IfcCartesianPoint"
    RULE_NAME = "WR1"

    @staticmethod    
    def __call__(self):
        Coordinates = self.Coordinates
        
        assert hiindex(Coordinates) >= 2
        



def calc_IfcCartesianPoint_Dim(self):
    Coordinates = self.Coordinates
    return \
    hiindex(Coordinates)



