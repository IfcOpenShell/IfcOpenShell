Hello, world!
=============

If you're reading this, we assume you already know IFC and just want to quickly
get started with IfcOpenShell.

IfcOpenShell can be used from **C++**, **Python**, and **JavaScript /
TypeScript**. All three share the same C++ core, so the concepts on this page
are the same whichever language you choose; only the syntax differs. Every code
block below has a tab for each language, and each block switches on its own.

This crash course guides you through basic code snippets that give you a general
idea of the low-level functionality that IfcOpenShell-python provides. You'll need to
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

Install IfcOpenShell for your language, see :doc:`install`. Every code block on
this page is cut from a program in ``docs/ifcopenshell/examples/hello_world``,
which the test suite runs against a small IFC4 model. Each program takes the
path of the model as its first argument, and later code blocks assume that the
model is already open as ``model``.

- **Python** snippets can also be typed into a Python console one after the
  other.
- **C++** snippets use the IFC4 schema, so that the generated ``Ifc4`` classes
  can be used by name, such as ``Ifc4::IfcWall``. The C++ core is not tied to a
  single schema though, see :ref:`Schema-agnostic parsing of IFCs
  <schema-agnostic-parsing-of-ifcs>`.
- **JavaScript** snippets are ES modules, and can be used in TypeScript as they
  are. The JavaScript and TypeScript bindings are a work in progress, and their
  API is subject to change.

Loading the model
-----------------

Let's start with loading the model into a variable called ``model``.

.. snippet:: hello_world/load_model
    :caption-cpp: A file that could not be read reports as not good, which is
        how you check that parsing succeeded.
    :caption-js: Load the schema plugin for your model before opening it.
        ``open()`` takes bytes rather than a path, so in Node.js the file is
        read first.

    .. lang-note:: js

        In the browser, obtain the same bytes from an uploaded ``File`` or an
        HTTP response. For example, replace the ``readFile`` call with:

        .. code-block:: javascript

            const response = await fetch('/models/model.ifc');
            if (!response.ok) throw new Error(`Failed to load IFC: ${response.status}`);
            const bytes = new Uint8Array(await response.arrayBuffer());

Inspecting the schema
---------------------

Let's see what IFC schema we are using:

.. snippet:: hello_world/schema
    :js: hello_world/by_id#schema
    :caption-cpp: ``model.schema()`` returns the schema declaration itself, whose
        name is the verbatim name from the EXPRESS schema.
    :caption-js: ``schema()`` returns the general schema version, without
        addendum or technical corrigendum suffixes.

Getting an instance by ID
-------------------------

Let's get the first piece of data in our IFC file:

.. snippet:: hello_world/by_id

Getting an instance by GlobalId
-------------------------------

But getting data from beginning to end isn't too meaningful to humans. What if
we knew a ``GlobalId`` value instead?

.. snippet:: hello_world/by_guid
    :js: hello_world/walls#by_guid
    :caption-js: Looking up an ID or a GlobalId which is not in the file raises
        an error.

Counting the instances of a type
--------------------------------

If we're not looking specifically for a single element, perhaps let's see how
many walls are in our file, and count them:

.. snippet:: hello_world/count_walls
    :js: hello_world/walls#count
    :caption-js: Type queries return ordinary arrays.
        ``model.byTypeExclSubtypes()`` selects only the exact IFC class.

The class of an instance
------------------------

Once we have an element, we can see what IFC class it is:

.. snippet:: hello_world/instance_class
    :js: hello_world/walls#instance_class

You can also test if it is a certain class, as well as check for parent classes
too:

.. snippet:: hello_world/is_a
    :js: hello_world/walls#is_a

The STEP ID of an instance
--------------------------

Let's quickly check the STEP ID of our element:

.. snippet:: hello_world/step_id
    :js: hello_world/walls#step_id

Reading attributes
------------------

Let's get some attributes of an element. IFC attributes have a particular
order. We can access it just like a list, so let's get the first and third
attribute:

.. snippet:: hello_world/attribute_by_index
    :js: hello_world/walls#attribute_by_index

Knowing the order of attributes is boring and technical. We can access them by
name too:

.. snippet:: hello_world/attribute_by_name
    :js: hello_world/walls#attribute_by_name
    :caption-cpp: The generated classes have accessors named after the
        attribute, which are strongly typed and which wrap optional attributes
        in a ``std::optional``.

Getting all attributes
----------------------

Getting attributes one by one is tedious. Let's grab them all:

.. snippet:: hello_world/all_attributes
    :js: hello_world/walls#all_attributes
    :caption-cpp: The C++ API does not return a dictionary of all attributes,
        but every instance can print itself as it appears in the IFC file.

Reading the property sets of an element
---------------------------------------

Let's see all the properties and quantities associated with this wall:

