.. This file was generated with the assistance of an AI coding tool.

Code examples
=============

These examples assume an initialized runtime and an open ``model``, as in
:doc:`hello_world`. They use the entity graph directly, including forward and
inverse attributes.

Get all entities
----------------

``model.ids`` lists the STEP ids in ascending order:

.. code-block:: javascript

   for (const id of model.ids) {
     const entity = model.byId(id);
     {
       if (!entity) continue;
       console.log(entity.id(), entity.isA());
       if (entity.attributes().includes('Name')) console.log(entity.get('Name'));
     }
   }

Get all wall types
------------------

.. code-block:: javascript

   const types = model.byType('IfcWallType');
   {
     for (const type of types) console.log(type.id(), type.get('Name'));
   }

Find the type of an occurrence
------------------------------

An IFC4 occurrence refers to its type through ``IsTypedBy``. Follow the
relationship and read its ``RelatingType``:

.. code-block:: javascript

   const walls = model.byType('IfcWall');
   {
     for (const wall of walls) {
       const relations = wall.inverse('IsTypedBy');
       {
         for (const relation of relations) {
           const type = relation.get('RelatingType');
           if (type instanceof ifcopenshell.EntityInstance) {
             {
               console.log(wall.get('Name'), type.get('Name'));
             }
           }
         }
       }
     }
   }

For IFC2X3, type relationships are among ``IsDefinedBy``; select those whose
class is ``IfcRelDefinesByType``.

Find the spatial container of an element
----------------------------------------

The following finds the immediate containment relationship. An element can
also inherit containment through an aggregate, which requires following its
``Decomposes`` relationships.

.. code-block:: javascript

   const walls = model.byType('IfcWall');
   {
     for (const wall of walls) {
       const relations = wall.inverse('ContainedInStructure');
       {
         for (const relation of relations) {
           const container = relation.get('RelatingStructure');
           if (container instanceof ifcopenshell.EntityInstance) {
             {
               console.log(wall.id(), container.isA(), container.get('Name'));
             }
           }
         }
       }
     }
   }

Read property sets
------------------

For occurrence property sets, follow ``IfcRelDefinesByProperties`` from
``IsDefinedBy``. This example reads single-value properties; quantities,
complex properties, and type-level property sets have their own IFC attributes.

.. code-block:: javascript

   const walls = model.byType('IfcWall');
   {
     for (const wall of walls) {
       const relations = wall.inverse('IsDefinedBy');
       {
         for (const relation of relations) {
           if (!relation.isA('IfcRelDefinesByProperties')) continue;
           const pset = relation.get('RelatingPropertyDefinition');
           if (!(pset instanceof ifcopenshell.EntityInstance)) continue;
           {
             if (!pset.isA('IfcPropertySet')) continue;
             const properties = pset.get('HasProperties');
             if (!Array.isArray(properties)) continue;
             try {
               for (const property of properties) {
                 if (!(property instanceof ifcopenshell.EntityInstance)) continue;
                 if (!property.isA('IfcPropertySingleValue')) continue;
                 const value = property.get('NominalValue');
                 {
                   console.log(pset.get('Name'), property.get('Name'),
                     value instanceof ifcopenshell.EntityInstance ? value.get(0) : value);
                 }
               }
             } finally {
               for (const property of properties) {
               }
             }
           }
         }
       }
     }
   }

Navigate references
-------------------

``model.getInverse(entity)`` returns a set of referring entities, deduplicated
by IFC identity. ``model.traverse(entity, maxDepth)`` follows forward references;
use ``-1`` for unlimited depth or ``traverseBreadthFirst`` for breadth-first order.
Traversal returns an ordinary JavaScript array.

.. code-block:: javascript

   const entity = model.byId(model.ids[0]);
   {
     if (entity) {
       const referring = [...model.getInverse(entity)];
       const referenced = model.traverse(entity, 1);
       {
         console.log('Referenced by:', referring.map(item => item.id()));
         console.log('Forward traversal:', referenced.map(item => item.id()));
       }
     }
   }

Query units
-----------

``getUnit()`` returns the unit magnitude for a unit type. For example, a
millimetre-based model has a length magnitude of ``0.001`` relative to metres:

.. code-block:: javascript

   console.log(model.getUnit('LENGTHUNIT'));

See :doc:`geometry_processing` for extracting transformed geometry and
:doc:`schema_querying` for querying attribute declarations.
