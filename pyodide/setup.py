# setup.py is getting deprecated, but we still use it,
# because `tool.setuptools.ext-modules` is still experimental in pyproject.toml
# and we need it to get the wheel suffix right.
import os
from pathlib import Path

import tomllib
from setuptools import Extension, find_packages, setup

REPO_FOLDER = Path(__file__).parent


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
)
