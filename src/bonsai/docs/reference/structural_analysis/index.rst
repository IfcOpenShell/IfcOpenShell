Structural Analysis
===================

.. include:: /_incomplete_message.rst


.. figure:: images/interface_property-editor_structural-analysis.png
   :alt: property editor structural analysis sub-tab

   Structural Analysis sub-tab.

Generate Structural Model (Beams & Columns)
-----------------------------------------

Select profile-based beams or columns and use **Generate from Selected** to
create linked structural curve members. Each supported element must have one
material and an extruded section. The member shares the section profile and
material with the element, and shares its profile set when one is assigned.
Editing shared data through either member or element can affect both, as well
as other elements using the same profile or material. An alternative section
cannot be tested independently by editing that shared data.

Members are joined only where their ends fall within the merge tolerance of
each other. Running the operator again on elements that already have a
generated member deletes that member and generates it again, which discards
manual changes to the analysis model but does not update the building. Point
connections with a boundary condition or load are kept and reused. Objects that
cannot be generated are listed in the report and left selected.
Generation is available for IFC4 and IFC4X3.