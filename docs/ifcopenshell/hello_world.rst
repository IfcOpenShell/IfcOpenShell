Hello, world!
=============

If you're reading this, we assume you already know IFC and just want to quickly
get started with IfcOpenShell.

IfcOpenShell can be used from **Python**, **C++**, and **JavaScript /
TypeScript**. All three share the same C++ core, so the concepts on this page
are the same whichever language you choose; only the syntax differs. Every
snippet below has a tab for each language. Pick one, and every other snippet on
this page, and on the other shared guides, switches with it.

This crash course guides you through basic code snippets that give you a general
idea of the low-level functionality that IfcOpenShell provides. You'll need to
have IfcOpenShell installed and a sample IFC model. To get the most out of it,
try out the code yourself and see what results you get!

If you don't have an IFC model available, here's a small one for your
convenience provided by the Institute for Automation and Applied Informatics
(IAI) / Karlsruhe Institute of Technology.  It's in German, so you may need to
use some creativity when reading the data :)

.. container:: blockbutton

    `Download sample IFC <https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc>`__

.. seealso::

    You can find more sample models online in the `OSArch Open Data Directory
    <https://wiki.osarch.org/index.php?title=AEC_Open_Data_directory>`__

Before you start
----------------

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        Install IfcOpenShell-Python as described in
        :doc:`../ifcopenshell-python/installation`. The snippets are meant to
        be typed into a Python console one after the other.

    .. tab-item:: C++
        :sync: cpp

        Build and install the C++ library as described in
        :doc:`installation`. Every C++ snippet on this page is cut from a
        standalone program in ``docs/ifcopenshell-cpp/hello_world``, which is
        compiled and run as part of the documentation's test suite, see
        :ref:`building-and-running-the-examples`. Each program takes the path of
        the model as its first command line argument, and the snippets assume
        that it has been loaded into a variable called ``model``.

        The examples use the IFC4 schema, so that the generated ``Ifc4``
        classes can be used by name, such as ``Ifc4::IfcWall``. The C++ core is
        not tied to a single schema though, see :ref:`Schema-agnostic parsing of
        IFCs <schema-agnostic-parsing-of-ifcs>` for how to write the same logic
        in a way that processes all schema versions at once.

    .. tab-item:: JavaScript
        :sync: js

        Install the ``ifcopenshell`` package as described in
        :doc:`../ifcopenshell-js/installation`. The package works in Node.js and
        in browsers, through WebAssembly. Examples use JavaScript ES modules,
        and can be used in TypeScript as they are.

        Every JavaScript snippet on this page is cut from a program in
        ``docs/ifcopenshell-js/hello_world`` or
        ``docs/ifcopenshell-js/code_examples``, which the test suite runs
        against a small IFC4 model, see :doc:`../ifcopenshell-js/running_tests`.
        Each program takes the model path as its first argument, and later
        snippets assume that file is already open as ``model``.

        .. note::

            The JavaScript and TypeScript bindings are a work in progress, and
            their API is subject to change.

Loading the model
-----------------

Let's start with loading the model into a variable called ``model``.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        Import the IfcOpenShell module, then use the ``open`` function.

        .. code-block:: python

            import ifcopenshell
            model = ifcopenshell.open('/path/to/your/model.ifc')

    .. tab-item:: C++
        :sync: cpp

        The equivalent of Python's ``ifcopenshell.open()`` is the
        ``ifcopenshell::file`` constructor. A file that could not be read
        reports as not good, which is how you check that parsing succeeded.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/01_load_model.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        Initialize the runtime, and load the schema plugin for your model before
        opening it. This example uses an IFC4 file. ``open()`` accepts a
        ``Uint8Array`` or ``ArrayBuffer`` rather than a filesystem path, so in
        Node.js the file is read as bytes first:

        .. literalinclude:: ../ifcopenshell-js/hello_world/01_open.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

        In the browser, obtain the same bytes from an uploaded ``File`` or an
        HTTP response. For example, replace the ``readFile`` call with:

        .. code-block:: javascript

            const response = await fetch('/models/model.ifc');
            if (!response.ok) throw new Error(`Failed to load IFC: ${response.status}`);
            const bytes = new Uint8Array(await response.arrayBuffer());

Inspecting the schema
---------------------

Let's see what IFC schema we are using:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(model.schema) # May return IFC2X3, IFC4, or IFC4X3.

    .. tab-item:: C++
        :sync: cpp

        There is no ``schema_identifier()`` in C++. ``model.schema()`` returns
        the schema declaration itself, whose name is the verbatim name from the
        underlying EXPRESS schema.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/02_schema.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``schema()`` returns the general schema version, without addendum or
        technical corrigendum suffixes, like Python's ``model.schema``.

        .. literalinclude:: ../ifcopenshell-js/hello_world/02_by_id.mjs
            :language: javascript
            :start-after: // tag::schema
            :end-before: // end::schema

