Property Editor
===============

Overview
--------

BlenderBIM adds new functionality to the `Property Editor` -> `Scene` tab.

.. figure:: images/interface_property-editor_project-overview_start-up.png
   :alt: Property editor on Blender start-up

   The property editor on Blender startup.

Most of these sub-tabs become available with a created or loaded IFC file.
Don't worry, the default Blender scene properties are still reachable under their own dedicated sub-tab.

.. figure:: images/interface_property-editor_icons.png
   :alt: Overview over the added property sub-tabs by BlenderBIM

   Overview over the added property sub-tabs by BlenderBIM.

1. Project Overview
2. Object Information
3. Geometry and Materials
4. Drawings and Documents
5. Services and Systems
6. Structural Analyses
7. Costing and Scheduling
8. Facility Management
9. Quality and Coordination
10. Blender Properties - the default Blender scene properties moved under its own dedicated panel
11. Switch Tab - quick access to switch between the last 2 used Property panels

You can also select the needed panel via the drop-down menue.

.. figure:: images/interface_property-editor_panel-dropdown.png
   :alt: BlenderBIM property editor sub-tabs drop-down menue

   Switching between BlenderBIM property editor sub-tabs via the drop-down menue.

Project Overview
----------------

.. figure:: images/interface_property-editor_project-overview.png
   :alt: property editor project overview sub-tab

   Project Overview sub-tab with subsection panels.


Project Info
^^^^^^^^^^^^

The "Project Info" subsection in the BlenderBIM Add-on interface changes depending on the state of the IFC project. When no project is loaded, the subsection displays options to create a new project or load an existing one. If a new IFC project is created but not yet saved, the subsection shows a "No File Found" message, indicating that the project is not yet saved. Once an IFC project is loaded or created and saved, the subsection presents an overview of the project's metadata, including the IFC schema version, MVD, author, organization, last saved date, filename, and file path. Users can edit specific metadata fields, select a different IFC file, or unload the current project from within this subsection.

**Not Created or Loaded state**

When no IFC file is loaded, the "Project Info" subsection displays options to create a new IFC project or load an existing one.

Buttons:

- **Create Project**. Button to create a new IFC project with the selected IFC schema, unit system, and template. Clicking this button changes to the Not Saved mode, waiting for user to edit metadata and save the IFC file.
- **Load Project**. Button to load an existing IFC file into the Blender scene. Clicking this button opens a file browser dialog, enabling users to navigate to and select the desired IFC file.

**Not Saved state**

When a new IFC project is created but not yet saved, the "Project Info" subsection displays the following message: "No File Found". Indicates that the current IFC project has not been saved to a file. The IFC header can be edited by clicking the pencil button. In this mode you can't unload the IFC project and go back to the Not Create or Loaded mode. You have to save the IFC file first and then unload the project.

Buttons:

- **Edit (pencil icon)**: Clicking this button switches the "Project Info" subsection to editing mode, allowing users to modify the IFC header/metadata fields.

**Saved and Loaded state**

Fields:

- **Filename**. Displays the name of the loaded IFC file. Example: "demo.ifc"
- **File path**. Shows the location of the loaded IFC file on the user's file system. Example: "/home/user/Docum...lenderbim/"

Buttons:

When an IFC project is created or loaded and saved additional buttons appear (beside the Edit button):

- **Select a different IFC file**: This button allows users to choose and load a different IFC file. Clicking the button will open a file browser dialog, enabling users to navigate to and select the desired IFC file.
- **Unload the IFC project**: This button allows users to unload the currently loaded IFC file from the Blender scene. Clicking the button will remove the IFC data and clear the "Project Info" subsection, returning it to the "Not create or Loaded" mode.

**IFC Header Editing toggle**

Clicking the pencil button (which doesn't exist when in the Not Created or Loaded state) switches the "Project Info" subsection to editing mode, allowing users to modify the IFC header/metadata fields

Fields:

- **IFC Schema**. Indicates the version of the Industry Foundation Classes (IFC) schema used by the loaded file. Example: "IFC4"
- **IFC MVD**. Specifies the Model View Definition (MVD) used by the loaded IFC file. An MVD defines a subset of the IFC schema for a specific data exchange purpose. Example: "DesignTransferView"
- **Author**. Displays the author of the IFC file.
- **Author Email**. Shows the email address of the IFC file author.
- **Organisation**. Indicates the organization associated with the IFC file.
- **OrganisationEmail**. Displays the email address of the organization.
- **Authoriser**. Shows the authoriser of the IFC file, if available. Example: "Nobody"
- **Saved**. Displays the last saved date and time of the loaded IFC file. Example: "2024-06-10 13:15"


Project Setup
^^^^^^^^^^^^^

tbd

Geometry
^^^^^^^^

tbd

Stakeholders
^^^^^^^^^^^^

tbd

Grouping and Filtering
^^^^^^^^^^^^^^^^^^^^^^

tbd

Object Information
------------------

.. figure:: images/interface_property-editor_object-information.png
   :alt: property editor object information sub-tab

   Object Information sub-tab.

Object Metadata
   tbd

Miscellaneous
   tbd

Geometry and Materials
----------------------

.. figure:: images/interface_property-editor_geometry-materials.png
   :alt: property editor geometry and materials sub-tab

   Geometry and Materials sub-tab.

Placement
   tbd

Representations
   tbd

Geometric Relationships
   tbd

Parametric Geometry
   tbd

Profiles
   tbd

Materials
   tbd

Styles
   tbd

Drawings and Documents
----------------------

.. figure:: images/interface_property-editor_drawings-documents.png
   :alt: property editor drawings and documents sub-tab

   Drawings ans Documents sub-tab.

Sheets
   tbd

Drawings
   tbd

Schedules
   tbd

References
   tbd

Services and Systems
--------------------

.. figure:: images/interface_property-editor_services-systems.png
   :alt: property editor services and systems sub-tab

   Services and Systems sub-tab.

Services
   tbd

Zones
   tbd

Structural Analyses
-------------------

.. figure:: images/interface_property-editor_structural-analysis.png
   :alt: property editor structural analysis sub-tab

   Structural Analysis sub-tab.

Costing and Scheduling
----------------------

.. figure:: images/interface_property-editor_costing-scheduling.png
   :alt: property editor costing and scheduling sub-tab

   Costing and Scheduling sub-tab.

Status
   tbd

Resources
   tbd

Cost
   tbd

Construction Scheduling
   tbd

Facility Management
-------------------

.. figure:: images/interface_property-editor_facility-management.png
   :alt: property editor facility management sub-tab

   Facility Management sub-tab.

Commissioning and Handover
   tbd

Operations and Maintenance
   tbd

Quality and Coordination
------------------------

.. figure:: images/interface_property-editor_quality-coordination.png
   :alt: property editor quality and coordination sub-tab

   Quality and Coordination sub-tab.

Quality Control
   tbd

Clash Detection
   tbd

Collaboration
   tbd

Sandbox
   tbd
