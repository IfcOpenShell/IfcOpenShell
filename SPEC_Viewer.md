# SPEC_Viewer.md — Viewer display tools

Specification of the BonsaiViewer display tools: section, colour, box,
display, zoom, search bar. Local working document (do not commit as-is
unless decided otherwise). This document describes the implementation as it
exists in the code.

## Scope and conventions

- All these functions are **viewer-side only**: no exchange with the Python
  engine, no change to `SPEC_Engine_Interface.md`.
- Interface labels are in **English** (decided), like the rest of the viewer.
  This spec quotes them between « ».
- The buttons live in a **new ribbon tab** (decided name: « Display »), on
  **a single line**: ZOOM + BOX flush at the left edge, SECTION + COLOR
  centred between them and the centre, DISPLAY centred in the band's
  remaining space. The buttons are **compact** (16 px icon, reduced font)
  so they fit on the line.
- The same functions are also available in a **« Display Tools » dock
  panel**, placed under the Properties panel (stacked vertically, not
  tabbed), with a visibility toggle in the Panels tab. Ribbon and panel
  share one button factory and stay **synchronised** (section and category
  toggle states).
- The search bar sits in the **left corner of the ribbon band**, on every
  tab, vertically centred within its area (224 px wide).
- One button = `makeButton` (compact variant available) + `makeButtonGroup`
  + an SVG icon in `icons/`.
- **Every button and the search bar carry a tooltip** (hover) describing its
  function; the Categories menu actions show their IFC mapping as tooltip.
- **Toggle buttons** (« Hide Planes », « Suspend Sections »): the active
  state is visible on the button (checkable button).
- Custom tool cursors: « knife » for the section, « set square » for the
  perpendicular view. After use, the cursor returns to its original shape
  and selection function.

# SECTION (section cuts)

## « Add Section » — add a section plane
Clicking « Add Section » turns the cursor into a small knife.
The tool is **single-shot**: on the next left-click on a surface, the
surface normal at the picked point is retrieved (viewport picking), a
section plane is produced through the picked point, perpendicular to the
surface normal, then **the tool deactivates** and the cursor returns to its
original selection shape and function.

Kept half-space: the side **pointed at by the normal** is kept, the opposite
side is cut away.

Several section planes can coexist; all cuts apply simultaneously. (The
historical « Section » tool in the Navigate tab and the K key remain
available in multi-plane mode.)

## « Remove Sections » — remove the planes
This function removes every section plane present in the view. Cuts are
deleted whether they are hidden, suspended or shown.

## « Hide Planes » — hide the planes
This toggle button hides the section plane objects. The cut still applies,
but the planes are no longer visible.
It applies to **all planes** at once. First click hides the planes; second
click shows them again.

## « Suspend Sections » — suspend the cuts
This toggle button suspends the cuts: the planes are hidden and the cutting
effect is stopped. It applies to all planes at once.
On the second click the planes are shown again and the cuts reactivated —
even if the planes had been hidden before suspension.

Difference with « Hide Planes »: suspending stops the cutting effect;
hiding keeps the cut active without showing the plane.

## Moving a section plane
A plane can be translated by clicking its gizmo (the plane arrow — so the
plane must be visible, neither hidden nor suspended) and holding the button.
The drag moves the plane **only along its normal axis**, pushing the cut
depth forward or backward. This works whenever a plane is visible, whether
the « Add Section » tool is armed or not. Del removes the selected plane
(requires the Section tool to be armed); Esc disarms the tool.

**Right-click on a plane gizmo** opens a context menu with one action,
« Delete plane », which removes that specific plane (works whenever the
planes are visible).

# COLOR (colouring)

## « Paint » — colour the selected elements
Clicking « Paint » opens a colour selection dialog.
Clicking OK colours every selected element with that colour.

## « Remove Color » — remove the colour
Each element concerned **gets its original colour back** (the one baked at
load from the IFC model). Transparency, if any, is kept (the two settings
are independent).

## « Transparency » — transparency of the selected elements
Clicking « Transparency » opens a dialog to choose the transparency to
apply. Choice by **presets** (decided: 100 % / 75 % / 50 % / 25 % opacity).
Clicking OK changes the transparency of every selected element. The 100 %
(opaque) preset is equivalent to removing the transparency and restores the
original opacity.

