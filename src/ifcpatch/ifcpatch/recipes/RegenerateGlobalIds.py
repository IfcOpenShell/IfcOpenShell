import ifcopenshell


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        if self.args and self.args[0] == "DUPLICATE":
            guids = set()
            for element in self.file.by_type("IfcRoot"):
                if element.GlobalId in guids:
                    element.GlobalId = ifcopenshell.guid.new()
                elif len(element.GlobalId) != 22 or element.GlobalId[0] not in "0123":
                    element.GlobalId = ifcopenshell.guid.new()
                else:
                    try:
                        ifcopenshell.guid.expand(element.GlobalId)
                    except:
                        element.GlobalId = ifcopenshell.guid.new()
                guids.add(element.GlobalId)
        else:
            for element in self.file.by_type("IfcRoot"):
                element.GlobalId = ifcopenshell.guid.new()
