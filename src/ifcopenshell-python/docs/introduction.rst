Introduction
============

**IfcOpenShell** is an open source software library for software developers and BIM powerusers working with Industry Foundation Classes (`IFC <https://technical.buildingsmart.org/standards/ifc/>`_).

In addition to a C++ and Python API, **IfcOpenShell** comes with an ecosystem of tools, notably including **IfcConvert** (an application to convert IFC models to other formats), **Bonsai** (an add-on to Blender providing a graphical IFC authoring platform), and many other libraries, CLI apps, and more. Support is also provided for auxiliary standards such as BCF, bSDD, and IDS.

Things you can do
-----------------

**IfcOpenShell** is designed to be a complete BIM authoring platform. Its
capabilities have a similar scope to other BIM libraries, modeling platforms,
costing programs, scheduling software, CAD packages, and simulation software.
It is too numerous to list in full, but an example of what is possible include:

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

What makes IfcOpenShell special?
--------------------------------

IfcOpenShell has a huge amount of unique features and capabilities not found in any other technology.

- IfcOpenShell is the oldest and most mature open source IFC library available. It's developed since 2011 by a community of hundreds of developers and trusted to deliver many AEC technologies that power our industry. IfcOpenShell is also taught in numerous universities and cited in hundreds of academic publications.
- Lots of platforms and package management options are available: Windows, Mac Intel, Mac Silicon (M1, M2), Linux, Web Assembly (WASM), Docker, AWS Lambda, Google Colab, and more.
- Develop in C++, Python, or JavaScript via Pyodide.
- All tools can be used either as a developer library, through a command line interface, or using a rich graphical interface. Whether you're deploying headless server tools for your own pipeline, writing your own apps, or an end-user, there's something for you.
- Supports IFC2X3, IFC4, and IFC4.3. Custom schemas (such as experimental or draft schemas) may be loaded at run-time instead of having to recompile.
- Built-in IFC validation is possible from basic syntax validation to more detailed "Where Rule" checks. This is the same validation that powers the official buildingSMART validation engine.
- Read and write IFC-SPF, IFCJSON, IFCXML, IFCHDF5, MySQL, and SQLite.
- High level API for hundreds of tasks. Perform complex authoring like copying objects, cost calculation, or 4D simulation with one line of code. Imagine a complete native IFC authoring and editing platform where every function is available to you as a library.
- Convert parametric geometry into explicit geometry for any CAD system from booleans to complex sweeps. Geometry has been battle-tested over many years to accommodate complex geometric edge cases with an extensive test suite.
- Geometry may be converted into voxels and analysed through voxels to resolve complex non-manifold geometry and precision issues. This analysis may be used from things like head height calculations, formwork analysis, to egress distances.
- Generate and annotate 2D drawings from 3D geometry with ease. Preserve drawing semantics and link model data to and from drawing symbols. Drawings may be richly annotated with text, line styles, hatches, symbols, and more and are used to deliver commercial drawings for projects.
-  Clash detection, model comparison, and conversion to over 10 other formats (DAE, GLB, OBJ, SVG, and more). Integrate with technologies like IDS, BCF, and bSDD, and more.
-  Extensive documentation, user guides, academic courses, and a vibrant user community to help you begin your journey.

IfcOpenShell utilities
----------------------

IfcOpenShell is a modular ecosystem of tools that work together, where each tool focuses on a particular task.

