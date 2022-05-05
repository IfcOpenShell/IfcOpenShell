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

To navigate, can use the **Navigate Gizmo** on the top right corner of the
**Viewport** panel. Click and drag on the coloured axes to **Orbit**, click and
drag on the magnifying glass to **Zoom**, and click and drag on the hand icon to
**Pan**.  You can also click on the grid icon to switch between perspective and
orthographic view.

To switch to a top view, front view, or side view, click the relevant axis on
the **Navigate Gizmo**.

.. image:: navigate-gizmo.png

You can also use your mouse to navigate. Hover your mouse over the **Viewport**
panel and click and drag the Middle Mouse Button (MMB) to **Orbit**. Scroll the
mousewheel to **Zoom**, and use Shift-MMB to **Pan**.

If you have a numpad, you can use the numpad keys to quickly switch to top,
front, or side view. Use ``7`` for top view, ``1`` for front view, and ``3`` for
side view.

.. warning::

   Blender's hotkeys are context sensitive. This means that a hotkey has a
   different meaning depending on the panel your mouse cursor is hovering over.
   If you press ``7`` to go to top view, make sure your mouse cursor is over the
   **Viewport** panel. Be very careful where your mouse is, or you might press a
   hotkey and it will have unintended consequences!

If you click on an object, such as a wall in the **Viewport** panel, you can
zoom to the selected object by clicking on ``View > Frame Selected``. The hotkey
is the ``.`` button on the numpad. After zooming into an element, when you
**Orbit** the 3D view will rotate around the center of that element.

You can also zoom to all objects in the project by clicking on ``View > Frame
All``.

.. image:: frame-selected.png

Another good way to navigate is by flying or walking around similar to a video
game. Choose ``View > Navigation > Walk Navigation``, or use the ``Shift-```
hotkey (the backtick key is usually to the left of the number 1 on the
keyboard). With **Walk Navigation** enabled, use the ``WASD`` keys and the mouse
to move around like a video game. You can use the ``Shift`` key to switch
between moving fast and slow. If you scroll with the mousewheel, it will adjust
the speed that you move at.

Sometimes, you want to look through objects. You can toggle **X-Ray Mode** by
pressing the button on the top right of the **Viewport** panel. The hotkey is
``Alt-Z``.

.. image:: x-ray-mode.png

.. tip::

   Blender has lots of hotkeys to do things quickly, but these can take time to
   learn but it is worth it as you will be much faster. These hotkeys can be
   customised in Blender's preferences.


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
