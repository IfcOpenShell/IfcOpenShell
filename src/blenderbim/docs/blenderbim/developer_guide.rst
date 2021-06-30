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
as nothing of significance is stored in the Blender system.

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

Code structure
--------------

TODO
