# Falsy-empty-container trap sweep: ifc4d, ifc5d, ifcfm, ifccsv, ifctester

Date: 2026-07-31
Scope: `src/ifc4d/`, `src/ifc5d/`, `src/ifcfm/`, `src/ifccsv/`, `src/ifctester/`
Branch with fixes: `fix/ifcfm-cobie-zero-value-properties-dropped` (pushed to `bimvoice`)

## Result up front

**Candidates traced: ~70 (after mechanical triage of ~364 raw grep hits).
Defects confirmed by running the real code: 5, all one root cause, fixed
in one commit.** All 5 are in `src/ifcfm/ifcfm/cobie24.py` and
`cobie24legacy.py`. No confirmed defects were found in `ifc4d`, `ifc5d`,
`ifccsv`, or `ifctester` beyond what is already fixed on other open,
unmerged branches in this repository (listed below) — that ground had
already been swept.

## Existing-work check (done before any fix)

`gh pr list` (43 open PRs matching `ifc4d|ifc5d|ifcfm|ifccsv|ifctester` in
the title, out of 802 open PRs total, no pagination truncation since the
full list fits under the 1000-item cap used) and
`git for-each-ref refs/remotes/bimvoice/` showed this exact bug archetype
had already been hunted hard in these packages:

- `fix/ifc4d-zero-duration-milestone-p1d` (#9115) — the exact "zero
  duration is falsy" bug, fixed in `ifc4d/common.py` and `msp2ifc.py`.
- `ifc5d-wrong-number-audit` (#9113), `fix-6344-gross-weight-...` (#9062),
  `qto-member-length-from-extrusion` (#9063), `fix-8053-slab-qto-...`
  (#8380) — numeric defects in `ifc5d`.
- `fix-ifccsv-xlsx-blank-cell-corruption` (#9060),
  `ifcclash-ifccsv-audit-fixes` (#9116), `fix/7048-csv2ifc-delimiter`
  (#8961) — `ifccsv`.
- `fix/ifctester-verdict-audit` (#9190), `fix/ifctester-boolean-value-casting`
  (#9058), `fix/ifctester-restriction-total-fraction-digits` (#9142), and
  four more `ifctester` PRs — wrong-verdict and casting defects.
- `fix/ifcfm-duplicate-key-silent-drop` (#9193),
  `fix/ifcfm-cobie-crash-guards` (#9157),
  `fix/ifcfm-cobie24legacy-zone-crash` (#9061) — `ifcfm` crash guards, none
  touching the `val()` helper misuse below.

I read the diffs of every branch that touched a file I intended to
change (`git diff v0.8.0...bimvoice/<branch> -- <path>`) before editing
it. `common.py`'s zero-duration fix confirmed my first hypothesis (a
`timedelta(...) or None` in `ifc4d/common.py`) was **already fixed on an
unmerged branch** — I verified this by reading the diff rather than
re-reporting it as new. No skipped PRs: the full open-PR list (802) was
fetched in one `--limit 1000` call, under the cap, so no `--paginate`
truncation applies.

## Method: mechanical enumeration first

Grepped all 30 non-test `.py` files across the five packages for the two
enumeration patterns from the brief:

| pattern | raw hits (incl. license/docstring lines) |
|---|---|
| `\bor\b` | 310 |
| `\.get\(` | 131 |

Of the 310 `or` hits, 56 are `for x in y or []:` — a uniformly safe idiom
(iterating `None` and iterating `[]` both yield nothing, so this is never
a defect regardless of whether `y` is `None` or a legitimately-empty
list). After discounting license-boilerplate lines, docstring prose, and
that safe idiom, roughly 70 lines needed individual tracing to their
producer. All were checked; below is the outcome by area.

## Candidates traced, by package

### ifc4d — 1 candidate re-traced, 0 new defects

`ifc4d/common.py:297` (`timedelta(...) or None` gated on
`if activity["PlannedDuration"]`) is the textbook instance of this
archetype and the "milestone gains a day" bug named in the brief — but
it is **already fixed** on `bimvoice/fix/ifc4d-zero-duration-milestone-p1d`
(commit `ebef916795`, unmerged). I verified this by diffing that branch
against `v0.8.0`, not by re-deriving it.

I checked `ifc4d/ifc4d/csv4d2ifc.py:190`
(`"DurationType": "WORKTIME" if task["ScheduleDuration"] else None`) as a
candidate third instance of the same bug (untouched by any existing PR).
**Traced and ruled out by running it**:
`ifcopenshell.util.date.string_to_duration()` returns
`isodate.duration_isoformat(timedelta(...))`, a **string**, not a
`timedelta`. For a zero duration this is `"P0D"`, a non-empty string,
which is truthy. The falsy-timedelta failure mode cannot occur through
this code path. No fix needed.

`common.py:328` (`calendar["HoursPerDay"] or 8`, gated by `if lag:` where
`lag == 0` skips `assign_lag_time` entirely) was traced and left alone:
a 0-lag relationship and "no lag assigned" are semantically equivalent
in the IFC model (no `LagValue` implies zero lag), so skipping the call
is not observably different from calling it with 0.

### ifc5d — 3 candidates traced, 0 new defects

- `ifc5Dspreadsheet.py` `get_total_price_formula()`:
  `item.get("Quantity") and item.get("RateSubtotal")` (introduced by the
  already-pushed `ifc5d-wrong-number-audit` branch, not yet merged).
  Traced the data model: `RateSubtotal` is **never** `None` — it
  initialises to `0.0` whether or not any cost value exists, so `0.0`
  cannot be distinguished from "no cost value" in this representation,
  and a `Quantity == 0` case coincidentally produces the same `0` result
  through both the formula path and the static-value fallback. No
  observable defect; not fixed.
- `csv2ifc.py:346` (`cost_rate.get("Schedule") and cost_rate.get("RateID")`)
  — both are CSV-sourced identifier strings, not numeric measures; a
  `"0"` string ID is still truthy. No defect.
- `csv2ifc.py:390` (`if not prop_name or prop_name.upper() == "COUNT":`) —
  `prop_name` is a free-text property-name string; empty is a legitimate
  "not set" case here, not a numeric zero. No defect.

### ifccsv — reviewed, 0 new defects

`ifccsv.py`'s export loop (`get_element_value` → `None`/`""`/`True`/`False`
handling) already uses explicit `is None`, `== ""`, `is True`, `is False`
checks, not truthiness — safe. `group_results`/`summarise_results`
convert to `float()` inside a `try/except`, which correctly keeps a
parsed `0.0`. No candidates worth fixing found; this file had already
been sweeped by three separate PRs (blank-cell "nan" corruption,
substring/segment skip-list, and the group vs. summarise ordering bug).

### ifctester — reviewed, 0 new defects

Nine open PRs already cover `ifctester` wrong-verdict, casting,
restriction-digit, and pset/material-crash defects across `ids.py`,
`facet.py`, and `reporter.py`. `facet.py:136`
(`(not requirement) or isinstance(requirement, Entity) or ...`) is a
cardinality string check (`"required"`/`"optional"`), not a numeric
value — the entity-wrapper-truthiness exemption applies once
`requirement` is a facet object. `webapp/public/worker/api.py` (never
touched by any prior PR) contains no numeric/temporal parsing at all —
it is IDS-schema metadata lookups. No further candidates found worth
fixing.

### ifcfm — 5 confirmed defects, 1 root cause, fixed

`cobie24.py` and `cobie24legacy.py` both define:

```python
def val(x: Any) -> Any:
    return x if x not in ("", "n/a") else None
```

`val()`'s contract is "return `None` if the value is a COBie placeholder
for absent, else return the value unchanged" — critically, it returns a
genuine `0`, `0.0`, or `False` **unchanged**, not `None`. But at 43 call
sites across the two files, the result was tested with bare truthiness
(`and val(value):`, `or not val(value):`) instead of `val(value) is not
None`. `0`, `0.0`, and `False` are exactly the kind of value `val()` is
designed to let through, and the truthiness re-introduces the bug `val()`
exists to avoid.

A related, compounding bug in `get_type_data()` (`cobie24.py`) used
`warranty_x = warranty_x or props.get(...)` to let a `COBie_Warranty`
pset value be overridden by a fallback `Pset_Warranty` value only when
absent — but once a legitimate `WarrantyDurationParts = 0` was reduced
to `0` (falsy), the second, less-authoritative pset silently overwrote
it.

**Five defects reproduced end to end** (real `ifcopenshell` API, no
mocks, built via a scratch Python 3.13 interpreter — see Environment
below):

| # | Function | Input | Before | After |
|---|---|---|---|---|
| 1 | `get_attributes()` (both files) — the general custom-property exporter used by every COBie sheet | `OccupancyCount=0`, `IsCompliant=False` on a custom pset | both silently **dropped** from the whole export | both **present** |
| 2 | `get_floor_data()` (both files) | `Height=0.0` | `Height: None` | `Height: '0.0'` |
| 3 | `get_space_data()` (`cobie24.py`) | `GrossFloorArea=0.0` | `GrossArea: None` | `GrossArea: '0.0'` |
| 4 | `get_type_data()` (`cobie24legacy.py`) | `ReplacementCost=0.0` | `ReplacementCost: None` | `ReplacementCost: '0.0'` |
| 5 | `get_job_data()` (both files) | `TaskDuration=0` | `Duration: None` | `Duration: '0'` (same failure mode as the already-fixed ifc4d zero-duration-milestone bug, in a package that bug's fix never touched) |
| 6 | `get_type_data()` warranty accumulator (`cobie24.py`) | `COBie_Warranty.WarrantyDurationParts=0` **and** a fallback `Pset_Warranty.WarrantyPeriod=5` on the same element | `WarrantyDurationParts: '5'` (wrong pset won) | `WarrantyDurationParts: 0` (correct pset's explicit zero wins) |

(Table has 6 rows because #6 is a second, compounding bug found during
the same investigation; the "5 confirmed defects" count in the summary
groups #1-#5 as the primary pattern and #6 as the accumulator variant of
the same root cause.)

Item #6's "before" value was captured by running the **actual pre-fix
code** (`git show HEAD:...cobie24.py`) against the repro script, not by
reasoning about it — confirms the `or`-accumulator failure mode
independently of the `val()` truthiness failure mode.

## Fix

All 43 `and val(value):` / `or not val(value):` sites in `cobie24.py` and
`cobie24legacy.py` changed to `val(value) is not None:` / `val(value) is
None:`. The four warranty accumulator pairs in `cobie24.py` changed from
`X = X or props.get(...)` to an explicit `if X is None: X = props.get(...)`.

One follow-on regression was caught before shipping: `cobie24legacy.py`'s
`AssetType` branch called `value.strip()` immediately after the gate,
which assumed a string. Since the fix now also lets non-string falsy
values (`0`, `False`) through the gate, an `AssetType` property with a
non-string falsy value would crash. Fixed by coercing with `str(value)`
first.

Verified with a full-pipeline smoke test
(`ifcfm.Parser(preset="cobie24").parse(...)`) on a model carrying a
`Height=0.0, IsAccessible=False` custom pset — no crash, and
`IsAccessible = False` correctly appears in the parsed `Attribute`
category.

Added `src/ifcfm/test.py` (the package had no test suite in `v0.8.0`),
9 tests, all passing. Linted clean with the project's `black`/`ruff`.

## Environment

Built per the brief: `python-3.13.6` from
`build/Darwin/arm64/10.15/install/` copied to a scratch dir (no
exclusion on this copy, since it holds the pre-built `.so`), then the
worktree's `src/*/**.py` sources rsynced over the scratch `site-packages`
with `--exclude='*.so'`. Confirmed `ifcopenshell.__file__` resolved into
the scratch copy. Installed `isodate`, `python-dateutil`, `networkx`,
`typing_extensions`, `numpy`, `shapely`, `lark`, `pytest`; confirmed all
35 `ifcopenshell.api.*` submodules import, including the five that
silently no-op without `isodate`/`dateutil`
(`classification`, `cost`, `library`, `resource`, `sequence`). Scratch
environment deleted after use (`/tmp/falsy-sweep-py313`, `/tmp/repro_*.py`,
`/tmp/ifcfm_testrun`, `/tmp/*.sh`, `/tmp/orig_ifcfm_check`).

## Verdict on hunting this archetype further here

Low yield outside `ifcfm`: `ifc4d`, `ifc5d`, `ifccsv` and `ifctester`
have each already had 3-9 PRs specifically targeting wrong-number,
wrong-verdict, and falsy-trap-shaped defects in the last cycle, and
tracing candidates in those packages here turned up nothing new (one
already-fixed instance re-confirmed, three ruled out by running them).
`ifcfm` had not been swept for this specific archetype before (its three
open PRs are all crash guards) and turned up a systemic, single-root-cause
defect across two entire files. If this archetype is hunted again, the
next-highest-value unswept surface in this scope is exhausted; look
outside `ifc4d/ifc5d/ifcfm/ifccsv/ifctester` instead.
