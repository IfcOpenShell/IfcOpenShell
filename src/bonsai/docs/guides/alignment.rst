Road and Rail Alignments
========================

An alignment is the reference line that a road, railway, bridge, or tunnel is built along. In IFC it
is an ``IfcAlignment`` made of up to three layouts, each a sequence of segments:

- the **horizontal** layout, the alignment in plan: tangents (straights), circular curves, and
  transition spirals;
- the **vertical** layout, the profile: constant grades joined by parabolic vertical curves, measured
  by distance along the horizontal;
- the **cant** layout, for railways: the superelevation of the rails, measured the same way.

Bonsai creates both the semantic definition (the layouts) and the geometry (``IfcCompositeCurve``,
``IfcGradientCurve``, and ``IfcSegmentedReferenceCurve``) and keeps the two in step as you edit.
Positions along the alignment are expressed as **stations**, set by stationing referents.

Alignments need an IFC4X3 project. The alignment tools are in the **Alignments** tab of the Bonsai
properties panel.

Adding an alignment
-------------------

1. In the **Alignments** tab, click **Add Alignment**.
2. Enter a **Name**, then choose the **Definition**:

   - **Layouts (PI method)** gives horizontal, vertical, and cant layouts drawn PI by PI. This is
     the usual choice for design work.
   - **Polyline** gives a 2D or 3D polyline with no layouts, for example for early planning or
     survey data. See `Polyline alignments`_.
   - **Offset Curve** gives a curve at a set distance from another alignment, such as an edge of
     pavement or a rail. It is only offered once the project has another alignment to offset from.
     See `Offset curve alignments`_.

3. Leave **Define Start Station** on and enter the **Start Station**, the station at the start of
   the alignment. Plain numbers and stationing notation are both accepted, e.g. ``1000``,
   ``10+00``, or ``1+000``. The start station can be changed later.
4. Click **OK**. The new alignment is empty until its horizontal alignment is drawn.

Drawing the horizontal alignment
--------------------------------

The horizontal alignment is drawn tangent by tangent, by placing its PIs (points of intersection).
Every PI starts as a sharp corner, and curves are added afterwards.

1. Select the alignment and click **Draw Horizontal Alignment**.
2. Click in the viewport to place the start point and then each PI. Snapping works as it does for
   Bonsai's other polyline tools.
3. To type a PI's position instead, press :kbd:`D` for the distance from the previous PI and
   :kbd:`A` for the angle. The **Angle** field accepts:

   - an angle, e.g. ``30``;
   - a quadrant bearing, e.g. ``N 30 15 24 E``;
   - a deflection from the previous tangent, e.g. ``12 30 Rt`` or ``12 30 Lt``.

   The **Bearing** readout shows the bearing of the tangent being drawn. Bearings are grid bearings,
   so they account for the project's map rotation.

4. Place the end point, then right-click or press :kbd:`Enter` to finish. :kbd:`Esc` cancels without
   creating anything.

The alignment is created with a marker at each interior PI, ready for curves to be added.

Adding curves at PIs
^^^^^^^^^^^^^^^^^^^^

1. Select a PI marker in the viewport. Its settings appear in the **Alignments** tab.
2. Choose a **Curve Type**:

   - **None (sharp PI)** keeps the PI a sharp corner;
   - **Circular** is a circular curve;
   - **Spiral-Circular**, **Circular-Spiral**, and **Spiral-Circular-Spiral** add transition spirals
     ahead of the curve, after it, or on both sides.

3. Enter the **Radius** and, for curves with spirals, the spiral lengths and the **Spiral Family**.
   The clothoid is the usual spiral. The cubic, Helmert curve, Bloss curve, cosine curve, and sine
   curve are also available, and the Viennese bend once the alignment has a cant layout. A Viennese
   bend also needs the gravity centerline height.
4. Click **Apply Curve**. The whole alignment is regenerated from the current markers.
5. Repeat for the other PIs, then click **Finish** to remove the markers.

Apply Curve reports an error when a curve doesn't fit, for example when the tangents on either side
of a PI are too short for its curve and spirals.

Compound and reverse curves
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two neighbouring curves can meet directly, with no tangent between them. The result is a compound
curve (P.C.C.) when both curves turn the same way, or a reverse curve (P.R.C.) when they turn opposite
ways.

