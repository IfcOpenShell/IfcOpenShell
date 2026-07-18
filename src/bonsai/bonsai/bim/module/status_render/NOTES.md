# status_render — developer notes

Per-drawing render overrides: select IFC elements with a filter and apply render
effects (exposure, gamma, transparency) to them. Aimed at drawing underlays
("existing faded", "demolished ghosted") but also works for plain F12 renders.

## Two-layer architecture

Effects live where they can actually be shown, both driven by the one
**Enable Render Overrides** toggle:

| Layer | Effect | Mechanism | Applied | Visible |
|-------|--------|-----------|---------|---------|
| Live material | Transparency | Temp material copy with a Transparent BSDF mixed into the surface (`surface_render_method = "BLENDED"`) | Persistently while enabled | Rendered viewport **and** render |
| Render compositor | Exposure / gamma | Cryptomatte object matte → Exposure/Gamma → Mix, per rule, chained | Built per render, removed after | Render only |

Transparency is a *real* material change so the geometry behind shows through
(compositing can't reveal occluded geometry after an opaque render). Because it's
a material, EEVEE Next renders it live in the viewport — that's the WYSIWYG path.

Exposure/gamma stay in the compositor because that's the faithful colour-management
tonemap. They are render-only: the viewport compositor can't read render passes
(Cryptomatte), so per-object masking isn't available there.

## Why Cryptomatte (not the Object Index pass)

EEVEE Next always renders the Object Index pass as 0 (Blender bug #121690).
Cryptomatte works in both EEVEE and Cycles. Note: node-socket string subscripting
keys by `.identifier`, not `.name` — relevant if ever touching pass sockets again.

## Apply / restore seam

- `sync_live_effects(scene)` — single source of truth for live material state:
  restore all temp materials, then apply transparency for the active camera's
  enabled rules. Idempotent; safe to call any time.
- `build_compositor(scene, props)` / `clear_compositor(scene)` — render-only colour
  nodes; clearing leaves live materials untouched.

## Lifecycle / handlers (operator.py)

- enable toggle + transparency slider (prop `update=`), add/remove rule → `sync_live_effects`
- `render_init` → sync materials, then `build_compositor`
- `render_complete` / `render_cancel` → `clear_compositor` (materials persist)
- `save_pre` → `restore_transparency` (never bake temp materials into the .blend)
- `save_post`, `load_post` → `sync_live_effects` (re-apply the live preview)

## Storage / gating

- Per-drawing: stored on the camera datablock as `Camera.BIMRenderOverrideProperties`
  (self-contained — the core drawing module does not depend on this one).
- Per-rule filters reuse the shared Search system; resolver keys are
  `status_render_{rule_index}` (see `tool/search.py`).
- The render path is the compositor, which only runs for F12 and `render.render()`
  drawing underlays. Viewport/OpenGL drawings bypass it, so the panel disables the
  toggle when the *applied* shading style (`EPset_Drawing.CurrentShadingStyle`) is
  not "Default" render type. The drawing also needs an underlay for the override to
  appear in it.

## IFC persistence (coarse auto-sync)

Rules are mirrored into the IFC model so they travel with the drawing, not just the
`.blend`. The camera props remain the working/edit copy; IFC is the source of truth.

- **Property:** `EPset_Drawing.RenderOverrides` — a JSON list of
  `{name, query, exposure, gamma, transparency}` per rule. `query` uses the same
  `tool.Search.export/import_filter_query` serialization as the drawing
  Include/Exclude filters.
- **Write (coarse):** on add/remove rule, and on `save_pre` for every drawing camera
  (`save_rules_to_ifc`). Deliberately *not* on every slider tick (would spam IFC).
  Field edits (exposure/gamma/transparency/filter) therefore persist at the next
  add/remove or at the next save.
- **Read:** rules are pulled from the pset by `ensure_rules_loaded` (guarded: it only
  loads when the camera props are empty, so it never clobbers in-session edits). This
  runs from:
  - `data.refresh()` — called by `bonsai.bim.handler.refresh_ui_data()`, which fires
    at the end of `load_project_elements`. **This is the path that handles opening an
    IFC into a fresh session** — `load_post` fires *before* the IFC import creates the
    drawing cameras, so it can't see them.
  - `load_post` — for reopening a `.blend` (cameras already exist; usually a no-op
    since their props came from the file).
  - `render_init` — belt-and-braces before a render.
  `deserialize_rules` uses direct id-property writes so it doesn't fire the
  live-preview update per rule.
- **Not persisted to IFC:** the `enabled` toggle (session/working state, lives in the
  `.blend` only). So rules are portable across `.blend` files; whether the preview is
  currently *on* is not.

Caveats:
- The pset writes are raw `ifcopenshell.api.pset.edit_pset` calls (matching
  `edit_element_filter`), not wrapped in `tool.Ifc.Operator`, so they are not in
  Bonsai's IFC undo stack and may not flip the "unsaved IFC" indicator. They are
  rewritten from the camera props on the next save, so the stored JSON self-heals.
- Saving the IFC *without* a `.blend` save after a slider/filter edit may miss that
  edit (it's flushed in `save_pre`, a `.blend`-save handler). Add/remove a rule or
  save the `.blend` to flush.

## Active-drawing switch

Switching the active drawing reassigns `scene.camera` but fires no handler. A msgbus
subscription on `(bpy.types.Scene, "camera")` (`subscribe_camera_change`) catches it
and re-syncs the live materials (the previous drawing's transparency is removed, the
new drawing's applied). The notify defers via `bpy.app.timers` so material datablock
edits happen outside the msgbus notification context. msgbus is cleared on file load,
so we re-subscribe in `load_post` (and on register).

## Filter edits

Editing a rule's filter via `bim.edit_filter_query` (or `bim.apply_filter_from_text`)
re-syncs the live preview: those operators call `tool.Search.on_filter_query_edited`,
which dispatches to `operator.sync_live_effects` for `status_render_*` modules. This
keeps the coupling in `tool.Search` (which already special-cases `status_render` in
`get_filter_groups`), leaving the shared search operators generic.

## Deferred robustness (TODO when the concept proves out)

- **Undo** can desync live state — re-toggle to refresh.
- Transparency slider re-syncs on every increment (creates/removes temp materials);
  fine for now, could debounce on large scenes.
- Exposure/gamma in the viewport would require re-expressing them as material tweaks
  (approximate); intentionally not done — they stay faithful + render-only.
