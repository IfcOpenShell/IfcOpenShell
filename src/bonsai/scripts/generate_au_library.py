# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# fmt: off
# pylint: skip-file

import bpy
import ifcopenshell
import ifcopenshell.api
import bonsai.tool as tool


class LibraryGenerator:
    def generate(self):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.materials = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProject", name="Australian Library"
        )
        self.library = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name="Australian Library"
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[self.library], relating_context=self.project
        )
        unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])

        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        plan = ifcopenshell.api.run("context.add_context", self.file, context_type="Plan")
        self.representations = {
            "model_body": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=model,
            ),
            "plan_body": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Plan",
                context_identifier="Annotation",
                target_view="PLAN_VIEW",
                parent=plan,
            ),
        }

        self.materials = {
            "TBD": {"Category": "other"},
            "BRK": {"Category": "brick"},
            "BLK": {"Category": "block"},
            "CON": {"Category": "concrete"},
            "WD": {"Category": "wood"},
            "ST": {"Category": "steel"},
            "AL": {"Category": "aluminium"},
            "GLZ": {"Category": "glass"},
            "PBD": {"Category": "gypsum"},
            "AIR": {"Category": "air"},
            "MEM": {"Category": "membrane"},
        }

        for name, data in self.materials.items():
            self.materials[name]["ifc"] = ifcopenshell.api.run("material.add_material", self.file, name=name)
            self.materials[name]["ifc"].Category = data["Category"]

        self.layer_types = {
            "WAL01": {"type": "IfcWallType", "Description": "110mm Single brick",
                "Layers": [("LoadBearing", "BRK", 110)]},
            "WAL02": {"type": "IfcWallType", "Description": "250mm Brick veneer",
                "Layers": [("Finish", "BRK", 110), ("Ventilation", "AIR", 50), ("LoadBearing", "WD", 90)]},
            "WAL03": {"type": "IfcWallType", "Description": "270mm Double brick",
                "Layers": [("Finish", "BRK", 110), ("Ventilation", "AIR", 50), ("LoadBearing", "BRK", 110)]},
            "WAL04": {"type": "IfcWallType", "Description": "150mm Reinforced concrete",
                "Layers": [("LoadBearing", "CON", 150)]},
            "WAL05": {"type": "IfcWallType", "Description": "200mm Reinforced concrete",
                "Layers": [("LoadBearing", "CON", 200)]},
            "WAL06": {"type": "IfcWallType", "Description": "250mm Reinforced concrete",
                "Layers": [("LoadBearing", "CON", 250)]},
            "WAL07": {"type": "IfcWallType", "Description": "300mm Reinforced concrete",
                "Layers": [("LoadBearing", "CON", 300)]},
            "WAL08": {"type": "IfcWallType", "Description": "140mm Hollow core block",
                "Layers": [("LoadBearing", "BLK", 190)]},
            "WAL09": {"type": "IfcWallType", "Description": "140mm Core filled block",
                "Layers": [("LoadBearing", "BLK", 190)]},
            "WAL10": {"type": "IfcWallType", "Description": "190mm Hollow core block",
                "Layers": [("LoadBearing", "BLK", 190)]},
            "WAL11": {"type": "IfcWallType", "Description": "190mm Core filled block",
                "Layers": [("LoadBearing", "BLK", 190)]},
            "WAL12": {"type": "IfcWallType", "Description": "90mm Wooden frame",
                "Layers": [("LoadBearing", "WD", 90)]},
            "WAL13": {"type": "IfcWallType", "Description": "64mm Steel frame",
                "Layers": [("LoadBearing", "ST", 64)]},
            "CLD01": {"type": "IfcCoveringType", "Description": "110mm Face brick",
                "Layers": [("LoadBearing", "BRK", 110)]},
            "CLD02": {"type": "IfcCoveringType", "Description": "13mm Plasterboard lining",
                "Layers": [("LoadBearing", "PBD", 13)]},
        }

        for name, data in self.layer_types.items():
            self.layer_types[name]["ifc"] = self.create_layer_set_type(name, data)

        product = self.create_layer_type("IfcCoveringType", "DEMO20", 0.02)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=product, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"LayerSetDirection": "AXIS2"})

        product = self.create_layer_type("IfcCoveringType", "DEMO30", 0.03)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=product, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"LayerSetDirection": "AXIS3"})

        self.create_layer_type("IfcRampType", "DEMO200", 0.2)

        profile = self.file.create_entity("IfcCircleProfileDef", ProfileType="AREA", Radius=0.3)
        self.create_profile_type("IfcPileType", "DEMO1", profile)

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
            ProfileName="DEMO-I",
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
            ProfileName="DEMO-C",
            ProfileType="AREA",
            Depth=0.2,
            Width=0.1,
            WallThickness=0.0015,
            Girth=0.03,
            InternalFilletRadius=0.005,
        )
        self.create_profile_type("IfcBeamType", "DEMO2", profile)

        self.create_type("IfcWindowType", "DEMO1", {"model_body": "Window", "plan_body": "Window-Annotation"})
        self.create_type("IfcDoorType", "DEMO1", {"model_body": "Door", "plan_body": "Door-Annotation"})
        self.create_type("IfcFurnitureType", "BUNNY", {"model_body": "Bunny", "plan_body": "Bunny-Annotation"})

        self.file.write("bonsai-au-library.ifc")

    def create_layer_set_type(self, name, data):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=data["type"], name=name)
        element.Description = data["Description"]
        rel = ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialLayerSet")
        layer_set = rel.RelatingMaterial
        for layer_data in data["Layers"]:
            layer = ifcopenshell.api.run(
                "material.add_layer", self.file, layer_set=layer_set, material=self.materials[layer_data[1]]["ifc"]
            )
            layer.Name = layer_data[0]
            layer.LayerThickness = layer_data[2]
        ifcopenshell.api.run("project.assign_declaration", self.file, definitions=[element], relating_context=self.library)
        return element

    def create_layer_type(self, ifc_class, name, thickness):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialLayerSet")
        layer_set = rel.RelatingMaterial
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=layer_set, material=self.materials["TBD"]["ifc"])
        layer.LayerThickness = thickness
        ifcopenshell.api.run("project.assign_declaration", self.file, definitions=[element], relating_context=self.library)
        return element

    def create_profile_type(self, ifc_class, name, profile):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialProfileSet")
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.run(
            "material.add_profile", self.file, profile_set=profile_set, material=self.materials["TBD"]["ifc"]
        )
        ifcopenshell.api.run("material.assign_profile", self.file, material_profile=material_profile, profile=profile)
        ifcopenshell.api.run("project.assign_declaration", self.file, definitions=[element], relating_context=self.library)

    def create_type(self, ifc_class, name, representations):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        for rep_name, obj_name in representations.items():
            obj = bpy.data.objects.get(obj_name)
            representation = ifcopenshell.api.run(
                "geometry.add_representation",
                self.file,
                context=self.representations[rep_name],
                blender_object=obj,
                geometry=obj.data,
                total_items=max(1, len(obj.material_slots)),
            )
            styles = []
            for slot in obj.material_slots:
                style = ifcopenshell.api.run("style.add_style", self.file, name=slot.material.name)
                ifcopenshell.api.run(
                    "style.add_surface_style",
                    self.file,
                    style=style,
                    ifc_class="IfcSurfaceStyleRendering",
                    attributes=tool.Style.get_surface_rendering_attributes(slot.material),
                )
                styles.append(style)
            if styles:
                ifcopenshell.api.run(
                    "style.assign_representation_styles", self.file, shape_representation=representation, styles=styles
                )
            ifcopenshell.api.run(
                "geometry.assign_representation", self.file, product=element, representation=representation
            )
        ifcopenshell.api.run("project.assign_declaration", self.file, definitions=[element], relating_context=self.library)


LibraryGenerator().generate()
