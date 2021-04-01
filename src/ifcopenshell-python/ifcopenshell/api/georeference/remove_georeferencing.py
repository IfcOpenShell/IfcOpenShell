class Usecase:
    def __init__(self, file, **settings):
        self.file = file

    def execute(self):
        map_conversion = self.file.by_type("IfcMapConversion")[0]
        projected_crs = self.file.by_type("IfcProjectedCRS")[0]
        if projected_crs.MapUnit and len(self.file.get_inverse(projected_crs.MapUnit)) == 1:
            # TODO: go deeper for conversion units
            self.file.remove(projected_crs.MapUnit)
        self.file.remove(projected_crs)
        self.file.remove(map_conversion)
