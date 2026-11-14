Structural Analysis
===================

.. include:: /_incomplete_message.rst


.. figure:: images/interface_property-editor_structural-analysis.png
   :alt: property editor structural analysis sub-tab

   Structural Analysis sub-tab.

Generate Structural Model (Beams & Columns)
-----------------------------------------

Select profile-based beams or columns and use **(Re)Generate from Selected** to
create linked structural curve members. Each supported element must have one
material and an extruded section. The member shares its section and material
with the element; editing shared data can therefore affect both.

The panel reports differences between linked members and their elements.
**Update Structural Model** explicitly refreshes the members' axes,
orientations, sections and materials from the elements. It can overwrite
manual changes to the analysis model, but does not update the building.
Comparisons require the relevant objects to be loaded. Generation is available
for IFC4 and IFC4X3.