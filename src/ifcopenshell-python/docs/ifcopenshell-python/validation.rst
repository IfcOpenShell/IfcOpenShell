Validation
==========

SPF syntax validation
---------------------

IfcOpenShell can validate whether or not an IFC-SPF file contains correct SPF syntax.

.. code-block::

    $ python -m ifcopenshell.simple_spf path/to/model.ifc
    Valid

Here are some examples of failures:

.. code-block::

    $ python -m ifcopenshell.simple_spf fixtures/fail_double_comma.ifc
    On line 8 column 21:
    Unexpected comma (',')
    Expecting one of DBLQUOTE DOT HASH INT LPAR NONE QUOTE REAL STAR UPPER
    00008 | #1=IFCPERSON($,$,'',,$,$,$,$);
                                ^

    $ python -m ifcopenshell.simple_spf fixtures/fail_double_semi.ifc
    On line 27 column 66:
    Unexpected semicolon (';')
    Expecting one of ENDSEC HASH
    00027 | #20=IFCPROJECT('2AyG2X0sb16Bjd4gQc07yZ',#5,'',$,$,$,$,(#11),#19);;
                                                                             ^

    $ python -m ifcopenshell.simple_spf fixtures/fail_duplicate_id.ifc
    On line 27:
    Duplicate instance name #19
    00027 | #19=IFCPROJECT('2AyG2X0sb16Bjd4gQc07yZ',#5,'',$,$,$,$,(#11),#19);
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    $ python -m ifcopenshell.simple_spf fixtures/fail_no_header.ifc
    On line 2 column 1:
    Unexpected hex ('F')
    Expecting HEADER
    00002 | FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
            ^

The optional ``--json`` argument may be used to instead get results in JSON.

.. code-block::

    $ python -m ifcopenshell.simple_spf test.ifc
    {"type": "unexpected_token", "lineno": 8, "column": 48, "found_type": "semicolon", "found_value": ";", "expected": ["ENDSEC"], "line": "#1= IFCPERSON($,'Nicht definiert',$,$,$,$,$,$);;", "message": "On line 8 column 48:\nUnexpected semicolon (';')\nExpecting ENDSEC\n00008 | #1= IFCPERSON($,'Nicht definiert',$,$,$,$,$,$);;\n                                                       ^"}

IFC schema validation
---------------------

IfcOpenShell can validate models against the IFC schema itself. It checks against attributes, entity names, data types, cardinality, and where rules.

.. code-block:: console

    $ python -m ifcopenshell.validate -h

    usage: validate.py [-h] [--rules] [--json] [--fields] [--spf] files [files ...]

    positional arguments:
      files       The IFC file to validate.

    options:
      -h, --help  show this help message and exit
      --rules     Run express rules.
      --json      Output in JSON format.
      --fields    Output more detailed information about failed entities (only with --json).
      --spf       Output entities in SPF format (only with --json).


For example:

.. code-block:: bash

    python -m ifcopenshell.validate /path/to/model.ifc --rules
