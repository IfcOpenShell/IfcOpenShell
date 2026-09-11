<!-- This file was generated with the assistance of an AI coding tool. -->

# MergeProjects duplicate representation contexts (+ MergeDuplicateContexts recipe)

> **Living dev note** for the `fix-mergeprojects-dup-contexts` branch/PR (stacked on
> `merge-duplicate-contexts`). Read before working on the feature; append decisions and
> findings as the PR is refined. This is *not* user documentation — at merge it is
> removed or its durable parts promoted to code comments. See [README.md](README.md)
> for the convention.

Covers two stacked PRs:

- **#8701 → PR #8706** (`merge-duplicate-contexts`): new `MergeDuplicateContexts`
  ifcpatch recipe (the cleanup tool).
- **#8700 → PR #8707** (this branch): use that recipe to stop `MergeProjects` emitting
  duplicate contexts (the root-cause fix).

## Problem / symptom

A layered wall with per-layer material styles renders in the 3D viewport with a
**single style for the whole wall**. Root cause chain:

- `bonsai.tool.Loader.slice_layerset_mesh()` resolves each layer's style via
  `ifcopenshell.util.representation.get_material_style(layer.Material, body)` where
  `body = get_context(ifc, "Model", "Body", "MODEL_VIEW")`.
- `get_context()` returns only the **first** context matching those attributes. The
  file had **two** `Model/Body/MODEL_VIEW` contexts; the material styles'
  `IfcStyledRepresentation`s hung off the *second*, so `get_material_style` returned
  `None` for every layer → one style.

The duplicate contexts came from the **`MergeProjects` ifcpatch recipe**, not from the
clipboard (an earlier hypothesis — the clipboard engine was investigated and cleared).

## Root cause (MergeProjects)

`MergeProjects.reuse_existing_contexts()` repoints each merged-in context that
duplicates an existing one, adds it to a `to_delete` **set**, then removes each via
`remove_deep2`. Two compounding issues:

1. `remove_deep2` **silently returns without deleting** any element that still has an
   inverse not contained in its traversal subgraph (documented contract), and the
   recipe wraps it in a bare `except: pass`.
2. Depending on iteration order, the repoint loop leaves a **residual inverse** on a
   matched context, so `remove_deep2` skips it and it survives as an orphaned
   duplicate.

Captured trace (survivors are exactly the contexts that still held an inverse):

```
[MergeProjects] === removal loop (order-sensitive) ===
  #142 Model/Body    inv_before=1  refs=[IfcShapeRepresentation]              -> SURVIVED
  #150 Plan/Axis     inv_before=1  refs=[IfcShapeRepresentation]              -> SURVIVED
  #123 Model parent  inv_before=8  refs=[IfcGeometricRepresentationSubContext]-> SURVIVED
  #127 Plan parent   inv_before=4  refs=[IfcGeometricRepresentationSubContext]-> SURVIVED
[MergeProjects] === after merge: 2 Model/Body/MODEL_VIEW context(s) -> [20, 142] ===
```

## Why it is a safety-net fix, not a rewrite of the removal

The failure is **nondeterministic and could not be reproduced in a fresh process** —
important context so nobody wastes time trying:

- Not in the file bytes: a `to_string()`-saved copy of the live model is byte-identical
  to the disk file and merges **clean**.
- Not `PYTHONHASHSEED` (41 seeds, all clean) and not matching/removal order in a fresh
  parse (200 randomized orders, all clean). Manual parent-first vs child-first: clean.
- An `entity_instance`'s hash embeds the **file's C++ pointer**, so `set` iteration
  order varies with process/memory state. Bonsai's long-running, heavily-edited process
  hits a failing order; short-lived fresh processes do not. The same input reproduces
  in Bonsai but not standalone.

Because the failing order is not reproducible on demand, a "fix the removal ordering"
change can't be verified against a failing case. So the fix makes the **outcome**
robust instead: run `MergeDuplicateContexts` once after all merges (in `patch()`),
collapsing whatever slipped through `reuse_existing_contexts`. Verified it collapses the
real merged files and is a no-op on clean merges.

`MergeDuplicateContexts` itself keeps the first context per
`(ContextType, ContextIdentifier, TargetView)`, repoints references via
`ifcopenshell.util.element.replace_element`, removes the duplicates, and dedupes
SET-typed aggregates (e.g. `IfcProject.RepresentationContexts`). Subcontexts and parent
contexts are handled in separate passes so a subcontext is never merged into a parent.

## Files

- `src/ifcpatch/ifcpatch/recipes/MergeDuplicateContexts.py` — new recipe (PR #8706).
- `src/ifcpatch/ifcpatch/recipes/MergeProjects.py` — import + one call after the merge
  loop (this PR).
- Tests: `test_MergeDuplicateContexts.py` (new); `test_MergeProject.py` gains
  `test_never_emits_duplicate_contexts`, which injects a duplicate the reuse pass never
  touches (so it fails without the dedupe, passes with it).

## Test checklist

- [x] `MergeDuplicateContexts`: collapse + reference repoint + project-aggregate dedup,
      IFC4 and IFC2X3; no-op when there are no duplicates.
- [x] `MergeProjects`: new regression test passes with the fix (1 Body), fails without (2).
- [x] No regression: `test_reusing_geometric_contexts` (contexts == 2),
      `test_using_the_georeferencing` (CRS == 1, MapConversion == 1).
- [x] Repairs the real captured files (`merged.ifc`, `testymerge.ifc`): 2 Body → 1,
      styles preserved, legitimately-empty subcontexts left alone.
- [ ] Not yet exercised: a merge that genuinely triggers the order-dependent skip inside
      a fresh process (see reproduction caveats above) — covered only indirectly.

## Open questions / follow-ups

- A proper root fix for `reuse_existing_contexts` (make the removal order-independent —
  e.g. fully repoint via `replace_element`, remove child-first, drop the bare `except`)
  would let the safety-net be removed. Deferred because it is unverifiable without a
  deterministic repro. The same fragile pattern exists in
  `ifcopenshell.api.project.append_asset.reuse_existing_contexts`; worth auditing.
