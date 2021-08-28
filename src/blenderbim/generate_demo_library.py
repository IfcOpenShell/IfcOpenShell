
# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api


class LibraryGenerator:
    def generate(self):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name="BlenderBIM Demo Library"
        )
        ifcopenshell.api.run("unit.assign_unit", self.file, length={"is_metric": True, "raw": "METERS"})
        ifcopenshell.api.run("context.add_context", self.file, context="Model")
        self.representations = {
            "body": ifcopenshell.api.run(
                "context.add_context", self.file, context="Model", subcontext="Body", target_view="MODEL_VIEW"
            )
        }
        ifcopenshell.api.run("context.add_context", self.file, context="Plan")
        self.annotation = ifcopenshell.api.run(
            "context.add_context", self.file, context="Model", subcontext="Annotation", target_view="PLAN_VIEW"
        )

        self.material = ifcopenshell.api.run("material.add_material", self.file, name="Unknown")

        self.create_layer_type("IfcWallType", "DEMO50", 0.05)
        self.create_layer_type("IfcWallType", "DEMO100", 0.1)
        self.create_layer_type("IfcWallType", "DEMO200", 0.2)
        self.create_layer_type("IfcWallType", "DEMO300", 0.3)

        self.create_layer_type("IfcCoveringType", "DEMO10", 0.01)

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

        self.create_type("IfcWindowType", "DEMO1", {"body": "Window"})
        self.create_type("IfcDoorType", "DEMO1", {"body": "Door"})

        self.file.write("blenderbim-demo-library.ifc")

    def create_layer_type(self, ifc_class, name, thickness):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSet")
        layer_set = rel.RelatingMaterial
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=layer_set, material=self.material)
        layer.LayerThickness = thickness
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.project)
        return element

    def create_profile_type(self, ifc_class, name, profile):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialProfileSet")
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.run(
            "material.add_profile", self.file, profile_set=profile_set, material=self.material
        )
        ifcopenshell.api.run("material.assign_profile", self.file, material_profile=material_profile, profile=profile)
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.project)

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
            ifcopenshell.api.run(
                "style.assign_representation_styles",
                self.file,
                **{
                    "shape_representation": representation,
                    "styles": [
                        ifcopenshell.api.run("style.add_style", self.file, **self.get_style_settings(s.material))
                        for s in obj.material_slots
                    ],
                },
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", self.file, product=element, representation=representation
            )
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.project)

    def get_style_settings(self, material):
        transparency = material.diffuse_color[3]
        diffuse_colour = material.diffuse_color
        if (
            material.use_nodes
            and hasattr(material.node_tree, "nodes")
            and "Principled BSDF" in material.node_tree.nodes
        ):
            bsdf = material.node_tree.nodes["Principled BSDF"]
            transparency = bsdf.inputs["Alpha"].default_value
            diffuse_colour = bsdf.inputs["Base Color"].default_value
        transparency = 1 - transparency
        return {
            "name": material.name,
            "external_definition": None,
            "surface_colour": tuple(material.diffuse_color),
            "transparency": transparency,
            "diffuse_colour": tuple(diffuse_colour),
        }


LibraryGenerator().generate()
