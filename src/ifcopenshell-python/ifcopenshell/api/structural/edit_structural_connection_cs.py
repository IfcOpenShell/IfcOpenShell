class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"structural_item": None, "axis": [0.0, 0.0, 1.0], "ref_direction": [1.0, 0.0, 0.0]}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["structural_item"].ConditionCoordinateSystem is None:
            point = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ccs = self.file.createIfcAxis2Placement3D(point, None, None)
            self.settings["structural_item"].ConditionCoordinateSystem = ccs
            print(ccs)

        ccs = self.settings["structural_item"].ConditionCoordinateSystem
        print("use case")
        print(ccs)
        if ccs.Axis and len(self.file.get_inverse(ccs.Axis)) == 1:
            self.file.remove(ccs.Axis)
        ccs.Axis = self.file.createIfcDirection(self.settings["axis"])
        if ccs.RefDirection and len(self.file.get_inverse(ccs.RefDirection)) == 1:
            self.file.remove(ccs.RefDirection)
        ccs.RefDirection = self.file.createIfcDirection(self.settings["ref_direction"])
