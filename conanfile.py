
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, load
from conan.tools.apple import is_apple_os

required_conan_version = ">=2.1"

IFC_SCHEMAS = sorted(["2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"])

def parse_version():
    return "0.8.4"
    # versionFile = load(self, "VERSION")
    # try:
    #     return "%s_%s" % (git.get_branch(), git.get_revision())
    # except:
    #     return versionFile.strip()
    #   conan_version = os.getenv("MYPACKAGE_VERSION", "1.0")
    #   if os.path.exists(".git"):
    #         output = StringIO()
    #         ConnanRunner()("git describe ... ", output)
    #         conan_version = output.get_value().some_regex_or_parsing()
    #    ....


ifcopenshell_version = parse_version()

class IfcopenshellConan(ConanFile):
    name = "ifcopenshell"
    version = ifcopenshell_version
    description = "Open source IFC library and geometry engine"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/IfcOpenShell/IfcOpenShell"
    topics = ("ifc", "bim", "building", "3d")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_ifcgeom": [True, False],
        "build_ifcgeomserver": [True, False],
        "build_convert": [True, False],
        "build_convert_with_usd": [True, False],
        "build_convert_with_proj": [True, False],
        "ifcxml_support": [True, False],
        "use_mmap": [True, False],
        "with_cgal": [True, False],
        "with_hdf5": [True, False],
        "with_rocksdb": [True, False],
        
        # "with_wasm": [True, False],
        # "with_build_optimizations": [True, False],
        
        "with_ifcpython": [True, False],
        "with_examples": [True, False],
        "with_collada_support": [True, False],
        "build_qtviewer": [True, False],
    }
    
    options.update({f"schema_{schema}": [True, False] for schema in IFC_SCHEMAS})
        
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_ifcgeom": True,
        "build_ifcgeomserver": True,
        "build_convert": True,
        "build_convert_with_usd": False,
        "build_convert_with_proj": True,
        # XML used optionally XML by IfcParse and IfcConvert
        "ifcxml_support": True,
        # XML used optionally XML by IfcParse and IfcConvert
        "use_mmap": True,
        
        "with_cgal": True,
        # XML used optionally XML by IfcGeom, Serializers and IfcConvert
        "with_hdf5": True,
        "with_rocksdb": True,
        

        
        # TODO: using https://conan.io/center/recipes/wasm-micro-runtime?version=1.2.3 ?
        # https://docs.conan.io/1/integrations/cross_platform/emscripten.html
        # "with_wasm": False,
        # "with_build_optimizations": False,
        
        "with_ifcpython": False,
                
        "with_examples": False,
        "with_collada_support": False,
        "build_qtviewer": True,
    }
    # Limit the default set of schemas to the basic ones and the latest to limit the size of the build.
    default_options.update({f"schema_{schema}": schema in ["2x3", "4", "4x3_add2"] for schema in IFC_SCHEMAS})
    # default_options.update({f"schema_{schema}": schema in ["2x3"] for schema in IFC_SCHEMAS})
    implements = ["auto_shared_fpic"]

    @property
    def _selected_ifc_schemas(self):
        return [schema for schema in IFC_SCHEMAS if self.options.get_safe(f"schema_{schema}")]
    
    exports_sources = "aws/**", "choco/**", "CMakeLists.txt", "utilities.cmake", "cmake/**", "src/**", "docs/**", "**.md"

    def config_options(self):
        if self.settings.os == "Emscripten":
            self.options.build_ifcgeom = False
            self.options.build_ifcgeomserver = False
            self.options.build_convert = False
            self.options.build_convert_with_usd = False
            self.options.build_convert_with_proj = False
            self.options.ifcxml_support = False
            self.options.use_mmap = False
            self.options.with_cgal = False
            self.options.with_hdf5 = False
            self.options.with_rocksdb = False
            self.options.build_qtviewer = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.build_ifcgeom:
            del self.options.with_cgal
    
    def layout(self):
        cmake_layout(self)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.build_convert and not self.options.build_ifcgeom:
            raise ConanInvalidConfiguration("build_convert requires build_ifcgeom to be enabled")
        # TODO: add condition on with_examples and schema version

    def requirements(self):
        # self.requires("boost/[>=1.88 <2.0]", transitive_headers=True, transitive_libs=True, force=True)
        # self.requires("boost/1.86.0", transitive_headers=True, transitive_libs=True, force=True)
        # Use latest release to be able to cross compile to WASM
        self.requires("boost/1.89.0", transitive_headers=True, transitive_libs=True, force=True)
        if self.options.get_safe("with_hdf5"):
            # Used in public serializers/HdfSerializer.h, ifcgeom/kernels/opencascade/IfcGeomTree.h
            self.requires("hdf5/[^1.8]", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_rocksdb"):
            self.requires("rocksdb/[^10.5.1]")
        if self.options.build_ifcgeom:
            self.requires("opencascade/[^7.8]", transitive_headers=True, transitive_libs=True)
            # ifcgeom/taxonomy.h
            self.requires("eigen/3.4.0", transitive_headers=True)
            if self.options.get_safe("with_cgal"):
                # Used in ifcgeom/kernels/cgal public headers
                self.requires("cgal/[>=5.6]", transitive_headers=True, transitive_libs=True)
                # Used for svgfill submodule
                # TODO: remove these dependencies once svgfill managed as a conan dependency
                if self.options.with_ifcpython:
                    self.requires("svgpp/1.3.1")
        if self.options.get_safe("with_cgal") or self.options.ifcxml_support:
            self.requires("libxml2/[^2.12.5]")

        # See https://github.com/valgur/conan-center-index/commit/1d32179df715d1e6855843a2c67c2413e78f7c56
        # self.requires("manifold/3.0.1")

        if self.options.build_convert:
            if self.options.build_convert_with_usd:
                # See https://github.com/conan-io/conan-center-index/pull/24506
                self.requires("openusd/25.11")
            if self.options.build_convert_with_proj:
                self.requires("proj/9.7.0")
        if self.options.build_qtviewer:
            # Use an older qt release to avoid issue of https://github.com/conan-io/conan-center-index/issues/27912
            self.requires("qt/6.5.3")
            # self.requires("qt/6.8.3")
            self.requires("fontconfig/2.14.2", override=True)
            # self.requires("openscenegraph/3.6.5")
            # self.requires("libpng/1.6.48", override=True)
            # self.requires("zstd/1.5.7", override=True)
            
    def build_requirements(self):
        if self.options.with_ifcpython:
            self.tool_requires("swig/4.1.0")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["SCHEMA_VERSIONS"] = ";".join(self._selected_ifc_schemas)
        
        tc.cache_variables["BUILD_IFCGEOM"] = self.options.build_ifcgeom
        tc.cache_variables["BUILD_GEOMSERVER"] = self.options.build_ifcgeomserver
        tc.cache_variables["BUILD_CONVERT"] = self.options.build_convert
        tc.cache_variables["USD_SUPPORT"] = self.options.build_convert and self.options.build_convert_with_usd
        tc.cache_variables["WITH_PROJ"] = self.options.build_convert and self.options.build_convert_with_proj
        tc.cache_variables["IFCXML_SUPPORT"] = self.options.ifcxml_support
        tc.cache_variables["USE_MMAP"] = self.options.use_mmap
        tc.cache_variables["WITH_OPENCASCADE"] = self.options.build_ifcgeom
        tc.cache_variables["WITH_CGAL"] = self.options.get_safe("with_cgal", False)
        tc.cache_variables["HDF5_SUPPORT"] = self.options.get_safe("with_hdf5")
        tc.cache_variables["WITH_ROCKSDB"] = self.options.get_safe("with_rocksdb")
        
        # tc.cache_variables["WASM_BUILD"] = self.options.with_wasm
        # tc.cache_variables["ENABLE_BUILD_OPTIMIZATIONS"] = self.options.with_build_optimizations
        
        tc.cache_variables["BUILD_IFCPYTHON"] = self.options.with_ifcpython

        tc.cache_variables["BUILD_EXAMPLES"] = self.options.with_examples and self.options.schemas.contains("2x3")
        tc.cache_variables["COLLADA_SUPPORT"] = self.options.with_collada_support
        
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cmake")
        # cmake.configure(build_script_folder="cmake", cli_args=["--graphviz=graph.dot"])
        cmake.build(cli_args=["--verbose"])
        # cmake.build(cli_args=["--verbose"], build_tool_args=["-j", "1"])

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # No official CMake or .pc config exported. Based on CPack values for consistency.
        self.cpp_info.set_property("cmake_file_name", "IfcOpenShell")
        # For svgfill, to remove once svgfill is managed as a conan dependency, svgfill is only used by ifcwrap
        if self.options.with_ifcpython:
            self.cpp_info.requires = ["svgpp::svgpp"]
        
        def _add_component(name, requires=None):
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", name)
            component.libs = [name]
            component.requires = requires or []
            return component

        ifcparse = _add_component("IfcParse", requires=[
            "boost::system",
            "boost::program_options",
            "boost::regex",
            "boost::thread",
            "boost::date_time",
        ])
        if self.options.use_mmap:
            ifcparse.requires.extend(["boost::iostreams", "boost::filesystem",])
            ifcparse.defines.append("USE_MMAP")
        if self.options.ifcxml_support:
            ifcparse.requires.append("libxml2::libxml2")
            ifcparse.defines.append("WITH_IFCXML")
        ifcparse.defines.append(f"SCHEMA_SEQ=({')('.join(self._selected_ifc_schemas)})")
        for schema in self._selected_ifc_schemas:
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
                # ifcgeom.requires.append("geometry_kernel_cgal")
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
            # if self.options.with_cgal:
            #     _add_component("geometry_kernel_cgal", requires=["cgal::cgal", "mpfr::mpfr", "gmp::gmp", "eigen::eigen",])
            #     ifcgeom.requires.append("geometry_kernel_cgal")
            #     simple = _add_component("geometry_kernel_cgal_simple", requires=["cgal::cgal", "gmp::gmp", "eigen::eigen",])
            #     simple.defines.append("IFOPSH_SIMPLE_KERNEL")
            #     ifcgeom.requires.append("geometry_kernel_cgal_simple")

            # _add_component("geometry_kernel_opencascade", requires=[
            #     "opencascade::occt_tkernel",
            #     "opencascade::occt_tkmath",
            #     "opencascade::occt_tkbrep",
            #     "opencascade::occt_tkgeombase",
            #     "opencascade::occt_tkgeomalgo",
            #     "opencascade::occt_tkg3d",
            #     "opencascade::occt_tkg2d",
            #     "opencascade::occt_tkshhealing",
            #     "opencascade::occt_tktopalgo",
            #     "opencascade::occt_tkmesh",
            #     "opencascade::occt_tkprim",
            #     "opencascade::occt_tkbool",
            #     "opencascade::occt_tkbo",
            #     # "opencascade::occt_tkfillet",
            #     "opencascade::occt_tkxsbase",
            #     "opencascade::occt_tkoffset",
            #     "opencascade::occt_tkhlr",
            #     "eigen::eigen",
            # ])
            # ifcgeom.requires.append("geometry_kernel_opencascade")
            # ifcgeom.defines.append("IFOPSH_WITH_OPENCASCADE")
            if self.options.with_hdf5:
                ifcgeom.requires.append("hdf5::hdf5_cpp")
            # for schema in self._selected_ifc_schemas:
            #     _add_component(f"geometry_mapping_ifc{schema}", requires=["IfcParse"])
            #     ifcgeom.requires.append(f"geometry_mapping_ifc{schema}")

        if self.options.build_convert:
            serializers = _add_component("Serializers", requires=["IfcGeom"])
            if self.options.with_hdf5:
                serializers.requires.append("hdf5::hdf5_cpp")
            if self.options.build_convert_with_usd:
                serializers.requires.append("usd::usd")
            if self.options.build_convert_with_proj:
                serializers.requires.append("proj::proj")

            # for schema in self._selected_ifc_schemas:
            #     component_name = f"Serializers_ifc{schema}"
            #     _add_component(component_name)
            #     self.cpp_info.components["Serializers"].requires.append(component_name)

            # geometry_serializer = _add_component("geometry_serializer", ["IfcParse", "IfcGeom", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep"])
            # for schema in self._selected_ifc_schemas:
            #     component_name = f"geometry_serializer_ifc{schema}"
            #     # _add_component(component_name, requires=["IfcParse", f"Serializers_ifc{schema}", f"geometry_mapping_ifc{schema}", "IfcGeom", "opencascade::occt_tkmesh", "opencascade::occt_tkxmesh", "opencascade::occt_tkmeshvs", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep", "opencascade::occt_tkgeomalgo"])                _add_component(component_name, requires=["IfcParse", f"Serializers_ifc{schema}", f"geometry_mapping_ifc{schema}", "IfcGeom", "opencascade::occt_tkmesh", "opencascade::occt_tkxmesh", "opencascade::occt_tkmeshvs", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep", "opencascade::occt_tkgeomalgo"])
            #     _add_component(component_name, requires=["IfcParse", f"Serializers_ifc{schema}", "IfcGeom", "opencascade::occt_tkmesh", "opencascade::occt_tkxmesh", "opencascade::occt_tkmeshvs", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep", "opencascade::occt_tkgeomalgo"])
            #     geometry_serializer.requires.append(component_name)
