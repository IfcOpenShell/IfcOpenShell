Serialiser settings
===================

The geometry serialiser has a variety of settings which can impact its output.
This is set during the construction of the serialiser.

Here's an example of changing settings in Python:

.. code-block:: python

    serialiser_settings = ifcopenshell.geom.serializer_settings()
    serialiser_settings.set("use-element-guids", True)

base-uri
^^^^^^^^

+--------+-------------------+---------+
| Type   | IfcConvert Option | Default |
+========+===================+=========+
| STRING | ``--base-uri``    | ""      |
+--------+-------------------+---------+

Base URI for products to be used in RDF-based serializations.

use-element-names
^^^^^^^^^^^^^^^^^

+------+-------------------------+---------+
| Type | IfcConvert Option       | Default |
+======+=========================+=========+
| BOOL | ``--use-element-names`` | False   |
+------+-------------------------+---------+

Use entity instance IfcRoot.Name instead of unique IDs for naming elements upon serialization. Applicable for OBJ, DAE, STP, and SVG output.

use-element-guids
^^^^^^^^^^^^^^^^^

+------+-------------------------+---------+
| Type | IfcConvert Option       | Default |
+======+=========================+=========+
| BOOL | ``--use-element-guids`` | False   |
+------+-------------------------+---------+

Use entity instance IfcRoot.GlobalId instead of unique IDs for naming elements upon serialization. Applicable for OBJ, DAE, STP, and SVG output.

use-element-step-ids
^^^^^^^^^^^^^^^^^^^^

+------+----------------------------+---------+
| Type | IfcConvert Option          | Default |
+======+============================+=========+
| BOOL | ``--use-element-step-ids`` | False   |
+------+----------------------------+---------+

Use the numeric step identifier (entity instance name) for naming elements upon serialization. Applicable for OBJ, DAE, STP, and SVG output.

use-element-types
^^^^^^^^^^^^^^^^^

+------+-------------------------+---------+
| Type | IfcConvert Option       | Default |
+======+=========================+=========+
| BOOL | ``--use-element-types`` | False   |
+------+-------------------------+---------+

Use element types instead of unique IDs for naming elements upon serialization.  Applicable to DAE output.

y-up
^^^^

+------+-------------------+---------+
| Type | IfcConvert Option | Default |
+======+===================+=========+
| BOOL | ``--y-up``        | False   |
+------+-------------------+---------+

Change the 'up' axis to positive Y, default is Z UP. Applicable to OBJ output.

ecef
^^^^

+------+-------------------+---------+
| Type | IfcConvert Option | Default |
+======+===================+=========+
| BOOL | ``--ecef``        | False   |
+------+-------------------+---------+

Write glTF in Earth-Centered Earth-Fixed coordinates. Requires PROJ.

digits
^^^^^^

+------+-------------------+---------+
| Type | IfcConvert Option | Default |
+======+===================+=========+
| INT  | ``--digits``      | 15      |
+------+-------------------+---------+

Sets the precision to be used to format floating-point values, 15 by default.  Use a negative value to use the system's default precision (should be 6 typically). Applicable for OBJ and DAE output. For DAE output, value >= 15 means that up to 16 decimals are used, and any other value means that 6 or 7 decimals are used.

wkt-use-section
^^^^^^^^^^^^^^^

+------+-----------------------+---------+
| Type | IfcConvert Option     | Default |
+======+=======================+=========+
| BOOL | ``--wkt-use-section`` | False   |
+------+-----------------------+---------+

Use a geometrical section rather than full polyhedral output and footprint in TTL WKT.
