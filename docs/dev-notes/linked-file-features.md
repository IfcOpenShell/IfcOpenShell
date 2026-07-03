<!-- This file was generated with the assistance of an AI coding tool. -->

# Linked file features — queries, styles, transforms, and multi-linking for linked IFC models

> **Living dev note** for the `Linked_File_Features` branch/PR. Read before working
> on the feature; append decisions and findings as the PR is refined. This is *not* user
> documentation — at merge it is removed or its durable parts promoted to code comments.
> See [README.md](README.md) for the convention (introduced on the
> `opening-template-on-type` branch; not yet on this branch's base).

## Problem

Linked IFC models (`bim.link_ifc`) had several gaps that made them hard to use as a
"reference in other trades' models" workflow:

- One shared `.ifc.cache.blend` per IFC file meant the **same file could not be linked
  twice with different selector queries** — both links showed whichever query was cached
  first in-session, and whichever was cached last after reopening (Blender reuses one
  library datablock per path).
- The selector query was not durably stored anywhere in the host IFC, so save → reopen
  lost or cross-wired the filter; a scripted `bpy.ops.bim.reload_link()` also wiped it.
- Linked geometry got **flat diffuse-only materials** — external `.blend` styles
  (`IfcExternallyDefinedSurfaceStyle`) and per-layer materials (layerset slicing) that
  the normal import applies were ignored.
- Moving a linked model required an explicit enable-edit → move → save dance on the
  active link only, with save/cancel buttons in the panel header.
- The Explore tool's highlight broke (GPU type errors), drew at the link's *original*
  location when the link had been moved, and `bim.append_inspected_linked_element`
  placed appended elements at the original location too.

## Key facts established

- **Cache architecture**: `LoadLink.link_ifc` generates a Python script and runs a
  background Blender subprocess that executes `bim.load_linked_project` and saves a
  `.ifc.cache.blend`. The host session then *links* (not appends) the `IfcProject/...`
  collection from that blend and instances it via an empty (the link "handle").
  Georeferencing metadata lives in a sidecar `.cache.json`; extracted properties in
  `.cache.sqlite` (whole file, query-independent — deliberately shared across queries).
- **Blender reuses an in-session library per path.** Loading the same blend path twice
  yields the same library/collection. This is what broke multi-query linking with a
  shared cache filename, and why per-query *filenames* (not cache invalidation) are the
  fix.
- **Last-used operator properties** are reused on the next *interactive* invocation
  (UI button), while scripted `bpy.ops` calls always start from defaults. LoadLink's
  internal `self.query = link.query` fallback assignment was remembered by Blender and
  leaked into the next button click (`operator_query='IfcWindow'` for the door link).
  Any `is_property_set()`-based logic is corrupted the same way. Fix: `SKIP_SAVE` on
  volatile props. **A GUI-only bug like this is invisible to scripted repro** — both
  headless and windowed `--python` test runs passed while the manual flow failed.
- **`IfcDocumentReference`** per link: attribute index 1 (`Identification`) already
  stores the link's 4×4 transformation (existing Bonsai convention). `Description`
  (IFC4+; **absent in IFC2X3**) now stores the selector query. One
  `IfcDocumentInformation` (Scope `LINKED_MODEL`) per file, one reference per link.
- **Geometry iterator materials**: `material.instance_id()` is the STEP id of the
  `IfcSurfaceStyle` — or of an `IfcMaterial` when the item has a material but no style,
  hence the `is_a("IfcSurfaceStyle")` guard when resolving external styles.
- **External styles**: `IfcExternallyDefinedSurfaceStyle.Location` (`.blend`, relative
  paths resolve against the *linked* IFC, not the host) + `Identification` in
  `data_block_type/name` form (e.g. `materials/Brick`), same convention as
  `bim.activate_external_style`.
- **Chunk pipeline dedups materials by RGBA color** (`np.unique` on a color array), so
  style identity must ride along as an extra column to survive — added only for styles
  that actually resolve to an external material, so plain colored styles dedupe exactly
  as before.
- **`slice_layerset_mesh` needs a local-space, per-element mesh** (bisect planes are in
  object space), which the chunk path can't provide (world-space, many elements per
  mesh) — hence routing multi-layer elements through the instanced path. Its
  `dissolve_limit` produces **ngons**, which broke the Explore highlight's
  triangles-from-`polygon.vertices` assumption downstream.
