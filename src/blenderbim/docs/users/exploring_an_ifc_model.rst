Exploring an IFC model
======================

We're going to load an existing IFC model and explore some common properties
most users will be interested in.

If you don't have an IFC model available, here's a small one for your
convenience provided by the Institute for Automation and Applied Informatics
(IAI) / Karlsruhe Institute of Technology.  It's in German, so you may need to
use some creativity when reading the data.

.. container:: blockbutton

    `Download sample IFC <https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc>`__

.. seealso::

    You can find more sample models online in the `OSArch Open Data Directory
    <https://wiki.osarch.org/index.php?title=AEC_Open_Data_directory>`__

Loading a model
---------------

Blender's interface is divided into panels. The main **Viewport** panel shows 3D
geometry.  The top right **Outliner** panel shows a tree of geometric objects.
The bottom right **Properties** panel shows data and relationships.

.. image:: blenderbim-layout.png

The **Properties** panel has tabs to switch between different types of
properties. Make sure you have the **Scene Properties** tab activated, and find
the **IFC Project** subpanel. Click on the **Load Project** and browse to your
``.ifc`` file.

.. image:: properties-loadproject.png

After loading, you will see the model appear in the **Viewport** panel.

.. image:: example-project.png

Let's take a look at the **IFC Project** subpanel again. It shows the loaded
filename, as well as the **IFC Schema**. There are two commonly seen **IFC
Schema** versions: IFC2X3 and IFC4. Checking the **IFC Schema** is important
because it has an impact on what BIM data may be stored. IFC4 is the newer
version and it is recommended to use IFC4 models as it has significantly more
BIM capabilities compared to IFC2X3. 

.. tip::

   Blender's interface is highly customisable. Panels, panel types, colours,
   sizes, and tabs may be edited to suit your workflow. 

Navigating a model in 3D
------------------------

TODO

Overview of all objects
-----------------------

TODO

Viewing element classes
-----------------------

TODO

Viewing attributes and properties
---------------------------------

TODO

Viewing construction types
--------------------------

TODO

Viewing materials
-----------------

TODO
