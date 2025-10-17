from setuptools import setup, Extension, find_packages

setup(
    name="ifcopenshell",
    version="0.8.0",
    description=(
        "IfcOpenShell is an open source (LGPL) software library "
        "for working with the Industry Foundation Classes (IFC) file format."
    ),
    author="Thomas Krijnen",
    author_email="thomas@aecgeeks.com",
    url="https://ifcopenshell.org",
    packages=["ifcopenshell"],
    package_data={
        # "*.so" is needed to include prebuilt binary extension. Otherwise it would try to build it and fail.
        "ifcopenshell": ["util/schema/*.json", "util/schema/*.ifc", "*.so"],
        "": ["*.json", "*.ifc"],
    },
    # Has to provide extension to get the correct wheel suffix.
    ext_modules=[Extension("ifcopenshell._ifcopenshell_wrapper", sources=[])],
)