Getting an instance by ID
-------------------------

Every entity instance in an IFC-SPF file has a STEP ID, such as ``#1``. Let's
get the first piece of data in our IFC file:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(model.by_id(1))

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/03_by_id.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. literalinclude:: ../ifcopenshell-js/hello_world/02_by_id.mjs
            :language: javascript
            :start-after: // tag::by_id
            :end-before: // end::by_id

Getting an instance by GlobalId
-------------------------------

But getting data from beginning to end isn't too meaningful to humans. What if
we knew a ``GlobalId`` value instead?

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(model.by_guid('0EI0MSHbX9gg8Fxwar7lL8'))

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/04_by_guid.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        Looking up an ID or a GlobalId which is not in the file raises an error.

        .. literalinclude:: ../ifcopenshell-js/hello_world/03_walls.mjs
            :language: javascript
            :start-after: // tag::by_guid
            :end-before: // end::by_guid

Counting the instances of a type
--------------------------------

If we're not looking specifically for a single element, perhaps let's see how
many walls are in our file, and count them. Querying by type includes subtypes,
so ``IfcWallStandardCase`` instances are returned for ``IfcWall`` as well.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            walls = model.by_type('IfcWall')
            print(len(walls))

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/05_count_walls.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        Type queries return ordinary JavaScript arrays.
        ``model.byTypeExclSubtypes(typeName)`` selects only the exact IFC
        class.

        .. literalinclude:: ../ifcopenshell-js/hello_world/03_walls.mjs
            :language: javascript
            :start-after: // tag::count
            :end-before: // end::count

The class of an instance
------------------------

Once we have an element, we can see what IFC class it is. You can also test if
it is a certain class, as well as check for parent classes too.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            wall = model.by_type('IfcWall')[0]
            print(wall.is_a()) # Returns 'IfcWall'

            print(wall.is_a('IfcWall')) # Returns True
            print(wall.is_a('IfcElement')) # Returns True
            print(wall.is_a('IfcWindow')) # Returns False

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/06_instance_type.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/07_is_a.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. literalinclude:: ../ifcopenshell-js/hello_world/03_walls.mjs
            :language: javascript
            :start-after: // tag::is_a
            :end-before: // end::is_a

The STEP ID of an instance
--------------------------

Let's quickly check the STEP ID of our element:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(wall.id())

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/08_step_id.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. code-block:: javascript

            console.log(wall.id());

Reading attributes
------------------

Let's get some attributes of an element. IFC attributes have a particular
order, and can be addressed by their position just like a list. Knowing the
order of attributes is boring and technical though, so we can access them by
name too.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(wall[0]) # The first attribute is the GlobalId
            print(wall[2]) # The third attribute is the Name

            print(wall.GlobalId)
            print(wall.Name)

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/09_attribute_by_index.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        The generated classes have accessors named after the attribute, which
        are strongly typed and which wrap optional attributes in a
        ``std::optional``.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/10_attribute_by_name.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``get()`` reads an attribute by its position, or by its name. Schema
        attributes can also be read as properties, such as ``wall.Name``.

        .. literalinclude:: ../ifcopenshell-js/hello_world/03_walls.mjs
            :language: javascript
            :start-after: // tag::attributes
            :end-before: // end::attributes

Getting all attributes
----------------------

Getting attributes one by one is tedious. Let's grab them all:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            # Gives us a dictionary of attributes, such as:
            # {'id': 8, 'type': 'IfcWall', 'GlobalId': '2_qMTAIHrEYu0vYcqK8cBX', ... }
            print(wall.get_info())

    .. tab-item:: C++
        :sync: cpp

        The C++ API does not return a dictionary of all attributes, but every
        instance can print itself as it appears in the IFC file.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/11_instance_info.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``getInfo()`` returns a flat object of attributes, with ``id`` and
        ``type`` keys, like Python's ``get_info()``.

        .. code-block:: javascript

            console.log(wall.getInfo());

Reading the property sets of an element
---------------------------------------

Let's see all the properties and quantities associated with this wall:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            import ifcopenshell.util
            import ifcopenshell.util.element
            print(ifcopenshell.util.element.get_psets(wall))

    .. tab-item:: C++
        :sync: cpp

        Python has ``ifcopenshell.util.element.get_psets()``, but the C++ core
        does not ship a ready made property set helper, so the relationships
        are walked by hand.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/12_property_sets.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The JavaScript bindings do not ship a property set helper yet either,
        so the relationships are walked by hand.

        .. literalinclude:: ../ifcopenshell-js/code_examples/05_property_sets.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

