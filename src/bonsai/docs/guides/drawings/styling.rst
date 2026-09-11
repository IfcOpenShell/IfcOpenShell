Styling drawings with stylesheets
==================================

Every 2D drawing Bonsai produces is an SVG file, and every SVG file is styled
by a CSS stylesheet, the same technology that styles web pages. This means
you can change how your drawings look, heavier walls, dashed hidden lines,
grey background elements, larger dimension text, without touching the 3D
model at all. You do not need to know CSS to use this page: copy the
recipes below, or start from one of the ready-made files in
``bonsai/bim/data/assets/``.

This page assumes you already know how to create a drawing (see
:doc:`index`). It does not require Inkscape, Blender scripting, or any
programming experience.

.. contents::
   :local:
   :depth: 1

What the stylesheet is
-----------------------

Bonsai's built-in stylesheet lives at
``bonsai/bim/data/assets/default.css``, inside the add-on. It is a plain
text file of rules like:

.. code-block:: css

   .cut { fill: black; stroke: black; stroke-width: 0.35; }

Each rule says: "elements tagged with this class should look like this".
When Bonsai draws your walls, dimensions, grids and text, it tags every
shape in the SVG with one or more classes describing what it is, whether
it is a cut or a projection, what kind of annotation it is, what material
it represents, and so on. The stylesheet is what turns those tags into
actual colours, line weights and dash patterns.

Where the setting lives
------------------------

Every drawing has a **Stylesheet** setting: a comma-separated list of file
paths. When a new drawing is created, Bonsai fills this setting in from one
of two places, in this order:

1. **Project setting.** A property called ``StylesheetPath`` inside a
   property set called ``BBIM_Documentation`` on the ``IfcProject``. This
   pset is not built in by default, you add it yourself: select the
   project (or any element that lets you reach the Property Sets tab),
   add a property set named ``BBIM_Documentation``, and add a text
   property called ``StylesheetPath``.
2. **Add-on preferences.** If the project setting is not present, Bonsai
   falls back to *Edit > Preferences > Add-ons > Bonsai > Drawing >
   Default Stylesheet*.

.. important::

   These two settings only decide the stylesheet for **drawings you
   create from now on**. They are copied onto the drawing once, at
   creation time. Changing either setting later does not change drawings
   that already exist.

   To change the stylesheet path of a drawing you already created, select
   that drawing in the *Drawings* list (Scene Properties > Drawings tab),
   open its Property Sets, and edit the ``Stylesheet`` property inside
   ``EPset_Drawing`` directly.

The contents of the CSS file(s) themselves are **not** copied anywhere.
Bonsai reads them fresh every time it regenerates the drawing, so editing
a stylesheet file and regenerating the drawing is enough, you never need
to touch the pset again just to see a styling change.

The override pattern
---------------------

**Do not edit** ``default.css``. It ships with the add-on, so an update to
Bonsai can silently overwrite your changes, and every project sharing that
install would be affected. Instead, write your own small file with just the
rules you want to change, and list it *after* ``default.css`` in the
Stylesheet setting.

Bonsai loads each file in the list in order and appends its rules to the
drawing, one after another. This means normal CSS cascade rules apply:
when two files set the same property on the same class, **the file that
was loaded later wins**. A one-line file that only touches
``stroke-width`` leaves everything else, colours, dashes, fonts, exactly
as ``default.css`` defined it.

Worked example: say you want heavier cut lines project-wide. Create a file
``my-office.css`` next to your project, with just:

.. code-block:: css

   .cut { stroke-width: 0.5; }

Then set the Stylesheet setting (project pset or add-on preferences) to:

.. code-block:: text

   C:\path\to\default.css, C:\path\to\my-office.css

or on macOS/Linux:

.. code-block:: text

   /path/to/default.css, /path/to/my-office.css

Every other rule in ``default.css`` still applies. Only the stroke width
of cut elements changes.

This behaviour was verified directly: a two-file stylesheet list, split on
the comma and loaded in order, produces a drawing where the second file's
rule visibly overrides the first for the property it sets, while any
property the second file does not mention is inherited from the first.

Three ready-to-use starting points ship alongside ``default.css`` in
``bonsai/bim/data/assets/``:

