IfcClash
========

IfcClash is both a CLI utility and library that lets you perform clash detection
on one or more IFC models. Clashes are defined in terms of clash sets with
filters using the IFC query syntax.

PyPI
----

.. code-block::

    pip install ifcclash

Source installation
-------------------

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. Optionally `install bcf <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/bcf>`_ (needed for BCF reports of results)
3. `Clone the source code <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifcclash>`_.
4. ``cd /path/to/IfcOpenShell/src/ifcclash``

Here is a minimal example of how to use IfcClash as a Python module or CLI
utility:

.. code-block:: console

    $ python -m ifcclash -h

    usage: __main__.py [-h] [-o OUTPUT] input

    Clashes geometry between two IFC files

    positional arguments:
      input                 A JSON dataset describing a series of clashsets

    options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            The JSON diff file to output. Defaults to output.json

Instructions on what clashes to perform are structured in terms of clash sets.
Each clash set contains instructions of collisions that we want to perform, and
can be named so it is easy to distinguish. A typical name would be "Structure
and Pipes", to describe that we are are detecting collisions between structural
elements and pipes.

Each clash set may include two groups of objects, named ``A`` and ``B``. This
tells IfcClash to attempt to find collisions between any object in group ``A``
with any object in group ``B``. Group ``A`` is mandatory, but group ``B`` is
optional. If group ``B`` is not provided, IfcClash will detect all clashes
within objects of group ``A``.

Within group ``A`` or ``B``, you may define one or more data sources of objects.
A data source must include a path to the IFC file which the objects come from.
You may also optionally provide a filter to only include or exclude certain
objects. If no filter is provided, then all objects will be used to detect
collisions.

Here's a sample JSON description of a single clash set, with both groups
defined with data sources.

.. code-block:: json

    [
        {
            "name": "Clash Set A",
            "a": [
                {
                    "file": "/path/to/one.ifc"
                }
            ],
            "b": [
                {
                    "file": "/path/to/two.ifc",
                    "selector": "IfcWall",
                    "mode": "i"
                }
            ]
        }
    ]

Once your have your JSON description of your clashes, usage is like any other
CLI app.

.. code-block:: bash

    ifcclash clash_sets.json
    cat output.json

Here is a minimal example of how to use IfcClash as a library:

.. code-block:: python

    import sys
    import json
    import logging
    import ifcclash

    settings = ClashSettings()
    settings.output = "output.json"
    settings.logger = logging.getLogger("Clash")
    settings.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    settings.logger.addHandler(handler)
    ifc_clasher = Clasher(settings)
    with open(args.input, "r") as clash_sets_file:
        ifc_clasher.clash_sets = json.loads(clash_sets_file.read())
    ifc_clasher.clash()
    ifc_clasher.export()

You can also alias it to a command:

.. code-block:: bash

    alias ifcclash='python -m ifcclash'

Alternatively, you can package it as an executable.

::

    python make.py
    ./dist/ifcclash
