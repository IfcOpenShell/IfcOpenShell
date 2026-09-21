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
    homepage = "https://ifcopenshell.org/"
    url = "https://github.com/IfcOpenShell/IfcOpenShell"
    description = "Open source IFC library and geometry engine"
    topics = ("ifc", "bim", "building", "3d")
    settings = "os", "arch", "compiler", "build_type"

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
        "build_geomserver": True,
        "build_convert": True,
        "build_convert_with_usd": False,
        "build_convert_with_proj": False,
        "build_convert_with_gltf": False,
        "ifcxml_support": False,
        "use_mmap": False,
        "with_cgal": True,
        "with_rocksdb": True,
        "with_manifold": True,
        "with_ifcpython": True,
        "with_examples": True,
        "with_collada": True,
        "build_bonsaiviewer": True,
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
                "with_collada",
                "build_bonsaiviewer",
                "ifcxml_support",
                "use_mmap",
                "with_cgal",
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
            # Without tk to avoid "src/unix/../generic/tkEntry.c:3226:15: error: expected identifier or ‘(’ before ‘bool’" error with shared build
            self.requires(
                "opencascade/[>=7.8 <8]", options={"with_tk": False}, transitive_headers=True, transitive_libs=True
            )
            self.requires("eigen/3.4.0", transitive_headers=True)
            if self.options.with_cgal:
                self.requires("cgal/[>=5.6 <6]", transitive_headers=True, transitive_libs=True)
            if self.options.with_manifold:
                self.requires("manifold/[>=3.0 <4]", transitive_headers=True, transitive_libs=True)
        if self.options.with_rocksdb:
            self.requires(
                "rocksdb/[>=10.5 <11]",
                options={"use_rtti": True, "with_zstd": True},
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_rocksdb or self.options.build_bonsaiviewer:
            self.requires("zstd/[>=1.5 <1.6]")
        if self.options.build_convert_with_usd:
            self.requires("openusd/26.08", options={"opensubdiv/*:with_tbb": True})
        if self.options.build_convert_with_proj:
            self.requires("proj/9.7.0")
        if self.options.build_convert_with_gltf:
            self.requires("nlohmann_json/3.11.3")
        if self.options.with_collada:
            self.requires("opencollada/1.6.68")
        if self.options.build_bonsaiviewer:
            self.requires("qt/6.11.1", options={"qtsvg": True})
            self.requires("fontconfig/2.14.2", override=True)

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
                "WITH_ROCKSDB": self.options.with_rocksdb,
                "BUILD_IFCPYTHON": self.options.with_ifcpython,
                "BUILD_EXAMPLES": self.options.with_examples,
                "COLLADA_SUPPORT": self.options.with_collada,
                "BUILD_BONSAIVIEWER": self.options.build_bonsaiviewer,
                "WASM_BUILD": self.settings.os == "Emscripten",
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
        self.cpp_info.cmake_extra_variables = [f"SCHEMA_VERSIONS=({')('.join(self._selected_schemas())})"]

        if self.options.with_ifcpython:
            self.cpp_info.requires = ["svgpp::svgpp"]

        def _add_component(name, requires=None):
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", f"IfcOpenShell::{name}")
            component.libs = [name]
            component.requires = requires or []
            return component

        ifcparse = _add_component(
            "IfcParse",
            requires=[
                # "boost::system",
                "boost::program_options",
                "boost::regex",
                "boost::thread",
                "boost::date_time",
            ],
        )
        ifcparse.defines.append(f"SCHEMA_SEQ=({')('.join(self._selected_schemas())})")
        if self.options.use_mmap:
            ifcparse.requires.extend(
                [
                    "boost::iostreams",
                    "boost::filesystem",
                ]
            )
            ifcparse.defines.append("USE_MMAP")
        if self.options.ifcxml_support:
            ifcparse.requires.append("libxml2::libxml2")
            ifcparse.defines.append("WITH_IFCXML")
        if self.options.with_rocksdb:
            ifcparse.requires.append("rocksdb::rocksdb")
            ifcparse.defines.append("IFOPSH_WITH_ROCKSDB")

        for schema in self._selected_schemas():
            ifcparse.defines.append(f"HAS_SCHEMA_{schema}")
        if self.options.shared:
            ifcparse.defines.append("IFC_SHARED_BUILD")
        if self.settings.os in ["Linux", "FreeBSD"]:
            ifcparse.system_libs = ["m", "dl"]

        if self.options.build_ifcgeom:
            ifcgeom = _add_component("IfcGeom", requires=["IfcParse", "eigen::eigen"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                ifcgeom.system_libs.append("pthread")

            # When kernels, mappings and geometry_serializers are built as OBJECT target, we define conan dependencies directly to IfcGeom
            if self.options.get_safe("with_cgal"):
                ifcgeom.defines.append("IFOPSH_WITH_CGAL")
                ifcgeom.requires += ["cgal::cgal", "eigen::eigen"]
            ifcgeom.requires += [
                "opencascade::occt_tkernel",
                "opencascade::occt_tkmath",
                "opencascade::occt_tkbrep",
                "opencascade::occt_tkgeombase",
                "opencascade::occt_tkgeomalgo",
                "opencascade::occt_tkg3d",
                "opencascade::occt_tkg2d",
                "opencascade::occt_tkshhealing",
                "opencascade::occt_tktopalgo",
                "opencascade::occt_tkmesh",
                "opencascade::occt_tkprim",
                "opencascade::occt_tkbool",
                "opencascade::occt_tkbo",
                "opencascade::occt_tkfillet",
                "opencascade::occt_tkxsbase",
                "opencascade::occt_tkoffset",
                "opencascade::occt_tkhlr",
                "eigen::eigen",
            ]
            ifcgeom.defines.append("IFOPSH_WITH_OPENCASCADE")

        if self.options.build_convert:
            serializers = _add_component("Serializers", requires=["IfcGeom"])
            if self.options.with_hdf5:
                serializers.requires.append("hdf5::hdf5_cpp")
            if self.options.with_rocksdb:
                serializers.requires.append("rocksdb::librocksdb")
            if self.options.build_convert_with_usd:
                serializers.requires.append("usd::usd")
            if self.options.build_convert_with_proj:
                serializers.requires.append("proj::proj")

            geometry_serializer = _add_component(
                "geometry_serializer",
                ["IfcParse", "IfcGeom", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep"],
            )
            for schema in self._selected_schemas():
                component_name = f"geometry_serializer_ifc{schema}"
                _add_component(
                    component_name,
                    requires=[
                        "IfcParse",
                        "IfcGeom",
                        "opencascade::occt_tkmesh",
                        "opencascade::occt_tkxmesh",
                        "opencascade::occt_tkmeshvs",
                        "opencascade::occt_tktopalgo",
                        "opencascade::occt_tkbrep",
                        "opencascade::occt_tkgeomalgo",
                    ],
                )
                geometry_serializer.requires.append(component_name)
        if self.options.build_qtviewer:
            self.cpp_info.components["qtviewer"].libs = []
            self.cpp_info.components["qtviewer"].requires = ["qt::qtbase"]
