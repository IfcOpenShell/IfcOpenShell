class Usecase:
    def __init__(self, file):
        self.file = file

    def execute(self):
        self.file.createIfcOrganization("APTR", "Aperture Science")
