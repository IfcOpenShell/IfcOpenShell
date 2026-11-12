Schema querying
===============

Schema declarations
-------------------

IfcOpenShell can query the IFC schema itself without instantiating or loading an IFC dataset.

.. code-block:: python

    import ifcopenshell
    ifc4 = ifcopenshell.schema_by_name("IFC4")

A schema definition is known as a declaration. You may loop through all declarations or retrieve a declaration by name. All declarations have a name.

.. code-block:: python

    for declaration in ifc4.declarations():
        print(declaration.name()) # 'IfcAbsorbedDoseMeasure', 'IfcAccelerationMeasure', 'IfcActionRequest', ...

    ifcwall = ifc4.declaration_by_name("IfcWall")

You can check if an entity is abstract, and retrive both the supertype and subtypes of an entity:

.. code-block:: python

    print(ifcwall.is_abstract()) # False
    print(ifcwall.supertype()) # <entity IfcBuildingElement>
    print(ifcwall.subtypes()) # (<entity IfcWallElementedCase>, <entity IfcWallStandardCase>)

You can retrieve only the direct attributes of an entity, or all the direct attributes including inherited attributes, or inverse attributes:

.. code-block:: python

    print(ifcwall.attributes())
    print(ifcwall.all_attributes())
    print(ifcwall.all_inverse_attributes())

buildingSMART property set templates
------------------------------------

For each IFC schema version, buildingSMART publishes built in property and quantity set templates for standardised properties. These define property names, property sets, data types, and which IFC class they are applicable to. You can query these templates.

.. code-block:: python

    import ifcopenshell.util.pset
    templates = ifcopenshell.util.pset.PsetQto("IFC4")

To get just the names of applicable templates for an entity:

.. code-block:: python

    # ['Pset_EnvironmentalImpactIndicators', 'Pset_EnvironmentalImpactValues', 'Pset_WallCommon', 'Qto_WallBaseQuantities', ...]
    print(templates.get_applicable_names("IfcWall"))

They may also be retrieved as an ``IfcPropertySetTemplate`` entity:

.. code-block:: python

    print(templates.get_applicable("IfcWall"))

A single template may be retrieved by name:

.. code-block:: python

    templates.get_by_name('Pset_WallCommon')

You may add your own IFC files containing pset template definitions:

.. code-block:: python

    my_pset_library = ifcopenshell.open('/path/to/library.ifc')
    templates.templates.append(my_pset_library)
