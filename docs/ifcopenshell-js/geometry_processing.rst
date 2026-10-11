.. This file was generated with the assistance of an AI coding tool.

Geometry processing
===================

Preparing geometry plugins
--------------------------

Geometry processing needs the model's schema, the corresponding mapping, and
a geometry kernel. These examples assume the IFC4 ``model`` and ``runtime``
from :doc:`hello_world`:

.. code-block:: javascript

   import * as geom from 'ifcopenshell/geom';

   await runtime.loadPlugin('mapping', 'ifc4');
   await runtime.loadPlugin('kernel', 'opencascade');

The mapping plugin interprets IFC representations. The kernel performs the
geometry operations. The native build also provides kernels including
``manifold``, ``cgal``, and ``cgalsimple``; load the selected kernel and pass
its identifier as ``geometryLibrary`` or the last ``createShape()`` argument.

Individual processing
---------------------

``createShape()`` converts one product into a geometry element. This example
extracts a wall's triangulation, placement, and per-face material assignments:

.. code-block:: javascript

   const settings = new geom.Settings();
   const walls = model.byType('IfcWall');
   {
     settings.set('weld-vertices', false);
     const wall = walls.find(wall => {
       const representation = wall.get('Representation');
       {
         return representation instanceof ifcopenshell.EntityInstance;
       }
     });
     if (wall) {
       const shape = geom.createShape(settings, wall);
       {
         if (shape) {
           const triangulation = shape.asTriangulationElement();
           {
             if (triangulation) {
               const geometry = triangulation.geometry();
               {
                 console.log(shape.id(), shape.guid());
                 console.log(geometry.vertsBuffer(Float32Array));
                 console.log(geometry.facesBuffer(Uint32Array));
                 console.log(geometry.edgesBuffer(Int32Array));
                 console.log(geometry.normalsBuffer(Float32Array));
                 console.log(geometry.materialIdsBuffer(Int32Array));
                 console.log(shape.transformationBuffer(Float64Array));
               }
             }
           }
         }
       }
     }
   }

Vertices are flattened XYZ coordinates and faces are flattened triangle vertex
indices. With local coordinates, apply the shape's column-major 4 by 4
transformation matrix when displaying the geometry. Set ``use-world-coords``
to ``true`` to request world-coordinate vertices instead. Geometry coordinates
use metres by default; see :doc:`../ifcopenshell/geometry_settings` for settings
such as ``convert-back-units``.

Typed buffers are detached copies, so they can be retained after disposing the
native geometry handles. Dispose borrowed geometry and triangulation handles
before their owning shape.

Geometry iterator
-----------------

Use the iterator for processing a whole model. It can reuse shared geometry
and accepts include or exclude filters containing STEP ids or IFC type names:

.. code-block:: javascript

   const settings = new geom.Settings();
   const iterator = new geom.Iterator(settings, model, {
     geometryLibrary: 'opencascade',
     numThreads: 1,
     include: ['IfcWall', 'IfcSlab'],
   });
   try {
     if (iterator.initialize()) {
       do {
         const shape = iterator.get();
         {
           if (shape) console.log(shape.id(), shape.guid(), shape.name());
         }
       } while (iterator.next());
     }
   } finally {
     iterator.dispose();
   }

``initialize()`` positions the iterator at its first element. Call ``get()``
once at each position, then ``next()`` to advance. ``include`` and ``exclude``
are mutually exclusive. Keep the model and settings alive until iteration
finishes. Processing runs synchronously; a browser application can run it in
a worker to keep its interface responsive. Thread counts depend on the WASM
build's threading support.

Processing a particular representation
--------------------------------------

The optional third argument to ``createShape()`` selects a representation of
the product. For example, this reads the first shape representation of a wall:

.. code-block:: javascript

   const walls = model.byType('IfcWall');
   const settings = new geom.Settings();
   {
     const wall = walls[0];
     if (wall) {
       const definition = wall.get('Representation');
       if (definition instanceof ifcopenshell.EntityInstance) {
         {
           const representations = definition.get('Representations');
           if (Array.isArray(representations)) {
             try {
               const representation = representations[0];
               if (representation instanceof ifcopenshell.EntityInstance) {
                 const shape = geom.createShape(settings, wall, representation);
                 {
                   if (shape) console.log(shape.id(), shape.context());
                 }
               }
             } finally {
               for (const representation of representations) {
               }
             }
           }
         }
       }
     }
   }

Serialising geometry
--------------------

The ``exportToBuffer()`` convenience function exports OBJ, SVG, or TTL text.
Load the format's serializer plugin before exporting. OBJ returns both the
geometry text and material text:

.. code-block:: javascript

   import { exportToBuffer } from 'ifcopenshell/serializers';

   await runtime.loadPlugin('geometry_serializer', 'obj');
   const settings = new geom.Settings();
   {
     const result = await exportToBuffer(model, settings, 'obj', {
       kernel: 'opencascade',
       numThreads: 1,
     });
     if (result) {
       await writeFile('model.obj', result.primary, 'utf8');
       await writeFile('model.mtl', result.secondary, 'utf8');
     }
   }

This Node.js example uses ``writeFile`` from :doc:`hello_world`. In the browser,
create downloadable blobs from the returned strings. A ``null`` result means
the geometry iterator could not initialize. The generated native API also
exposes serializer factories for other formats present in the plugin manifest.
