import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


class LibraryGenerator:
    def generate(self):
        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name="BlenderBIM Demo Library"
        )
        ifcopenshell.api.run("unit.assign_unit", self.file, length={"is_metric": True, "raw": "METERS"})

        self.material = ifcopenshell.api.run("material.add_material", self.file, name="Unknown")

        self.create_layer_type("IfcWallType", "DEMO50", 0.05)
        self.create_layer_type("IfcWallType", "DEMO100", 0.1)
        self.create_layer_type("IfcWallType", "DEMO200", 0.2)
        self.create_layer_type("IfcWallType", "DEMO300", 0.3)

        self.create_layer_type("IfcSlabType", "DEMO150", 0.2)
        self.create_layer_type("IfcSlabType", "DEMO250", 0.3)

        profile = self.file.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=0.5, YDim=0.6)
        self.create_profile_type("IfcColumnType", "DEMO1", profile)

        profile = self.file.create_entity(
            "IfcCircleHollowProfileDef", ProfileType="AREA", Radius=0.25, WallThickness=0.005
        )
        self.create_profile_type("IfcColumnType", "DEMO2", profile)

        profile = self.file.create_entity(
            "IfcRectangleHollowProfileDef",
            ProfileType="AREA",
            XDim=0.075,
            YDim=0.15,
            WallThickness=0.005,
            InnerFilletRadius=0.005,
            OuterFilletRadius=0.005,
        )
        self.create_profile_type("IfcColumnType", "DEMO3", profile)

        profile = self.file.create_entity(
            "IfcIShapeProfileDef",
            ProfileType="AREA",
            OverallWidth=0.1,
            OverallDepth=0.2,
            WebThickness=0.005,
            FlangeThickness=0.01,
            FilletRadius=0.005,
        )
        self.create_profile_type("IfcBeamType", "DEMO1", profile)

        profile = self.file.create_entity(
            "IfcCShapeProfileDef",
            ProfileType="AREA",
            Depth=0.2,
            Width=0.1,
            WallThickness=0.0015,
            Girth=0.03,
            InternalFilletRadius=0.005,
        )
        self.create_profile_type("IfcBeamType", "DEMO2", profile)

        self.file.write("blenderbim-demo-library.ifc")

    def create_layer_type(self, ifc_class, name, thickness):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSet")
        layer_set = ifcopenshell.util.element.get_material(element)
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=layer_set, material=self.material)
        layer.LayerThickness = thickness
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.project)

    def create_profile_type(self, ifc_class, name, profile):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialProfileSet")
        profile_set = ifcopenshell.util.element.get_material(element)
        material_profile = ifcopenshell.api.run(
            "material.add_profile", self.file, profile_set=profile_set, material=self.material
        )
        ifcopenshell.api.run("material.assign_profile", self.file, material_profile=material_profile, profile=profile)
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.project)


LibraryGenerator().generate()
