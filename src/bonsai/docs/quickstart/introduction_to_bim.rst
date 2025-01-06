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

When you use Bonsai, you will be able to view and create **BIM** objects and
relationships using the **IFC** standard.

Things you can do
-----------------

Bonsai is designed to be a comprehensive and truly native BIM authoring
platform. Its capabilities include a wide range of tasks and workflows
typically found across various BIM and CAD software, costing programs,
scheduling tools, and simulation applications. While not an exhaustive list,
some of the key things you can do with Bonsai include:

- View and explore IFC models, including spaces, properties, and relationships
- Edit and extract attributes, properties, and metadata directly from IFC data
- Move, rotate, and modify the geometry of objects while preserving IFC semantics
- Create new objects using predefined library elements or custom parametric types
- Manage classification systems, document references, and link to external libraries
- Generate 2D drawing views like plans, sections, and elevations with customizable annotations
- Investigate and edit structural analysis models with support for various steel profiles
- Model and manage complex distribution systems like HVAC, plumbing, and electrical (MEP)
- Create construction schedules, perform critical path analysis, and generate sequence animations
- Derive quantities from model elements and create cost schedules with formulas
- Perform clash detection and coordinate models, managing issues across disciplines
- Integrate non-geometric data like costing, scheduling, and asset management
