Georeferencing
==============

In the AEC industry, works in the built environment are split between vertical
construction (such as buildings and sites), and horizontal construction (such as
transit, transmission, and subterranean networks). Blender and the BlenderBIM
Add-on is only suitable for vertical construction.

IFC4 onwards supports georeferencing. The BlenderBIM Add-on has full support for
IFC georeferencing. Here are the potential scenarios you will encounter in the
wild for vertical construction.

1. Correctly georeferenced IFC4 with a map conversion transformation
2. Correctly georeferenced IFC4 without a map conversion transformation
3. Non-georeferenced georeferenced IFC4
4. Non-georeferenced IFC2X3

The first scenario is desired for most disciplines, such as architects and all
engineers (except for civil).

For scenarios 2, 3, and 4, the BlenderBIM Add-on will automatically attempt to
offset coordinates to preserve the precision of the model. The first coordinate
greater than 1km will be detected and used as an offset coordinate. It is
possible to specify a custom offset coordinate.

Non-georeferenced workarounds
-----------------------------

The unfortunate reality is that IFC2X3 does not support georeferencing, and most
vendors have poor and inconsistent support for georeferencing, even in IFC4.
Some users may be under the impression that their file is correctly
georeferenced, but this is rarely the case. This creates problems. You can see
whether your file is correctly georeferenced in the ``IFC Georeferencing``
scene panel. If you see "Not Georeferenced", your file is not correctly
georeferenced. If your file is georeferenced, it is no guarantee that the
georeferencing data is actually correct, but how to determine this is out of
scope of this article.

As an invalid workaround for correct georeferencing, many other BIM vendors
simply offset their object coordinates from local engineering to map coordinates
without properly storing a projection system and optionally a map
transformation. There are two common invalid workarounds that are used.

The first invalid workaround is to shift the origin point of objects in the
model. We call this the ``OBJECT_PLACEMENT`` workaround. The second invalid
workaround is to shift the coordinates of geometry within the objects
themselves, and typically leave the object origin untouched (such as back at (0,
0, 0)). We call this the ``CARTESIAN_POINT`` workaround. Sometimes, BIM
applications combine both of these invalid workarounds. To see which workaround
was used on an object, check the "Blender Offset" property in the ``Transform``
object panel.

Sometimes, a model shifts their coordinates for some objects, but not all. For
example, the walls in a model may have their object placement or cartesian
points shifted to map coordinates, however, the object placement of the site is
still at 0, 0, 0. This creates a problem, because either we can display the
walls accurately, or the site placement accurately, but not both. Users may not
even realise this is an issue because many IFC viewers don't show object
placements because they are "invisible". However, because the BlenderBIM Add-on
is a full authoring platform, we do need to show these placements and thus it is
the users responsibility to reconcile this inconsistency in their coordinates.
Either the user needs to fix their file to consistently offset all coordinates,
or the user needs to manually tell the BlenderBIM Add-on which offset to choose.
In the absence of manual intervention, the BlenderBIM Add-on will make an
intelligent guess, but it may be wrong.

To manually specify an offset, simply load an IFC project with Advanced Mode
enabled. Then enable the ``Import and Offset Model`` option and specify a new
coordinate to replace the origin's default of 0,0,0 in the ``Model Offset
Coordinates`` option.

Coordinates and precision limits
--------------------------------

Blender, and subsequently the BlenderBIM Add-on, is not designed for map
coordinate systems. Blender internally uses single precision floating point
calculations. A full description of the precision implications are described in
the `Blender working limits documentation
<https://docs.blender.org/manual/en/latest/advanced/limits.html>`__.

From a software perspective, lengths greater than 5,000 meters start to
accumulate precision errors that affect the nearest millimeter. Therefore, from
a software perspective, it is unwise to embark on a project with coordinates
ranging greater than +/- 5km.

However, if working in local engineering coordinates, a single transformation is
required to convert from local engineering coordinates to map coordinates. This
transformation includes a scale factor. The scale factor is only assumed to be
constant for small sites (defined approximately as less than 1km square).
This practical limit of georeferenced vertical construction is smaller than the
software limit, so this is the actual limiting factor.