Colour and transparency are **independent**: changing one does not cancel
the other. A transparency applied alone keeps the element's original colour
(implementation: "alpha-only" sentinel on the instance override).

## Persistence and Clash Filter interaction
On a model reload, the manual colour and transparency are **reset** (the
elements get their original appearance back).

Interaction with the Clash Filter colouring: manual colouring **overrides**
the clash red/orange; a new clash run recolours the concerned objects.

# BOX (box)

One group of functions gathers the following. The single concept is the
**box**: a temporary set of objects. There is one **current box** and three
memory slots.

## « Selection → Box » — the selection becomes the current box
The content of the current box is replaced by the selected elements.

## « Add to Box » — add the selection
The selected elements are added to the current box.

## « Remove from Box » — remove the selection
The selected elements are removed from the current box.

## « Isolate Box » — show only the current box
Isolates the view on the current box objects (hides everything, then shows
the box). Members of a disabled category are never shown (see the DISPLAY
rule).

## « Hide Box » — hide the current box
Hides the current box objects in the active view.

## « Box Storage » — box storage
Clicking the button opens a dropdown with the 6 following items:

1. Save Box to Slot 1
2. Show Box 1
3. Save Box to Slot 2
4. Show Box 2
5. Save Box to Slot 3
6. Show Box 3

« Save Box to Slot N » copies the content of the current box into slot N
(overwriting it if occupied).

« Show Box N » **isolates the view** on the objects saved in slot N, without
touching the current box.

Lifetime: the slots only live for the **current session**; they are lost
when the viewer closes.

Closing a model: the objects of the closed model are **removed** from the
current box and slots 1 to 3 (purged as soon as the model list changes).

# DISPLAY (display)

Buttons: « Show Selection », « Hide Selection », « Show All ».
("Hide All" was removed — decided.)

## « Categories » menu (dropdown)
The per-category filters are grouped in a **dropdown menu** on the
« Categories » button (infrequent actions, to minimise the ribbon width).
The menu has two sections:

- **Show / Hide** (immediate, temporary visual effect): Walls, Slabs, Roofs,
  Ceilings, Spaces, Openings.
- **Enable / Disable (session)** (durable toggle for the current session,
  not persisted across sessions, applied at every model load): Spaces,
  Openings. Both start **disabled by default** (hidden at every model load
  until enabled). Toggling Enable/Disable only touches the affected
  category — it never re-shows elements hidden by other means (isolation,
  Hide Selection, …).

### IFC mapping

| Label | IFC category |
|---|---|
| Walls | `IfcWall` (subtypes included, hence `IfcWallStandardCase`) |
| Slabs | `IfcSlab` |
| Roofs | `IfcRoof` |
| Ceilings | `IfcCovering` with predefined type `CEILING` (`PredefinedType` attribute in IFC4+, `CoveringType` in IFC2x3) |
| Spaces | `IfcSpace` |
| Openings | `IfcOpeningElement` |

Scope: the filters apply to every loaded model.

### "Never shown while disabled" rule
A **disabled** category (Enable/Disable) can **never** be shown while the
deactivation is active, whatever the path: « Show Selection », box
isolations (slots included), search results, « Show All » — including the
Inspect tab's « Show All » and the Alt+H shortcut, which re-apply the
category filters after any global show.

# ZOOM

## « Fit View » — fit the active view
On click, the camera frames the **visible objects** (union of the AABBs of
the non-hidden elements — not the whole-scene box): after an isolation, the
zoom tightens on the isolated objects.

If no visible object is present, a popup opens:
« The active view is empty. »

After positioning, the viewer looks for a single visible object within
200 m of the camera plane (it can stop at the first one).
If it finds at least one, there is nothing to do.
If it finds none, an informational popup is shown: « The objects are far
away. » The view stays fitted as is, with no automatic action.

