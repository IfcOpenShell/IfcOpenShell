.. This file was generated with the assistance of an AI coding tool.

Code examples and mechanisms
============================

The snippets on this page form a progression: they open a file, look at its
schema, read data from it, and then move on to the two mechanisms which are
most commonly surprising, the relationship graph and property sets.

Getting Started with IFC parsing
--------------------------------

The basis of all parsing and getting information from the IFC starts with
obtaining an ``ifcopenshell::file`` object and validating that it is good for
use. The schema of the file is detected while parsing, and is available as
``model.schema()``.

.. literalinclude:: code_examples/01_open_and_check.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

.. _schema-agnostic-parsing-of-ifcs:

Schema-agnostic parsing of IFCs
-------------------------------

It is advisable to design your programme in a schema-agnostic fashion to be able
to process all schema versions of input IFCs. In C++ the schema is normally a
compile time concept: ``Ifc4::IfcProduct`` and ``Ifc2x3::IfcProduct`` are
generated classes which are unrelated to each other, and the schema libraries
you want to support have to be linked.

The runtime part of the API is not tied to a schema though. Instances are
``express::base`` values which know their own declaration, and
``instances_by_type()`` also accepts the name of an entity as it appears in the
IFC schema, so the same code processes IFC2x3, IFC4 and IFC4.3 input.

.. literalinclude:: code_examples/02_schema_agnostic.cpp
    :language: cpp
    :start-after: // tag::runtime-example
    :end-before: // end::runtime-example

If you do want the strongly typed accessors, the shared logic can be templated
over the schema, and the schema dispatched on once.

.. literalinclude:: code_examples/02_schema_agnostic.cpp
    :language: cpp
    :start-after: // tag::typed-example
    :end-before: // end::typed-example

Reading out attributes of an IfcProduct
---------------------------------------

The attributes of an ``IfcProduct``, and by extension of any derived class, can
be read by calling the accessor of the same name, such as ``GlobalId()`` or
``Name()``. Note that optional properties like name, long name, or description,
among others, are wrapped in a ``std::optional``, and that properties which
reference another instance report as empty - their ``operator bool`` returns
false - when they are not set.

.. literalinclude:: code_examples/03_read_attributes.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

The same values are available without the generated classes, by index, in the
order in which the attributes appear in the IFC schema, or by name. This is what
the schema-agnostic code above is built on.

.. literalinclude:: code_examples/03_read_attributes.cpp
    :language: cpp
    :start-after: // tag::agnostic-example
    :end-before: // end::agnostic-example

Navigating relationships in IFC
-------------------------------

While it is natural to look at the IFC format as a representation of a physical
building model where physical objects are related to each other in a tree
structure (e.g. site > building > storey > slab), the IFC format allows for the
representation of information in a graph-like manner, joining physical objects
to meta-information through relationships. A detailed explanation of
relationships in IFC is provided in this `blog post
<https://constructingdata.wordpress.com/2018/04/09/ifc-for-the-layman-part-3-relationships/>`__.

The following function shows how property sets can be extracted from a given
``IfcObject``. Note that in the generated classes the inverse attribute
``IsDefinedBy()`` is already narrowed to the ``IfcRelDefinesByProperties``
relationships, so it is the unwrapping of the relationship, not the filtering,
which is the part to get right.

.. literalinclude:: code_examples/04_navigate_relationships.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Reading properties and quantities from an element
-------------------------------------------------

A frequent point of confusion is that ``IsDefinedBy()`` does *not* return the
property set or quantity set itself. It is an inverse attribute that lists every
``IfcRelDefinesByProperties`` relationship pointing at the element, and the
relationship still needs to be unwrapped via ``RelatingPropertyDefinition()`` to
reach the actual ``IfcPropertySet`` (regular properties) or
``IfcElementQuantity`` (physical quantities such as length, area, or volume).
Both classes derive from ``IfcPropertySetDefinition``, so a single cast check
tells you which one you got.

The definition of the relationship is a select, so it is either a single
definition or - when the property sets are assigned as a group - a definition
set. The value of a property is a select as well, so it is cast to the value type
you expect it to hold, which has to be tested with the declaration of the value
rather than with the value in a condition:

.. literalinclude:: code_examples/05_properties_and_quantities.cpp
    :language: cpp
    :start-after: // tag::value-casts
    :end-before: // end::value-casts

Both definitions are then handled by the same helper:

.. literalinclude:: code_examples/05_properties_and_quantities.cpp
    :language: cpp
    :start-after: // tag::print-definitions
    :end-before: // end::print-definitions

.. literalinclude:: code_examples/05_properties_and_quantities.cpp
    :language: cpp
    :start-after: // tag::element-level
    :end-before: // end::element-level

There is a second, easily-missed source of properties: the element's **type**.
Properties assigned to a type (e.g. a shared "IfcWallType") apply to every
element of that type, and are reached completely differently, through
``IsTypedBy()`` and then ``RelatingType()->HasPropertySets()`` directly, with no
relationship to unwrap:

.. literalinclude:: code_examples/05_properties_and_quantities.cpp
    :language: cpp
    :start-after: // tag::type-level
    :end-before: // end::type-level

Reading a value without the schema types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Casting a value to a schema type requires you to know which of the value types a
property holds, and the cast has to be tested before it is used. An attribute can
also be read in the type it is stored in, with a visitor over the attribute
value, which needs none of the schema level types:

.. literalinclude:: code_examples/05_properties_and_quantities.cpp
    :language: cpp
    :start-after: // tag::value-visitor
    :end-before: // end::value-visitor

Which is then used like this:

.. literalinclude:: code_examples/05_properties_and_quantities.cpp
    :language: cpp
    :start-after: // tag::value-visitor-use
    :end-before: // end::value-visitor-use

Defensive programming with IfcOpenShell
---------------------------------------

The need for (down-)casting when accessing various properties in an IFC entity
is evident from the previous code samples, as the methods and properties usually
return the abstract class of the entity, or a select. It is hence important to
check for empty values when performing such casts. In C++ that check is the same
expression as the cast itself, because a cast which does not apply returns an
empty value.

The existence of optional attributes should also be checked, which is what
``std::optional`` and the empty reference attributes above are for. A reference
which never resolved, such as a STEP ID pointing at an instance which does not
exist in the file, is reported the same way rather than throwing.

.. literalinclude:: code_examples/06_defensive_programming.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

.. note::

    IfcOpenShell has as of now not been tested explicitly against malicious
    inputs. Schema validation (the correctness of attribute types and
    conformance to the rules of the schema) is currently only available in
    Python, using ``ifcopenshell.validate --rules``, see
    :doc:`../ifcopenshell-python/validation`.
