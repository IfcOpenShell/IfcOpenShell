Scene Properties
================

The scene properties panels allow you to manage data that applies to your entire
IFC project as a whole, or to multiple elements.

Building Information Modeling Panel
-----------------------------------

System Setup
^^^^^^^^^^^^

* **Quick Project Setup** - this will create a basic spatial tree. It will
  create a tree of collections with the structure ``IfcProject > IfcSite >
  IfcBuilding > IfcStorey`` This is merely for convenience instead of having to
  create it all by yourself, since all IFC exports require a valid spatial
  tree. You can see the tree of collections in the outliner when this is done.
* **Schema Directory** - this folder stores the current IFC schema. You can
  download different schemas from the buildingSMART website. Unless you are an
  IFC guru, you probably shouldn't touch this. Bonsai recognises different
  IFC data based on what is provided in this schema folder. It defaults to the
  ``{{BLENDER_ADDONS_DIR}}/bonsai/schema/`` folder, which is prepackaged
  with the IFC4 schema. This is known as the ``{SCHEMA_DIR}``.
* **Data Directory** - the data directory holds the auxiliary data related to
  your IFC model. Examples include related property definitions, documents, and
  classification systems. Each project should have its own data directory. It
  defaults to the data directory in the
  ``{{BLENDER_ADDONS_DIR}}/bonsai/data/`` folder, which comes with some
  example preset data. You are encouraged to copy this template and set your
  own. This is known as the ``{DATA_DIR}``.

Software Identity
^^^^^^^^^^^^^^^^^

* **GlobalId** - this field let's you enter an IFC element's ``GlobalId``. It
  must be in the 22-character encoded form.
* **Select GlobalId** - this will select an element that has the same
  ``GlobalId`` attribute as what you have specified, based on what is currently
  visible in the scene.

IFC Categorisation
^^^^^^^^^^^^^^^^^^

* **IFC Class** - this dropdown lets you pick from a list of all non-abstract
  children of ``IfcElement`` and ``IfcSpatialStructureElement``
* **IFC Predefined Type** - this dropdown lets you pick from an enumeration of
  valid ``PredefinedType`` values for the currently selected *IFC Class*. It
  changes dynamically with the currently selected *IFC Class*.
* **IFC Userdefined Type** - this field lets you enter a value for a user
  defined type. It is stored as the ``ObjectType`` attribute of an
  ``IfcProduct``. It is only set when the **IFC Predefined Type** is set to
  ``USERDEFINED``, otherwise it is ignored. It is recommended to make this
  value uppercase and alphabetic, to match the conventions for the
  ``PredefinedType`` enumeration.
* **Assign Class** - this applies the active *IFC Class*, *IFC Predefined Type*
  and *IFC Userdefined Type* to any selected objects.
* **Select Class** - this will select any objects that are currently visible
  that also have the same IFC class as the currently active *IFC Class* dropdown.
* **Select Type** - same as *Select Class*, but it also filters by the
  currently active *IFC Predefined Type* dropdown, as well as the *IFC
  Userdefined Type* field.

Property Sets
^^^^^^^^^^^^^

- **Pset Name** - this lets you select from a list of available property set
  types. The list is derived from the folders in
  ``{DATA_DIR}/pset``. Each folder name corresponds to a property set name. If
  you want to assign properties to an object based on an IFC standard pset,
  just create a new folder with the same name as the pset. You can also create
  your own custom property sets, so long as the folder name does not start with
  ``Pset_``, as these are reserved for official IFC property sets.
- **Pset File** - this lets you select from a list of available property set
  data. The available property sets depends on the currently selected *PSet
  Name* dropdown. Each property set is represented by a ``.csv`` file inside
  ``{DATA_DIR}/pset/{PSET_NAME}/``. You can create your own ``.csv`` files
  with any software, where each line contains a property name and property
  value pair. Data types are automatically converted based on the property set
  templates defined in ``{SCHEMA_DIR}``. If the pset is part of an official IFC
  standard, you can only use property names that are part of the IFC standard.
  If you want to add your own custom properties, you will need to create your
  own *PSet Name* folder first, and then you can put in your own ``.csv`` file
  which contains any property names and values that you want.
