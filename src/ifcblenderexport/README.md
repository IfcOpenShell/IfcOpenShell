# Blender BIM IFC

_Under heavy development!_

Let's use Blender to create BIM models, because why not?

## Features

 - IFC4 is a first-class citizen. IFC4 has been an ISO standard since 2013, with
   the latest published in 2018. In contrast, other programs are dragging their
   feet with IFC2X3, published back in 2005.
 - Use Blender to do digital modeling! Blender is an amazing open-source
   software that supports the full 3D content creation pipeline that the CG
   industry uses. Don't let your designs fall short just because your modeling
   tool isn't good enough!
 - Create complex spatial structures with multiple sites, buildings, facilities,
   bridges, and building parts. In contrast, some BIM tools (uh, Revit?) don't
   even allow you to specify buildings.
 - Classify any geometry as any IFC type. Just because it is a wall doesn't
   mean you should be limited to modeling it in a certain way. Easily change
   from one type to another without damaging your geometry.
 - Support element compositions and decompositions with full control over the
   classifications of their parts. Most BIM programs don't give this
   flexibility.
 - Allow BIM objects to instance a shared geometric representations. This allows
   you to place the same shape in multiple objects without drastically
   increasing your filesize.
 - Provide a custom value to any simple IFC attribute of an IFC product.
 - Create product types that regular IFC products can inherit attributes from.
 - Define your own property sets with control over exactly how the data in the
   property sets are stored.
 - Applies array modifiers to create instances.

## Demo

It's only just started, so everything can and will change. But if you want to
check it out:

 1. Install [Blender](https://www.blender.org/).
 2. Install [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell),
    ensuring that is is compiled to the same Python version and architecture of
    your Blender installation.
 3. Launch Blender. Open `untitled.blend`. You should see the `export.py`
    script already loaded. Change the hardcoded paths from
    `/home/dion/Projects/blender-bim-ifc/` to wherever you've cloned this
    repository.
 4. Ensure `ifcopenshell` is in your Blender Python's path, so that it can
    `import ifcopenshell`. You can run
    `sys.path.append('/path/to/your/ifcopenshell/module')` in the Blender Python
    console to do this.
 5. Select all objects that you want to export. Press `Run Script`, and you will
    get the results in `output.ifc`.

A naming convention of `IfcClass/IfcName` is enforced. If you name your object
`IfcWall/Foo`, it will turn into an `IfcWall` with the name attribute set to
`Foo`. You can override object attributes using Blender's `Custom Properties`.
Your objects must live in a top level `Collection` defined as a context class,
usually something like `IfcProject/Foo`. You can then nest spatial structures
underneath to create a hierarchy.

![Blender screenshot](blender-screenshot.png)

... this Blender files creates this IFC file ...

![IfcOpenShell screenshot](ifcopenshell-screenshot.png)
