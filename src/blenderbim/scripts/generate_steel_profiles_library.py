# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 @Andrej730
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

# fmt: off
# pylint: skip-file

import ifcopenshell
import ifcopenshell.api
import boltspy as bolts


class LibraryGenerator:
    def generate(self, parse_profiles_type="EU", output_filename="IFC4 EU Steel.ifc"):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.materials = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProject", name=f"{parse_profiles_type} Steel Profiles Library"
        )
        self.library = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name=f"{parse_profiles_type} Steel Profiles Library"
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definition=self.library, relating_context=self.project
        )
        unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])

        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        plan = ifcopenshell.api.run("context.add_context", self.file, context_type="Plan")
        self.representations = {
            "body": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=model,
            ),
            "annotation": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Plan",
                context_identifier="Annotation",
                target_view="PLAN_VIEW",
                parent=plan,
            ),
        }

        self.material = ifcopenshell.api.run("material.add_material", self.file, name="Unknown")

        # parameters could be optional (example: welded i-beams don't have FilletRadius)
        profiles_translation = {
            "profile_i": ("IfcIShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "OverallDepth", "b": "OverallWidth", "r": "FilletRadius"}),
            "profile_z": ("IfcZShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "Depth", "c1": "FlangeWidth"}),
            "profile_c": ("IfcUShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "Depth", "b": "FlangeWidth", "r": "FilletRadius"}),
            "profile_l*_equal": ("IfcLShapeProfileDef", {"a": "Depth", "t": "Thickness", "r1": "FilletRadius", "r2": "EdgeRadius"}),
            "profile_l*_unequal": ("IfcLShapeProfileDef", {"a": "Depth", "b": "Width", "t": "Thickness", "r1": "FilletRadius", "r2": "EdgeRadius"}),
            "profile_hollow*_circle": ("IfcCircleHollowProfileDef", {"t": "WallThickness", "D": "Radius"}),
            "profile_hollow*_square": ("IfcRectangleHollowProfileDef", {"t": "WallThickness", "b": "XDim", "ri": "InnerFilletRadius", "ro": "OuterFilletRadius"}),
            "profile_hollow*_rectangular": ("IfcRectangleHollowProfileDef", {"t": "WallThickness", "b": "XDim", "h": "YDim", "ri": "InnerFilletRadius", "ro": "OuterFilletRadius"}),
        }

        if parse_profiles_type == "AU":
            bolt_class_filter = lambda x: "bluescope" in x.id
        elif parse_profiles_type == "EU":
            bolt_class_filter = lambda x: "bluescope" not in x.id
        else:
            bolt_class_filter = lambda x: True

        for prof_type in profiles_translation:
            ifc_profile_name, ifc_params_translation = profiles_translation[prof_type]
            col_name, _, prof_keyword = prof_type.partition("*")
            bolt_col = bolts.repo.collections[col_name]

            for bolt_class in bolts.repo.collection_classes.get_dsts(bolt_col):
                if not bolt_class_filter(bolt_class):
                    continue

                if prof_keyword and prof_keyword not in bolt_class.id:
                    continue
                
                if not bolt_class.parameters.tables:
                    # some bolt classes have no data attached
                    # like hollow_generic_square
                    continue

                bolts_cols = bolt_class.parameters.tables[0].columns
                bolts_cols = [ifc_params_translation.get(c, "unused") for c in bolts_cols]
                bolts_data = bolt_class.parameters.tables[0].data

                for prof_name in bolts_data.keys():
                    ifc_params = dict(zip(bolts_cols, bolts_data[prof_name]))
                    if "unused" in ifc_params:
                        del ifc_params["unused"]

                    if prof_type == "profile_hollow*_square":
                        ifc_params["YDim"] = ifc_params["XDim"]
                    elif prof_type == "profile_hollow*_circle":
                        # by default bolts provides diameter, so we need to convert it to radius
                        ifc_params["Radius"] /= 2
                    
                    # profile is setup by type of profile and by supplying it's parameters
                    # ProfileType stays AREA
                    profile = self.file.create_entity(ifc_profile_name, ProfileName=prof_name, ProfileType="AREA", **ifc_params)

                    # building profiles for each of 3 types
                    self.create_profile_type("IfcBeamType", prof_name, profile)
                    self.create_profile_type("IfcMemberType", prof_name, profile)
                    self.create_profile_type("IfcColumnType", prof_name, profile)

        self.file.write(output_filename)

    def create_layer_set_type(self, name, data):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=data["type"], name=name)
        element.Description = data["Description"]
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSet")
        layer_set = rel.RelatingMaterial
        for layer_data in data["Layers"]:
            layer = ifcopenshell.api.run(
                "material.add_layer", self.file, layer_set=layer_set, material=self.materials[layer_data[1]]["ifc"]
            )
            layer.Name = layer_data[0]
            layer.LayerThickness = layer_data[2]
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.library)
        return element

    def create_layer_type(self, ifc_class, name, thickness):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSet")
        layer_set = rel.RelatingMaterial
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=layer_set, material=self.materials["TBD"]["ifc"])
        layer.LayerThickness = thickness
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.library)
        return element

    def create_profile_type(self, ifc_class, name, profile):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialProfileSet")
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.run(
            "material.add_profile", self.file, profile_set=profile_set, material=self.material
            # material=self.materials["TBD"]["ifc"]
        )
        ifcopenshell.api.run("material.assign_profile", self.file, material_profile=material_profile, profile=profile)
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.library)

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
        ifcopenshell.api.run("project.assign_declaration", self.file, definition=element, relating_context=self.library)


if __name__ == "__main__":
    LibraryGenerator().generate(parse_profiles_type="EU", output_filename="..\\blenderbim\\bim\\data\\libraries\\IFC4 EU Steel.ifc")
    LibraryGenerator().generate(parse_profiles_type="AU", output_filename="..\\blenderbim\\bim\\data\\libraries\\IFC4 AU Steel.ifc")

# C:\Projects\GitHub\IfcOpenShell\src\blenderbim\scripts\generate_steel_profiles_library.py
# C:\Projects\GitHub\IfcOpenShell\src\blenderbimIFC4 AU Steel.ifc