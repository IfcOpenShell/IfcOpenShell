IfcPatch
========

IfcPatch is both a CLI utility and library that lets you run a predetermined
modification on an IFC file, known as a patch recipe. This is great for running
prepackaged scripts on IFC models on a server with a standardised interface.
It's also great for distributing little scripts that need to modify an IFC to
users who don't know how to code or aren't interested in knowing the details.

PyPI
----

.. code-block::

    pip install ifcpatch

Source installation
-------------------

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the source code <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifcpatch>`_.
3. ``cd /path/to/src/ifcpatch``

Here is a minimal example of how to use IfcPatch as a Python module or CLI
utility:

.. code-block:: console

    $ python -m ifcpatch -h

    usage: __main__.py [-h] -i INPUT [-o OUTPUT] -r RECIPE [-l LOG]
                       [-a ARGUMENTS [ARGUMENTS ...]]

    Patches IFC files to fix badly formatted data

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            The IFC file to patch
      -o OUTPUT, --output OUTPUT
                            The output file to save the patched IFC
      -r RECIPE, --recipe RECIPE
                            Name of the recipe to use when patching
      -l LOG, --log LOG     Specify a log file
      -a ARGUMENTS [ARGUMENTS ...], --arguments ARGUMENTS [ARGUMENTS ...]
                            Specify custom arguments to the patch recipe

Exactly how it is run depends on the recipe. A recipe may require zero or more
arguments which are specific to the recipe. Here's an example which runs the
`ExtractElements` recipe, which, as the same suggests, extracts out elements.
This recipe expects one argument, which uses the
:ref:`ifcopenshell-python/selector_syntax:filtering elements` syntax.  In this
example, we'll extract out all `IfcWall` elements.

.. code-block:: bash

    ifcpatch -i input.ifc -o output.ifc -r ExtractElements -a "IfcWall"
    cat output.ifc

Here is a minimal example of how to use IfcPatch as a library:

.. code-block:: python

    import ifcpatch

    output = ifcpatch.execute({
        "input": "input.ifc",
        "file": ifcopenshell.open("input.ifc"),
        "recipe": "ExtractElements",
        "arguments": ["IfcWall"],
    })
    ifcpatch.write(output, "output.ifc")

You can also alias it to a command:

.. code-block:: bash

    alias ifcpatch='python -m ifcpatch'

Alternatively, you can package it as an executable.

.. code-block:: bash

    python make.py
    ./dist/ifcpatch

Patch recipes
-------------

You can view all built-in patches in IfcPatch here: :doc:`List of IfcPatch recipes <autoapi/ifcpatch/recipes/index>`.
