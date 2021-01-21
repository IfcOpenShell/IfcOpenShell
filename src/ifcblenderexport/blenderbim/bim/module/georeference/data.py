from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    map_conversion = {}
    projected_crs = {}

    @classmethod
    def load(cls):
        file = IfcStore.get_file()
        if not file:
            return
        cls.map_conversion = {}
        cls.projected_crs = {}
        if file.schema == "IFC2X3":
            return
        for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            map_conversion = context.HasCoordinateOperation[0]
            cls.map_conversion = map_conversion.get_info()
            cls.map_conversion["SourceCRS"] = cls.map_conversion["SourceCRS"].id()
            cls.map_conversion["TargetCRS"] = cls.map_conversion["TargetCRS"].id()
            cls.projected_crs = map_conversion.TargetCRS.get_info()
            if cls.projected_crs["MapUnit"]:
                cls.projected_crs["MapUnit"] = map_conversion.TargetCRS.MapUnit.get_info()
            break
        cls.is_loaded = True
