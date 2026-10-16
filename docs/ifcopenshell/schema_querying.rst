Schema querying
===============

Schema declarations
-------------------

IfcOpenShell can query the IFC schema itself without instantiating or loading an IFC dataset.

.. snippet:: schema_querying/declarations
    :caption-js: ``runtime.raw.parse.schemaNames()`` lists the schemas
        registered with the runtime.

A schema definition is known as a declaration. You may loop through all declarations or retrieve a declaration by name. All declarations have a name.

.. snippet:: schema_querying/declarations
    :tag: loop
    :title: Declarations by name

Entity inheritance and attributes
---------------------------------

You can check if an entity is abstract, and retrive both the supertype and subtypes of an entity:

.. snippet:: schema_querying/entity
    :caption-js: Entity declarations do not expose their name in JavaScript
        yet, so the example prints attribute counts instead.

You can retrieve only the direct attributes of an entity, or all the direct
attributes including inherited attributes, or inverse attributes:

.. snippet:: schema_querying/entity
    :tag: attributes
    :title: Attributes of an entity

Enumerations and select types
-----------------------------

.. snippet:: schema_querying/enumeration

buildingSMART property set templates
------------------------------------

For each IFC schema version, buildingSMART publishes built in property and quantity set templates for standardised properties. These define property names, property sets, data types, and which IFC class they are applicable to. You can query these templates.

.. snippet:: schema_querying/pset_templates
    :na: cpp, js
    :caption-python: The templates ship with IfcOpenShell-Python, in
        ``ifcopenshell.util.pset``.

To get just the names of applicable templates for an entity:

.. snippet:: schema_querying/pset_templates
    :tag: names
    :na: cpp, js
    :title: Names of applicable templates

They may also be retrieved as an ``IfcPropertySetTemplate`` entity:

.. snippet:: schema_querying/pset_templates
    :tag: applicable
    :na: cpp, js
    :title: Templates as entities

A single template may be retrieved by name:

.. snippet:: schema_querying/pset_templates
    :tag: by_name
    :na: cpp, js
    :title: A template by name

You may add your own IFC files containing pset template definitions:

.. snippet:: schema_querying/pset_templates
    :tag: library
    :na: cpp, js
    :title: Adding your own templates
