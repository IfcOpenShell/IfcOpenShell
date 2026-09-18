# This file was generated with the assistance of an AI coding tool.
#
# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Benchmark a Bonsai spatial-visibility operator against a heavy IFC file.

This script must be run *inside* headless Blender (it imports ``bpy``),
since it is timing a real Bonsai operator, not bare ifcopenshell. See
``test/performance/README.md`` in this directory for the full before/after
workflow: this same script is run unmodified once per code state (e.g. once
with ``SRC_BONSAI`` pointing at a pre-fix worktree, once at a post-fix
worktree), and the two JSON results are compared.

Example::

    /Applications/Blender5.2.app/Contents/MacOS/Blender -b -P benchmark_visibility.py \\
        -- --ifc /tmp/heavy_3000.ifc --src-bonsai /path/to/worktree/src/bonsai \\
           --out /tmp/result_after.json

Everything the script needs is passed after a literal ``--`` (Blender's own
argument separator), so Blender doesn't try to parse them itself.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time


def _parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ifc", required=True, help="Path to the heavy .ifc file to load")
    parser.add_argument("--src-bonsai", required=True, help="Path to a src/bonsai checkout to benchmark")
    parser.add_argument("--out", required=True, help="Where to write the JSON result")
    parser.add_argument("--repeats", type=int, default=7, help="Timed repeats per scenario (default: 7)")
    parser.add_argument(
        "--small-container-name",
        default=None,
        help="Name of a single small container (e.g. one storey) to isolate. "
        "Defaults to the middle storey found in the file.",
    )
    return parser.parse_args(argv)


def _load_bonsai_from(src_bonsai: str):
    """Force `import bonsai` to resolve from `src_bonsai`, per this repo's dev-loop convention.

    A dev extension named `bl_ext.raw_githubusercontent_com.bonsai` is expected to already be
    registered in Blender's user extensions (see test/performance/README.md for setup). We only
    use it to get Blender to run the addon's register() hooks; the actual `bonsai` package is
    then imported fresh from whichever `src_bonsai` checkout the caller points at, by shadowing
    sys.path, so the same script can benchmark two different code states without reinstalling
    anything.
    """
    import bpy

    for mod in ("bl_ext.user_default.bonsai", "bl_ext.raw_githubusercontent_com_001.bonsaiPR"):
        try:
            bpy.ops.preferences.addon_disable(module=mod)
        except Exception:
            pass
    for name in [m for m in list(sys.modules) if m == "bonsai" or m.startswith("bonsai.")]:
        del sys.modules[name]
    try:
        bpy.app.translations.unregister("bonsai")
    except Exception:
        pass

    if src_bonsai in sys.path:
        sys.path.remove(src_bonsai)
    sys.path.insert(0, src_bonsai)

    bpy.ops.preferences.addon_enable(module="bl_ext.raw_githubusercontent_com.bonsai")
    import bonsai  # noqa: F401

    assert bonsai.__file__.startswith(src_bonsai), f"bonsai loaded from {bonsai.__file__}, expected {src_bonsai}"


def _reset_visibility():
    import bpy

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        try:
            obj.hide_set(False)
        except Exception:
            pass
        bim_props = getattr(obj, "BIMObjectProperties", None)
        if bim_props is not None:
            if hasattr(bim_props, "is_manually_hidden"):
                bim_props.is_manually_hidden = False
            if hasattr(bim_props, "is_hidden_by_status"):
                bim_props.is_hidden_by_status = False


def _time_operator(fn, repeats: int) -> dict:
    # One untimed warm-up call to avoid attributing first-call caching effects to the fix itself.
    fn()
    _reset_visibility()
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
        _reset_visibility()
    return {
        "samples": samples,
        "min": min(samples),
        "median": statistics.median(samples),
        "mean": statistics.mean(samples),
    }


def main():
    args = _parse_args()
    _load_bonsai_from(args.src_bonsai)

    import bpy
    import ifcopenshell.util.element

    import bonsai.tool as tool

    bpy.ops.bim.load_project(filepath=args.ifc, is_advanced=False, should_start_fresh_session=True)
    ifc = tool.Ifc.get()
    total_products = len(ifc.by_type("IfcProduct"))

    bpy.ops.bim.import_spatial_decomposition()
    props = tool.Spatial.get_spatial_props()

    containers = list(props.containers)
    storeys = [c for c in containers if c.ifc_class == "IfcBuildingStorey"]
    building_index, building = next((i, c) for i, c in enumerate(containers) if c.ifc_class == "IfcBuilding")

    if args.small_container_name:
        small_index, small = next(
            (i, c)
            for i, c in enumerate(containers)
            if c.ifc_class == "IfcBuildingStorey" and c.name == args.small_container_name
        )
    else:
        small = storeys[len(storeys) // 2]
        small_index = containers.index(small)

    small_entity = ifc.by_id(small.ifc_definition_id)
    small_element_count = len(set(ifcopenshell.util.element.get_decomposition(small_entity)))

    result = {
        "ifc_path": args.ifc,
        "src_bonsai": args.src_bonsai,
        "total_products": total_products,
        "small_container_name": small.name,
        "small_container_element_count": small_element_count,
        "repeats": args.repeats,
        "scenarios": {},
    }

    # Scenario 1: isolate ONE small storey out of a large multi-storey model.
    # This is the case sboddy's concern targets: a small filtered set, but the fix's
    # ISOLATE loop walks every IfcProduct in the whole file to decide what to re-show.
    props.active_container_index = small_index
    props.should_include_children = True

    def isolate_small():
        bpy.ops.bim.set_element_visibility(mode="ISOLATE", should_filter=False)

    result["scenarios"]["isolate_one_storey"] = _time_operator(isolate_small, args.repeats)

    # Scenario 2: isolate the WHOLE building (filtered set ~= total element count).
    props.active_container_index = building_index
    props.should_include_children = True

    def isolate_building():
        bpy.ops.bim.set_element_visibility(mode="ISOLATE", should_filter=False)

    result["scenarios"]["isolate_whole_building"] = _time_operator(isolate_building, args.repeats)

    # Scenario 3: HIDE the one small storey (no isolate loop, just the filtered-set write path).
    props.active_container_index = small_index

    def hide_small():
        bpy.ops.bim.set_element_visibility(mode="HIDE", should_filter=False)

    result["scenarios"]["hide_one_storey"] = _time_operator(hide_small, args.repeats)

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {args.out}")
    print(json.dumps(result["scenarios"], indent=2))


if __name__ == "__main__":
    main()
