# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 @Andrej730
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

import ifcopenshell
import ifcopenshell.api
import boltspy as bolts
from math import cos, pi
from pathlib import Path
from ifcopenshell.util.shape_builder import ShapeBuilder, V


class LibraryGenerator:
    def generate(self, parse_profiles_type="EU", output_filename="IFC4 EU Steel.ifc"):
        print(f'Generating {parse_profiles_type} steel library "{output_filename}"')
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
            "project.assign_declaration", self.file, definitions=[self.library], relating_context=self.project
        )
        dim_exponents = self.file.createIfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0)
        length_unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        builder = ShapeBuilder(self.file)

        # define angle unit to use degrees for IfcPlaneAngleMeasure:
        # https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPlaneAngleMeasure.htm
        angle_unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="PLANEANGLEUNIT")
        value_component =  self.file.createIfcReal(pi/180)
        angle_unit = self.file.createIfcMeasureWithUnit(ValueComponent=value_component, UnitComponent=angle_unit)
        angle_unit = self.file.createIfcConversionBasedUnit(Name="degree", Dimensions=dim_exponents, UnitType="PLANEANGLEUNIT", ConversionFactor=angle_unit)
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[length_unit, angle_unit])

        self.material = ifcopenshell.api.run("material.add_material", self.file, name="Unknown")

        # NOTE: parameters could be optional (example: welded i-beams don't have FilletRadius)
        profiles_translation = {
            "profile_i": ("IfcIShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "OverallDepth", "b": "OverallWidth", "r": "FilletRadius", "sf": "FlangeSlope", "r1": "FilletRadius", "r2": "FlangeEdgeRadius"}),
            "profile_t": ("IfcTShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "Depth", "b": "FlangeWidth", "r": "FilletRadius", "r1": "FilletRadius", "r2": "FlangeEdgeRadius"}),

            "profile_z": ("IfcZShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "Depth", "c1": "FlangeWidth"}),
            "profile_z_lips": ("IfcArbitraryClosedProfileDef", {"t": "WallThickness", "c1": "FirstFlangeWidth", "c2": "SecondFlangeWidth", "h": "Depth", "r": "FilletRadius", "ll": "Girth"}),

            "profile_c": ("IfcUShapeProfileDef", {"tw": "WebThickness", "tf": "FlangeThickness", "h": "Depth", "b": "FlangeWidth", "r": "FilletRadius", "sf": "FlangeSlope", "r1": "FilletRadius", "r2": "EdgeRadius"}),
            "profile_c_lips": ("IfcCShapeProfileDef", {"t": "WallThickness", "b": "Width", "h": "Depth", "ll": "Girth", "r": "InternalFilletRadius"}),
            
            "profile_l*_equal": ("IfcLShapeProfileDef", {"a": "Depth", "t": "Thickness", "r1": "FilletRadius", "r2": "EdgeRadius"}),
            "profile_l*_unequal": ("IfcLShapeProfileDef", {"a": "Depth", "b": "Width", "t": "Thickness", "r1": "FilletRadius", "r2": "EdgeRadius"}),
            "profile_l*lbeam_l_imp": ("IfcLShapeProfileDef", {"a": "Depth", "b": "Width", "t": "Thickness", "r1": "FilletRadius", "r2": "EdgeRadius"}),
            "profile_l*lbeam_2l": ("IfcLShapeProfileDef", {"a": "Depth", "b": "Width", "t": "Thickness", "g": "ProfilesGap"}),
            
            "profile_hollow*_circle": ("IfcCircleHollowProfileDef", {"t": "WallThickness", "D": "Radius"}),
            "profile_hollow*pipe_imp": ("IfcCircleHollowProfileDef", {"t": "WallThickness", "D": "Radius"}),
            "profile_hollow*_square": ("IfcRectangleHollowProfileDef", {"t": "WallThickness", "b": "XDim", "ri": "InnerFilletRadius", "ro": "OuterFilletRadius"}),
            "profile_hollow*_rectangular": ("IfcRectangleHollowProfileDef", {"t": "WallThickness", "b": "XDim", "h": "YDim", "ri": "InnerFilletRadius", "ro": "OuterFilletRadius"}),
        }

        processed_profiles = set()
        def bolt_class_filter(x):
            identified_type = ""

            if "bluescope" in x.id:
                identified_type = "AU"
            elif x.id.endswith("_imp"):
                identified_type = "US"
            else:
                identified_type = "EU"

            return parse_profiles_type == identified_type

        for prof_type in profiles_translation:
            ifc_profile_name, ifc_params_translation = profiles_translation[prof_type]
            # prof_keyword == "" if there is no "*"
            col_name, _, prof_keyword = prof_type.partition("*")
            bolt_col = bolts.repo.collections[col_name]

            for bolt_class in bolts.repo.collection_classes.get_dsts(bolt_col):
                if bolt_class.id in processed_profiles:
                    continue

                if not bolt_class_filter(bolt_class):
                    continue

                if prof_keyword and prof_keyword not in bolt_class.id:
                    continue
                
                if not bolt_class.parameters.tables:
                    # some bolt classes have no data attached
                    # like hollow_generic_square
                    continue

                print(f'Processing {bolt_class.id}')

                bolts_cols_original = bolt_class.parameters.tables[0].columns
                bolts_cols = [ifc_params_translation.get(c, "unused") for c in bolts_cols_original]
                
                inch_to_mm = lambda x: x * 0.0254 * 1000
                def assure_data_units_is_mm(data, units):
                    data = data.copy()
                    for i in range(len(units)):
                        unit = units[i]
                        assert unit in ("Length (in)", "Length (mm)", "Angle (deg)"), f"Unit {unit} is not supported"

                        if unit != "Length (in)":
                            continue
                        for profile in data:
                            data[profile][i] = inch_to_mm(data[profile][i])
                    return data
                
                bolts_data = bolt_class.parameters.tables[0].data
                data_units = [bolt_class.parameters.types[col] for col in bolts_cols_original]
                bolts_data = assure_data_units_is_mm(bolts_data, data_units)

                for prof_name in bolts_data.keys():
                    ifc_params = dict(zip(bolts_cols, bolts_data[prof_name], strict=True))
                    if "unused" in ifc_params:
                        del ifc_params["unused"]

                    if prof_type == "profile_hollow*_square":
                        ifc_params["YDim"] = ifc_params["XDim"]
                    elif ifc_profile_name == "IfcCircleHollowProfileDef":
                        # by default bolts provides diameter, so we need to convert it to radius
                        ifc_params["Radius"] /= 2
                    elif prof_type == "profile_z_lips":
                        ifc_curve = builder.create_z_profile_lips_curve(**ifc_params)
                        ifc_params = {"OuterCurve": ifc_curve}
                    elif prof_type == "profile_l*lbeam_2l":
                        profiles_gap = ifc_params["ProfilesGap"]
                        del ifc_params["ProfilesGap"]
                    
                    # profile is setup by type of profile and by supplying it's parameters
                    # ProfileType stays AREA
                    profile = self.file.create_entity(ifc_profile_name, ProfileName=prof_name, ProfileType="AREA", **ifc_params)

                    if prof_type == "profile_l*lbeam_2l":
                        profile.ProfileName = None # to avoid name confusion
                        mode = "SLBB" if prof_name.endswith("_SLBB") else "LLBB"
                        profile = self.create_double_l_profile(profile, prof_name, profiles_gap, mode)

                    # building profiles for each of 3 types
                    self.create_profile_type("IfcBeamType", prof_name, profile)
                    self.create_profile_type("IfcMemberType", prof_name, profile)
                    self.create_profile_type("IfcColumnType", prof_name, profile)

                processed_profiles.add(bolt_class.id)

        self.file.write(output_filename)
        print('-----------------------')

    def create_profile_type(self, ifc_class, name, profile):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialProfileSet")
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.run(
            "material.add_profile", self.file, profile_set=profile_set, material=self.material
            # material=self.materials["TBD"]["ifc"]
        )
        ifcopenshell.api.run("material.assign_profile", self.file, material_profile=material_profile, profile=profile)
        ifcopenshell.api.run("project.assign_declaration", self.file, definitions=[element], relating_context=self.library)

    def create_double_l_profile(self, profile, resulting_profile_name=None, profiles_gap=0, mode = "LLBB"):
        def create_derived_profile(profile, mirrored=False):
            """
            LLBB mode = long legs back-to-back

            SLBB mode = short legs back-to-back
            """
            derived_profile = self.file.createIfcDerivedProfileDef(
                ParentProfile=profile,
                Operator=self.file.createIfcCartesianTransformationOperator2D(),
                ProfileType=profile.ProfileType
            )
            transform = derived_profile.Operator
            transform.LocalOrigin = self.file.createIfcCartesianPoint()
            if mode == "LLBB":
                offset = profile.Depth/2 + profiles_gap
                if mirrored:
                    transform.Axis1 = self.file.createIfcDirection(V(0, 1))
                    transform.Axis2 = self.file.createIfcDirection(V(-1, 0))
                    transform.LocalOrigin.Coordinates = V(-offset, 0)
                else:
                    transform.LocalOrigin.Coordinates = V(offset, 0)
                    transform.Axis1 = self.file.createIfcDirection(V(0, 1))
                    transform.Axis2 = self.file.createIfcDirection(V(1, 0))
            elif mode == "SLBB":
                offset = profile.Width/2 + profiles_gap
                if mirrored:
                    transform.Axis1 = self.file.createIfcDirection(V(-1, 0))
                    transform.LocalOrigin.Coordinates = V(-offset, 0)
                else:
                    transform.LocalOrigin.Coordinates = V(offset, 0)

            return derived_profile
        
        composite_profile = self.file.createIfcCompositeProfileDef(Profiles=[
                create_derived_profile(profile),
                create_derived_profile(profile, mirrored=True)
            ],
            ProfileType = profile.ProfileType
        )
        composite_profile.ProfileName = resulting_profile_name
        return composite_profile


if __name__ == "__main__":
    path = Path(__file__).parents[1] / "bonsai/bim/data/libraries"
    LibraryGenerator().generate(parse_profiles_type="EU", output_filename=str(path / "IFC4 EU Steel.ifc"))
    LibraryGenerator().generate(parse_profiles_type="AU", output_filename=str(path / "IFC4 AU Steel.ifc"))
    LibraryGenerator().generate(parse_profiles_type="US", output_filename=str(path / "IFC4 US Steel.ifc"))
