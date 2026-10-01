"""Conan 2 recipe for src/ifcviewer-web (Emscripten / WebAssembly build).

Place this file next to src/ifcviewer-web/CMakeLists.txt.

Usage (from src/ifcviewer-web):

    conan build . -pr:b=default -pr:h=profiles/emscripten --build=missing
    python3 -m http.server --directory build/Release 8080
    # open http://localhost:8080/IfcViewerWeb.html

Note: CMakeLists.txt does add_subdirectory(../ifcviewer), so the recipe must be
built in-place (`conan build` / `conan install` + `conan build`) inside the
IfcOpenShell checkout. `conan create` would only export this directory and
therefore miss ../ifcviewer.
"""
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy

required_conan_version = ">=2.0"


class IfcViewerWebConan(ConanFile):
    name = "ifcviewer-web"
    version = "0.1.0"
    description = "IfcViewer web (Emscripten + WebGPU) build"
    license = "LGPL-3.0-or-later"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    # ------------------------------------------------------------------ deps
    def requirements(self):
        # Header-only; found through find_package(Eigen3) in ../ifcviewer.
        # (wgpu_native is a no-op under EMSCRIPTEN, zstd is vendored.)
        self.requires("eigen/3.4.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")
        self.tool_requires("ninja/[>=1.11]")
        # Provides emcc/em++ and exposes Emscripten.cmake through
        # tools.cmake.cmaketoolchain:user_toolchain, so no `emcmake` is needed.
        self.tool_requires("emsdk/3.1.73")

    def validate(self):
        if self.settings.os != "Emscripten":
            raise ConanInvalidConfiguration(
                "ifcviewer-web only builds for Emscripten. "
                "Use a wasm host profile: -pr:h=profiles/emscripten"
            )

    # ---------------------------------------------------------------- layout
    def layout(self):
        cmake_layout(self)  # sources in ".", build in build/<build_type>

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()
        CMakeDeps(self).generate()

    # ----------------------------------------------------------------- build
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # The CMakeLists has no install() rules; the wasm and the static pages
        # are emitted at the root of the build directory.
        dist = os.path.join(self.package_folder, "dist")
        for pattern in ("IfcViewerWeb.js", "IfcViewerWeb.wasm", "ifcviewer.js", "*.html"):
            copy(self, pattern, src=self.build_folder, dst=dist, keep_path=False)
        copy(self, "package.json", src=self.source_folder, dst=self.package_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["dist"]
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []