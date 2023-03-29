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
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
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
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
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
        'Height' : "get_height",
        'Width' : { "function_name" : "get_length", "args" : ", main_axis = 'x'"},
        'Thickness' : "get_width",
        'Weight' : None,
    },
    'Qto_CableSegmentBaseQuantities' : {
        'GrossWeight' : None,
        'Length' : "get_length",
        'CrossSectionArea' : None,
        'OuterSurfaceArea' : "get_outer_surface_area",
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
        'Length' : "get_length",
        'Volume' : "get_net_volume",
        'Weight' : "get_net_weight",
    },
    'Qto_PictorialSignQuantities' : {
        'Area' : "get_net_side_area",
        'SignArea' : None,
    },
    'Qto_SpaceHeaterBaseQuantities' : {
        'Length' : "get_length",
        'GrossWeight' : None,
        'NetWeight' : None,
    },
    'Qto_CoveringBaseQuantities' : {
        'Width' : "get_covering_width",
        'GrossArea' : "get_covering_gross_area",
        'NetArea' : "get_covering_net_area",
    },
    'Qto_PipeSegmentBaseQuantities' : {
        'Length' : "get_length",
        'GrossCrossSectionArea' : None,
        'NetCrossSectionArea' : "get_cross_section_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
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
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
    },
    'Qto_ArealStratumBaseQuantities' : {
        'Area' : "get_net_footprint_area",
        'Length' : "get_length",
        'PlanLength' : None,
    },
    'Qto_SiteBaseQuantities' : {
        'GrossPerimeter' : "get_gross_perimeter",
        'GrossArea' : "get_gross_footprint_area",
    },
    'Qto_MotorConnectionBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_RoofBaseQuantities' : {
        'GrossArea' : "get_gross_footprint_area",
        'NetArea' : "get_net_footprint_area",
        'ProjectedArea' : None,
    },
    'Qto_ChimneyBaseQuantities' : {
        'Length' : "get_height",
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
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
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
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
        'CrossSectionArea' : "get_cross_section_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'GrossSurfaceArea' : "get_gross_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
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
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
    },
    'Qto_EarthworksCutBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Depth' : "get_height",
        'UndisturbedVolume' : "get_net_volume",
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
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
        'Depth' : None,
        'Volume' : "get_net_volume",
        'Weight' : None,
    },
    'Qto_PavementBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Depth' : "get_height",
        'GrossArea' : "get_gross_footprint_area",
        'NetArea' : "get_net_footprint_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
    },
    'Qto_ControllerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_SolarDeviceBaseQuantities' : {
        'GrossWeight' : None,
        'GrossArea' : None,
    },
    'Qto_RampFlightBaseQuantities' : {
        'Length' : "get_stair_length",
        'Width' : "get_width",
        'GrossArea' : "get_gross_stair_area",
        'NetArea' : "get_net_stair_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
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
        'Area' : "get_net_footprint_area",
        'Length' : "get_length",
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
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
    },
    'Qto_StairFlightBaseQuantities' : {
        'Length' : "get_stair_length",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
    },
    'Qto_SwitchingDeviceBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_BurnerBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_ConstructionMaterialResourceBaseQuantities' : {
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
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
        'GrossSurfaceArea' : "get_gross_surface_area",
        'NetSurfaceArea' : "get_net_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'Depth' : "get_length",
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
        'Length' : "get_length",
        'Width' : "get_width",
        'Thickness' : "get_height",
        'Volume' : "get_net_volume",
        'GrossVolume' : "get_gross_volume",
        'Weight' : None,
    },
    'Qto_CondenserBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_FireSuppressionTerminalBaseQuantities' : {
        'GrossWeight' : None,
    },
    'Qto_RailingBaseQuantities' : {
        'Length' : "get_length",
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
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
    },
    'Qto_SleeperBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
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
        'TotalSurfaceArea' : "get_outer_surface_area",
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
        'NetSurfaceArea' : "get_net_surface_area",
        'NetVolume' : "get_net_volume",
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
        'Length' : "get_length",
        'CrossSectionArea' : "get_cross_section_area",
        'OuterSurfaceArea' : "get_outer_surface_area",
        'GrossSurfaceArea' : "get_gross_surface_area",
        'NetSurfaceArea' : "get_net_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'GrossWeight' : "get_gross_weight",
        'NetWeight' : "get_net_weight",
    },
    'Qto_BodyGeometryValidation' : {
        'GrossSurfaceArea' : "get_gross_surface_area",
        'NetSurfaceArea' : "get_net_surface_area",
        'GrossVolume' : "get_gross_volume",
        'NetVolume' : "get_net_volume",
        'SurfaceGenusBeforeFeatures' : None,
        'SurfaceGenusAfterFeatures' : None,
    },
    'Qto_VolumetricStratumBaseQuantities' : {
        'Area' : "get_net_footprint_area",
        'Mass' : None,
        'PlanArea' : "get_net_footprint_area",
        'Volume' : "get_net_volume",
    },
    'Qto_SpatialZoneBaseQuantities' : {
        'Length' : "get_length",
        'Width' : "get_width",
        'Height' : "get_height",
    },
    'Qto_ReinforcingElementBaseQuantities' : {
        'Count' : None,
        'Length' : "get_length",
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