- **ID properties round-trip as `IDPropertyArray`**, not plain lists (verified in
  4.5.7: empty list → flat `IDPropertyArray`; nested lists → list of `IDPropertyArray`
  items), and `GPUIndexBuf` rejects them — selection geometry must be converted to
  plain tuples on read.
- **`scene.ray_cast` returns the hit instance's world matrix** (link empty matrix
  included). For instanced occurrence objects the object's own local matrix is *not*
  identity, so resolving the instancing empty must compare against
  `empty.matrix_world @ obj.matrix_world`, not the empty's matrix alone.
- **Link matrix math**: the handle empty's matrix is `inv(L) @ T @ G` (L = host local
  matrix from georef props, T = stored transformation, G = linked model's global
  matrix from the cache json). The world-space displacement of a moved link is
  therefore `inv(L) @ T @ L` — no json read needed (`calculate_link_delta_matrix`).
- **Undo consistency of auto-saved moves**: Blender undo of a handle move fires another
  depsgraph update, so the handler re-saves the reverted matrix — stored state stays
  consistent without transactions (a handler can't open one).

## Design

### Per-query caches + query persistence (multi-linking)

`tool.Project.get_link_cache_paths(filepath, query)` appends `.md5(query)[:8]` to the
cache blend/json names; the empty query keeps the legacy un-suffixed names so existing
caches stay valid. Every cache-path consumer goes through it — `link_ifc` build and
invalidation, the subprocess json write, model-origin/georef indicator reads,
`calculate_link_matrix`, `save_link_transformation`, and the per-link
selectability/wireframe/visibility toggles (which match collections *by library
filepath* and would otherwise affect every link of the file at once).

The query persists on each link's `IfcDocumentReference.Description` (written by
`LinkIfc` and `ReloadLink`); `load_linked_models_from_ifc` restores from it, with a
legacy-JSON fallback that only applies when the file has a **single** link (with
several links the shared JSON can't say which link it belonged to). IFC2X3 hosts have
no `Description` — custom queries are not restorable there (accepted).

`LoadLink`/`ReloadLink` volatile properties are `SKIP_SAVE` (see key facts). Cache
clearing tolerates a missing blend (a reload with a brand-new query points at a
not-yet-existing filename).

### External styles + layerset slicing in the linked loader

`LoadLinkedProject.get_external_material(style_id)` resolves a style id → appended
Blender material from the external `.blend`, cached two ways (per style id; per
appended data-block, so styles sharing one material don't append duplicates). Appended
materials get their stale `ifc_definition_id` cleared (the source `.blend` may have
been authored in a Bonsai session; the id would be misread in the linked file *and*
in the host once the cache links in). Applied in both loading paths — instanced
occurrences directly, chunks via the style-id column.

Multi-layer elements (`IfcMaterialLayerSetUsage`, >1 layer) route through the
instanced path and get `slice_layerset_mesh`, which gained a pluggable
`style_to_material` resolver (defaults to the old `tool.Ifc.get_object` for the normal
import) — the linked resolver prefers the external material, falling back to a flat
diffuse from the style's shading colour. Also fixed there: newly appended layer
materials are registered in the dedup dict (two layers sharing one style used to
append it twice).

Trade-off: layered walls become individual instanced objects instead of chunk members;
meshes shared between elements (same geometry id) bake the slice from the first
element's layerset usage — same behaviour as the normal importer.

### Reload Link dialog

`bim.reload_link` now exposes File Path (+ browse button), Use Relative Path
(defaulting to the stored path form), Use Cache (default off = old always-rebuild
behaviour), the False Origin Mode project props, and Query. A file browser can't open
from inside a props dialog, so the browse button runs `bim.select_link_filepath`
(fileselect) which *reopens* the reload dialog with the chosen path, carrying the
in-progress dialog state through the round trip (op props are baked at draw time).
Path changes update `link.name`/`filepath` and, with a host IFC, the reference
`Location` + document name — which is why `ReloadLink` became a `tool.Ifc.Operator`.
Script calls without arguments preserve all stored link values via `is_property_set`.

### Per-row lock toggle + auto-saved transforms

Link editing moved from the panel header into each list row as a lock/unlock icon:
unlock (`bim.enable_editing_link`) frees the handle; **any movement is persisted
immediately** by a `depsgraph_update_post` handler (lazy — ticks without transform
updates cost ~nothing); lock (`bim.disable_editing_link`) saves and locks.
`bim.edit_link` and the explicit save step are **removed**; cancel/restore semantics
no longer exist (undo or move it back). The save math lives in
`tool.Project.save_link_transformation`. Enable/disable take a `link_index`
(default −1 = active link) so several links can be edited at once and script calls
stay compatible.

### Explore tool + append fixes for moved links

- Highlight triangles come from `mesh.calc_loop_triangles()` filtered to the queried
  element's polygon range (ngon-safe); edges keep `polygon.edge_keys` (no diagonals).
- `get_selected_geometry` converts the ID-prop round trip to plain tuples (GPU
  rejects `IDPropertyArray`); TRIS drawing gated on its own data.
- `QueryLinkedElement` passes the ray-cast instance matrix through;
  `find_obj_root` compares it against `empty @ obj_local` and falls back to the
  collection's only instance when no matrix is available (select-by-GUID flow).
- `bim.append_inspected_linked_element` pre-multiplies the imported object's matrix by
  `calculate_link_delta_matrix(link)`, matching the link by the queried instance's
  root empty first (filepath alone is ambiguous with several links per file). The
  element's IFC placement syncs to the moved location on save — intended.

## Status — implemented (verified in Blender, incl. headless + GUI repro runs)

Six commits on `Linked_File_Features`:

- `0096c0f6a2` reload_link without a query preserves the stored one.
- `40db55e52d` external styles + layerset slicing for linked models
  (`project/operator.py`, `tool/loader.py`).
- `d210d4c814` full Reload Link dialog + `bim.select_link_filepath`.
- `3dc161f0f2` per-row lock toggle, auto-save handler, `edit_link` removed
  (`project/operator.py`, `project/ui.py`, `project/__init__.py`, `tool/project.py`).
- `0571d22855` Explore highlight (ngons, IDPropertyArray), moved-link highlight,
  append placement (`tool/project.py`, `project/operator.py`, `project/decorator.py`).
- `c14592ec0a` per-query caches, Description persistence, SKIP_SAVE.

End-to-end verified with a two-links-one-file kit (window/door, distinct queries):
correct visuals on load, after save → reopen → reload, in both headless and windowed
Blender.

## Things to test / verify

- **IFC2X3 host**: `Description` doesn't exist — link queries silently not restored on
  reopen (legacy fallback only for single-link files). Acceptable? Warn?
- **Relative-path links** (`use_relative_path`) through the whole cycle: cache paths,
  reference `Location`, reload path change, query restore.
- Same file linked twice, **both moved differently**: Explore highlight and append
  placement per instance (root-empty matching), per-link visibility toggles.
- External styles with **image textures**: paths relative to the style's source
  `.blend` may not resolve from the cache blend's location (shared limitation with the
  normal import path).
- Stale cache orphans: per-query filenames accumulate one blend+json pair per distinct
  query next to the IFC; nothing auto-deletes them. Cleanup on unlink? Document?
- Mid-drag auto-save writes the IFC reference outside Bonsai's transaction system —
  confirm no undo-stack weirdness in longer editing sessions.
- Layerset slicing on meshes shared by elements with *different* usages (offset/sense)
  bakes the first element's slice — same as normal import, but worth a look with types.
- `bim.select_link_filepath` round trip when the reload dialog was opened for a
  non-active link, and dialog-state carry-over after editing the query *then* browsing.