- ``override-heavy-lineweight.css``, thicker lines for drawings that need
  to read clearly from a distance or when printed small.
- ``override-fine-lineweight.css``, finer lines for dense, detailed
  drawings.
- ``override-presentation-greys.css``, greys out background and
  projection geometry so cut elements stand out, useful for client-facing
  presentation drawings.

Copy whichever one is closest to what you want, add it after
``default.css`` in your Stylesheet setting, and edit it to taste.

Class reference
----------------

This reference was generated by reading ``default.css`` directly and
cross-checking every selector against where Bonsai actually emits that
class in the drawing code, so it should not drift from what the software
does. All stroke widths below are in millimetres (see `Units`_).

Geometry (cut, projection, surface)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Selector
     - Controls
   * - ``.cut``
     - Elements sliced by the drawing's cut plane, for example a wall in
       plan, or a slab in section. This is usually the heaviest line
       weight in a drawing.
   * - ``.projection``
     - Elements seen beyond the cut plane but not cut by it, for example
       a wall visible through a doorway.
   * - ``.surface``
     - Flat surface fills (used for some annotation fills).

Edge classification
^^^^^^^^^^^^^^^^^^^^

These apply directly to individual ``<path>`` edges based on how sharp or
significant that edge is in the 3D geometry (see the edge classification
notes in ``default.css``). Because they target the ``<path>`` element
itself, they take priority over the more general ``.projection`` rule
above regardless of which loads first.

.. list-table::
   :header-rows: 1

   * - Selector
     - Controls
   * - ``path.outline``
     - The silhouette edge of an object, its outer boundary as seen from
       the camera. Drawn heaviest of the four.
   * - ``path.boundary``
     - A strong edge between two clearly different faces (for example
       where a wall meets a roof).
   * - ``path.crease``
     - A moderate edge, a visible but softer change in surface direction.
   * - ``path.sharp``
     - A minor edge, a small but real change in direction.
   * - ``path.flush``
     - An edge between two faces that are nearly coplanar. Drawn
       lightest, often barely visible.

Line weights
^^^^^^^^^^^^

These only apply to plain linework annotations (``PredefinedType`` of
``LINEWORK``), and only take effect combined with that predefined type, so
the selector is always the pair together, for example
``.PredefinedType-LINEWORK.thick``. You choose which one applies to a
specific annotation object by adding the word (``fine``, ``dashed``, etc.)
to that object's ``EPset_Annotation`` > ``Classes`` property.

