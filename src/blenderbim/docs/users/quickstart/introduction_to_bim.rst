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

The BlenderBIM Add-on is designed to be a comprehensive and truly native
BIM authoring platform. Its capabilities include a wide range of tasks
and workflows typically found across various BIM and CAD software, costing
programs, scheduling tools, and simulation applications. While not
an exhaustive list, some of the key things you can do with BlenderBIM include:

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


Roadmap and Upcoming Features
-----------------------------

While BlenderBIM already offers a comprehensive set of BIM authoring capabilities,
the development team and community are continuously working to expand its functionality and improve existing workflows.
Some of the most ambitious features and enhancements on the roadmap include:

Usability and Workflow Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Improve user-friendliness to equip average "Joe" with capabilities to model simple projects like single family homes, making BlenderBIM a viable alternative to SketchUp.
- Make BlenderBIM more approachable for users across different skill levels, from advanced BIM experts to architects working on smaller residential projects.

Improved Drawing and Documentation Workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Continued enhancements to the drawing generation capabilities, including better dimensioning tools and support for associative dimensions linked to model geometry.
- Advanced annotation tools with customizable tags, callouts, and the ability to define reusable annotation styles and templates.
- Streamlined sheet layout management and improved integration with external tools like Inkscape for creating title blocks and sheet compositions.
- Continued improvement of BlenderBIM's ability to generate comprehensive documentation sets, including drawing annotations, door schedules, wall schedules, and material tagging.

Expanded Parametric Modeling Capabilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Native modeling tools for complex building elements like curtain wall systems and facade panels.
- Expanded libraries with support for country-specific and manufacturer-provided object types.
- Enhanced support for multi-story modeling, enabling efficient duplication and coordination of building elements across various levels.
- Expanded parametric relationships and automating more common BIM tasks to reduce manual effort and enhance productivity.

Enhanced Coordination and Collaboration Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Robust model merge and coordination workflows, with detailed clash detection capabilities across different disciplines and data sources.
- Built-in support for version control and model sharing using Git repositories, enabling better team collaboration and change tracking.


The development roadmap is continuously updated based on user feedback, industry requirements,
and contributions from the open-source community. By embracing an open and collaborative approach,
BlenderBIM aims to push the boundaries of what's possible in BIM authoring,
ensuring that it remains at the forefront of innovation in the AEC industry.