1. Select the first PI's marker and set its curve type to **Circular** or **Spiral-Circular**. The
   side where the two curves join can't have a spiral.
2. Turn on **Join to Next PI (Compound/Reverse Curve)**.
3. Choose how the junction is placed:

   - **Radius**: this curve's radius is given, and the next PI's radius is computed to close the
     junction.
   - **Distance**: enter the distance from this PI to the junction. Both radii are computed.

4. Click **Apply Curve**.

Editing the horizontal alignment
--------------------------------

Editing with PI markers
^^^^^^^^^^^^^^^^^^^^^^^

1. Select the alignment and click **Edit PIs** (the marker icon next to Draw Horizontal Alignment).
   A marker is placed at the start point, the end point, and each PI.
2. Edit the markers:

   - **Move** a marker by dragging it. Moving the start or end point moves the ends of the alignment.
   - Use **Move with Distance/Angle** to place the selected marker with the same typed input as the
     draw tool, measured from the neighbouring PI.
   - Click **Insert PI** to add a PI halfway along the tangent after the selected marker, or
     **Delete PI** to remove the selected PI. Its neighbours are rejoined when you apply.
   - Change a PI's curve settings as described in `Adding curves at PIs`_.

3. Click **Apply Curve** to regenerate the alignment, then **Finish**.

Segments keep their identity (their GlobalIds) through an edit wherever they still correspond to the
same PI, so anything that refers to them stays connected. Only segments of added or deleted PIs are
created or removed.

Editing in a table
^^^^^^^^^^^^^^^^^^

**Edit PIs (Table)** lists every PI's Easting, Northing, and curve settings in one table. It is useful
for typing exact values, or for changing many curves at once.

1. Select the alignment and click **Edit PIs (Table)**.
2. Edit the rows. **Insert Before** and **Insert After** add a PI next to the selected row, and the
   minus button deletes it.
3. Click **Apply Horizontal Curves**, then **Finish** to close the table.

Extending the alignment
^^^^^^^^^^^^^^^^^^^^^^^

1. Select the alignment and click **Extend** (the arrow icon).
2. Place more PIs past the current end, as when drawing. Distances and angles are measured from the
   current end, against its last tangent.
3. Right-click or press :kbd:`Enter` to finish.

The old end point becomes a sharp PI; give it a curve as for any PI. The vertical and cant layouts
are not extended: extend them separately, or use **Match** (see `Layouts of different lengths`_).

The vertical alignment
----------------------

The vertical alignment is drawn and edited in the **profile view**, which docks below the 3D viewport.
Its horizontal axis is station and its vertical axis is elevation.

- Click the graph icon next to **Vertical Profile** in the Alignments tab to show or hide the
  profile view.
- :kbd:`Shift` + mouse wheel pans along the alignment, and :kbd:`Home` fits the whole alignment.
- **VE** sets the vertical exaggeration.

Drawing the vertical alignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The horizontal alignment must be drawn first, because the vertical alignment is measured along it.

1. Select the alignment and, in the **Vertical Alignment** panel, click **Draw Vertical Alignment**.
   The profile view opens if it isn't already open.
2. Click to place the start point, each VPI (vertical point of intersection), and the end point.
   The start point is held at the start of the alignment, and VPIs can't go past its end.
3. To type values instead, press :kbd:`Tab` to cycle through **Elevation**, **Slope** (%), and
   **Distance Along**, or :kbd:`E`, :kbd:`S`, or :kbd:`D` to jump to one. Any two typed values fix
   the VPI. With one typed, the mouse supplies the rest.
4. :kbd:`Backspace` removes the last VPI. Right-click or :kbd:`Enter` finishes, and :kbd:`Esc`
   cancels.
5. The VPIs are listed in the Vertical Alignment panel. For each VPI that needs a vertical curve, set
   the **Curve** to parabolic and enter the curve length.
6. Click **Apply Vertical Curves**, then **Finish**.

Editing the vertical alignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. In the **Alignment Segments** panel, click **Edit PIs** on the vertical's row. The VPIs are
   listed in the Vertical Alignment panel.
2. Edit the values in the list, or click **Drag PIs in Profile** to drag VPIs in the profile view.
   **Insert Before**, **Insert After**, and the minus button add and remove VPIs.
