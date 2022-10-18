Hello, world!
=============

What's inside an IFC?
---------------------

An IFC model can be considered as a collection of elements with relationships to
other elements in a graph-like database. Together, these elements and their
relationships describe the digital built environment.

Each element has a type known as an **IFC Class**. These types define the
attributes that the element may store. For example, the **IfcWall Class** is
allowed to store a **Name** and **Description** attribute.

There are many **IFC Classes** available, defined through an **Object Oriented**
hierarchy. For example, because all **IfcElement** classes can have a
**GlobalId** attribute, that means that because **IfcWall** is a subtype of
**IfcElement**, it can also have a **GlobalId** attribute.

This IFC database can be stored in many formats. The most common is the ``.ifc``
format, which stores data in plain text. If you open a ``.ifc`` file in a text
editor, you'll see something like this:

::

    #1=IFCPROJECT('3Cbhu4euf1hfgM_SHZbeqM',$,'My Project',$,$,$,$,$,#4);
    #2=IFCSIUNIT(*,.LENGTHUNIT.,.MILLI.,.METRE.);
    #3=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
    #4=IFCUNITASSIGNMENT((#2,#3));
    #5=IFCCARTESIANPOINT((0.,0.,0.));

In this example there are 5 elements in the graph. The element with the ID of
**#1** has an **IFC Class** of **IfcProject**. This element has 9
comma-separated attributes.

::

       IFC Class   Quoted string value     Null value               ID reference
       ↓           ↓                       ↓                        ↓
    #1=IFCPROJECT('3Cbhu4euf1hfgM_SHZbeqM',$,'My Project',$,$,$,$,$,#4);
    ↑             ↑ 
    Element ID    Comma-separated list of attributes

By selecting elements by their **IFC Class**, and reading their attributes, you
can navigate from one element to another. The relationships between elements are
called **IFC Concepts** and create meaning in our industry. For example, if a
**IfcWall** element is related to an **IfcBuildingStorey** element in a
particular way, it might mean that the wall is located in the ground floor of
the building.

The official IFC documentation describes hundreds of **IFC Classes**, ranging
from walls, door, to tasks, cost items, parametric materials, and structural
analysis constraints. There are also hundreds of **IFC Concepts**, which may
describe how a wall is in a storey, a construction task might occur one after
another, or how an surface bounds a space for energy analysis.

IfcOpenShell can help you navigate these IFC elements, read their attributes,
and traverse relationships. Your journey begins here.

Core functionality crash course
-------------------------------

This crash course guides you through basic code snippets that give you a general
idea of the low-level functionality that IfcOpenShell-python provides. You'll
need to have IfcOpenShell installed and a sample IFC model. To get the most out
of it, try out the code yourself and see what results you get!

If you don't have an IFC model available, here's a small one for your
convenience provided by the Institute for Automation and Applied Informatics
(IAI) / Karlsruhe Institute of Technology.  It's in German, so you may need to
use some creativity when reading the data :)

.. container:: blockbutton

    `Download sample IFC <https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc>`__

.. seealso::

    You can find more sample models online in the `OSArch Open Data Directory
    <https://wiki.osarch.org/index.php?title=AEC_Open_Data_directory>`__

Let's start with loading the model. Import the IfcOpenShell module, then use the
``open`` function to load the model into a variable called ``model``.

.. code-block:: python

    import ifcopenshell
    model = ifcopenshell.open('/path/to/your/model.ifc')

Let's see what IFC schema we are using:

.. code-block:: python

    print(model.schema) # May return IFC2X3 or IFC4

Let's get the first piece of data in our IFC file:

.. code-block:: python

    print(model.by_id(1))

But getting data from beginning to end isn't too meaningful to humans. What if we knew a ``GlobalId`` value instead?

.. code-block:: python

    print(model.by_guid('0EI0MSHbX9gg8Fxwar7lL8'))

If we're not looking specifically for a single element, perhaps let's see how many walls are in our file, and count them:

.. code-block:: python

    walls = model.by_type('IfcWall')
    print(len(walls))

Once we have an element, we can see what IFC class it is:

