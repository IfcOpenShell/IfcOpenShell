.. This file was generated with the assistance of an AI coding tool.

Geometry tree
=============

Geometry trees support spatial selection through the native geometry API.
These examples assume the IFC4 ``model`` and ``runtime``
from :doc:`hello_world`, and the ``geom`` import from :doc:`geometry_processing`.

Building a tree for spatial selection
-------------------------------------

Load the tree plugin in addition to the geometry plugins, then add a model to
the tree. The ``opencascade.brep`` backend supports selection using bounding
boxes, precise geometry, and rays:

.. code-block:: javascript

   await runtime.loadPlugin('mapping', 'ifc4');
   await runtime.loadPlugin('kernel', 'opencascade');
   await runtime.loadPlugin('tree', 'opencascade.brep');
   const settings = new geom.Settings();
   const tree = runtime.raw.geom.createTree('opencascade.brep');
   {
     if (tree) {
       tree.addFile(model, settings);
       const selected = tree.selectBoxBounds(-1, -1, -1, 1, 1, 1, false);
       {
         for (const entity of selected) {
           {
             if (entity) console.log(entity.id(), entity.className(false));
           }
         }
       }
     }
   }

The last bounding-box argument selects completely contained elements when
``true``; ``false`` allows overlapping bounds. ``selectPoint()`` queries precise
geometry, ``selectBoxPoint()`` queries bounding boxes, and ``selectRay()``
returns ray intersection records. Coordinates and distances use the geometry
tree's coordinate system and units, normally world coordinates in metres.

Selecting elements using a ray
------------------------------

``selectRay()`` returns intersections along a ray, including the element,
distance, intersection point, and surface normal. After loading the plugins
as above:

.. code-block:: javascript

   const settings = new geom.Settings();
   const tree = runtime.raw.geom.createTree('opencascade.brep');
   {
     if (tree) {
       tree.addFile(model, settings);
       const intersections = tree.selectRay(-2, 0, 0.5, 1, 0, 0, 100);
       {
         for (let index = 0; index < tree.rayIntersectionCount(intersections); index++) {
           const intersection = tree.rayIntersectionAt(intersections, index);
           const entity = intersection.instance();
           {
             console.log(entity.id(), intersection.distance(),
               intersection.position(), intersection.normal());
           }
         }
       }
     }
   }

The example starts at ``(-2, 0, 0.5)``, points along the positive X axis, and
limits the ray to a length of 100. Adapt the origin and direction to your model.

Keep the source model alive until the tree and its result handles are released.
``addIterator()`` is also available for populating a tree from a geometry iterator.
