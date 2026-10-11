.. This file was generated with the assistance of an AI coding tool.

Hello, world! (C++)
===================

This is the C++ counterpart of the Python :doc:`Hello, world!
<../ifcopenshell-python/hello_world>` crash course. It guides you through the
same basic code snippets, but using the IfcOpenShell C++ API, and shows the
direct C++ equivalent of each Python operation.

.. seealso::

    Every snippet on this page lives in its own ``.cpp`` file under
    ``docs/ifcopenshell/hello_world``, and each of them
    is compiled and run as part of the documentation's test suite. See
    :ref:`building-and-running-the-examples` to build and run them yourself.

The examples use the IFC4 schema, so that the generated ``Ifc4`` classes can be
used by name, such as ``Ifc4::IfcWall``. The C++ core is not tied to a single
schema though, see :ref:`Schema-agnostic parsing of IFCs
<schema-agnostic-parsing-of-ifcs>` for how to write the same logic in a way that
processes all schema versions at once.

.. note::

    Each example takes the path of the model as its first command line
    argument, and the snippets in this page assume that it has been loaded into
    a variable called ``model``, exactly like the Python crash course assumes.

Loading the model
-----------------

The equivalent of Python's ``ifcopenshell.open()`` is the ``ifcopenshell::file``
constructor. A file that could not be read reports as not good, which is how you
check that parsing succeeded.

.. literalinclude:: hello_world/01_load_model.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Inspecting the schema
---------------------

.. literalinclude:: hello_world/02_schema.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Getting an instance by ID
-------------------------

Every instance in an IFC-SPF file has a STEP ID, such as ``#1``.

.. literalinclude:: hello_world/03_by_id.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Getting an instance by GlobalId
-------------------------------

Getting data from beginning to end is not too meaningful to humans, but a
``GlobalId`` is.

.. literalinclude:: hello_world/04_by_guid.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Counting the instances of a type
--------------------------------

``instances_by_type()`` returns all instances of an entity type, including
subtypes, so ``IfcWallStandardCase`` instances are returned for ``IfcWall`` as
well.

.. literalinclude:: hello_world/05_count_walls.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

The class of an instance
------------------------

Once we have an instance we can ask it what it is.

.. literalinclude:: hello_world/06_instance_type.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

You can also test against other classes, including parent classes.

.. literalinclude:: hello_world/07_is_a.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

The STEP ID of an instance
--------------------------

.. literalinclude:: hello_world/08_step_id.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Reading attributes
------------------

IFC attributes have a particular order, and can be addressed by their position
just like a list.

.. literalinclude:: hello_world/09_attribute_by_index.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Knowing the order of attributes is boring and technical, so the generated classes
also have accessors named after the attribute, which are strongly typed and
which wrap optional attributes in a ``std::optional``.

.. literalinclude:: hello_world/10_attribute_by_name.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Printing everything an instance holds
-------------------------------------

The C++ API does not return a dictionary of all attributes, but every instance
can print itself as it appears in the IFC file, which is the equivalent of
Python's ``get_info()``.

.. literalinclude:: hello_world/11_instance_info.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Reading the property sets of an instance
----------------------------------------

Python has ``ifcopenshell.util.element.get_psets()``, but the C++ core does not
ship a ready made property set helper, so the relationships are walked by hand.

.. literalinclude:: hello_world/12_property_sets.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Inverse attributes
------------------

Some attributes are special, and are called "inverse attributes". They happen
when another instance is referencing our instance, for example to define a
relationship. Just treat them like regular attributes.

.. literalinclude:: hello_world/13_inverse_attributes.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Perhaps we want to see *all* instances which are referencing our instance,
regardless of which attribute they use to do so.

.. literalinclude:: hello_world/14_get_inverse.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Traversing references
---------------------

The opposite of the previous example: everything our instance references.

.. literalinclude:: hello_world/15_traverse.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Modifying data
--------------

To modify data, assign it to the relevant attribute.

.. literalinclude:: hello_world/16_set_attribute.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

You can also generate a new ``GlobalId``.

.. literalinclude:: hello_world/17_new_global_id.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Writing the model
-----------------

After modifying some IFC data, you can save it to a new IFC-SPF file.

.. literalinclude:: hello_world/18_write_file.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Creating a new file
-------------------

You can generate a new IFC file from scratch too, instead of reading an existing
one. Such a file is in memory only until it is written out.

.. literalinclude:: hello_world/19_new_file.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Creating instances
------------------

You can create new IFC instances, and they are added to the file that created
them straight away.

.. literalinclude:: hello_world/20_create_instance.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Alternatively, you can also create an instance from the name of the entity as it
appears in the IFC schema, which is the equivalent of Python's
``create_entity()``.

.. literalinclude:: hello_world/21_create_instance_by_name.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Attributes can be filled in straight away, by their position, in the order of
the attributes.

.. literalinclude:: hello_world/22_create_instance_attribute_order.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Again, knowing the order of attributes is difficult, so attributes can also be
assigned by name.

.. literalinclude:: hello_world/23_create_instance_attribute_names.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Sometimes it is easier to collect the attributes in a table first, and assign
them in a loop. This is the equivalent of expanding a Python dictionary into
``create_entity()``.

.. literalinclude:: hello_world/24_create_instance_from_table.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Some attributes of an instance are not text, but a reference to another instance.
The generated setters take the referenced instance directly.

.. literalinclude:: hello_world/25_set_reference_attribute.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Copying an instance into another file
-------------------------------------

What if we already have an instance in one file, and want to add it to another?
The forward references of the instance are copied along with it, and the copy is
created in the schema of the target file, so both files have to use the same one.

.. literalinclude:: hello_world/26_add_instance_to_another_file.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Note that, unlike Python's ``ifcopenshell.util.element.copy()``, this does copy
references recursively, but it makes no other attempts at resulting in a valid
file, for example it does not convert length units between the two files.

Removing an instance
--------------------

Fed up with an instance? Remove it.

.. literalinclude:: hello_world/27_remove_instance.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

.. _building-and-running-the-examples:

Building and running the examples
---------------------------------

The sources next to this page are a standalone CMake project which consumes an
installed IfcOpenShell through ``find_package(IfcOpenShell CONFIG)``, the same
way any other third party consumer would:

.. code-block:: shell

    cd docs/ifcopenshell/hello_world
    cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/ifcopenshell
    cmake --build build --config RelWithDebInfo

Every example is registered as a test which runs it with
``hello_world.ifc``, a small IFC4 model that ships with the examples:

.. code-block:: shell

    ctest --test-dir build -C RelWithDebInfo --output-on-failure

There is also a single custom command which builds and runs all of them at once,
and which fails if any of the examples reports a failure:

.. code-block:: shell

    cmake --build build --config RelWithDebInfo --target run_examples

This is only a small sample of the basic building blocks of working with IFC
data in C++. See :doc:`getting_started` for more on parsing, and the
:doc:`Geometry processing <geometry_iterator>` pages for turning this data into
geometry.
