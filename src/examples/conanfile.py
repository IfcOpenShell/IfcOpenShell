from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os
import os.path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(os.path.join(self.folders.build_folder, "arbitrary_open_profile_def"), env="conanrun")
            os.path.exists("arbitrary_open_profile_def.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "composite_profile_def"), env="conanrun")
            os.path.exists("composite_profile_def.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "csg_primitive"), env="conanrun")
            os.path.exists("csg_primitive.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "ellipse_pies"), env="conanrun")
            os.path.exists("ellipse_pies.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "faces"), env="conanrun")
            os.path.exists("faces.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "ifc_curve_rebar"), env="conanrun")
            os.path.exists("ifc_curve_rebar.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "profiles"), env="conanrun")
            os.path.exists("IfcUShapeProfileDef.ifc")
            os.path.exists("IfcTShapeProfileDef.ifc")
            os.path.exists("IfcZShapeProfileDef.ifc")
            os.path.exists("IfcEllipseProfileDef.ifc")
            os.path.exists("IfcIShapeProfileDef.ifc")
            os.path.exists("IfcLShapeProfileDef.ifc")
            os.path.exists("IfcCShapeProfileDef.ifc")
            os.path.exists("IfcCircleProfileDef.ifc")
            os.path.exists("IfcRectangleProfileDef.ifc")
            os.path.exists("IfcTrapeziumProfileDef.ifc")
            self.run(
                os.path.join(self.cpp.build.bindir, "IfcParseExamples ")
                + os.path.join(self.folders.source_folder, "IfcParseExamples_test.ifc"),
                env="conanrun",
            )
            self.run(os.path.join(self.cpp.build.bindir, "IfcOpenHouse"), env="conanrun")
            os.path.exists("IfcOpenHouse.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "IfcAdvancedHouse"), env="conanrun")
            os.path.exists("IfcAdvancedHouse.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "IfcAlignment"), env="conanrun")
            os.path.exists("IfcAlignment.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "IfcSimplifiedAlignment"), env="conanrun")
            os.path.exists("IfcSimplifiedAlignment.ifc")
            self.run(os.path.join(self.cpp.build.bindir, "triangulated_faceset"), env="conanrun")
            os.path.exists("triangulated_faceset.ifc")