3. Click **Apply Vertical Curves**, then **Finish**.

To add VPIs past the end of a vertical, click **Extend Vertical** (the arrow icon) on its row.

Multiple vertical alignments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One horizontal alignment can have several verticals, such as the profiles of the left and right edges
of a road. Draw each vertical in turn. To tell them apart, click a vertical's name in the Alignment
Segments panel to rename it. The eye icon on each vertical's row shows or hides it in the profile
view.

Cant
----

Cant (superelevation) is the difference in height between the two rails. The cant layout follows the
horizontal alignment's segments: no cant on tangents, full cant on curves, and a linear change over
the transition spirals between them. Spirals are recommended wherever the cant changes.

1. Draw the horizontal and vertical alignments.
2. In the **Alignment Segments** panel, click **Generate Cant Layout** on the vertical's row.
3. Enter the **Cant**: the full height difference between the rails on the curves. The outer rail of
   each curve is raised.
4. Click **OK**.

To set a different cant on individual curves, edit the cant segments in a table (see
`Editing segments in a table`_). When the horizontal alignment is edited later, the cant layout is
updated to match.

Editing segments in a table
---------------------------

Each layout's segments can also be edited directly. Use this for layouts that were not made by the PI
method, or to adjust single segments.

1. In the **Alignment Segments** panel, click the pencil icon on the horizontal, vertical, or cant
   row.
2. Edit each segment's type, length, and radii, grades, or cants. The buttons below the table add,
   remove, and reorder segments.
3. Click **Apply** to rebuild the layout, or the cross to discard the changes.

Layouts of different lengths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A vertical or cant layout doesn't have to end exactly where the horizontal does. When it doesn't,
its row in the Alignment Segments panel shows how far it ends past, or short of, the horizontal.
Click **Match** to stretch or shorten its last segment so that it ends with the horizontal.

Polyline alignments
-------------------

A polyline alignment is a sequence of straight legs with no curves and no layouts.

1. Add an alignment with the **Polyline** definition.
2. Click **Draw Polyline** and place the points as for a horizontal alignment. Press :kbd:`V` to
   switch between 2D (every point at Z = 0) and 3D. In 3D, points snap to scene geometry,
   :kbd:`Shift` + :kbd:`X`, :kbd:`Y`, or :kbd:`Z` locks a plane, and a :kbd:`Z` field is added to
   the typed input.
3. Right-click or press :kbd:`Enter` to finish.

To edit the points, use **Edit Points** to drag markers, **Edit Points (Table)** to type coordinates,
or **Extend** to add points past the end. The Alignment Segments panel lists each point with its
station. A 3D polyline's profile can be shown in the profile view with **Show Profile**.

Offset curve alignments
-----------------------

An offset curve alignment follows another alignment at given lateral (and, in 3D, vertical) offsets.
The offsets can vary along its length. Examples are an edge of pavement, a curb line, or a second track.

1. Click **Add Alignment** and choose the **Offset Curve** definition.
2. In **Offset From**, choose the curve to offset from:

   - another alignment's horizontal, for a 2D offset curve;
   - one of its verticals, for a 3D offset curve that follows that profile;
   - another offset curve.

3. Enter the **Offset Lateral**, positive to the left when facing along the alignment, and for a 3D
   curve the **Offset Vertical**, positive up.
4. Click **OK**. The offset curve starts with that one constant offset.
5. To vary the offset, click **Edit Offsets**. Add rows of **Distance Along**, **Lateral**, and, for
   3D, **Vertical** offset. Click **Apply Offsets**.

Offset curves are added without stationing by default. Use **Add Stationing** in the Stationing
panel if one is needed. A 3D offset curve's profile can be shown in the profile view.

Stationing
----------

The **Stationing** panel shows the start station and any station equations of the selected alignment.

- Click the pencil icon next to the start station to change it.
- Click **Add Station Equation** to change the station numbering at a point along the alignment.
  Enter the **Distance Along**, the **Incoming Station** (the station just before the point, i.e. the
  back station), and the **Outgoing Station** (the station just after it, i.e. the ahead station).
  An outgoing station greater than the incoming station makes a gap in the numbering, and a smaller
  one makes an overlap. Turn on **Reverse Stationing Direction** for stations that decrease with
  distance along from that point.
