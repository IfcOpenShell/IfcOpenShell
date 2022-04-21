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
2. Correctly georeferenced IFC4 with a map conversion without a transformation
3. Non-georeferenced IFC4
4. Non-georeferenced IFC2X3

The first scenario is desired for most disciplines, such as architects and all
engineers (except for civil). Typically, this results in small local engineering
coordinates, which work well in Blender.

Correct georeferencing requires a projected CRS and a map conversion.
Unfortunately, many users may be under the impression that their file is
correctly georeferenced, but this is rarely the case. You can check whether your
file is correctly georeferenced in the ``IFC Georeferencing`` scene panel. If
you see "Not Georeferenced", your file is not correctly georeferenced. If your
file is georeferenced, it is still no guarantee that the georeferencing data is
actually correct, but how to determine this is out of scope of this article.

For scenarios 2, 3, and 4, coordinates may be quite large. To present this data
in Blender, the BlenderBIM Add-on will automatically attempt to create a false
origin to preserve the precision of the model. The first coordinate greater than
1km will be detected and used as an offset coordinate. You can see the false
origin, if any, in the ``Blender Offset`` section of the ``IFC Georeferencing``
scene panel.

Instead of relying on an automatic false origin, you can also specify a custom
origin coordinate. To do this, choose ``Enable Advanced Mode`` when loading an
IFC project.  Then enable the ``Import and Offset Model`` option and specify a
new coordinate to replace the origin's default of 0,0,0 in the ``Model Offset
Coordinates`` option.

Dealing with large coordinates
------------------------------

In scenarios 2, 3, and 4, a BIM vendor will typically choose from two possible
methods to offset their coordinates into large map coordinates.

The first method is to shift the origin point of objects in the model relative
to the global coordinate system. We call this the ``OBJECT_PLACEMENT`` method.
The second method is to shift the coordinates of geometry within the objects
themselves relative to the object placement. We call this the
``CARTESIAN_POINT`` method. Sometimes, BIM applications combine both of these
methods in a single IFC project. To see which workaround was used on an object,
check the "Blender Offset" property in the ``Transform`` object panel.

Sometimes, a model shifts their coordinates for some objects, but not all. For
example, the walls in a model may have their object placement or cartesian
points shifted to map coordinates, however, the object placement of the site is
still at 0, 0, 0. Since these coordinates are so far apart, this creates a
problem, because Blender needs to choose between displaying the walls accurately
and sacrificing precision at the site placement, or vice versa, but it is
impossible to satisfy both simultaneously in the same Blender session.

Many IFC viewers only show geometry, and don't show object placements. This may
give users the false impression that their coordinates in their IFC project do
not have such a large range. However, because the BlenderBIM Add-on is a full
authoring platform, we do need to show these placements and thus it is the users
responsibility to reconcile this inconsistency in their coordinates.  Either the
user needs to fix their file to consistently offset all coordinates, or the user
needs to manually tell the BlenderBIM Add-on the coordinates of the desired
false origin. In the absence of manual intervention, the BlenderBIM Add-on will
make an intelligent guess, but it may be wrong.

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
constant for small sites (defined approximately as less than 1km square).  This
practical limit of georeferenced vertical construction is smaller than the
software limit, so this surveying convention is the actual limiting factor, not
the software.
