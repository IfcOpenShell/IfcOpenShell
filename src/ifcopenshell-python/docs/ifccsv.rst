IfcCSV
======

IfcCSV lets you view and edit IFC data using spreadsheets or tabular datasets.
IfcCSV supports CSV (Comma Separated Values), ODS (Open Document Spreadsheet),
XLSX (Microsoft Excel), Pandas DataFrames, and regular Python lists.

IfcCSV lets you select rooted elements using the IFC selection queries. These
elements may be physical elements (walls, doors, windows, etc), construction
types (wall types, door types, window types, etc), or even non-geometric
(tasks, resources, cost items, etc).

Once you have selected a list of elements, you may specify attributes,
properties, quantities, or relationships to extract and use as columns in your
table.

For example, you might use a selection query of ``IfcDoor``, for all doors in
your project. You may then specify a ``class`` attribute, a ``Name`` attribute,
a ``type.Name`` relationship, and a ``type.Description`` relationship. You can
then produce a spreadsheet like this:

+------------------------+---------+------+-----------+------------------------------------+
| GlobalId               | Class   | Name | Type Name | Type Description                   |
+========================+=========+======+===========+====================================+
| 3AjGVS9EjBeBrDA5_tAcwQ | IfcDoor | 01   | DT-A      | Single swing steel frame door      |
+------------------------+---------+------+-----------+------------------------------------+
| 07BewvHLn2$x6HsHH06rAA | IfcDoor | 02   | DT-A      | Single swing steel frame door      |
+------------------------+---------+------+-----------+------------------------------------+
| 3b3Mk8uIb3Qu_eSPKxsI8x | IfcDoor | 01   | DT-B      | Double swing steel frame fire door |
+------------------------+---------+------+-----------+------------------------------------+
| ...                    | ...     | ...  | ...       | ...                                |
+------------------------+---------+------+-----------+------------------------------------+

.. note::

   By default, IfcCSV automatically inserts the GlobalId column at the
   beginning, in order to uniquely identify the element.

This tabular data may then be exported in your desired format.

You may then edit the data, and reimport the data back into IFC. The changes
you make in the spreadsheet or table will also be made in the IFC.

There are different methods of installation, depending on your situation.

1. **PyPI** is recommended for developers using Pip.
2. **Using Bonsai** is recommended for non-developers wanting a
   graphical interface.
3. **Source installation** is recommended for developers wanting to use the
   latest code as a library or a CLI utility.

PyPI
----

.. code-block::

    pip install ifccsv

Using Bonsai
---------------------------

Bonsai is a Blender Add-on that provides a graphical interface for IfcOpenShell.
Other than providing a graphical IFC authoring platform, it also comes with
IfcOpenShell, its utilities, and a Python shell built-in. This means you don't
need to install Python first, and you also can compare your IfcOpenShell
scripting to what you see with a visual model viewer, or use a graphical
interface to access the IfcOpenShell utilities.

1. Install Bonsai by following the `Bonsai
   installation documentation
   <https://docs.bonsaibim.org/guides/installation.html>`_.

2. Launch Blender. Change to the **Scene Properties** tab in the **Properties
   Panel**. Scroll down to the **IFC Collaboration > IFC CSV Import / Export**
   panel.

3. Browse to your IFC file.

4. Type in a filter query, such as ``IfcDoor``.

5. Optionally add attributes you'd like to export.

6. Press **Export IFC to CSV**

TODO: add pictures and make this clearer for non-developers.

Source installation
-------------------

1. :doc:`Install IfcOpenShell <ifcopenshell-python/installation>`
2. `Clone the source code <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifccsv>`_.
3. ``cd /path/to/IfcOpenShell/src/ifccsv``

Depending on which formats you want to edit, you will need to install more
dependencies:

- ``pip install odfpy`` for ODS support
- ``pip install openpyxl`` for XLSX support
- ``pip install pandas`` for ODS, XLSX, and Pandas DataFrame support

Here is a minimal example of how to use IfcDiff as a Python module or CLI
utility:

.. code-block:: console

    $ python -m ifccsv -h
    usage: ifccsv.py [-h] -i IFC [-s SPREADSHEET] [-f FORMAT] [-d DELIMITER] [-n NULL] [-e EMPTY] [--bool_true BOOL_TRUE] [--bool_false BOOL_FALSE] [--concat CONCAT] [-q QUERY] [-a ATTRIBUTES [ATTRIBUTES ...]]
                     [--headers HEADERS [HEADERS ...]] [--sort SORT [SORT ...]] [--order ORDER [ORDER ...]] [--export] [--import]

    Exports IFC data to and from CSV

    options:
      -h, --help            show this help message and exit
      -i IFC, --ifc IFC     The IFC file
      -s SPREADSHEET, --spreadsheet SPREADSHEET
                            The spreadsheet file
      -f FORMAT, --format FORMAT
                            The format, chosen from csv, ods, or xlsx
      -d DELIMITER, --delimiter DELIMITER
                            The delimiter in CSV. Defaults to a comma.
      -n NULL, --null NULL  How to represent null values. Defaults to N/A.
      -e EMPTY, --empty EMPTY
                            How to represent empty strings. Defaults to a hyphen.
      --bool_true BOOL_TRUE
                            How to represent true values. Defaults to YES.
      --bool_false BOOL_FALSE
                            How to represent false values. Defaults to NO.
      --concat CONCAT       How to concatenate lists. Defaults to ', '.
      -q QUERY, --query QUERY
                            Specify a IFC query selector, such as "IfcWall"
      -a ATTRIBUTES [ATTRIBUTES ...], --attributes ATTRIBUTES [ATTRIBUTES ...]
                            Specify attributes that are part of the extract, using the IfcQuery syntax such as 'class', 'Name' or 'Pset_Foo.Bar'
      --headers HEADERS [HEADERS ...]
                            Specify human readable headers that correlate to each attribute.
      --sort SORT [SORT ...]
                            Specify one or more attributes to sort by.
      --order ORDER [ORDER ...]
                            Choose the sort order from ASC or DESC for each sorted attribute.
      --export              Export from IFC to the desired format.
      --import              Import from the autodetected format to IFC.
    $ python -m ifccsv -i model.ifc -s out.csv -f csv -q IfcProduct -a "Name" "Description" --export
    $ cat out.csv

Here is a minimal example of how to use IfcCSV as a library:

.. code-block:: python

    import ifcopenshell
    from ifccsv import IfcCsv

    model = ifcopenshell.open("/path/to/model.ifc")
    # Using the selector is optional. You may specify elements as a list manually if you prefer.
    # e.g. elements = model.by_type("IfcElement")
    elements = ifcopenshell.util.selector.filter_elements(model, "IfcElement")
    attributes = ["Name", "Description"]

    # Export our model's elements and their attributes to a CSV.
    ifc_csv = IfcCsv()
    ifc_csv.export(model, elements, attributes, output="out.csv", format="csv", delimiter=",", null="-")

    # Optionally, you can explicitly export to different formats.
    # ifc_csv = IfcCsv()
    # ifc_csv.export(model, elements, attributes)
    ifc_csv.export_csv("out.csv", delimiter=";")
    ifc_csv.export_ods("out.ods")
    ifc_csv.export_xlsx("out.xlsx")

    # Optionally, you can create a Pandas DataFrame.
    df = ifc_csv.export_pd()
    print(df)

    # Optionally, you can directly fetch the headers and rows as Python lists.
    print(ifc_csv.headers)
    print(ifc_csv.results)

    # You can also import changes from a CSV
    ifc_csv.Import(model, "input.csv")
    model.write("/path/to/updated_model.ifc")
