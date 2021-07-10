import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        return ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcStructuralAnalysisModel", predefined_type="LOADING_3D"
        )
