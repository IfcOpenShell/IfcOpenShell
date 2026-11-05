# defer-type-preview-jobs

Branch: `defer-type-preview-jobs` (off `v0.9.0`)

## Problem

`Object.asset_generate_preview()` queues a **threaded** icon render job. Philipp Oeser
diagnosed this on blender/blender#105325 (comment 893982): "`ED_asset_generate_preview` calls
`UI_icon_render_id` as a job, whereas `previews_id_ensure` doesnt". That job calls
`DEG_graph_build_from_view_layer()` on a worker thread.

`Model.update_thumbnail_for_element` called it synchronously, once per type on the current Type
Manager page. Because `bim.load_type_thumbnails` is also fired from property update callbacks
(`update_ifc_class`, `update_type_page`, `update_search_name`), and thumbnails are invalidated
by `mark_thumbnail_for_update` after every parametric edit, this ran repeatedly during ordinary
modelling — not only when the Type Manager was opened. The jobs then walked objects, meshes and
materials that the main thread was in the middle of rebuilding.

Three crashes on this machine, two Blender versions, two projects:

| # | Blender | Crash site | Fault |
|---|---------|------------|-------|
| 1 | 5.2.1 | `TreeDisplayViewLayer::add_layer_collections_recursive` (outliner redraw) | read `0x10`, null `Collection` |
| 2 | 5.2.1 | `BKE_base_is_visible` via `context.selected_objects` from a viewport draw handler | read `0x26`, garbage `Base` |
| 3 | 5.1.2 | `DepsgraphNodeBuilder::build_materials` ← `object_preview_render` ← `icon_preview_startjob_all_sizes` ← `do_job_thread` | read `0x0` |

Crash 3 is the only conclusive one — it died *inside* the preview job, on the job thread. 1 and
2 are consistent with the same race (`BKE_layer_collection_sync` rebuilds both
`layer_collections` and `object_bases`, and each crash is a main-thread consumer walking one of
those halves) but are not proof.

## Decision

Queue the renders and start them one at a time, only once the scene has settled:

- `PREVIEW_IDLE_SECONDS = 0.5`, a pending list, and a `bpy.app.timers` drain in `tool/model.py`.
- `note_scene_change` registered on `depsgraph_update_post` so "settled" tracks real scene
  mutation rather than a fixed delay.
- The queue holds **object names, not `Object` references** — the objects can be freed before
  the drain runs, and a stale `bpy_struct` would raise `ReferenceError` (or worse).

Rejected alternatives:

- **Delete the `asset_generate_preview()` call.** Tempting, since `preview_ensure()` is the safe
  non-threaded path and is already called just above. But `preview_ensure()` only *allocates*
  the preview; `asset_generate_preview()` queues the render that actually draws thumbnails for
  objects with mesh data. Deleting it loses those thumbnails. `c333535ae5` (fixing #6839 /
  blender/blender#140903) deliberately kept it when it added `preview_ensure()`.
- **Gate on the Type Manager being open.** Doesn't fix it — the thumbnails also appear in the
  workspace tool panel and the relating-type dropdown, which are visible while authoring.
- **Cancel in-flight jobs on scene change**, which is what Blender does internally for material
  previews. No Python binding for it.

## Known limitation

This **narrows** the race, it does not close it. Nothing stops the user authoring 10 ms after a
job starts. Closing it properly needs an upstream change — either `object_preview_render`
building its depsgraph on the main thread, or the job being stopped on data changes the way
material preview is. A Blender report is planned.

`bpy.app.is_job_running("RENDER_PREVIEW")` would be the obvious guard but, per the existing
comment in `LoadTypeThumbnails.execute`, it does not reflect asset preview generation.

## Gotcha for anyone touching this

`import bonsai.tool.model` **cannot** go at module scope in `bim/__init__.py`. It pulls in
`bonsai.tool` → `tool.debug` → `bim.ifc` → `bim.handler` → `from bonsai.bim.ifc import IfcStore`
while `bim.ifc` is still initialising, and add-on registration fails outright with
`ImportError: cannot import name 'IfcStore' from partially initialized module`. The
`bim.ifc`/`bim.handler` cycle is pre-existing; this import just exposes it. Import inside
`register()`/`unregister()` instead.

Also note `hasattr(bpy.ops.bim, "<op>")` returns `True` even when registration has failed,
because `bpy.ops` resolves lazily. Check something real like
`hasattr(bpy.types.Scene, "BIMProperties")`.

## Testing

Verified headless in Blender 5.1 (`--background`, no `--factory-startup`):

- Bonsai registers; `BIMProperties` and `BIMModelProperties` both present; no circular imports.
- `note_scene_change` present in `depsgraph_update_post`; `tool.model.__file__` resolves into
  the repo via the site-packages symlink.
- Queue defers while the scene is changing and drains once settled.
- `test/tool/test_model.py`: 4 failed, 30 passed — identical to pristine `HEAD` on this machine.
  The four `TestApplyIfcMaterialChanges` failures are environmental: their `setup_test()` sets
  `unit_settings.length_unit = "MILLIMETERS"`, which does not exist because the local homefile
  is Imperial. Pinning `system = "METRIC"` beforehand does not help — a test earlier in the run
  reloads the homefile.

Not covered by automated tests: the deferral is timer- and UI-driven, so the real check is
days of authoring without a crash. `BONSAI_NO_PREVIEW`-style bisecting was used to confirm the
preview path before this fix.

## Still to do

- [ ] File the Bonsai issue and link it here.
- [ ] File the Blender issue for the underlying threaded-depsgraph race.
- [ ] Consider whether `LoadTypeThumbnails` should also stop being fired from property update
      callbacks, which is what makes this run so often in the first place.
