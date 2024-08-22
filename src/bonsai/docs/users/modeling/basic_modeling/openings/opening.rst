Opening Without Filling
=======================

An opening without a filling is a void in a building element,
typically a wall, that doesn't contain a door or window.

These openings can serve various purposes such as ventilation, pass-throughs, service penetrations, or architectural features.

In IFC, it's represented by the IfcOpeningElement entity, which is a subtype of IfcFeatureElementSubtraction.

This section covers how to create openings without fillings in your BIM model using Bonsai.


Creating an Opening Without Filling
-----------------------------------

Currently, there isn't a dedicated tool for creating openings without fillings.
However, every door or window is a filling for an opening element, so it's created implicitly.

It means, you can achieve an opening without a filling by creating a door or window and then removing it and its type.

Here's the process:

1. Select the wall where you want to create the opening.
2. Set the 3D cursor on the wall at the desired opening location.
3. Use either the "Create Door" or "Create Window" tool from the toolbar,
   depending on the shape you need for your opening.
4. Follow the steps to create a door or window as described in their respective sections.
5. After creating the door or window, select it in the 3D viewport and press Delete.
6. In the Outline panel, find the "Type" field and press Delete.

This process will leave you with an opening element without a filling.

Additionally, you can create an opening by using the "Add Void" button in Create Wall tool.
This tool will add an Opening IFC element to the Outline and its 3D representation in the 3D Vieport.
Blender move and scale tools will allow you to modify the opening.
After you finished with modifications, you can press the check mark to complete the void.

Modifying Openings
------------------

You can modify openings using various tools:

- Resize: Adjust the width and height parameters in the top bar.
- Move: Use Blender's standard move tools to reposition the opening.

.. note::
  The opening is hidden object. To show it, press the "eye" button hear the "Add Void" in the Create Wall tool.

.. note::
   After moving an opening, you need to recalculate the void in the wall. To do this:

   - Click on checkmark near the "Add Void" in the Create Wall tool.


See Also
--------

- :doc:`../creating_walls`
- :doc:`door`
- :doc:`window`
