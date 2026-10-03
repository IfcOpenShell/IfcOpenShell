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

## Blender version compatibility (4.x vs 5.x)

Blender 5.0 reworked the compositor and broke every API the first version of this
module used. All of it is funnelled through helpers in `operator.py` (`get_compositor_tree`,
`get_output_socket`, `add_gamma_node`, `add_mix_node`, `find_socket`) so the
graph-building code reads the same on both:

| | ≤ 4.5 | ≥ 5.0 |
|---|---|---|
| Node tree | `scene.node_tree` (embedded), enabled via `scene.use_nodes` | `scene.compositing_node_group` — a standalone `CompositorNodeTree` ID in `bpy.data.node_groups`. `scene.node_tree` is **gone**; `scene.use_nodes` is a deprecated no-op that no longer creates a tree |
| Final output | `CompositorNodeComposite` | node **removed** — use `NodeGroupOutput` plus `tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")` |
| Gamma | `CompositorNodeGamma` (image socket "Image") | `ShaderNodeGamma` (image socket "Color") — addressed positionally |
| Mix | `CompositorNodeMixRGB` | `ShaderNodeMix` with `data_type = "RGBA"`; sockets picked by identifier (`Factor_Float`, `A_Color`, `B_Color`, `Result_Color`) since several share a display name |
| Render Layers / Exposure / Cryptomatte | unchanged | unchanged |

Two 5.x-only wrinkles, both handled in `build_compositor`/`clear_compositor`:

- A compositing group is a standalone ID, so a Render Layers node created inside one
  is not implicitly bound to the scene being rendered — `render_layers.scene` is set
  when it comes back `None`.
- If no group existed, we create one and tag it with `MARKER`; `clear_compositor`
  deletes it and resets `scene.compositing_node_group` to `None`, so a scene that
  never composited doesn't end up permanently compositing through a passthrough graph.

Verified end-to-end (Cryptomatte-masked exposure and gamma both applied to the matched
object and not the background, everything torn down afterwards) on 4.5.7 and 5.2.0 —
identical rendered pixel values.

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
- `depsgraph_update_post` → re-apply after a geometry edit rebuilt an object we swapped
  (see below)

### Surviving representation reloads

Editing geometry replaces the object's data outright — `Geometry.change_object_data`
does `obj.data = data` — so the material slots come back from IFC and the temporary
transparent copies are silently dropped. Nothing notifies this module, so the preview
would just vanish until the toggle was cycled. Reproduced with:

```
bim.enable_editing_extrusion_profile → bim.direct_profile_edit → editmode_toggle
  → bim.edit_extrusion_profile → bim.direct_profile_edit
```

Two parts to the fix:

- `_transparency_restore` records the temp material alongside the original, and
  `restore_transparency` only undoes a slot that **still holds that temp material**.
  Otherwise the restore writes the pre-edit material over whatever the reload just put
  there.
- `depsgraph_update_post` → `live_state_is_stale()` → deferred `sync_live_effects`. Kept
  cheap: returns immediately unless transparency is applied *and* the update names an
  object in `_tracked_objects`. Skipped outside OBJECT mode (leaving edit mode fires
  another update), and deferred through `bpy.app.timers` so material writes happen
  outside the notification, as with the msgbus camera subscription. The staleness check
  is what stops it looping: our own re-apply leaves nothing stale.

### Scale: a rule can match thousands of objects

The first version copied a material **per slot**, so a rule matching a few thousand
elements created a few thousand material datablocks (each with its own node tree), and
every re-sync tore all of it down and rebuilt it. Two changes make that workable:

- **Shared temp materials.** `get_temp_material(material, amount)` caches by
  `(source material name, amount)`, so the count is the number of distinct
  material/amount pairs — usually a handful — not the number of slots. Sharing stays
  safe for `user_remap` precisely because every user of a temp material had the same
  original. The source material name is recorded on the temp as `SOURCE_KEY`.
- **Incremental sync.** `sync_live_effects` no longer restores everything and re-applies.
  Pass 1 keeps slots already carrying the right temp material and undoes only what is no
  longer wanted; pass 2 applies only to what is not already covered. As a side effect it
  can no longer destroy a preview it is unable to rebuild, which was its own bug.

Two supporting details:

- `live_state_is_stale(names)` is scoped to the objects a depsgraph update actually
  touched. Walking every swapped slot on every update is wasted work at this scale.
- `_tracked_objects` holds what the rules **want**, not what was successfully applied, so
  an object whose mesh is mid-rebuild is still watched and picked up when it returns.
  Objects with nothing swappable never report stale, or they would request a resync
  forever.

`sync_live_effects` also **adopts orphans** — a slot holding one of our temp materials
with no matching entry, left behind by a rebuild we did not observe. It is traced back
via `SOURCE_KEY` and re-registered, rather than silently baked into the saved file.

Smoke-tested headless on 4.5.7: three objects sharing one source material produce exactly
one temp material, and a stray reference is remapped rather than emptied.

### Known limitation: elements with no material

Transparency is produced by **copying the element's existing material** and mixing a
Transparent BSDF into it. An element with no Blender material — no IFC surface style —
has nothing to copy, so `apply_transparency` skips it and the rule silently does
nothing for that element (`has NO material slots` in the debug trace). Confirmed
2026-09-02: assigning the elements a material makes it work.

Making it work regardless means inventing a material and appending a slot, which
mutates `obj.data` — IFC-linked geometry that Bonsai checksums via
`Geometry.record_object_materials` to decide whether styles need writing back. Not done
for that reason; revisit only with a test that the model is not dirtied.

Do not confuse this with a slot that exists but is *empty*. That was a bug in this
module — `bpy.data.materials.remove()` unlinks from every user, so deleting a temp
material that had ridden onto a rebuilt mesh emptied the live slot. Fixed by
`user_remap`-ing back to the original first and never force-deleting a temp material
that still has users.

## Storage / gating

- Per-drawing: stored on the camera datablock as `Camera.BIMRenderOverrideProperties`
  (self-contained — the core drawing module does not depend on this one).
- Per-rule filters reuse the shared Search system; resolver keys are
  `status_render_{rule_index}` (see `tool/search.py`).
- The render path is the compositor, which only runs for F12 and `render.render()`
  drawing underlays. Viewport/OpenGL drawings bypass it, so the panel disables the
  toggle when the style is not a "Default" render type. The gate reads exactly what
  `generate_underlay` branches on — `BIMCameraProperties.get_active_drawing_style()`,
  the row highlighted in the Drawing Styles list — **not**
  `EPset_Drawing.CurrentShadingStyle`, which is only rewritten by
  `bim.activate_drawing_style` and readily goes stale (see issue #9319). The drawing
  also needs an underlay for the override to appear in it.

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
