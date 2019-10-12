# Blender BIM IFC

_Under heavy development!_

Let's use Blender to create BIM models, because why not?

## Features

 - IFC4 is a first-class citizen. IFC4 has been an ISO standard since 2013, with
   the latest published in 2018. It contains many more features than IFC2X3,
   published back in 2005.
 - Available for Windows, Mac, and Linux!
 - Use open-source Blender 2.8 to do digital modeling! Used by NASA, Hollywood,
   and Ubisoft, Blender allows real-time modeling in rendered view, animations,
   file linking, proxy objects, Blender Cloud collaboration, lighting analysis,
   CFD, energy modeling, and a huge ecosystem of add-ons with a thriving
   community. No licensing, and with a strong Python API to integrate into your
   custom workflow.
 - Create complex spatial structures with multiple sites, buildings, facilities,
   bridges, and building parts. Sites can be broken down into sub-sites and
   multiple buildings per site. You can categorise different floors to different
   buildings.
 - Classify any geometry as any IFC type. Just because it is a wall doesn't
   mean you should be limited to modeling it in a certain way. Easily change
   from one type to another, switch relationships and aggregations, reuse or
   even remove geometry altogether, without damaging your geometry or breaking
   your BIM model.
 - Use collections to create element compositions and decompositions with full
   control over the classifications of their parts. Most BIM programs don't give
   this flexibility. Create collection instances to efficiently duplicate
   composite objects.
 - Allow BIM objects to instance a shared geometric representations. This allows
   you to place the same shape in multiple objects without drastically
   increasing your filesize.
 - Provide a custom value to any simple IFC attribute of an IFC product.
 - Create product types that regular IFC products can inherit attributes from.
 - Define your own property sets with control over exactly how the data in the
   property sets are stored using property set template definitions which you
   can download or create yourself. Property sets can apply to both types and
   objects, and object property sets can selectively override type property
   sets.
 - Applies array modifiers to create instances.
 - Basic quantity take-off support for costing.
 - Settings to toggle export of quantities or geometric representations.
   Exporting IFC data without geometric representations is much faster and a
   fraction of the filesize.
 - Maintain `GlobalId` between exports, so that you can manipulate the IFC
   reliably in other software while making changes.
 - Not all objects need full solid geometry. Create representations as 2D or 3D
   curves / wireframes for rapid and lightweight BIM development.
 - Create map conversions and coordinate reference system definitions to link
   BIM to GIS.
 - Export basic materials with surface and diffuse colours for representation.
   You can also link materials to an externally defined file, such as a `.blend`
   Cycles material, V-Ray material, or even Radiance material for lighting
   simulation.
 - Switch between different types of metric units when modeling.
 - Model multiple representations for different purposes for a single BIM
   object or type, such as footprints, axis, reference, or clearance geometry.
   You can export just the type of representation required for your usecase, or
   export multiple for the user to choose from.
 - Record qualitative objectives such as design intentions, health and safety
   strategies, or code compliance, performance solutions, and more, in the BIM
   model and directly associate them to objects or types.
 - Classify objects and types to different classification systems such as
   Uniclass, Omniclass, or your custom system.
 - Associate external document files such as plans, brochures, specifications,
   warranties, or anything to objects and types.
 - Specify swept solid geometries, allowing you to round-trip geometry
   manipulation with other BIM software which have more limited geometric tools,
   like Revit.
 - Create material layer sets, for objects which have materials in predefined
   layers with thicknesses.
 - Create material constituent sets, for objects which are made up of
   arbitrarily mixed ingredients.
 - Specify nested and hosted element relationships.
 - Specify predefined door attributes as defined in the IFC4 specification.
 - Specify predefined window attributes as defined in the IFC4 specification.
 - Specify surface styles either defined as part of a material or assigned
   directly to an object's representation.
 - Colour coding by IFC class to visually spot mistakes

Some more experimental features:

 - Cut sections for documentation with OpenCascade
 - Export gbXML files that are linked to your IFC file to do energy analysis
 - QA module to generate Gherkin unit tests to validate your BIM models
 - HTML formatter to generate reports from QA results
 - COBie spreadsheet extraction to import into CAFM systems

## Demo

[See demo video](https://www.youtube.com/watch?v=iD3v3eu2AjY)

It's only just started, so everything can and will change. But if you want to
check it out:

 1. Install [Blender](https://www.blender.org/) 64-bit version.
 2. Download the latest packaged version of Blender BIM from
    [here](https://thinkmoult.com/blenderbim/).
 3. Launch Blender. Go to `Edit->Preferences->Add-ons->Install...`. Browse to
    the downloaded `.zip` file from step 2.
 4. Enable the checkbox next to the Import-Export IFC Blender plugin which will
    show up.
 5. All done! You will find an import and export IFC option in the `File` menu.

By default, Blender BIM will export whatever you have selected. The objects you
have selected _must_ belong in an `IfcProject` and spatially contained, such as
witihn an `IfcBuilding`. It must also follow the naming convention. Please see
the screenshot below for an example scene.

A naming convention of `IfcClass/IfcName` is enforced. If you name your object
`IfcWall/Foo`, it will turn into an `IfcWall` with the name attribute set to
`Foo`. You can override object attributes using Blender's `Custom Properties`.
Your objects must live in a top level `Collection` defined as a context class,
usually something like `IfcProject/Foo`. You can then nest spatial structures
underneath to create a hierarchy.

## Pictures

![UI](https://aws1.discourse-cdn.com/business6/uploads/buildingsmart1/original/1X/ce820c3ee22adcffae59b40f98ff23379f7e3547.png)

![Blender screenshot](blender-screenshot.png)

... this Blender files creates this IFC file ...

![IfcOpenShell screenshot](ifcopenshell-screenshot.png)
