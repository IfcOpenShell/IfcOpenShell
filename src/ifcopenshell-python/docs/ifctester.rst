IfcTester
=========

IfcTester lets you author and read Information Delivery Specification (IDS)
files. You can validate IFC models against IDS and generate reports in multiple
formats. It works from the command line, as a web app, or as a library.

PyPI
----

.. code-block::

    pip install ifctester

Examples
--------

You can execute IfcTester using a CLI.

.. code-block:: console

    # Validate an IFC with an IDS and report to console
    python -m ifctester example.ids example.ifc

    # Generate a HTML report instead
    python -m ifctester example.ids example.ifc -r Html -o report.html

Alternatively, you can use Python:

.. code-block:: python

    import ifcopenshell
    from ifctester import ids, reporter

    # Create new IDS
    specs = ids.Ids(title="My IDS")

    # add specification to it
    spec = ids.Specification(name="My first specification")
    spec.applicability.append(ids.Entity(name="IFCWALL"))
    requirement = ids.Property(
        baseName="IsExternal",
        value="TRUE", 
        propertySet="Pset_WallCommon", 
        dataType="IfcBoolean",
        uri="https://identifier.buildingsmart.org/uri/.../prop/LoadBearing", 
        instructions="Walls need to be load bearing.",
        cardinality="required")
    spec.requirements.append(requirement)
    specs.specifications.append(spec)

    # Save to a file
    specs.to_xml("IDS.xml")

    # Open IFC file:
    my_ifc = ifcopenshell.open("model.ifc")

    # Validate IFC model against IDS requirements:
    specs.validate(my_ifc)

    # Show results in a console
    reporter.Console(specs).report()

    # Alternatively, to JSON
    report = reporter.Json(specs)
    report.report()
    report.to_file("report.json")

    # Or to ODS spreadsheet
    report = reporter.Ods(specs)
    report.report()
    report.to_file("report.ods")

    # Or to HTML spreadsheet
    report = reporter.Html(specs)
    report.report()
    report.to_file("report.html")

    # Or to BCF
    report = reporter.Bcf(specs)
    report.report()
    report.to_file("report.bcf")

CLI manual
----------

.. code-block:: console

    $ python -m ifctester -h

    usage: __main__.py [-h] [-r REPORTER] [--no-color] [--excel-safe] [-o OUTPUT] ids [ifc]

    Uses an IDS to audit an IFC

    positional arguments:
      ids                   Path to an IDS
      ifc                   Path to an IFC

    options:
      -h, --help            show this help message and exit
      -r REPORTER, --reporter REPORTER
                            The reporting method to view audit results
      --no-color            Disable colour output (supported by Console reporting)
      --excel-safe          Make sure exported ODS is safely exported for Excel
      -o OUTPUT, --output OUTPUT
                            Output file (supported for all types of reporting except Console)