Inverse attributes
------------------

Some attributes are special, called "inverse attributes". They happen when
another element is referencing our element. They can reference it for many
reasons, like to define a relationship, such as if they create a void in our
wall, join our wall, or define a quantity take-off value for our wall, among
others. Just treat them like regular attributes:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(wall.IsDefinedBy)

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/13_inverse_attributes.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. code-block:: javascript

            console.log(wall.IsDefinedBy);

Perhaps we want to see *all* elements which are referencing our wall,
regardless of which attribute they use to do so?

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(model.get_inverse(wall))

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/14_get_inverse.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``getInverse()`` returns a ``Set`` that is unique by IFC identity. This
        snippet also shows ``traverse()``, from the next section.

        .. literalinclude:: ../ifcopenshell-js/code_examples/06_navigate.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

Traversing references
---------------------

Let's do the opposite, let's see all the elements which our wall references
instead:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            print(model.traverse(wall))
            # Or, let's just go down one level deep
            print(model.traverse(wall, max_levels=1))

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/15_traverse.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The depth is required, and ``-1`` means unlimited.
        ``traverseBreadthFirst()`` takes the same arguments.

        .. code-block:: javascript

            console.log(model.traverse(wall, -1));
            // Or, let's just go down one level deep
            console.log(model.traverse(wall, 1));

Modifying data
--------------

If you want to modify data, just assign it to the relevant attribute.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            wall.Name = 'My new wall name'

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/16_set_attribute.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        Attributes are changed with ``set()``.

        .. code-block:: javascript

            wall.set('Name', 'My new wall name');

You can also generate a new ``GlobalId``:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            wall.GlobalId = ifcopenshell.guid.new()

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/17_new_global_id.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The JavaScript bindings do not have a GlobalId generator yet. Assign a
        distinct, valid 22 character IFC GlobalId which your application
        generates itself.

        .. code-block:: javascript

            wall.set('GlobalId', '0YvctVUKr0kugbFTf53O9L');

Writing the model
-----------------

After modifying some IFC data, you can save it to a new IFC-SPF file:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            model.write('/path/to/a/new.ifc')

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/18_write_file.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``toString()`` serializes the model as IFC-SPF text. In Node.js, write
        it with ``writeFile`` from ``node:fs/promises``:

        .. literalinclude:: ../ifcopenshell-js/hello_world/04_edit.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

        In a browser, ``new Blob([model.toString()], { type: 'text/plain' })``
        produces a downloadable IFC file.

Creating a new file
-------------------

You can generate a new IFC from scratch too, instead of reading an existing
one. Such a file is in memory only until it is written out.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            ifc = ifcopenshell.file()
            # Or if you want a particular schema:
            ifc = ifcopenshell.file(schema='IFC4')

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/19_new_file.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        Load the schema plugin before constructing the file. This program also
        creates a wall, which is covered next.

        .. literalinclude:: ../ifcopenshell-js/hello_world/05_create.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

Creating instances
------------------

You can create new IFC elements, and add them to an existing or newly created
IFC file. Elements can be created from a class, or from the name of the entity
as it appears in the IFC schema. Their attributes can be filled in while
creating the element, either by position in the order of the attributes, or,
since knowing that order is difficult, by name.

This demonstrates entity creation only. A complete exchange model also needs the
appropriate project, units, contexts, and relationships, and every root entity
needs its own distinct, valid GlobalId.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            # Will return #1=IfcWall($,$,$,$,$,$,$,$,$) - notice all of the attributes are blank!
            new_wall = model.createIfcWall()
            # Will return a list with our wall in it: [#1=IfcWall($,$,$,$,$,$,$,$,$)]
            print(model.by_type('IfcWall'))

        Alternatively, you can also use this way to create new elements:

        .. code-block:: python

            model.create_entity('IfcWall')

        Specifying more arguments lets you fill in attributes while creating
        the element instead of assigning them separately. You specify them in
        the order of the attributes.

        .. code-block:: python

            # Gives us #1=IfcWall('0EI0MSHbX9gg8Fxwar7lL8',$,$,$,$,$,$,$,$)
            model.create_entity('IfcWall', ifcopenshell.guid.new())

        Again, knowing the order of attributes is difficult, so you can use
        keyword arguments instead:

        .. code-block:: python

            # Gives us #1=IfcWall('0EI0MSHbX9gg8Fxwar7lL8',$,'Wall Name',$,$,$,$,$,$)
            model.create_entity('IfcWall', GlobalId=ifcopenshell.guid.new(), Name='Wall Name')

        Sometimes, it's easier to expand a dictionary:

        .. code-block:: python

            data = {
                'GlobalId': ifcopenshell.guid.new(),
                'Name': 'Wall Name'
            }
            model.create_entity('IfcWall', **data)

    .. tab-item:: C++
        :sync: cpp

        Instances are added to the file that created them straight away.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/20_create_instance.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        Creating an instance from the name of the entity is the equivalent of
        Python's ``create_entity()``.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/21_create_instance_by_name.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        Attributes filled in by position:

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/22_create_instance_attribute_order.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        Attributes assigned by name:

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/23_create_instance_attribute_names.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        Collecting the attributes in a table first, and assigning them in a
        loop, is the equivalent of expanding a Python dictionary into
        ``create_entity()``.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/24_create_instance_from_table.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``model.create()`` takes the name of the entity, and optionally an
        object of attributes by name, so it covers both the keyword argument
        and the dictionary forms of Python. The new entity is added to the file
        straight away.

        .. code-block:: javascript

            const wall = model.create('IfcWall');
            const namedWall = model.create('IfcWall', {
              GlobalId: '0YvctVUKr0kugbFTf53O9L',
              Name: 'Wall Name',
            });