.. code-block:: python

    wall = model.by_type('IfcWall')[0]
    print(wall.is_a()) # Returns 'IfcWall'

You can also test if it is a certain class, as well as check for parent classes too:

.. code-block:: python

    print(wall.is_a('IfcWall')) # Returns True
    print(wall.is_a('IfcElement')) # Returns True
    print(wall.is_a('IfcWindow')) # Returns False

Let's quickly check the STEP ID of our element:

.. code-block:: python

    print(wall.id())

Let's get some attributes of an element. IFC attributes have a particular order. We can access it just like a list, so let's get the first and third attribute:

.. code-block:: python

    print(wall[0]) # The first attribute is the GlobalId
    print(wall[2]) # The third attribute is the Name

Knowing the order of attributes is boring and technical. We can access them by name too:

.. code-block:: python

    print(wall.GlobalId)
    print(wall.Name)

Getting attributes one by one is tedious. Let's grab them all:

.. code-block:: python

    # Gives us a dictionary of attributes, such as:
    # {'id': 8, 'type': 'IfcWall', 'GlobalId': '2_qMTAIHrEYu0vYcqK8cBX', ... }
    print(wall.get_info())

Let's see all the properties and quantities associated with this wall:

.. code-block:: python

    import ifcopenshell.util
    import ifcopenshell.util.element
    print(ifcopenshell.util.element.get_psets(wall))

Some attributes are special, called "inverse attributes". They happen when another element is referencing our element. They can reference it for many reasons, like to define a relationship, such as if they create a void in our wall, join our wall, or define a quantity take-off value for our wall, among others. Just treat them like regular attributes:

.. code-block:: python

    print(wall.IsDefinedBy)

Perhaps we want to see all elements which are referencing our wall?

.. code-block:: python

    print(model.get_inverse(wall))

Let's do the opposite, let's see all the elements which our wall references instead:

.. code-block:: python

    print(model.traverse(wall))
    # Or, let's just go down one level deep
    print(model.traverse(wall, max_levels=1))

If you want to modify data, just assign it to the relevant attribute:

.. code-block:: python

    wall.Name = 'My new wall name'

You can also generate a new ``GlobalId``:

.. code-block:: python

    wall.GlobalId = ifcopenshell.guid.new()

After modifying some IFC data, you can save it to a new IFC-SPF file:

.. code-block:: python

    model.write('/path/to/a/new.ifc')

You can generate a new IFC from scratch too, instead of reading an existing one:

.. code-block:: python

    ifc = ifcopenshell.file()
    # Or if you want a particular schema:
    ifc = ifcopenshell.file(schema='IFC4')

You can create new IFC elements, and add it either to an existing or newly created IFC file object:

.. code-block:: python

    # Will return #1=IfcWall($,$,$,$,$,$,$,$,$) - notice all of the attributes are blank!
    new_wall = model.createIfcWall()
    # Will return a list with our wall in it: [#1=IfcWall($,$,$,$,$,$,$,$,$)]
    print(model.by_type('IfcWall'))

Alternatively, you can also use this way to create new elements:

.. code-block:: python

    model.create_entity('IfcWall')

Specifying more arguments lets you fill in attributes while creating the element instead of assigning them separately. You specify them in the order of the attributes.

.. code-block:: python

    # Gives us #1=IfcWall('0EI0MSHbX9gg8Fxwar7lL8',$,$,$,$,$,$,$,$)
    model.create_entity('IfcWall', ifcopenshell.guid.new())

Again, knowing the order of attributes is difficult, so you can use keyword arguments instead:

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

Some attributes of an element aren't just text, they may be a reference to another element. Easy:

.. code-block:: python

    wall = model.createIfcWall()
    wall.OwnerHistory = model.createIfcOwnerHistory()

What if we already have an element from one IFC file and want to add it to another?

.. code-block:: python

    wall = model.by_type('IfcWall')[0]
    new_model = ifcopenshell.file()
    new_model.add(wall)

Fed up with an object? Let's delete it:

.. code-block:: python

    model.remove(wall)

This is only a small sample of the basic building blocks of manipulating IFC
data. IFC comes with a huge utility library and API for performing common tasks.
See :doc:`Code examples<code_examples>` for more.
