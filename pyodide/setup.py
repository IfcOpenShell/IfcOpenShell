# setup.py is getting deprecated, but we still use it,
# because `tool.setuptools.ext-modules` is still experimental in pyproject.toml
# and we need it to get the wheel suffix right.
import os
import sys
from pathlib import Path

import tomllib
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

# Detect repo folder: if setup.py is in pyodide folder, go to parent
SETUP_DIR = Path(__file__).parent
REPO_FOLDER = SETUP_DIR.parent if SETUP_DIR.name == "pyodide" else SETUP_DIR


def get_version() -> str:
    if "PKG_VERSION" in os.environ:
        # Inside pyodide build environment.
        return os.environ["PKG_VERSION"]
    return (REPO_FOLDER / "VERSION").read_text().strip()


# Read dependencies from pyproject.toml
def get_dependencies() -> list[str]:
    pyproject_toml = REPO_FOLDER / "src" / "ifcopenshell-python" / "pyproject.toml"
    pyproject_data = tomllib.loads(pyproject_toml.read_text())
    dependencies = pyproject_data["project"]["dependencies"]
    return dependencies


class UnixBuildExt(build_ext):
    """Customize ``build_ext`` to support packing on Windows."""

    def finalize_options(self):
        from distutils import sysconfig

        super().finalize_options()
        if sys.platform == "win32":
            self.compiler = "unix"

            # Configure sysconfig for Windows builds
            # CCSHARED is the only variable that's not customizable with env vars.
            # Basically avoiding this:
            # File ".venv\Lib\site-packages\setuptools\_distutils\sysconfig.py", line 366, in customize_compiler
            #     compiler_so=cc_cmd + ' ' + ccshared,
            #                 ~~~~~~~~~~~~~^~~~~~~~~~
            # TypeError: can only concatenate str (not "NoneType") to str
            sysconfig.get_config_vars()  # Initialize config cache
            if sysconfig._config_vars.get("CCSHARED") is None:
                sysconfig._config_vars["CCSHARED"] = "-fPIC"
            # Override compiler type before it's instantiated

        # Set Emscripten compiler environment variables
        os.environ["CC"] = "emcc"
        os.environ["CXX"] = "em++"
        os.environ["CFLAGS"] = ""
        os.environ["CXXFLAGS"] = ""
        os.environ["LDSHARED"] = "emcc -shared"
        os.environ["AR"] = "emar"
        os.environ["ARFLAGS"] = "rcs"
        os.environ["SETUPTOOLS_EXT_SUFFIX"] = ".cpython-313-wasm32-emscripten.so"


setup(
    name="ifcopenshell",
    version=get_version(),
    description=(
        "IfcOpenShell is an open source (LGPL) software library "
        "for working with the Industry Foundation Classes (IFC) file format."
    ),
    author="Thomas Krijnen",
    author_email="thomas@aecgeeks.com",
    url="https://ifcopenshell.org",
    install_requires=get_dependencies(),
    packages=find_packages(include=["ifcopenshell", "ifcopenshell.*"]),
    package_data={
        # "*.so" is needed to include prebuilt binary extension. Otherwise it would try to build it and fail.
        "ifcopenshell": ["util/schema/*.json", "util/schema/*.ifc", "*.so"],
        "": ["*.json", "*.ifc"],
    },
    # Has to provide extension to get the correct wheel suffix.
    ext_modules=[Extension("ifcopenshell._ifcopenshell_wrapper", sources=[])],
    cmdclass={"build_ext": UnixBuildExt},
)
