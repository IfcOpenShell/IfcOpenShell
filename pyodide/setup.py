from setuptools import setup, find_packages

setup(name='ifcopenshell',
      version='0.8.0',
      description='IfcOpenShell is an open source (LGPL) software library for working with the Industry Foundation Classes (IFC) file format.',
      author='Thomas Krijnen',
      author_email='thomas@aecgeeks.com',
      url='http://ifcopenshell.org',
      packages=find_packages(),
      package_data={'ifcopenshell': ['util/schema/*.json', 'util/schema/*.ifc'], '': ['*.so', '*.json', '*.ifc']},
)
