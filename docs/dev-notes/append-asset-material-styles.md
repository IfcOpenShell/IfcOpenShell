<!-- This file was generated with the assistance of an AI coding tool. -->

# append_asset material styles — preserving surface styles reached via a layer set usage

> **Living dev note** for this fix. Read before working on the feature; append decisions
> and findings as the PR is refined. This is *not* user documentation — at merge it is
> removed or its durable parts promoted to code comments. See [README.md](README.md) for
> the convention.

## Problem

Appending an object with `bpy.ops.bim.append_library_element_by_query()` (or any
`ifcopenshell.api.project.append_asset`) brought a wall's **materials** across but not the
**`IfcSurfaceStyle` assigned to each material**. In the project the appended materials came
out with `HasRepresentation == ()` — no `IfcMaterialDefinitionRepresentation`, so no colour.

Only reproduces when the material is reached through an **`IfcMaterialLayerSetUsage`**
(i.e. real wall *occurrences*), not a bare layer set on a type. A single directly-assigned
material, or a type product with a bare layer set, both carried styles fine — which is why
it evaded synthetic reproduction at first.

## Key facts established

- `append_asset` copies the style faithfully **when it runs**. The loss is purely that the
  code that transplants a material's inverse attributes (`check_inverses`) is **never called**
  on these materials — confirmed by tracing: `check_inverses` never fired for the styled
  materials, and the subgraph walk logged
  `subloop IfcMaterialLayerSet #… -> EXISTING (queue NOT extended)`.
- This is **not** a Bonsai import bug. `AppendLibraryElement.import_materials` →
  `import_material_styles` → `IfcImporter.create_style` were all correct; they just had no
  style data to import because the IFC arrived style-less. (Ruled out and reverted a red
  herring about `create_style`'s `active_style_type` update callback not firing.)
- Regression from the material-set **reuse** feature (`material_sets_are_equal`). The older
  `ifcopenshell` shipped on the reporter's machine (no `material_sets_are_equal`) carried
  styles fine; the newer repo copy Blender loads does not.

### Root cause (`append_asset.py`, `Usecase.add_element`)

1. The wall's `RelatingMaterial` is an `IfcMaterialLayerSetUsage` → `IfcMaterialLayerSet`.
2. `file_add` **forward-copies** the whole usage → set → layers → materials subgraph into the
   project. `file_add` only copies *forward* attributes; inverses (`HasRepresentation`,
   `HasProperties`, …) are the job of `check_inverses`, which runs from `add_element`'s
   subgraph traversal.
3. When that traversal reaches the layer set, `get_existing_element` matches the fresh
   forward-copy as "existing" (via `material_sets_are_equal`), so it takes the
   `if existing_element:` branch — which **does not extend the queue into the set**. The
   member `IfcMaterial`s are never visited, `check_inverses` never runs on them, and
   `IfcMaterial.HasRepresentation` (which carries the `IfcSurfaceStyle`) is never transplanted.
4. The subsequent type append short-circuits even earlier: the set is already in
   `added_elements`, so `add_element` returns immediately.

## Fix

In the `if existing_element:` branch, when the matched-existing subelement is a material set,
descend into it so each member material gets `check_inverses`:

```python
if subelement.is_a() in MATERIAL_SETS:
    subelement_queue.extend(self.settings["library"].traverse(subelement, max_levels=1)[1:])
```

The existing `has_whitelisted_inverses` guard keeps genuine reuse **idempotent**: when the
project already contains the same-named styled materials, the member materials are still
enqueued but their `check_inverses` is skipped (they already have `HasRepresentation`), so no
duplicate materials or styles are created — verified.

## Status — implemented and validated (no Blender/py3.11 binary needed)

- `src/ifcopenshell-python/ifcopenshell/api/project/append_asset.py`: the 2-line descent
  above (+ comment) in `add_element`. Single, localised change.
- `test/api/project/test_append_asset.py`:
  `test_append_an_occurrence_keeps_styled_materials_reached_via_a_layer_set_usage` — appends a
  wall occurrence (via a manually-built `IfcMaterialLayerSetUsage`) and asserts the member
  material keeps `HasRepresentation`, exactly one `IfcSurfaceStyle` survives, no duplicate
  materials, and the style is on the appended material.
- Validated by swapping the repo `append_asset.py` into the conda `Python312`
  `site-packages` `ifcopenshell` (the local one is too old to run the modern suite) and
  running the test body standalone: **FAILs without the fix** ("material lost
  HasRepresentation"), **PASSes with it**. Idempotency (no duplicates when materials
  pre-exist) checked separately.

## Things to test / verify

- Real-file confirmation in Blender (done by reporter): appended wall's materials now show
  their colours.
- IFC2X3 path: the added test also runs under `TestAppendAssetIFC4` (which subclasses the
  2X3 class); the `IfcMaterialLayerSetUsage` attributes used are common to both schemas.
- Other material-set kinds (`IfcMaterialConstituentSet`, `IfcMaterialProfileSet`) and their
  usages should benefit from the same descent, since the fix keys off `MATERIAL_SETS`; a
  profile-set occurrence (e.g. a styled steel column) is worth a spot-check.
- Performance: descending into already-existing sets adds queue work; bounded and guarded,
  but worth a glance on very large appends.
