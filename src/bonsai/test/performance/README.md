<!-- This file was generated with the assistance of an AI coding tool. -->

# Bonsai performance-regression testing utility

Tools for answering a specific kind of question: "does this Bonsai change
introduce a meaningful performance regression on a large, real-world-sized
model?" A functional fix can pass every unit test and still turn an O(1)
Blender operator call into an O(n) Python loop that is fine on a 20-element
test file and slow on a 5000-element real project. These two scripts let you
measure that, with real before/after numbers instead of a guess.

There are two independent pieces:

1. `generate_heavy_model.py` — builds a large, IFC-valid synthetic model
   (no `bpy` dependency, just `ifcopenshell`).
2. `benchmark_visibility.py` — loads a generated model into headless Blender
   and times a Bonsai operator. This one *does* need `bpy`, since it is
   timing real Bonsai/Blender behaviour, not bare `ifcopenshell`.

Neither script is specific to one bug. `generate_heavy_model.py` is a
general-purpose heavy-fixture generator; `benchmark_visibility.py` currently
times the spatial-visibility operator (`bim.set_element_visibility`) but is
a short, readable template for timing any other Bonsai operator the same
way — swap out the scenario functions in `main()`.

## 1. Generating a heavy fixture

```sh
cd src/bonsai/test/performance
python3 generate_heavy_model.py --out /tmp/heavy.ifc --walls 3000 --storeys 10
```

This produces a Project > Site > Building > N Storeys hierarchy. Each storey
is a rectangular grid of walls (real body geometry via
`ifcopenshell.api.geometry.add_wall_representation`/`create_2pt_wall`, so
representations aren't empty shells), some interior grid cells get an
`IfcSpace`, and a configurable fraction of walls get an `IfcDoor` or
`IfcWindow` filling (with their own body representations, related via
`IfcRelVoidsElement`/`IfcRelFillsElement`).

Useful flags (all have defaults, none are hardcoded):

- `--walls N` — target total wall count across the whole model.
- `--storeys N` — number of `IfcBuildingStorey` elements.
- `--spaces-per-storey N` — `IfcSpace` count per storey.
- `--door-every N` / `--window-every N` — insert a filling every Nth
  interior/perimeter wall segment (0 disables).
- `--schema IFC4|IFC4X3|...`

Or call it as a library:

```python
from generate_heavy_model import generate_heavy_model
stats = generate_heavy_model("/tmp/heavy.ifc", wall_count=5000, storeys=15)
```

**Do not commit the generated `.ifc` file.** It's a throwaway fixture,
regenerate it whenever you need one. A 3000-wall / 10-storey file takes
about 8 seconds to generate and is ~5.7 MB.

## 2. Benchmarking before vs after

The harness assumes you have two code states to compare — typically a
pre-fix and a post-fix checkout of `src/bonsai`. The cleanest way to get
both without disturbing your main working copy is two separate git
worktrees:

```sh
git worktree add ../wt-before <pre-fix-ref>
git worktree add ../wt-after  <post-fix-ref>   # or your current branch
```

`benchmark_visibility.py` needs `bpy`, so it must run inside a real Blender
binary, not bare Python. It resolves the `bonsai` package from whatever
`--src-bonsai` path you give it (by shadowing `sys.path` and clearing
`sys.modules`), so **the same script, unmodified, can benchmark two
different worktrees** just by pointing `--src-bonsai` at each in turn:

```sh
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender   # adjust for your platform

$BLENDER -b -P benchmark_visibility.py -- \
  --ifc /tmp/heavy.ifc --src-bonsai /path/to/wt-before/src/bonsai \
  --out /tmp/result_before.json --repeats 7

$BLENDER -b -P benchmark_visibility.py -- \
  --ifc /tmp/heavy.ifc --src-bonsai /path/to/wt-after/src/bonsai \
  --out /tmp/result_after.json --repeats 7
```

Note the literal `--` before the script's own arguments — that's Blender's
argument separator, without it Blender tries to parse your flags itself.

This script requires a Blender extension entry named
`bl_ext.raw_githubusercontent_com.bonsai` to already be registered in your
Blender profile (any dev checkout registered as an unofficial/URL
extension works; only its `register()`/`unregister()` hooks are used — the
actual `bonsai` package is then imported fresh from `--src-bonsai`, not from
the registered extension's own files). If your local Blender profile uses a
different extension module name for this purpose, adjust the two
`bpy.ops.preferences.addon_*` calls in `_load_bonsai_from()` accordingly.

Each run: loads the heavy file via `bpy.ops.bim.load_project`, populates the
Spatial Manager container tree via `bpy.ops.bim.import_spatial_decomposition`,
then times three scenarios with `time.perf_counter()`, each preceded by one
untimed warm-up call and followed by a full visibility reset (not counted):

- `isolate_one_storey` — Isolate a single storey out of the whole model
  (small filtered set, large total element count). This is the scenario
  that exposes a per-element loop over *every* element in the file, even
  though only a small subset is the target.
- `isolate_whole_building` — Isolate the whole building (filtered set ~=
  total element count).
- `hide_one_storey` — Hide a single storey (no "isolate" full-file scan,
  just the per-filtered-element write path).

Compare the **relative** delta between the two JSON results, not their
absolute values — absolute timings are noisy across machines, thermal
state, and background load. Re-run a couple of times if the two numbers are
close; system noise on a shared/laptop machine can easily be tens of percent
run-to-run for the same code.

## Worked example: PR #8720

PR #8720 ("compose element visibility with the Status filter instead of
overwriting it") rewrote `SetElementVisibility`'s Isolate mode from two bulk
`bpy.ops.object.hide_view_set` calls to an explicit Python loop over every
`IfcProduct` in the file. Benchmarked on this machine with the tools above
(3000-wall and 6000-wall generated models, 7 timed repeats each, before =
`v0.8.0` HEAD at the PR's merge-base, after = the PR's branch tip):

| Scenario | Products | Before (median) | After (median) | Delta |
|---|---|---|---|---|
| Isolate 1 storey | 4172 | 0.162 s | 0.431 s | **+166%** |
| Isolate 1 storey | 8138 | 0.382 s | 1.481 s | **+288%** |
| Isolate whole building | 4172 | 0.671 s | 0.858 s | +28% |
| Isolate whole building | 8138 | 2.564 s | 2.928 s | +14% |
| Hide 1 storey | 4172 | 0.161 s | 0.156 s | ~0% (noise) |
| Hide 1 storey | 8138 | 0.376 s | 0.400 s | +6% |

The regression is real, and it gets worse as the model grows: isolating one
small storey out of a bigger file went from a 166% slowdown at ~4200
elements to a 288% slowdown at ~8100 elements, consistent with the fix's new
loop being O(total elements in file) rather than O(filtered elements),
whereas the old `hide_view_set`-based code paid a roughly constant cost
regardless of how many elements were outside the isolated set. Isolating the
*whole* building (where the filtered set is nearly the whole file) and
plain Hide/Show (no full-file scan at all) show only a modest, largely
noise-level difference, because those paths don't hit the new full-scan
loop, or both old and new code already paid a similar per-element cost
there.