.. csv-table::
   :header: "Name", "Description"

    "`IfcOpenShell <https://docs.ifcopenshell.org/ifcopenshell.html>`_", "The core library for C++ developers. The library includes the ability to parse schemas, tessellate and process implicit geometry."
    "`IfcOpenShell-Python <https://docs.ifcopenshell.org/ifcopenshell-python.html>`_", "Python bindings to the core IfcOpenShell C++ system, as well as high level analysis and authoring functions."
    "`IfcConvert <https://docs.ifcopenshell.org/ifcconvert.html>`_", "A command-line application for converting IFC geometry into file formats such as OBJ, DAE, GLB, STP, IGS, XML, SVG, H5, and IFC itself."
    "`Bonsai <https://docs.ifcopenshell.org/bonsai.html>`_", "A graphical add-on for Blender that lets you analyse, author, and modify IFC with Blender. Graphically create BIM models from scratch!"
    "`BCF <https://docs.ifcopenshell.org/bcf.html>`_", "BIM Collaboration Format (BCF) is a standard to manage and exchange coordination topics between disciplines collaborating on a project by changing XML files or querying an API."
    "`BIMServer-Plugin <https://docs.ifcopenshell.org/bimserver-plugin.html>`_", "A plugin to the open source BIMServer CDE to allow you to use IfcOpenShell to parse, view, and audit models."
    "`BIMTester <https://docs.ifcopenshell.org/bimtester.html>`_", "A utility that allows you to write Gherkin-based tests for models."
    "`bSDD <https://docs.ifcopenshell.org/bsdd.html>`_", "A Python library to query the buildingSMART Data Dictionary API to search for standardised classifications and properties."
    "`Ifc2CA <https://docs.ifcopenshell.org/ifc2ca.html>`_", "Converts IFC models to FEM structural analytical models to be used in Code_Aster."
    "`Ifc4D <https://docs.ifcopenshell.org/ifc4d.html>`_", "A series of utilities for converting to and from various 4D software like MS Project, PowerProject, and Oracle P6."
    "`Ifc5D <https://docs.ifcopenshell.org/ifc5d.html>`_", "A collection of utilities of manipulating cost-related data to and from formats, reports, and optimisation engines."
    "`IfcCityJSON <https://docs.ifcopenshell.org/ifccityjson.html>`_", "A converter for CityJSON files and IFC. It currently only supports one-way conversion from CityJSON to IFC."
    "`IfcClash <https://docs.ifcopenshell.org/ifcclash.html>`_", "A CLI utility and library that lets you perform clash detection on one or more IFC models. Clashes are defined in terms of clash sets with filters using the IFC query syntax."
    "`IfcCSV <https://docs.ifcopenshell.org/ifccsv.html>`_", "View and edit IFC data using spreadsheets or tabular datasets, such as CSV, ODS, XLSX, Pandas DataFrames, and regular Python lists."
    "`IfcDiff <https://docs.ifcopenshell.org/ifcdiff.html>`_", "A CLI utility and library that lets you compare the changes between two IFC models."
    "`IfcFM <https://docs.ifcopenshell.org/ifcfm.html>`_", "A highly standards-compliant tool (e.g. COBie 2.4, COBie 3.0, AOH-BSEM) to convert FM data in IFC databases to spreadsheets and other machine readable formats, such as ODS, XLSX, CSV, Pandas, XML, and JSON."
    "`IfcMax <https://docs.ifcopenshell.org/ifcmax.html>`_", "A 3ds Max importer plugin able to import the IFC file format."
    "`IfcPatch <https://docs.ifcopenshell.org/ifcpatch.html>`_", "A CLI utility and library that lets you run and distribute predetermined modifications on an IFC file, known as a patch recipe. Useful in deploying a data pipeline or batch-fixing external models."
    "`IfcSverchok <https://docs.ifcopenshell.org/ifcsverchok.html>`_", "A node based visual programming add-on for Blender to interact with IFC and Sverchok."
    "`IfcTester <https://docs.ifcopenshell.org/ifctester.html>`_", "Author and read Information Delivery Specification (IDS) files. You can validate IFC models against IDS and generate reports in multiple formats. It works from the command line, as a web app, or as a library."
    "`VoxelisationToolkit <https://github.com/opensourceBIM/voxelization_toolkit>`_", "Converts .ifc geometry into voxels, and lets you perform voxel based geometric analysis."

.. note::

    **IfcOpenShell** and all of its libraries are licensed under LGPL-3.0-or-later. Two exceptions to this are **Bonsai** and **IfcSverchok**, which are both licensed under GPL-3.0-or-later.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   introduction/introduction_to_bim
   introduction/introduction_to_ifc
   introduction/how_to_contribute
