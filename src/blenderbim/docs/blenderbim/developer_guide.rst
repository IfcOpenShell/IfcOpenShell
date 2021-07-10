Developer guide
===============

The BlenderBIM Add-on takes a unique approach to authoring BIM data. Traditional
BIM authoring apps create features that are tailored for a single discipline's
paradigm, such as a 3D environment, or a spreadsheet view, and store their data
structure in a schema that is unique to their application. In order to
interoperate with others, there is an export or import process that translates
between their discipline-specific schema and the ISO standard for BIM: IFC.
After translation, they then serialise it typically into one of the various IFC
formats.

The BlenderBIM Add-on does things differently.

The BlenderBIM Add-on modifies ISO standard BIM data directly using the IFC
schema in memory. Every user operation reads or writes this data structure in
memory, and the IFC data becomes the source of truth for all data. There is no
such thing as an import or export, but simply a serialisation or deserialisation
operation. This also means that the ``.blend`` container is largely unnecessary,
as nothing of significance is stored in the Blender system. Unlike traditional
BIM which relies on translated IFC data, the BlenderBIM Add-on works with Native
IFC, and also works equally across all disciplines.

Due to this significant difference, hacking on the BlenderBIM Add-on requires
knowledge not just about how Blender works, but also how IFC works.

Technology stack
----------------

At a high level, the BlenderBIM Add-on works through two integration of two
systems. The IFC based system takes care of reading and writing IFC data using
the IfcOpenShell library. This system is agnostic of Blender and the BlenderBIM
Add-on. Data is read from the IFC dataset using ``Data`` classes. Data is
written into the IFC dataset using ``Usecase`` classes.

The Blender based system takes care of turning Blender into a BIM authoring
client. Like all Blender add-ons, ``Operators`` define user operations, such as
those triggered when pressing a button. ``UI`` defines the interface, such as
the layout of buttons, input fields, and panels. Finally, ``Props`` define
properties that Blender keeps track of, typically for interface input fields or
user settings.

The Blender system depends on the IFC system. The IFC system does not depend on
the Blender system.

.. image:: architecture.png

..
    digraph G {rankdir=LR;
      node [fontname = "Handlee", shape=rect];

      subgraph cluster_0 {
        node [style=filled,color=pink];

        IfcOpenShell -> Data;
        Usecase -> IfcOpenShell;

        label = "*IFC based*";
        fontsize = 20;
        color=grey
      }

      subgraph cluster_1 {
        node [style=filled,color=lightblue];

        Operators -> Usecase
        Data->UI
        Data->Operators

        Operators -> Props
        Props -> Operators
        Props -> UI

        label = "*Blender based*";
        fontsize = 20;
        color=grey
      }
    }

Of course, there are many details that we are glossing over, but it provides a
good representation of data flow in the BlenderBIM Add-on.

The code for these two systems may be found here:

- `ifcopenshell <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcopenshell-python>`__
- `blenderbim <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/blenderbim>`__

Module architecture
-------------------

Because BIM authoring is a vast field, the architecture is further grouped into
modules. Modules include things like project related capabilities, structural
related capabilities, costing related capabilities, and so on.

Each module consists an IFC based system, which does all the IFC manipulations,
and a Blender based counterpart, which exposes all of these operations to the
user via the Blender interface.

.. image:: module-architecture.png

..
    digraph G {
        node [fontname = "Handlee", shape=rect];
        subgraph cluster_1 {
            rank=same;
            {
                blender1 [label="Blender", style=filled, color=lightblue];
                ifc1 [label="IFC", style=filled, color=pink];
                ifc1 -> blender1
                blender1 -> ifc1
            }

            label = "*Project Module*";
            fontsize = 20;
            color=grey
        }
        subgraph cluster_2 {
            rank=same;
            {
                blender2 [label="Blender", style=filled, color=lightblue];
                ifc2 [label="IFC", style=filled, color=pink];
                ifc2 -> blender2
                blender2 -> ifc2
            }

            label = "*Structural Module*";
            fontsize = 20;
            color=grey
        }
        subgraph cluster_3 {
            rank=same;
            {
                blender3 [label="Blender", style=filled, color=lightblue];
                ifc3 [label="IFC", style=filled, color=pink];
                ifc3 -> blender3
                blender3 -> ifc3
            }

            label = "*XYZ Module*";
            fontsize = 20;
            color=grey
        }
    }

