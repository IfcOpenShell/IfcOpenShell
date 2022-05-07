Introduction to BIM
===================

**Building Information Modeling**, or **BIM**, is a way of digitally describing
our built environment to computers. Aspects of our built environment that can be
described are:

- **Products**, like walls, doors, and windows
- **Processes**, like construction or maintenance tasks, and procedures
- **Resources**, like labour, materials, and equipment
- **Controls**, like permits, orders, costs, or calendar availability
- **Actors**, like occupants, clients, architects, and liable parties
- **Groups**, like systems, inventories, or zones

These objects may have lots of data and relationships. Examples of data might be
classification systems, physical materials, associated documents, simulation
results, and construction types. The data may be relevant to multiple
disciplines, such as architecture, engineering, and construction.

.. note::

   BIM data is very different from a regular 3D model. In fact, geometry is
   optional, and most data is non-geometric. This means that it is not simply a
   3D format that you can import or export from and expect meaningful results.

**Industry Foundation Classes**, or **IFC**, is an international standard for
**BIM**. **IFC** is the most well-established open digital language for our
built environment. Most software will be able to describe their **BIM** data
using **IFC**. Most commonly, **IFC** models will be shared as a ``.ifc`` file.

For example, **IFC** will define a wall as an object that can have a name,
construction type, and quantities. **IFC** will also describe that a wall that
be associated with a location, like a building storey, or have an associated
cost item in a schedule.

When you use the BlenderBIM Add-on, you will be able to view and create **BIM**
objects and relationships using the **IFC** standard.

Things you can do
-----------------

The BlenderBIM Add-on is designed to be a full BIM authoring platform. Its
capabilities have a similar scope to other modeling platforms, costing programs,
scheduling software, CAD packages, and simulation software. It is too numerous
to list in full, but an example of what is possible include:

- Viewing models, including spaces, properties, and relationships
- Edit and extract attributes and properties
- Moving objects, and changing their geometry
- Create new objects using library elements
- Manage classification systems, document and library references
- Generating 2D drawings, schedules, and creating sheets
- Investigating and editing structural analysis models
- Connecting and managing distribution systems and ports
- Creating construction schedules, critical path analysis, and generating sequence animations
- Creating cost schedules, using formulas, and deriving quantities from model elements
- Clash detection and managing issues for model coordination

... and much, much more.
