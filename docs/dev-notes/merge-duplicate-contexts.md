<!-- This file was generated with the assistance of an AI coding tool. -->

# MergeDuplicateContexts recipe

> **Living dev note** for the `merge-duplicate-contexts` branch/PR. Read before working
> on the feature; append decisions and findings as the PR is refined. This is *not* user
> documentation — at merge it is removed or its durable parts promoted to code comments.
> See [README.md](README.md) for the convention.

PR #8706 → closes #8701. Also the cleanup half of #8700 (the root-cause fix lives on the
stacked `fix-mergeprojects-dup-contexts` branch, PR #8707, whose dev-note has the full
investigation).

## Problem

A well-formed IFC has a single geometric representation context per
`(ContextType, ContextIdentifier, TargetView)` (e.g. one `Model/Body/MODEL_VIEW`).
Merges, round-trips, and some exporters — and, concretely, the `MergeProjects` recipe
(see #8700) — leave two or more that are identical in all three. This is non-conformant
and breaks code that resolves a context by attributes:
`ifcopenshell.util.representation.get_context()` returns only the **first** match, so
geometry, material styles, or annotations attached to the others are silently orphaned.
Visible symptom: a layered wall renders with a single material style because each
layer's style hangs off a second, never-matched, Body context. There was no user-facing
tool to repair such a file.

## Design

For each `(ContextType, ContextIdentifier, TargetView)` key: keep the first context,
repoint every reference off the duplicates onto that survivor via
`ifcopenshell.util.element.replace_element` (generic — handles representations'
`ContextOfItems`, subcontexts' `ParentContext`, coordinate operations, etc.), remove the
duplicates, and dedupe any SET-typed aggregate (e.g. `IfcProject.RepresentationContexts`)
that would otherwise list the survivor twice.

Top-level contexts and subcontexts are keyed and processed in **separate passes** so a
subcontext is never merged into a parent context, and a surviving subcontext keeps a
valid `ParentContext`.

Takes no arguments → appears in the Bonsai IFC Patch dropdown with nothing to configure,
mirroring `MergeDuplicateTypes` / `MergeStyles`.

## Test checklist

- [x] IFC4 + IFC2X3: collapse two duplicate Body subcontexts + duplicate parent
      contexts; representation on the duplicate is repointed onto the survivor; project
      aggregate deduped to a single entry.
- [x] No-op when there are no duplicates (distinct subcontexts preserved).
- [x] Repairs real captured files (`merged.ifc`, `testymerge.ifc`): 2 Body → 1, styles
      preserved, legitimately-empty subcontexts left untouched.
