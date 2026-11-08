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

When you use **IfcOpenShell**, you will be able to view and create **BIM**
objects and relationships using the **IFC** standard.