Modules are not arbitrary divisions, but instead reflect subgraphs of IFC
relationships that minimise overlap with other subgraphs. Therefore modules are
mostly self contained, and allow developers to work on a single portion of the
code with relative certainty that their actions will not affects other
developers. Sometimes, overlap is inevitable.

There are over 40 modules, so we won't list them here.

- `IFC modules <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcopenshell-python/ifcopenshell/api>`__
- `Blender modules <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/blenderbim/blenderbim/bim/module>`__

IfcOpenShell Architecture
-------------------------

Manipulating IFC data is not simple. IFC may be serialised into multiple
formats, multiple schema versions must be supported, and geometry may be defined
in a highly parametric or implicit manner, which geometry kernels do not
natively support. All this heavy lifting is performed by the IfcOpenShell
library.

The IfcOpenShell library consists of a C++ based core. Its geometry processing
is done using OpenCascade, and optionally CGAL as an experimental option. By the
time the BlenderBIM Add-on interacts with IFC, it uses the IfcOpenShell Python
bindings, so all IFC data is already deserialised into Python objects. The inner
workings of the C++ base is out of scope.

.. image:: ifcopenshell-architecture.png

..
    digraph G {rankdir=LR;
        node [fontname = "Handlee", shape=rect, style=filled,color=pink];
        IfcOpenShell [label="IfcOpenShell C++", color=grey]
        ifcopenshell [label="IfcOpenShell-python"]
        OpenCascade [color=grey]
        CGAL [color=grey]

        OpenCascade -> IfcOpenShell
        CGAL -> IfcOpenShell
        IfcOpenShell -> ifcopenshell
        ifcopenshell -> Core
        ifcopenshell -> Utils
        ifcopenshell -> API
        API -> Module01
        API -> Module02
        API -> Module03
        Module03[label="..."]
        Module01 -> Data
        Module01 -> Usecase
    }


IfcOpenShell offers a core set of low-level functionality to read and write this
data. An example of the core functionality would be:

.. code-block:: python

    import ifcopenshell
    model = ifcopenshell.open("foo.ifc")
    wall = model.create_entity("IfcWall")
    wall.Name = "Foobar"

Core functions are simple read and write operations with no post processing.
Core functions also include geometry processing, which converts IFC geometry
into OpenCascade objects.

Sometimes, there are repetitive actions that need to be performed. These
functions are grouped into a ``util`` module. These include utility functions
for coordinate calculations, date conversions, filtering elements, unit
conversions, and more. Utility functions make no assumption about the context in
which they are used, and so perform highly specific tasks and nothing else.
Here's an example of utility functionality:

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.util.date
    import ifcopenshell.util.geolocation
    start = ifcopenshell.util.date.ifc2datetime(task_time.ScheduleStart)
    coordinates = ifcopenshell.util.geolocation.local2global(matrix, eastings, ...)

When authoring, core and utility functions are usually too low-level. To cater
for this, a high level API is provided. The API is divided into mostly isolated
modules, each module representing a distinct set of concepts in the IFC schema.
Unlike the util module, these API modules are highly context-sensitive, and
assume that you intend to be authoring native IFC.

This context-sensitive assumption means that the functions within the modules
are designed around typical usecases in an authoring environment. It performs
all the necessary manipulations to achieve a domain-specific usecase. Authoring
is complex and requires a deep knowledge of IFC to perform correctly and ensure
that the IFC graph state is well maintained. Typically, any authoring operation
that does not use the API is likely to contain mistakes.

Each module contains a Data class to extract various IFC data related to the IFC
concept that the module relates to. The ``Data`` classes parse the complex IFC
graph and convert it into a cache of primitive Python data. The ``Usecase``
clases perform a defined user operation. Here's an example of it in action:

.. code-block:: python

    import ifcopenshell.api
    ifcopenshell.api.run("grid.create_grid_axis", model, ...)
    ifcopenshell.api.run("structural.add_structural_load", model, ...)

Because the API performs all the IFC manipulations to achieve a usecase, no
further interaction is required in a typical native IFC authoring environment.
For this reason, the BlenderBIM Add-on only interacts with the API for its
authoring capabilities.

The code for IfcOpenShell's various systems can be found here:

- `ifcopenshell (core) <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcopenshell-python/ifcopenshell>`__
- `ifcopenshell.util <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcopenshell-python/ifcopenshell/util>`__
- `ifcopenshell.api <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcopenshell-python/ifcopenshell/api>`__


BlenderBIM Add-on architecture
------------------------------

TODO
