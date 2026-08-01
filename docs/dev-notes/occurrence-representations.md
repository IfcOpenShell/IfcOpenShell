<!-- This file was generated with the assistance of an AI coding tool. -->

# Occurrence representations — normalize occurrence-local reps onto the type

> **Living dev note** for the `occurrence-representations` branch/PR. Read before working
> on the feature; append decisions and findings as the PR is refined. This is *not* user
> documentation — at merge it is removed or its durable parts promoted to code comments.
> See [README.md](README.md) for the convention.

Tracking issue: [#8788](https://github.com/IfcOpenShell/IfcOpenShell/issues/8788). Supersedes
the closed PR #8789 (see "History / pivot"). Stacked on `dev-notes-system` (#8201) →
`opening-template-on-type` (#8200) → `select-by-representation-type` (#7916), because it shares
the Representations panel and `RepresentationsData`.

## Position (maintainer-aligned)

Per Dion Moult (project lead), **if a type has representations, its occurrences should share
them** — an occurrence carrying a representation the type lacks is an *anomaly to normalize up
to the type*, not something to preserve. This follows the MVD concept-template intent (mapped
representations mirror the type relationship) and the `IfcTypeProduct` text that typed
occurrences "have to reference the representation maps", even though EXPRESS has no WHERE rule
enforcing it. See the buildingSMART thread Moult started:
<https://forums.buildingsmart.org/t/must-mappedrepresentations-come-from-the-corresponding-ifc-type/3361>.

This branch therefore provides the **normalization path**, and deliberately does *not* try to
make occurrence-local reps a first-class, persisted thing.

## Scope

**In:**

1. **Promote to Type** (`bim.promote_representation_to_type`) — lift an occurrence-local rep
   onto its type as a `RepresentationMap`, so occurrences inherit it. The migration tool for
   imported/legacy models (Revit et al. emit occurrence-only / partial-from-type reps).
2. **Type / Occurrence panel split** — `BIM_PT_representations` groups rows under **Type**
   (mapped/inherited) vs **Occurrence** (local) headers, so an anomalous occurrence-local rep
   is *surfaced* instead of silent.

**Deliberately out (dropped from the earlier draft):**

- **Copy-time preservation** — `copy_class` is left as-is (occurrence-only reps are not
  re-added on duplicate). Preserving them perpetuates the anomaly; normalize first, then copy.
- **"Add to Occurrence" toggle** — removed. `add_representation` keeps stock behaviour
  (`geometry.assign_representation` already redirects a new rep onto the type when the type has
  maps). No force-local override.

## Design

### Promote to Type (slot-based, "type wins")

`bim.promote_representation_to_type` (`EXPORT` icon on Occurrence rows, only when
`element_has_type`) → `core.geometry.promote_representation_to_type`. Copies the promoted rep
onto the type as a new `RepresentationMap` (`tool.Geometry.add_type_representation_map`), then for
**every** occurrence of the type: removes **any** existing rep in the same **slot** and assigns
the type's mapped rep in its place. Occurrences with no rep in the slot simply inherit it.

"Any existing rep" is the load-bearing part: it covers a **local** (non-mapped) rep *and* an
already-**mapped** rep the occurrence inherited from another map — e.g. a floating
`IfcRepresentationMap` not anchored to the type, which Revit emits (each occurrence maps to its
own or a shared floating map, the type's `RepresentationMaps` is empty). Local reps are removed
via `core.remove_representation` (Blender-aware); mapped reps via a per-occurrence
`geometry.unassign_representation` + `geometry.remove_representation` (its `remove_deep2` keeps a
shared map alive until its last user is gone, so floating maps get garbage-collected). If the
type already holds a rep in the slot it is removed too, so promoting is idempotent (replaces
rather than accumulating maps). The slot key resolves through mapped items
(`resolve_mapped_representation`), because an inherited rep's own `RepresentationType` is
`"MappedRepresentation"`, not the underlying type.

The slot key is context (context/subcontext/target view) + `RepresentationIdentifier` +
resolved `RepresentationType`. **Geometry is not compared** — the type's representation replaces the
occurrence's for that slot even when the occurrence's geometry genuinely differs (e.g. an
independently meshed / mirrored / rotated Revit instance), so such occurrences visibly adopt the
type's geometry. The mapped rep uses `map_representation`'s identity transform, so a divergent
instance takes the type geometry at *its own placement* (baked per-instance mesh orientation is
lost — the accepted tradeoff of "type wins").

Rationale for dropping the earlier geometry comparison: for Revit-style imports each occurrence
carries an independently tessellated body (same vertex count but reordered + reoriented; no
single affine maps one to another, confirmed via a least-squares fit — `max_err ≈ 1.3 m`), so an
"only consolidate byte-identical" rule left most real-world duplicates unconsolidated. Slot-based
replace is the deliberate, user-chosen behaviour.

### Panel split

`RepresentationsData` (geometry/data.py) exposes `is_mapped`
(`resolve_representation(rep) != rep`), `element_is_type`, and `element_has_type`.
`draw_representation_row` is shared and carries the stack's `RepresentationIdentifier` column +
`select_by_representation_type` button; the Occurrence-group rows additionally show the promote
button. A type element shows a flat list.

## The divergent-occurrence case (decision made)

Two occurrences of one type that carry **different** geometry in the same slot cannot both live
on the type (one mapped rep per slot). The chosen resolution is **"type wins"**: promote
replaces every occurrence's local rep in that slot with the type's, discarding divergent
per-instance geometry. This favours a single authoritative type geometry over preserving
independently-authored instance bodies. (Intrinsic per-instance geometry — voids/joins;
`IfcRelVoidsElement` is occurrence-only — lives in a *different* mechanism and is unaffected.)
The broader "can occurrences ever legitimately diverge" question is still worth raising with
Moult on #8788, but Promote no longer tries to adjudicate it.

## Status — implemented (verified in live Blender)

- `tool/geometry.py`: `copy_representation_deep`, `add_type_representation_map`.
- `core/geometry.py`: `promote_representation_to_type` (slot-based).
- `core/tool.py`: interface decls for the two new `Geometry` methods.
- `bim/module/geometry/operator.py`: `PromoteRepresentationToType`.
- `bim/module/geometry/{data,ui}.py`: `is_mapped` / `element_is_type` / `element_has_type`;
  Type/Occurrence grouping merged with the stack's panel columns; old `*` suffix removed.
- `bim/module/geometry/__init__.py`: register `PromoteRepresentationToType`.
- `core/root.py`, `tool/root.py`, `core/geometry.py::add_representation`: reverted to base
  (copy-preservation + add-to-occurrence removed).

## History / pivot

Originally four pieces incl. a `copy_class` fix that re-added occurrence-only reps on duplicate,
and an "Add to Occurrence" toggle. PR #8789 was closed by Moult as "based on the wrong premise
— there shouldn't be representations on occurrence and not on type if the type has
representations." Re-scoped to the normalization-only subset above; copy-preservation and the
toggle removed.

## Things to test / verify

- Promote (verified on a Revit sink type, 5 occurrences): every occurrence ends up referencing
  the type's mapped rep — occurrences with a local body in the slot have it replaced (including
  independently-meshed/mirrored ones, which visibly adopt the type geometry), and occurrences
  with none inherit it. Exercises `remove_representation`'s Blender mesh/data-link side effects.
- Promoting a second slot (e.g. Body/PLAN_VIEW/Curve3D) adds a second `RepresentationMap` and all
  occurrences inherit both.
- Re-open the saved IFC and confirm the mapped instances render sensibly (the divergent ones will
  have changed orientation — that's the accepted "type wins" tradeoff, not a bug).
- Panel: Type vs Occurrence grouping correct for occurrence, typed occurrence with no local
  reps (only Type header), typeless element (only Occurrence), and a type element (flat list);
  columns still align with the stack's header row.
- Confirm copy/add behave as stock v0.8.0 (no regression from the removed pieces).
