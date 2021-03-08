import ifcopenshell
import ifcopenshell.util.schema


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        self.new = ifcopenshell.file(schema=self.args[0])
        migrator = ifcopenshell.util.schema.Migrator()
        for element in self.file:
            print("Migrating", element)
            print("Successfully converted to", migrator.migrate(element, self.new))
        self.file = self.new
