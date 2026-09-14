# This file was generated with the assistance of an AI coding tool.
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import load

required_conan_version = ">=2.1"


class IfcOpenShellConan(ConanFile):
    name = "ifcopenshell"
    license = "LGPL-3.0-or-later"
    homepage = "https://github.com/IfcOpenShell/IfcOpenShell"
    url = "https://github.com/IfcOpenShell/IfcOpenShell"
    description = "Open source IFC library and geometry engine"
    topics = ("ifc", "bim", "building", "3d")
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]

    _schemas = ("2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_ifcgeom": [True, False],
        "build_geomserver": [True, False],
        "build_convert": [True, False],
        "build_convert_with_usd": [True, False],
        "build_convert_with_proj": [True, False],
        "build_convert_with_gltf": [True, False],
        "ifcxml_support": [True, False],
        "use_mmap": [True, False],
        "with_cgal": [True, False],
        "with_hdf5": [True, False],
        "with_rocksdb": [True, False],
        "with_manifold": [True, False],
        "with_ifcpython": [True, False],
        "with_examples": [True, False],
        "with_collada": [True, False],
        "build_bonsaiviewer": [True, False],
    }
    options.update({f"schema_{schema}": [True, False] for schema in _schemas})
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_ifcgeom": True,
        "build_geomserver": False,
        "build_convert": True,
        "build_convert_with_usd": False,
        "build_convert_with_proj": False,
        "build_convert_with_gltf": False,
        "ifcxml_support": True,
        "use_mmap": False,
        "with_cgal": True,
        "with_hdf5": False,
        "with_rocksdb": False,
        "with_manifold": False,
        "with_ifcpython": True,
        "with_examples": False,
        "with_collada": False,
        "build_bonsaiviewer": False,
    }
    default_options.update({f"schema_{schema}": schema in ("2x3", "4", "4x3_add2") for schema in _schemas})
    exports_sources = (
        "aws/**",
        "cmake/**",
        "src/**",
        "docs/**",
        "VERSION",
        "*.md",
        "!**/node_modules/**",
        "!**/__pycache__/**",
    )

    def set_version(self):
        self.version = load(self, "VERSION").strip()

    def _selected_schemas(self):
        return [schema for schema in self._schemas if self.options.get_safe(f"schema_{schema}")]

    def config_options(self):
        if self.settings.os == "Emscripten":
            for option in (
                "build_ifcgeom",
                "build_geomserver",
                "build_convert",
                "build_convert_with_usd",
                "build_convert_with_proj",
                "build_bonsaiviewer",
                "ifcxml_support",
                "use_mmap",
                "with_cgal",
                "with_hdf5",
                "with_rocksdb",
                "with_manifold",
            ):
                setattr(self.options, option, False)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.build_ifcgeom:
            self.options.with_cgal = False
            self.options.with_manifold = False

    def layout(self):
        cmake_layout(self, src_folder="cmake")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.build_convert and not self.options.build_ifcgeom:
            raise ConanInvalidConfiguration("build_convert requires build_ifcgeom")
        if self.options.build_bonsaiviewer and not self.options.build_ifcgeom:
            raise ConanInvalidConfiguration("build_bonsaiviewer requires build_ifcgeom")

    def requirements(self):
        self.requires("boost/[>=1.86 <2.0]", transitive_headers=True, transitive_libs=True, force=True)
        if self.options.ifcxml_support or self.options.with_cgal:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.build_ifcgeom:
            self.requires("opencascade/[>=7.8 <8]", transitive_headers=True, transitive_libs=True)
            self.requires("eigen/3.4.0", transitive_headers=True)
            if self.options.with_cgal:
                self.requires("cgal/[>=5.6 <6]", transitive_headers=True, transitive_libs=True)
            if self.options.with_manifold:
                self.requires("manifold/[>=3.0 <4]", transitive_headers=True, transitive_libs=True)
        if self.options.with_hdf5:
            self.requires("hdf5/[>=1.8 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_rocksdb:
            self.requires(
                "rocksdb/[>=10.5 <11]", options={"use_rtti": True}, transitive_headers=True, transitive_libs=True
            )
            self.requires("zstd/[>=1.5 <1.6]")
        if self.options.build_convert_with_usd:
            self.requires("openusd/25.11")
        if self.options.build_convert_with_proj:
            self.requires("proj/9.7.0")
        if self.options.build_convert_with_gltf:
            self.requires("nlohmann_json/3.11.3")
        if self.options.build_bonsaiviewer:
            self.requires("qt/6.8.3")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <5]")
        if self.options.with_ifcpython:
            self.tool_requires("swig/[>=4.2 <5]")

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables.update(
            {
                "BUILD_SHARED_LIBS": self.options.shared,
                "SCHEMA_VERSIONS": ";".join(self._selected_schemas()),
                "BUILD_IFCGEOM": self.options.build_ifcgeom,
                "BUILD_GEOMSERVER": self.options.build_geomserver,
                "BUILD_CONVERT": self.options.build_convert,
                "USD_SUPPORT": self.options.build_convert_with_usd,
                "WITH_PROJ": self.options.build_convert_with_proj,
                "GLTF_SUPPORT": self.options.build_convert_with_gltf,
                "IFCXML_SUPPORT": self.options.ifcxml_support,
                "USE_MMAP": self.options.use_mmap,
                "WITH_OPENCASCADE": self.options.build_ifcgeom,
                "WITH_CGAL": self.options.get_safe("with_cgal", False),
                "WITH_MANIFOLD": self.options.get_safe("with_manifold", False),
                "HDF5_SUPPORT": self.options.with_hdf5,
                "WITH_ROCKSDB": self.options.with_rocksdb,
                "BUILD_IFCPYTHON": self.options.with_ifcpython,
                "BUILD_EXAMPLES": self.options.with_examples,
                "COLLADA_SUPPORT": self.options.with_collada,
                "BUILD_BONSAIVIEWER": self.options.build_bonsaiviewer,
                "BUILD_PACKAGE": True,
            }
        )
        toolchain.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["-v"])

    def package(self):
        CMake(self).install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "IfcOpenShell")
        self.cpp_info.set_property("cmake_target_name", "IfcOpenShell::IfcOpenShell")
        self.cpp_info.libs = ["IfcParse", "IfcGeom"]
        if self.options.build_convert:
            self.cpp_info.libs.append("Serializers")
        if self.options.shared:
            self.cpp_info.defines.append("IFC_SHARED_BUILD")
