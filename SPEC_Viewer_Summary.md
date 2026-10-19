# SPEC_Viewer.md — Summary

Local working document (do not commit as-is unless decided otherwise). Condensed
view of `SPEC_Viewer.md`, which remains the reference.

## General layout

- New **« Display » ribbon tab**, plus a synced **« Display Tools » dock
  panel** under Properties; both surfaces share one button factory and stay
  synchronised.
- Single-line layout: ZOOM + BOX at the left, SECTION + COLOR mid-left,
  DISPLAY centred; compact buttons (16 px icon, reduced font), hover tooltip
  on every button.
- Custom tool cursors (knife for the section, set square for the perpendicular
  view) revert to selection after use.

## Section (section cuts)

Cut the model with one or several planes, control their visibility and effect,
and move or delete them directly in the viewport. Planes are created by
clicking a surface and can coexist; all cuts apply simultaneously.

- **Add Section** — single-shot tool: click a surface to drop a plane
  perpendicular to its normal, keeping the side the normal points to; the
  tool then deactivates.
- **Remove Sections** — deletes every section plane in the view, whether
  shown, hidden or suspended.
- **Hide Planes** — toggle that hides the plane gizmos while the cuts stay
  active.
- **Suspend Sections** — toggle that stops the cuts and hides the planes;
  resuming re-shows the planes and reactivates the cuts.
- **Move a plane** — drag its gizmo to slide the plane along its normal axis,
  advancing or pulling back the cut depth.
- **Delete one plane** — right-click a plane gizmo and choose « Delete plane ».

## Colour

Change the appearance of the selected elements, with colour and opacity as two
independent settings. Both reset on model reload and override Clash Filter
colouring until a new clash run.

- **Paint** — opens a colour dialog and colours every selected element on OK.
- **Remove Color** — restores each element's original baked colour, keeping
  its transparency.
- **Transparency** — opens a preset dialog (100 / 75 / 50 / 25 % opacity);
  100 % restores the original opacity.

## Box

A temporary set of objects with three save slots, used to isolate or hide
groups quickly. The current box and the slots live for the session only and
are purged when a model closes.

- **Selection → Box** — replaces the current box with the selection.
- **Add to Box** — adds the selected elements to the current box.
- **Remove from Box** — removes the selected elements from the current box.
- **Isolate Box** — isolates the view on the current box objects.
- **Hide Box** — hides the current box objects in the active view.
- **Box Storage** — dropdown to save the current box to slot 1-3, or isolate
  the view on a saved slot without touching the current box.

## Display

Control element visibility globally and per IFC category. A disabled category
can **never** be shown while the deactivation is active, whatever the path
(selection, isolations, search, Show All).

- **Show Selection** — shows the selected elements.
- **Hide Selection** — hides the selected elements.
- **Show All** — shows everything, then re-applies the category filters.
- **Categories (menu)** — « Show / Hide » toggles for Walls, Slabs, Roofs,
  Ceilings, Spaces, Openings (immediate, temporary effect); « Enable / Disable
  (session) » toggles for Spaces and Openings only (disabled by default,
  durable for the session, applied at every model load).

## Zoom

Frame the visible objects and aim the camera at a picked surface. Both
commands work on the **visible** elements, so a fit after an isolation zooms
in on the isolated objects.

- **Fit View** — frames the visible objects; pop-ups warn about an empty
  view or objects farther than 200 m from the camera plane.
- **Perpendicular View** — one-shot tool: click a surface to look along
  −normal at it, then the view fits the visible objects.

## Search

Find objects by their parameters and isolate the view on the hits. The search
reads the loaded IFC models directly (no Python engine) and is case-insensitive
by default, matching by substring.

- **Fields (default)** — Name, Long Name, GUID, IFC class name, predefined
  type, storey name and long name, materials, model name.
- **Run** — Enter or the magnifier button isolates the view on the results;
  a « No results » popup leaves the view unchanged; « Show All » restores.
- **Prefixes** — `-fs` all properties, `-v` visible objects only, `-p`
  current box only, `-prop "Set.Name"` one property, `-c` case-sensitive;
  combinable before the search text.
