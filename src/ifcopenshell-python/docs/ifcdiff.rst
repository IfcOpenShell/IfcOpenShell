IfcDiff
=======

IfcDiff is both a CLI utility and library that lets you compare the changes
between two IFC models. Changes are made on the assumption that the GlobalId of
an element in one model is consistent with the same element in another model.
You may compare geometric changes, and changes in various IFC relationships and
properties. IfcDiff supports comparing across different IFC schema versions.

Changes will be sorted into three lists:

- **Added**: a list of GlobalIds of elements present in the new file but not
  present in the old file.
- **Deleted**: a list of GlobalIds of elements present in the old file but not
  present in the new file.
- **Changed**: A list of GlobalIds of elements present in both the old and new
  file, but changes were detected. A list of changes are provided.

There are different methods of installation, depending on your situation.

1. **PyPI** is recommended for developers using Pip.
2. **Using Bonsai** is recommended for non-developers wanting a graphical
   interface.
3. **Source installation** is recommended for users wanting to use the latest
   code as a library or a CLI utility.

PyPI
----

.. code-block::

    pip install ifcdiff

Using Bonsai
------------

Bonsai is a Blender based graphical interface to IfcOpenShell.  Other than
providing a graphical IFC authoring platform, it also comes with IfcOpenShell,
its utilities, and a Python shell built-in. This means you don't need to
install Python first, and you also can compare your IfcOpenShell scripting to
what you see with a visual model viewer, or use a graphical interface to access
the IfcOpenShell utilities.

1. Install Bonsai by following the `Bonsai
   installation documentation
   <https://docs.bonsaibim.org/quickstart/installation.html>`_.

2. Launch Blender. Change to the **Scene Properties** tab in the **Properties
   Panel**. Scroll down to the **IFC Quality Control > IFC Diff** panel.

3. Browse to your old IFC file, new IFC file.

4. Optionally add any relationships you want to check.

5. Optionally type in a filter query.

6. Press **Execute IFC Diff**

TODO: add pictures and make this clearer for non-developers.

Source installation
-------------------

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the source code <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifcdiff>`_.
3. ``cd /path/to/IfcOpenShell/src/ifcdiff``
4. ``pip install -r requirements.txt``

Here is a minimal example of how to use IfcDiff as a Python module or CLI
utility:

.. code-block:: console

    $ python -m ifcdiff -h
    usage: ifcdiff.py [-h] [-o OUTPUT] [-r RELATIONSHIPS] old new

    Show the difference between two IFC files

    positional arguments:
      old                   The old IFC file
      new                   The new IFC file

    options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            The JSON diff file to output. Defaults to diff.json
      -r RELATIONSHIPS, --relationships RELATIONSHIPS
                            A list of space-separated relationships, chosen from "type", "property", "container", "aggregate", "classification"
    $ python -m ifcdiff old.ifc new.ifc
    $ cat diff.json

Here is a minimal example of how to use IfcDiff as a library:

.. code-block:: python

    from ifcdiff import IfcDiff

    ifc_diff = IfcDiff("/path/to/old.ifc", "/path/to/new.ifc", "/path/to/diff.json")
    ifc_diff.diff()
    print(ifc_diff.change_register)
    ifc_diff.export()

.. seealso::

   For more information on how to use IfcDiff as a library, check out the :doc:`API
   reference <autoapi/ifcdiff/index>`.

You can also alias it to a command:

.. code-block:: bash

    alias ifcdiff='python -m ifcdiff'

Geometry changes
----------------

IfcDiff compares geometry changes using the underlying IFC geometric definition.
This means that if a shape is described in one file as an extrusion, and as a
mesh in another file, it is considered to be a change in geometry, even if they
resolve to be the same boundary representation.

Geometric tolerance is defined using the precision defined in the new IFC model.

Relationships
-------------

By default, IfcDiff only compares changes in attributes and geometry. You may
wish to optionally specify more relationships to compare. You may choose from:

- **type**: detects changes in the type relationship, such as when an
  occurrence now belongs to a different type.
- **property**: detects changes in property sets, properties, quantity sets,
  and quantities. Also includes detected changes in inherited properties.
- **container**: detects changes in the spatial container, handling indirect
  containment such as when an element is part of an aggregate.
- **aggregate**: detects changes in aggregation.
- **classification**: detects changes in classification references. Also
  includes detected changes in inherited classifications.
