class Data:
    is_loaded = False
    units = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.units = {}

    @classmethod
    def load(cls, file):
        if not file:
            return
        unit_assignment = file.by_type("IfcUnitAssignment")
        if not unit_assignment:
            return
        for unit in unit_assignment[0].Units:
            pass
        # TODO: implement along with UI
        cls.is_loaded = True
