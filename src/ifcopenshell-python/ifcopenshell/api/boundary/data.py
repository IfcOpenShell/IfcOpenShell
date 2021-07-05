class Data:
    is_loaded = False
    boundaries = {}
    spaces = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.boundaries = {}
        cls.spaces = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        for boundary in cls._file.by_type("IfcRelSpaceBoundary"):
            data = boundary.get_info()
            data["RelatingSpace"] = data["RelatingSpace"].id() if data["RelatingSpace"] else None
            data["RelatedBuildingElement"] = (
                data["RelatedBuildingElement"].id() if data["RelatedBuildingElement"] else None
            )
            del data["ConnectionGeometry"]
            if cls._file.schema == "IFC2X3":
                pass
            else:
                if boundary.is_a("IfcRelSpaceBoundary1stLevel"):
                    data["ParentBoundary"] = data["ParentBoundary"].id() if data["ParentBoundary"] else None
                if boundary.is_a("IfcRelSpaceBoundary2ndLevel"):
                    data["CorrespondingBoundary"] = (
                        data["CorrespondingBoundary"].id() if data["CorrespondingBoundary"] else None
                    )
            cls.boundaries[boundary.id()] = data
            cls.spaces.setdefault(data["RelatingSpace"], []).append(boundary.id())
        cls.is_loaded = True
