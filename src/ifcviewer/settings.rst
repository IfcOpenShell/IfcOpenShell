IfcViewer settings and environment variables
=============================================

User-facing performance and quality settings (min pixel radius, LOD1
threshold, HiZ resolution, etc.) live in the **Settings** dialog and are
persisted via ``QSettings``.  This page documents the remaining
environment variables — instrumentation knobs, regression-hunting
toggles, and LOD-build tuning — that are intentionally *not* surfaced
in the GUI because they target developers and benchmark runs.

All variables are read once at first use (most are static-cached
inside the function that consumes them), so set them in the shell
before launching ``BonsaiViewer`` rather than expecting hot-toggle
behaviour.

Diagnostic and benchmark instrumentation
----------------------------------------

These variables expose hooks that are useful when triaging performance
regressions or attributing frame cost.  They have no effect on
correctness and ship disabled.

.. csv-table::
   :header: "Variable", "Default", "Description"
   :widths: 22, 14, 64

   "``IFC_HIZ_MOTION``", "on (1)", "Trust the previous frame's HiZ pyramid even when the view-projection has drifted (the default).  Set to ``0`` to revert to the strict gate, which discards the pyramid the moment the camera moves — useful when chasing the *missing-geometry* class of HiZ correctness bug, since strict gating reproduces a known-good baseline."
   "``IFC_CULL_THREADS``", "on (1)", "Set to ``0`` to disable the multi-threaded culling path.  Forces a single-threaded sweep through every model's BVH, which is useful when bisecting a regression suspected to live in the parallel cull."
   "``IFC_SKIP_MDI``", "off", "Set to ``1`` to skip ``glMultiDrawElementsIndirect`` calls without changing any other state.  Cull, upload, and bind still run; only the actual draw is elided.  A large FPS jump means the workload is draw-bound (GPU front-end) rather than upload- or cull-bound."
   "``IFC_MAX_SUBDRAWS``", "unlimited", "Truncate the drawcount passed to each MDI to ``N``, preserving the forward/reflected ratio.  Lets you isolate per-subdraw command-processor overhead from raw triangle work — sweep ``N`` and watch where the FPS curve flattens."
   "``IFC_FPS_HITCH_MS``", "0 (off)", "When non-zero, log a ``[fps-hitch]`` line for any frame that costs more than ``N`` ms.  Only active in FPS (first-person) navigation mode.  Captures visible objects, sub-draws, and HiZ-rejection counts per hitch so the slowdown can be attributed."
   "``IFC_SUBDRAW_DIAG``", "off", "When set (any non-empty value), prints a one-shot histogram of sub-draw composition after the next ``finalizeModel`` — bucket counts of MDIs by sub-draw size, plus instances and triangles in each bucket.  Useful for tuning the visible-list packing strategy."

LOD build tuning
----------------

These affect how the LOD1 representation is generated when a sidecar
is *baked*; loading an existing ``.ifcfed`` does not re-read them.
Override only when you're regenerating sidecars and want to inspect or
adjust the trade-off between LOD0 fidelity and LOD1 triangle savings.

.. csv-table::
   :header: "Variable", "Default", "Description"
   :widths: 22, 14, 64

   "``IFC_LOD_ERROR``", "0.05 (clamped to ≥ 0.2)", "``meshopt_simplify`` ``target_error`` parameter — maximum positional error allowed when collapsing edges, normalised to the mesh AABB diagonal.  BIM meshes are typically non-manifold and a 0.2 floor still looks fine at sub-4 pixel sizes; smaller values often produce zero collapses on these inputs."
   "``IFC_LOD_RATIO``", "meshopt default", "``meshopt_simplify`` ``target_ratio`` parameter — desired fraction of the original index count to retain.  Combined with ``target_error`` it forms the simplification budget."
   "``IFC_LOD_MIN_SAVINGS``", "0.25", "Minimum fraction of triangles that must be eliminated for the LOD1 result to be accepted.  Below this, the LOD1 slot is left empty and LOD0 is always drawn for that mesh — avoids paying upload cost for trivial reductions."
   "``IFC_LOD_DEBUG``", "off", "Set to ``1`` to print per-mesh LOD build diagnostics for the first few meshes of each ``buildLodsForSidecar`` call: input/output triangle counts, target error, and the accept/reject decision.  Caps printing automatically so it can be left on for full builds without flooding the log."

GUI-promoted settings (no longer env-var driven)
------------------------------------------------

For reference, the following knobs were previously read from
environment variables and are now driven by ``AppSettings`` and the
**Settings** dialog.  Their old env-var spellings no longer have any
effect.

.. csv-table::
   :header: "Setting", "QSettings key", "Old env var", "Default"
   :widths: 28, 32, 22, 18

   "Min Pixel Radius", "``viewport/min_pixel_radius``", "``IFC_MIN_PX``", "2.0"
   "Motion Min Pixel Radius", "``viewport/motion_min_pixel_radius``", "``IFC_MIN_PX_MOTION``", "10.0"
   "LOD1 Pixel Threshold", "``viewport/lod1_pixel_threshold``", "``IFC_LOD1_PX``", "30.0"
   "HiZ Occlusion", "``viewport/hiz_enabled``", "``IFC_NO_HIZ`` (inverted)", "on"
   "HiZ Resolution", "``viewport/hiz_resolution``", "``IFC_HIZ_SIZE``", "256"