.. list-table::
   :header-rows: 1

   * - Selector
     - Stroke width
   * - ``.PredefinedType-LINEWORK.fine``
     - 0.18 mm (also greys the line to ``#777777``)
   * - ``.PredefinedType-LINEWORK.thin``
     - 0.25 mm (same as the LINEWORK default)
   * - ``.PredefinedType-LINEWORK.medium``
     - 0.35 mm
   * - ``.PredefinedType-LINEWORK.thick``
     - 0.5 mm
   * - ``.PredefinedType-LINEWORK.strong``
     - 1 mm
   * - ``.PredefinedType-LINEWORK.dashed``
     - no width change, switches the line to a dash pattern

Annotation predefined types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every annotation object has a "predefined type" (dimension, grid line,
section marker, and so on). Bonsai tags it in the SVG as
``PredefinedType-<TYPE>``. These are the ones ``default.css`` styles:

.. list-table::
   :header-rows: 1

   * - Selector
     - What it is
   * - ``.PredefinedType-LINEWORK``
     - Generic annotation linework (see line weights above).
   * - ``.PredefinedType-BACKGROUND``
     - Background reference linework, drawn faint by default.
   * - ``.PredefinedType-GRID``
     - Structural/setting-out grid lines.
   * - ``.PredefinedType-SECTION``
     - Section cut lines.
   * - ``.PredefinedType-SECTIONLEVEL``
     - Section level markers.
   * - ``.PredefinedType-PLANLEVEL``
     - Plan level markers.
   * - ``.PredefinedType-DIMENSION``
     - Dimension lines and their arrowheads.
   * - ``.PredefinedType-ANGLE``
     - Angle dimensions.
   * - ``.PredefinedType-RADIUS``
     - Radius dimensions.
   * - ``.PredefinedType-DIAMETER``
     - Diameter dimensions.
   * - ``.PredefinedType-FALL``, ``.PredefinedType-SLOPEANGLE``,
       ``.PredefinedType-SLOPEPERCENT``, ``.PredefinedType-SLOPEFRACTION``
     - Slope/fall callouts.
   * - ``.PredefinedType-STAIRARROW``
     - Stair up/down direction arrows.
   * - ``.PredefinedType-BOUNDARY``
     - Space/area boundary outlines.
   * - ``.PredefinedType-SEALANT``
     - Sealant/joint hatching.
   * - ``.PredefinedType-FILLAREA``
     - Filled area annotations (drawn first, underneath everything else).
   * - ``.PredefinedType-BREAKLINE``
     - Break lines (the zig-zag "this continues elsewhere" symbol).
   * - ``.PredefinedType-TEXT``
     - Plain annotation text.
   * - ``path.PredefinedType-TEXTLEADER`` /
       ``text.PredefinedType-TEXTLEADER``
     - Leader lines pointing from text to an element, and their text.

.. note::

   ``default.css`` also defines ``.PredefinedType-STUD``,
   ``.PredefinedType-WOOD``, ``.PredefinedType-STEEL``,
   ``.PredefinedType-CONCRETE`` and ``.PredefinedType-PLASTERBOARD``.
   These do not correspond to any value Bonsai currently emits for an
   annotation's predefined type, they appear to be dead rules left over
   from an earlier version of the styling system. Material hatching
   today goes through the ``.material-*`` and ``.PredefinedType-*``
   material-layer classes described below instead. Do not rely on these
   five selectors.

Text sizes
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Selector
     - Size
   * - ``text.small`` / ``tspan.small``
     - 1.8 mm
   * - ``text.regular`` / ``tspan.regular`` (the default if no size class
       is set)
     - 2.5 mm
   * - ``text.large`` / ``tspan.large``
     - 3.5 mm
   * - ``text.header`` / ``tspan.header``
     - 5 mm
   * - ``text.title`` / ``tspan.title``
     - 7 mm
   * - ``text.GRID`` / ``tspan.GRID``
     - 5 mm (grid bubble labels)

As with line weights, you choose the size by adding the word (``large``,
``header``, etc.) to the text object's ``EPset_Annotation`` > ``Classes``
property.

Materials
^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Selector
     - Controls
   * - ``.material-<name>``
     - The hatch/fill for an element whose IFC material (or material
       layer set) is named ``<name>``. ``default.css`` ships rules for
       ``blank``, ``diagonal1``/``2``/``3``, ``crosshatch1``/``2``/``3``,
       ``brick``, ``earth``, ``glass``, ``liquid``, ``grass``,
       ``honeycomb``, ``sand`` and ``concrete``, matched to a same-named
       pattern in ``patterns.svg``. See `Case sensitivity of material
       names`_ below, matching is exact and case-sensitive.
   * - ``.IfcSpace``
     - IfcSpace elements: no fill, no stroke, by default (invisible
       unless you override it). This is an example of selecting directly
       by IFC class rather than by annotation type.

.. note::

   The actual fallback class Bonsai writes when an element has no
   material at all is ``material-null``, which has no matching rule in
   ``default.css`` (so it falls back to whatever ``.cut``/``.projection``
   already set). ``default.css`` separately defines a ``.material-blank``
   rule, but nothing in the code currently emits a class called
   ``blank``, so that rule is presently unreachable too.

You are not limited to the names above. If you name an IFC material
"Marble", Bonsai will tag the element ``material-marble`` (see `Case
sensitivity of material names`_), and you can add your own
``.material-marble`` rule in an override file pointing at any pattern in
``patterns.svg`` (which has more patterns defined than ``default.css``
uses, including ``wood``, ``steel``, several ``tile`` and ``board``
variants) or a plain colour.

Units
------

**Stroke widths** (``stroke-width``, used on lines and outlines) are
already in millimetres of the printed drawing. A wall drawn with
``stroke-width: 0.35`` prints as a 0.35 mm line regardless of the
drawing's scale, this is standard technical drawing practice, where line
weight communicates meaning (cut vs projection) rather than a literal
model dimension.

**Font sizes** (``font-size``) are written in CSS pixels, but a pixel
here does not mean a pixel on your screen or a millimetre. Bonsai bakes a
fixed conversion factor (about 1.65) into ``default.css`` so that a given
class always prints at the same physical text height. ``default.css``
documents this in a comment on every text rule, so you never need to
calculate it yourself: pick a size from the table below, or, if you want
a size in between, multiply your target millimetre height by 1.65 to get
the ``font-size`` value.

.. list-table::
   :header-rows: 1

   * - Millimetres on paper
     - ``font-size``
   * - 1.8 mm
     - 2.97px
   * - 2.5 mm
     - 4.13px
   * - 3.5 mm
     - 5.78px
   * - 5 mm
     - 8.25px
   * - 7 mm
     - 11.55px

Recipes
--------

Each recipe below is a complete override file. Save it as its own
``.css`` file and add it after ``default.css`` in the Stylesheet setting,
following `The override pattern`_ above. You can combine several
recipes in one file.

Heavier cut lines
^^^^^^^^^^^^^^^^^^

Make walls and other cut elements stand out more in plan and section.
Ships as ``override-heavy-lineweight.css``.

.. code-block:: css

   .cut { stroke-width: 0.5; }

Grey out background elements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Push projected (uncut) geometry visually behind the cut plane. Ships as
part of ``override-presentation-greys.css``.

.. code-block:: css

   .projection { stroke: #808080; }

Dashed hidden lines
^^^^^^^^^^^^^^^^^^^^

If you have annotation linework marked as hidden/dashed via its
``EPset_Annotation`` > ``Classes`` property (add the word ``dashed``),
you can change the dash pattern itself:

.. code-block:: css

   .PredefinedType-LINEWORK.dashed { stroke-dasharray: 6, 3; }

Larger dimension text
^^^^^^^^^^^^^^^^^^^^^^

Dimension values use whatever text size class is set on that annotation.
To make all "regular" sized text a little bigger without touching every
individual annotation:

.. code-block:: css

   text.regular, tspan.regular { font-size: 4.95px; } /* 3mm */

A different hatch on concrete
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default concrete hatch is a stipple pattern. Swap it for a diagonal
hatch instead (remember the material name match is case-sensitive, see
below):

.. code-block:: css

   .material-concrete { fill: url(#diagonal2); }

Hiding a category
^^^^^^^^^^^^^^^^^^

Hide all IfcSpace boundary annotations from a drawing without deleting
them from the model:

.. code-block:: css

   .PredefinedType-BOUNDARY { display: none; }

Troubleshooting
-----------------

A rule I added does nothing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A typo in a class name (a missing dot, wrong capitalisation, wrong dash)
does not raise an error, CSS silently ignores any selector that matches
nothing. Check the class reference above for the exact spelling, and
confirm the class exists in the drawing by opening the SVG in a text
editor and searching for ``class="`` near the element you are trying to
style.

Case sensitivity of material names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

IFC material names are converted to a class name (``material-<name>``)
by removing spaces and punctuation only; letters are not lowercased. A
material named ``Concrete`` becomes ``material-Concrete``, not
``material-concrete``, so it will not match ``default.css``'s built-in
``.material-concrete`` rule. Either name your materials in lowercase, or
write your override rule with the exact capitalisation of your material
name.

Nothing in my stylesheet applies, and the console shows a warning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a path in the Stylesheet setting does not exist on disk, Bonsai prints
``WARNING. Couldn't find stylesheet for the drawing by the path: ...`` to
the console and simply skips that file, it does not stop the drawing from
generating. Open Blender's system console (*Window > Toggle System
Console* on Windows, or run Blender from a terminal on macOS/Linux) before
regenerating the drawing to see this warning.

I changed the Stylesheet setting but nothing changed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Remember the project/preferences setting only applies to *new* drawings.
For drawings that already exist, edit that drawing's own
``EPset_Drawing`` > ``Stylesheet`` property (see `Where the setting
lives`_), then regenerate the drawing.

My override loads but a whole default rule seems to disappear
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You are probably repeating every property from a ``default.css`` rule
instead of only the ones you want to change. Keep your override files
short, list only the properties you actually want to change, and let
everything else fall through from ``default.css``.
