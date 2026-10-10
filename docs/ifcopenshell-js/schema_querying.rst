.. This file was generated with the assistance of an AI coding tool.

Schema querying
===============

Schema declarations
-------------------

Query a loaded schema through the native ``parse`` API, without opening an IFC
model. This example uses the initialized ``runtime`` from :doc:`hello_world`:

.. code-block:: javascript

   const schema = ifcopenshell.schemaByName('IFC4');
   {
     if (schema) {
       console.log(schema.name());
       const declarations = schema.declarations();
       {
         for (const declaration of declarations) console.log(declaration.name());
       }
     }
   }

``runtime.raw.parse.schemaNames()`` lists schemas currently registered with
the runtime. Load a schema plugin before requesting its declarations.

Entity inheritance and attributes
---------------------------------

A declaration can represent an entity, enumeration, select, or defined type.
Use ``asEntity()`` to access entity-specific information:

.. code-block:: javascript

   const schema = ifcopenshell.schemaByName('IFC4');
   const declaration = schema?.declarationByName('IfcWall');
   const entity = declaration?.asEntity();
   {
     if (entity) {
       console.log('Abstract:', entity.isAbstract());
       const parent = entity.supertype();
       {
         console.log('Supertype attribute count:', parent?.attributeCount());
       }
       const subtypes = entity.subtypes();
       {
         console.log('Number of subtypes:', subtypes.length);
       }
       const attributes = entity.allAttributes();
       {
         for (const attribute of attributes) {
           const type = attribute.typeOfAttribute();
           {
             console.log(attribute.name(), attribute.optional(), type?.kind());
           }
         }
       }
     }
   }

``attributes()`` returns attributes declared directly on the entity;
``allAttributes()`` includes inherited ones. ``allInverseAttributes()`` exposes
inverse declarations. ``derived()`` identifies derived forward attributes.
Release declaration handles before releasing the schema handle.

Enumerations and select types
-----------------------------

.. code-block:: javascript

   const schema = ifcopenshell.schemaByName('IFC4');
   const declaration = schema?.declarationByName('IfcWallTypeEnum');
   const enumeration = declaration?.asEnumerationType();
   {
     if (enumeration) console.log(enumeration.enumerationItems());
   }

For a select declaration, ``asSelectType().selectListNames()`` returns its
permitted declaration names. Defined types expose their underlying parameter
type through ``asTypeDeclaration().declaredType()``. Each conversion and
returned native object has the same disposal requirements as the examples above.