Some attributes of an element aren't just text, they may be a reference to
another element. Easy:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            wall = model.createIfcWall()
            wall.OwnerHistory = model.createIfcOwnerHistory()

    .. tab-item:: C++
        :sync: cpp

        The generated setters take the referenced instance directly.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/25_set_reference_attribute.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. code-block:: javascript

            const wall = model.create('IfcWall');
            wall.set('OwnerHistory', model.create('IfcOwnerHistory'));

Copying an instance into another file
-------------------------------------

What if we already have an element from one IFC file and want to add it to
another?

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            wall = model.by_type('IfcWall')[0]
            new_model = ifcopenshell.file()
            new_model.add(wall)

    .. tab-item:: C++
        :sync: cpp

        The forward references of the instance are copied along with it, and
        the copy is created in the schema of the target file, so both files
        have to use the same one.

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/26_add_instance_to_another_file.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        Note that, unlike Python's ``ifcopenshell.util.element.copy()``, this
        does copy references recursively, but it makes no other attempts at
        resulting in a valid file, for example it does not convert length units
        between the two files.

    .. tab-item:: JavaScript
        :sync: js

        ``add()`` returns the copy in the target file.

        .. code-block:: javascript

            const wall = model.byType('IfcWall')[0];
            const newModel = new ifcopenshell.File('IFC4');
            const copy = newModel.add(wall);

Removing an instance
--------------------

Fed up with an object? Let's delete it:

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            model.remove(wall)

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/hello_world/27_remove_instance.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. code-block:: javascript

            model.remove(wall);

Releasing the model
-------------------

The model owns its IFC data, so keep it alive while you are accessing its
elements.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        The model is released by the garbage collector once nothing refers to it
        anymore.

    .. tab-item:: C++
        :sync: cpp

        ``ifcopenshell::file`` releases its instances in its destructor, so the
        model is released when it goes out of scope, and the instances must not
        outlive it.

    .. tab-item:: JavaScript
        :sync: js

        Only ``File`` and geometry ``Iterator`` objects implement
        ``Disposable``. Dispose them when finished to invoke their native C++
        destructors. Entity references and other binding wrappers use GC
        cleanup, and query results are ordinary JavaScript arrays.

        .. literalinclude:: ../ifcopenshell-js/hello_world/06_dispose.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

        TypeScript projects can use ``using`` declarations for automatic
        disposal:

        .. code-block:: typescript

            using model = new ifcopenshell.File('IFC4');
            const wall = model.create('IfcWall', { Name: 'Example wall' });
            console.log(wall.Name);

        The compiler transforms these declarations into cleanup calls. When
        writing JavaScript for runtimes without ``using`` support, use
        ``try`` / ``finally``.

Where to go next
----------------

This is only a small sample of the basic building blocks of manipulating IFC
data. See :doc:`geometry_processing` for turning this data into geometry, in
any of the three languages. Each language also has its own guides, for what is
done differently, or only available, in that language:

- :doc:`../ifcopenshell-python`, with a huge utility library and API for
  performing common tasks, see the :doc:`Python code examples
  <../ifcopenshell-python/code_examples>`.
- :doc:`../ifcopenshell-cpp`, with schema-agnostic parsing and defensive
  programming in the :doc:`C++ code examples
  <../ifcopenshell-cpp/code_examples>`.
- :doc:`../ifcopenshell-js`, for Node.js and the browser, see the
  :doc:`JavaScript code examples <../ifcopenshell-js/code_examples>`.
