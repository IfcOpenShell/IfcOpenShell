IfcCityJSON
===========

IfcCityJSON is a converter for CityJSON files and IFC. It currently only
supports one-way conversion from CityJSON to IFC.

PyPI
----

.. code-block::

    pip install ifccityjson

Source installation
-------------------

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the source code <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifccityjson>`_.
3. ``cd /path/to/IfcOpenShell/src/ifccityjson``
4. ``pip install .``

Usage
-----

An extended ifccityjson tutorial can be found on `the OSARCH wiki
<https://wiki.osarch.org/index.php?title=Ifccityjson>`_. Here's the built-in
documentation:

.. code-block:: console

    $ python -m ifccityjson -h

    usage: __main__.py [-h] -i INPUT [-o OUTPUT] [-n NAME] [--split-lod] [--no-split-lod] [--lod LOD]

    options:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            input CityJSON file
      -o OUTPUT, --output OUTPUT
                            output IFC file. Standard is output.ifc
      -n NAME, --name NAME  Attribute containing the name
      --split-lod           Split the file in multiple LoDs
      --no-split-lod        Do not split the file in multiple LoDs
      --lod LOD             extract LOD value (example: 1.2)

The example file that could be used is example/3D_BAG_example.json

.. code-block:: bash

    python ifccityjson.py -i example/geometries.json -o output.ifc -n identificatie

The following geometries are implemented:

- [x] "MultiPoint"
- [x] "MultiLineString"
- [x] "MultiSurface"
- [x] "CompositeSurface"
- [x] "Solid": exterior shell
- [ ] "Solid": interior shell
- [x] "MultiSolid"
- [x] "CompositeSolid"
- [ ] "GeometryInstance" 

TODO:

- [x] CityJSON Attributes as IFC properties in 'CityJSON_attributes' pset
- [x] Implement georeferencing
- [x] Do not use template IFC for new IFC file, but make IFC file from scratch
- [x] Create mapping to IFC for all CityJSON object types & semantic surfaces
- [ ] Implement conversion of all CitYJSON geometries
- [x] Implement conversion of all LODs instead of only the most detailed
