mapper = {
    'Qto_AudioVisualApplianceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_PlateBaseQuantities' : {
        'Width' : "get_height",
        'Perimeter' : "get_gross_perimeter",
        'GrossArea' : "get_gross_footprint_area",
        'NetArea' : "get_net_footprint_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_OpeningElementBaseQuantities' : {
        'Width' : "get_length",
        'Height' : "get_opening_height",
        'Depth' : "get_opening_depth",
        'Area' : "get_opening_mapping_area",
        'Volume' : "get_net_volume",
    },
    'Qto_MarineFacilityBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
        'Area' : "get_net_footprint_area",
        'Volume' : "get_net_volume",
    },
    'Qto_ChillerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_PileBaseQuantities' : {
        'Length' : "get_length",
        'CrossSectionArea' : "get_cross_section_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'GrossSurfaceArea' : "get_gross_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_VibrationIsolatorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_LampBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_VehicleBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
    },
    'Qto_PipeFittingBaseQuantities' : {
        'Length' : None,
        'GrossCrossSectionArea' : None,
        'NetCrossSectionArea' : None,
        'OuterSurfaceArea' : None,
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_CableCarrierFittingBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_HeatExchangerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_DoorBaseQuantities' : {
        'Width' : { "function_name" : "get_length", "args" : ", main_axis = 'x'"},
        'Height' : "get_height",
        'Perimeter' : "get_rectangular_perimeter",
        'Area' : "get_net_side_area",
    },
    'Qto_DuctSegmentBaseQuantities' : {
        'Length' : None,
        'GrossCrossSectionArea' : None,
        'NetCrossSectionArea' : None,
        'OuterSurfaceArea' : None,
        'GrossWeight' : None,
    },
    'Qto_TransformerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_FacilityPartBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
        'Area' : "get_net_footprint_area",
        'Volume' : "get_net_volume",
    },
    'Qto_ProjectionElementBaseQuantities' : {
        'Area' : "get_net_side_area",
        'Volume' : "get_net_volume",
    },
    'Qto_SignBaseQuantities' : {
        'Height' : None,
        'Width' : None,
        'Thickness' : None,
        'Weight' : None,
    },
    'Qto_CableSegmentBaseQuantities' : {
        'GrossWeight' : None,
        'Length' : None,
        'CrossSectionArea' : None,
        'OuterSurfaceArea' : None,
    },
    'Qto_BuildingBaseQuantities' : {
        'Height' : None,
        'EavesHeight' : None,
        'FootPrintArea' : None,
        'GrossFloorArea' : None,
        'NetFloorArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
    },
    'Qto_ElectricFlowStorageDeviceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_CommunicationsApplianceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_RailBaseQuantities' : {
        'Length' : None,
        'Volume' : None,
        'Weight' : None,
    },
    'Qto_PictorialSignQuantities' : {
        'Area' : None,
        'SignArea' : None,
    },
    'Qto_SpaceHeaterBaseQuantities' : {
        'Length' : None,
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_CoveringBaseQuantities' : {
        'Width' : "get_height",
        'GrossArea' : "get_gross_footprint_area",
        'NetArea' : "get_net_footprint_area",
    },
    'Qto_PipeSegmentBaseQuantities' : {
        'Length' : "get_length",
        'GrossCrossSectionArea' : None,
        'NetCrossSectionArea' : "get_cross_section_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_HumidifierBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ConstructionEquipmentResourceBaseQuantities' : {
        'UsageTime' : None,
        'OperatingTime' : None,
    },
    'Qto_AlarmBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_JunctionBoxBaseQuantities' : {
        'GrossWeight' : None,
        'NumberOfGangs' : None,
        'Length' : None,
        'Width' : None,
        'Height' : None,
    },
    'Qto_ArealStratumBaseQuantities' : {
        'Area' : None,
        'Length' : None,
        'PlanLength' : None,
    },
    'Qto_SiteBaseQuantities' : {
        'GrossPerimeter' : None,
        'GrossArea' : None,
    },
    'Qto_MotorConnectionBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_RoofBaseQuantities' : {
        'GrossArea' : None,
        'NetArea' : None,
        'ProjectedArea' : None,
    },
    'Qto_ChimneyBaseQuantities' : {
        'Length' : None,
    },
    'Qto_ElectricTimeControlBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ElectricMotorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_EarthworksFillBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Depth' : None,
        'CompactedVolume' : None,
        'LooseVolume' : None,
    },
    'Qto_ConduitSegmentBaseQuantities' : {
        'InnerDiameter' : None,
        'OuterDiameter' : None,
    },
    'Qto_SignalBaseQuantities' : {
        'Weight' : None,
    },
    'Qto_DuctFittingBaseQuantities' : {
        'Length' : None,
        'GrossCrossSectionArea' : None,
        'NetCrossSectionArea' : None,
        'OuterSurfaceArea' : None,
        'GrossWeight' : None,
    },
    'Qto_UnitaryControlElementBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ActuatorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_CurtainWallQuantities' : {
        'Length' : None,
        'Height' : None,
        'Width' : None,
        'GrossSideArea' : None,
        'NetSideArea' : None,
    },
    'Qto_BoilerBaseQuantities' : {
        'GrossWeight' : None,
        'NetWeight' : None,
        'TotalSurfaceArea' : None,
    },
    'Qto_FlowMeterBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_AirTerminalBaseQuantities' : {
        'GrossWeight' : None,
        'Perimeter' : None,
        'TotalSurfaceArea' : None,
    },
    'Qto_DuctSilencerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_WasteTerminalBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_SlabBaseQuantities' : {
        'Width' : "get_width",
        'Length' : "get_length",
        'Depth' : "get_height",
        'Perimeter' : "get_gross_perimeter",
        'GrossArea' : "get_gross_footprint_area",
        'NetArea' : "get_net_footprint_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_ImpactProtectionDeviceBaseQuantities' : {
        'Weight' : None,
    },
    'Qto_LightFixtureBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_FlowInstrumentBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_BuildingStoreyBaseQuantities' : {
        'GrossHeight' : None,
        'NetHeight' : None,
        'GrossPerimeter' : None,
        'GrossFloorArea' : None,
        'NetFloorArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
    },
    'Qto_ReinforcedSoilBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Depth' : None,
        'Area' : None,
        'Volume' : None,
    },
    'Qto_DistributionBoardBaseQuantities' : {
        'GrossWeight' : None,
        'NumberOfCircuits' : None,
    },
    'Qto_FootingBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Height' : None,
        'CrossSectionArea' : None,
        'OuterSurfaceArea' : None,
        'GrossSurfaceArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_PumpBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_CableCarrierSegmentBaseQuantities' : {
        'GrossWeight' : None,
        'Length' : None,
        'CrossSectionArea' : None,
        'OuterSurfaceArea' : None,
    },
    'Qto_InterceptorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ColumnBaseQuantities' : {
        'Length' : "get_length",
        'CrossSectionArea' : "get_cross_section_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'GrossSurfaceArea' : "get_gross_surface_area",
        'NetSurfaceArea' : "get_net_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_EarthworksCutBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Depth' : None,
        'UndisturbedVolume' : None,
        'LooseVolume' : None,
        'Weight' : None,
    },
    'Qto_StackTerminalBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_CoilBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_KerbBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Height' : None,
        'Depth' : None,
        'Volume' : None,
        'Weight' : None,
    },
    'Qto_PavementBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Depth' : None,
        'GrossArea' : None,
        'NetArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
    },
    'Qto_ControllerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_SolarDeviceBaseQuantities' : {
        'GrossWeight' : None,
        'GrossArea' : None,
    },
    'Qto_RampFlightBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'GrossArea' : None,
        'NetArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
    },
    'Qto_ElectricApplianceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ValveBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_DamperBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_SurfaceFeatureBaseQuantities' : {
        'Area' : None,
        'Length' : None,
    },
    'Qto_WallBaseQuantities' : {
        'Length' : { "function_name" : "get_length", "args" : ", main_axis = 'x'"},
        'Width' : "get_width",
        'Height' : "get_height",
        'GrossFootprintArea' : "get_gross_footprint_area",
        'NetFootprintArea' : "get_net_footprint_area",
        'GrossSideArea' : "get_gross_side_area",
        'NetSideArea' : "get_net_side_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_StairFlightBaseQuantities' : {
        'Length' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
    },
    'Qto_SwitchingDeviceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_BurnerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ConstructionMaterialResourceBaseQuantities' : {
        'GrossVolume' : None,
        'NetVolume' : None,
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_ElectricGeneratorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_LinearStratumBaseQuantities' : {
        'Diameter' : None,
        'Length' : None,
    },
    'Qto_CableFittingBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_DistributionChamberElementBaseQuantities' : {
        'GrossSurfaceArea' : None,
        'NetSurfaceArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
        'Depth' : None,
    },
    'Qto_CompressorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ProtectiveDeviceTrippingUnitBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_EvaporatorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_SpaceBaseQuantities' : {
        'Height' : "get_height",
        'FinishCeilingHeight' : "get_finish_ceiling_height",
        'FinishFloorHeight' : "get_finish_floor_height",
        'GrossPerimeter' : "get_gross_perimeter",
        'NetPerimeter' : None,
        'GrossFloorArea' : "get_gross_footprint_area",
        'NetFloorArea' : "get_net_floor_area",
        'GrossWallArea' : None,
        'NetWallArea' : None,
        'GrossCeilingArea' : "get_gross_ceiling_area",
        'NetCeilingArea' : "get_net_ceiling_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_space_net_volume",
    },
    'Qto_CourseBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Thickness' : None,
        'Volume' : None,
        'GrossVolume' : None,
        'Weight' : None,
    },
    'Qto_CondenserBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_FireSuppressionTerminalBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_RailingBaseQuantities' : {
        'Length' : None,
    },
    'Qto_TubeBundleBaseQuantities' : {
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_BeamBaseQuantities' : {
        'Length' : "get_length",
        'CrossSectionArea' : "get_cross_section_area",
        'GrossSurfaceArea' : "get_gross_surface_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'NetSurfaceArea' : "get_net_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_SleeperBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Height' : None,
    },
    'Qto_ProtectiveDeviceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_CooledBeamBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_TankBaseQuantities' : {
        'GrossWeight' : None,
        'NetWeight' : None,
        'TotalSurfaceArea' : None,
    },
    'Qto_AirToAirHeatRecoveryBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_CoolingTowerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_SensorBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_WindowBaseQuantities' : {
        'Width' : { "function_name" : "get_length", "args" : ", main_axis = 'x'"},
        'Height' : "get_height",
        'Perimeter' : "get_rectangular_perimeter",
        'Area' : "get_net_side_area",
    },
    'Qto_SanitaryTerminalBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_BuildingElementProxyQuantities' : {
        'NetSurfaceArea' : None,
        'NetVolume' : None,
    },
    'Qto_FanBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_OutletBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_UnitaryEquipmentBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_FilterBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_MemberBaseQuantities' : {
        'Length' : None,
        'CrossSectionArea' : None,
        'OuterSurfaceArea' : None,
        'GrossSurfaceArea' : None,
        'NetSurfaceArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_BodyGeometryValidation' : {
        'GrossSurfaceArea' : None,
        'NetSurfaceArea' : None,
        'GrossVolume' : None,
        'NetVolume' : None,
        'SurfaceGenusBeforeFeatures' : None,
        'SurfaceGenusAfterFeatures' : None,
    },
    'Qto_VolumetricStratumBaseQuantities' : {
        'Area' : None,
        'Mass' : None,
        'PlanArea' : None,
        'Volume' : None,
    },
    'Qto_SpatialZoneBaseQuantities' : {
        'Length' : None,
        'Width' : None,
        'Height' : None,
    },
    'Qto_ReinforcingElementBaseQuantities' : {
        'Count' : None,
        'Length' : None,
        'Weight' : None,
    },
    'Qto_EvaporativeCoolerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_AirTerminalBoxTypeBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_LaborResourceBaseQuantities' : {
        'StandardWork' : None,
        'OvertimeWork' : None,
    },
}