- **Assign Pset** - this assigns the currently selected *Pset file* to any
  selected objects. The assigned data will then be visible in the *Object
  Properties*. This only assigns a link to the ``.csv`` containing the data, so
  you can change the data in the ``.csv`` file and that will automatically
  propagate to all assigned elements when an IFC is exported, without needing
  to reassign the data.
- **Unassign Pset** - this removes the link to the property set ``.csv``
  file for all currently selected objects.

Aggregates
^^^^^^^^^^

- **Aggregate Class** - this lets you select what type of class you want an
  aggregate of parts to be.
- **Aggregate name** - this lets you set the name of an aggregate that you can
  can create.
- **Create Aggregate** - this will create a new aggregate from one or more
  currently selected objects. The selected objects will be moved out of the
  spatial tree into an ``IfcRelAggregates/*`` collection. Then, a collection
  instance will be created to represent the aggregation, and will be placed in
  the current location of the spatial tree, and the  The parts will then be
  hidden so only the whole composition (i.e. the aggregate object) will be shown.
- **Explode Aggregate** - this does the opposite of *Create Aggregate*, and
  will remove the aggregation.
- **Edit Aggregate** - this will hide the collection instance that represents
  the aggregate object, and show all of the individual parts. This allows you
  to select and modify the aggregate parts.
- **Save Aggregate** - this does the opposite of *Edit Aggregate*.

IFC Classifications Panel
-------------------------

- **Classification** - this lets you select which classification system you'd
  like to use. The list of possible classification systems is derived from the
  ``{DATA_DIR}/class/classifications.csv`` file. By default, Bonsai comes
  with Uniclass 2015 and Omniclass. If you need another classification system,
  you can add it to this ``.csv`` file.
- **Reference** - this lets you select a single classification reference item,
  filtered depending on the currently active *Classification*. The list is
  derived from the ``{DATA_DIR}/class/references.csv`` file. Out of the box,
  Bonsai only lists a single Uniclass reference as an example. It is
  advised to make a list of all the references you require for a project and
  add it to this ``.csv`` file.
- **Assign Classification** - this assigns the currently active *Reference* to
  all of the selected objects. You can see the results in the *Object
  Properties* pane.
- **Unassign Classification** - this removes the currently active *Reference*
  in all of the selected objects.

IFC Owner History Panel
-----------------------

- **Person** - this lets you select who you are. The values are derived from
  the ``{DATA_DIR}/owner/person.json`` file, particularly the
  ``Identification`` attribute, which is mandatory and a requirement in COBie
  data. You are encouraged to edit this file to add your own details. This
  information will be stored in the IFC file as part of the owner history to
  keep track of any objects which you edit. You will also be recorded as the
  author of the IFC file.
- **Organisation** - this lets you select which organisation you are part of.
  The values are derived from the ``{DATA_DIR}/owner/organisation.json`` file,
  in particular the ``Name`` attribute, which is mandatory and a requirement in
  COBie data. You are encouraged to edit this file to add your own organisation
  details.  This information will be stored in the IFC file as part of the
  owner history to keep track of any objects which you edit. The organisation
  will also be recorded as the author of the IFC file.


IFC Geometric Representation Contexts Panel
-------------------------------------------

- **Has Model Context** - enabling this will allow you to export geometric data
  related to the model view of your BIM data. This is generally 3D
  representations. It may also contain wireframe representations such as an
  Axis model for structural members. This defaults to being enabled, as most
  people want to export model geometry.

  - **Available Subcontexts** - this lets you select a possible subcontext to
    be used underneath the Model context.
  - **Available Target Views** - subcontexts may have a particular target view,
    which you can set here.
  - **Add Subcontext** - This will add a new subcontext based on the currently
    selected *Available Subcontext* and *Available Target View*.

    - **Subcontext Name** - for each subcontext you have added, it will show
      you the subcontext name. By default, the ``Body`` subcontext is added,
      as most people want to export the body geometry of products in their BIM data.
    - **Subcontext Target View** - same as *Subcontext Name*, but shows the
      target view. By default, the ``MODEL_VIEW`` target view is added, as most
      people will be viewing the model geometry of your BIM data.
    - **Remove Subcontext** - this will remove the subcontext.

- **Has Plan Context** - the same as *Has Model Context*, but it lets you add
  subcontexts and target views related to the ``PLAN`` context of your BIM
  data. This is usually plans, sections, RCPs, and other documentation views.
