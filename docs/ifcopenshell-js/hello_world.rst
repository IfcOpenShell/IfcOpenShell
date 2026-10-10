.. This file was generated with the assistance of an AI coding tool.

Hello, world!
=============

Opening an IFC file
-------------------

After :doc:`installation`, initialize the runtime and load the schema for your
sample model. This example uses an IFC4 file. In Node.js, read the file as bytes:

.. code-block:: javascript

   import { readFile, writeFile } from 'node:fs/promises';
   import * as ifcopenshell from 'ifcopenshell';

   const runtime = await ifcopenshell.init();
   await runtime.loadPlugin('schema', 'ifc4');
   const bytes = await readFile('model.ifc');
   const model = ifcopenshell.open(bytes, 'model.ifc');

In the browser, obtain the same bytes from an uploaded ``File`` or an HTTP
response. For example, replace the ``readFile`` call with:

.. code-block:: javascript

   const response = await fetch('/models/model.ifc');
   if (!response.ok) throw new Error(`Failed to load IFC: ${response.status}`);
   const bytes = new Uint8Array(await response.arrayBuffer());

``open()`` accepts a ``Uint8Array`` or ``ArrayBuffer``, rather than a filesystem
path. Load the file's schema plugin before calling it.

Finding and inspecting entities
-------------------------------

The examples below assume ``model`` is still open. Inspect its schema and
retrieve an entity by STEP id:

.. code-block:: javascript

   console.log(model.schema());
   const entity = model.byId(1);
   {
     if (entity) console.log(entity.id(), entity.isA());
   }

Query walls, check their IFC class, and read attributes by name or position:

.. code-block:: javascript

   const walls = model.byType('IfcWall');
   {
     console.log('Number of walls:', walls.length);
     const wall = walls[0];
     if (wall) {
       console.log(wall.isA());
       console.log(wall.isA('IfcElement'));
       console.log(wall.get(0)); // GlobalId
       console.log(wall.get('Name'));
     }
   }

``model.byGuid(globalId)`` retrieves an entity by GlobalId. Missing id or
GlobalId lookups raise an error. ``model.byType(typeName)`` includes subtypes;
``model.byTypeExclSubtypes(typeName)`` selects only the exact IFC class.
Type queries return ordinary JavaScript arrays.

Editing and saving
------------------

Use ``set()`` to change attributes. Serialize the IFC-SPF text with ``toString()``
and write it using your application's filesystem or download mechanism:

.. code-block:: javascript

   const walls = model.byType('IfcWall');
   {
     if (walls[0]) walls[0].set('Name', 'My new wall name');
     await writeFile('updated.ifc', model.toString(), 'utf8');
   }

In a browser, ``new Blob([model.toString()], { type: 'text/plain' })`` produces a
downloadable IFC file. Release the model after all queries and edits are done:

.. code-block:: javascript

   model.dispose();

Creating a new file
-------------------

An empty IFC file can also be constructed after loading its schema plugin:

.. code-block:: javascript

   const model = new ifcopenshell.File('IFC4');
   try {
     const wall = model.create('IfcWall', { Name: 'Example wall' });
     {
       wall.set('GlobalId', '0YvctVUKr0kugbFTf53O9L');
       console.log(wall.id(), wall.get('Name'));
       console.log(model.toString());
     }
   } finally {
     model.dispose();
   }

This demonstrates entity creation. A complete exchange model also needs the
appropriate project, units, contexts, and relationships. Use a distinct valid
IFC GlobalId for each root entity in your application.

Object lifetime
---------------

The model owns its IFC data. Only ``File`` and geometry ``Iterator`` objects
implement ``Disposable``. Dispose them when finished to invoke their native
C++ destructors. Entity references and other binding wrappers use GC cleanup;
query results are ordinary JavaScript arrays. Keep the model alive while
accessing its entities. ``model.remove()`` removes IFC data from the file.

TypeScript projects can use ``using`` declarations for automatic disposal:

.. code-block:: typescript

   using model = new ifcopenshell.File('IFC4');
   const wall = model.create('IfcWall', { Name: 'Example wall' });
   console.log(wall.get('Name'));

The compiler transforms these declarations into cleanup calls. When writing
JavaScript for runtimes without ``using`` support, use ``try`` / ``finally``.