- The pencil and cross icons on each equation edit or remove it.

Key points
^^^^^^^^^^

**Generate Key Points** adds a referent at every point where one segment meets the next. Each
referent is named with the alignment name, the station, and the kind of point, for example
``Main Street 12+45.67 (P.C.)``. Its labels include:

- horizontal: P.O.B. and P.O.E. (beginning and end), P.I., P.C. and P.T. (curve start and end), T.S.,
  S.C., C.S., and S.T. (spiral transitions), and P.C.C. and P.R.C. (compound and reverse curves);
- vertical: V.P.O.B. and V.P.O.E., P.V.I., P.V.C., and P.V.T.

Once generated, the key points are updated whenever the alignment is edited. Use
**Regenerate Key Points** to rebuild them, or the cross to remove them.

Reviewing an alignment
----------------------

The **Alignment Segments** panel lists the selected alignment's segments. Choose an alignment from
the list at the top, or select it in the viewport.

- **Horizontal** rows show each segment's type, length, radius, bearing, and start Easting and
  Northing. The coordinates include the project's map conversion.
- **Vertical** rows show each segment's type, horizontal length, grades in and out, and start
  distance along and elevation.
- **Cant** rows show each segment's type, length, and the cant of the left and right rails at its
  start and end, multiplied by 1000 (millimetres in a project in metres).

Click a segment's number to highlight the segment. A horizontal segment is highlighted in the 3D
viewport, with its start and end points, length, radius, PI, and center shown, together with its
tangent and radial lines. Vertical and cant segments are highlighted in the profile view. The text
icon on each layout's row turns the segment labels on or off.

Deleting
--------

- The trash icon on a layout's row deletes that layout. Layouts are deleted from the top down: a
  cant layout first, then its vertical, then the horizontal.
- The trash icon next to the draw tools deletes the whole alignment.

Importing an alignment from a CSV file
--------------------------------------

Use **File > Import > Alignment (.csv)** to create an alignment from PI data in a CSV file. The file
has one row for the horizontal alignment, followed by zero or more rows for vertical alignments:

.. csv-table:: Alignment by PI Method

   "X1","Y1","R1","X2","Y2","R2","...,","Xn-1","Yn-1","Rn-1","Xn","Yn","Rn"
   "D1","Z1","L1","D2","Z2","L2","...,","Dn-1","Zn-1","Ln-1","Dn","Zn","Ln"
   "D1","Z1","L1","D2","Z2","L2","...,","Dn-1","Zn-1","Ln-1","Dn","Zn","Ln"

where:

- Xi,Yi are the horizontal alignment PI points. X1,Y1 is the point of beginning (POB), and Xn,Yn is
  the point of ending (POE).
- Ri are the horizontal curve radii.
- Di,Zi are the vertical alignment PI points, as distance along and elevation.
- Li are the horizontal lengths of the parabolic vertical curves.

R1 and Rn, as well as L1 and Ln, are placeholder values and should be set to 0.0. The horizontal
row needs at least three points.

Alignments with a single horizontal layout and zero or one vertical layout are modeled per `IFC Concept Template 4.1.4.4.1.1, Alignment Layout - Horizontal, Vertical, and Cant, <https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/Alignment_Layout_-_Horizontal,_Vertical_and_Cant/content.html>`_. Alignments with multiple vertical layouts are modeled per `IFC Concept Template 4.1.4.4.1.2, Alignment Layout - Reusing Horizontal Layout, <https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/Alignment_Layout_-_Reusing_Horizontal_Layout/content.html>`_.

Example based on the `FHWA Bridge Geometry Manual <https://www.fhwa.dot.gov/bridge/pubs/hif22034.pdf>`_:

.. code-block:: text

   500,2500,0.0,3340,660,1000,4340,5000,1250,7600,4560,950,8480,2010,0
   0,100,0,2000,135,1600,5000,105,1200,7400,153,2000,9800,105,800,12800,90,0

Scripting
---------

Everything above is also available from Python through ``ifcopenshell.api.alignment``, for
example ``create_by_pi_method``, ``create_as_polyline``, ``create_as_offset_curve``, and
``add_stationing_referent``. See the IfcOpenShell API documentation for details and examples.