## « Perpendicular View » — perpendicular view
Clicking the button turns the cursor into a set square.
On the first **left-click** on a surface, the normal is retrieved.
The view plane becomes perpendicular to the normal, the camera looking along
−normal (opposite to the normal) toward the clicked surface, the target
staying on the picked point.
Then the viewer fits the zoom on the **visible objects** (same framing
distance as « Fit View »).
The function then deactivates (Esc cancels) and the cursor returns to its
original shape.

# SEARCH BAR

A search bar is placed in the left corner of the ribbon band (placeholder
« Search… », 224 px wide), visible on every tab, vertically centred within
its area. It searches
the BIM object parameters, for simple and fast queries. For more complex
queries, prefixes are available.

A small magnifier button sits at the right of the bar. Clicking it runs the
search. The Enter key also triggers the search.

**Result**: the view is **isolated** on the found objects (like « Isolate
Box »). If nothing is found, a « No results » popup is shown and the view is
unchanged. To return to the full display, the user clicks « Show All » (no
dedicated button in the search bar).

Objects of a **disabled category** are excluded from the results (the
announced count matches what will actually be isolated), as soon as their
model's live IFC source is available.

**Data**: the search reads the data of the IFC models already loaded by the
viewer (live IFC source through the SceneLoader) — nothing goes through the
Python engine. For a model without a live IFC source, only the element name,
GUID, class name and the model name are searched.

## Default behaviour
By default the search is case-insensitive. The searched value does not need
to equal the parameter value: the string only needs to be present in the
value (substring search).

Without a prefix, the search covers the following fields (only these, to
keep the search light):

- Name
- Long Name
- GUID
- IFC class name (e.g. `IfcWall`)
- Predefined type (`PredefinedType`, with fallback to the associated
  element type and `ObjectType`)
- Name of the `IfcBuildingStorey` the element is contained in
- Long Name of that storey
- Materials (through `IfcRelAssociatesMaterial`, material names including
  the materials of a layer set's layers)
- Model name

## Prefixes
Prefixes are written **before the search text**, separated by spaces, and
can be combined. Example: `-c -v béton` searches "béton" case-sensitively
within the active view.

| Prefix | Effect |
|---|---|
| `-fs` | Full search: the search extends to all object properties (property set names, property names and values) |
| `-v` | Restricts the search to the objects visible in the active view (approximation: element-level hidden objects; a fully hidden model is not filtered out) |
| `-p` | Restricts the search to the current box |
| `-prop <name>` | Restricts the search to one specific property, in the `Set.Name` format (e.g. `-prop Pset_Walls.General béton` searches only inside that property; without a dot, the property is searched in every set). If the name contains a space, write it **between quotes**: `-prop "Pset Murs" béton` |
| `-c` | Case-sensitive |

# Decisions made

- Interface labels are in **English**; the ribbon tab is named **« Display »**.
- **Compact buttons on a single line** (16 px icon, reduced font), tooltips
  on every button and the search bar.
- A **« Display Tools » dock panel** under Properties duplicates the same
  functions, synchronised with the ribbon.
- The per-category filters live in a **« Categories » dropdown menu**
  (infrequent actions).
- Mapping decided: Walls = `IfcWall` + subtypes; Ceilings = `IfcCovering`
  with `CEILING` type (`PredefinedType`/`CoveringType` depending on the
  schema); Openings = `IfcOpeningElement`.
- **A disabled category can never be shown** while the deactivation is
  active (every display path).
- A **right-click on a section-plane gizmo** opens a context menu with
  « Delete plane », removing that specific plane.
- « Fit View » frames the **visible objects** (not the whole scene); popups
  « The active view is empty. » and « The objects are far away. »;
  « No results » for the search.
- Transparency presets: **100 / 75 / 50 / 25 %** opacity.
- Enable/Disable spaces and openings: **current-session-only** toggle (not
  persisted across sessions); both are **disabled by default** and the
  toggle only affects its own category (no global re-show).
- Search: **Enter triggers the search**; return to the full display via
  **« Show All »**; `-prop` accepts quoted names; by default the search also
  covers **GUID, class name and predefined type**.
- On a model reload, the manual colour/transparency are **reset**; manual
  colouring overrides the Clash Filter red/orange, a new clash run recolours.
- On model close, its objects are **removed** from the current box and
  slots 1 to 3.