.. snippet:: hello_world/property_sets
    :js: code_examples/property_sets
    :caption-cpp: There is no ready made property set helper in C++, so the
        relationships are walked by hand.
    :caption-js: There is no property set helper in JavaScript yet, so the
        relationships are walked by hand.

Inverse attributes
------------------

Some attributes are special, called "inverse attributes". They happen when
another element is referencing our element. They can reference it for many
reasons, like to define a relationship, such as if they create a void in our
wall, join our wall, or define a quantity take-off value for our wall, among
others. Just treat them like regular attributes:

.. snippet:: hello_world/inverse_attributes
    :js: hello_world/walls#inverse_attributes

Perhaps we want to see all elements which are referencing our wall?

.. snippet:: hello_world/get_inverse
    :js: hello_world/walls#get_inverse
    :caption-js: ``getInverse()`` returns a ``Set`` that is unique by IFC
        identity.

Traversing references
---------------------

Let's do the opposite, let's see all the elements which our wall references
instead:

.. snippet:: hello_world/traverse
    :js: hello_world/walls#traverse
    :caption-js: The depth is required, and ``-1`` means unlimited.
        ``traverseBreadthFirst()`` takes the same arguments.

Modifying data
--------------

If you want to modify data, just assign it to the relevant attribute:

.. snippet:: hello_world/set_attribute
    :js: hello_world/walls#set_attribute

You can also generate a new ``GlobalId``:

.. snippet:: hello_world/new_global_id
    :js: hello_world/walls#new_global_id
    :caption-js: There is no GlobalId generator in JavaScript yet. Assign a
        distinct, valid 22 character GlobalId that your application generates.

Writing the model
-----------------

After modifying some IFC data, you can save it to a new IFC-SPF file:

.. snippet:: hello_world/write_file
    :caption-js: ``toString()`` serialises the model as IFC-SPF text. In a
        browser, ``new Blob([model.toString()])`` produces a downloadable file.

Creating a new file
-------------------

You can generate a new IFC from scratch too, instead of reading an existing
one:

.. snippet:: hello_world/new_file
    :caption-js: Load the schema plugin before constructing the file. This
        program also creates a wall, which is covered next.

Creating instances
------------------

You can create new IFC elements, and add it either to an existing or newly
created IFC file object:

.. snippet:: hello_world/create_instance
    :js: hello_world/create_instance#create_instance
    :caption-js: ``create()`` always takes the name of the entity.

Alternatively, you can also use this way to create new elements:

.. snippet:: hello_world/create_instance_by_name
    :na: js
    :caption-js: ``create()``, shown above, always takes the name of the entity.

Specifying more arguments lets you fill in attributes while creating the
element instead of assigning them separately. You specify them in the order of
the attributes.

.. snippet:: hello_world/create_instance_attribute_order
    :js: hello_world/create_instance#create_instance_attribute_order

Again, knowing the order of attributes is difficult, so you can use keyword
arguments instead:

.. snippet:: hello_world/create_instance_attribute_names
    :js: hello_world/create_instance#create_instance_attribute_names

Sometimes, it's easier to expand a dictionary:

.. snippet:: hello_world/create_instance_from_table
    :js: hello_world/create_instance#create_instance_from_table

Some attributes of an element aren't just text, they may be a reference to
another element. Easy:

.. snippet:: hello_world/set_reference_attribute
    :js: hello_world/create_instance#set_reference_attribute

Copying an instance into another file
-------------------------------------

What if we already have an element from one IFC file and want to add it to
another?

.. snippet:: hello_world/copy_instance
    :js: hello_world/create_instance#copy_instance
    :caption-js: ``add()`` returns the copy in the target file.

Removing an instance
--------------------

Fed up with an object? Let's delete it:

.. snippet:: hello_world/remove_instance
    :js: hello_world/create_instance#remove_instance

Releasing the model
-------------------

The model owns its IFC data, so keep it alive while you are accessing its
elements.

.. snippet:: hello_world/release_model
    :caption-python: The garbage collector releases the model once nothing
        refers to it anymore.
    :caption-cpp: ``ifcopenshell::file`` releases its instances in its
        destructor, so the instances must not outlive the model.
    :caption-js: Only ``File`` and geometry ``Iterator`` objects need to be
        disposed. Other wrappers use GC cleanup.

    .. lang-note:: js

        TypeScript projects can use ``using`` declarations for automatic
        disposal:

        .. code-block:: typescript

            using model = new ifcopenshell.File('IFC4');
            const wall = model.create('IfcWall', { Name: 'Example wall' });
            console.log(wall.Name);

        For runtimes without ``using`` support, call ``dispose()`` in a
        ``try`` / ``finally`` block.

Where to go next
----------------

This is only a small sample of the basic building blocks of manipulating IFC
data. IFC comes with a huge utility library and API for performing common tasks.
See :doc:`Code examples <code_examples>` for more.
