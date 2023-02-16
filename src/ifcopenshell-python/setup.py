from setuptools import setup
from pathlib import Path

cwd = Path(__file__).parent
long_description = (cwd / "README.md").read_text()

setup(name="ifcopenshell", long_description=long_description, long_description_content_type="text/markdown")
