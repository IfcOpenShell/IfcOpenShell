Environment variables and developer settings
============================================

User-facing performance and quality settings (min pixel radius, LOD1
threshold, HiZ resolution, …) live in the **Settings** dialog and are
persisted via ``QSettings``. This page documents the remaining
environment variables — instrumentation knobs, regression-hunting
toggles, and LOD-build tuning — that are intentionally *not* surfaced
in the GUI because they target developers and benchmark runs.

All variables are read once at first use (most are static-cached
inside the function that consumes them), so set them in the shell
before launching ``BonsaiViewer`` rather than expecting hot-toggle
behaviour.

Renderer (wgpu) knobs
---------------------

These steer the wgpu backend's renderer / cull / streaming subsystems.
They have no effect on geometric correctness and ship disabled.

.. csv-table::
   :header: "Variable", "Default", "Description"
   :widths: 26, 14, 60

   "``WGPU_HIZ``", "off (0)", "Set to ``1`` to enable HiZ occlusion culling. Disabled by default since task #58 surfaced HiZ false-rejection bugs on certain camera angles; will return to on-by-default once the strict-vs-loose gating is settled."
   "``WGPU_HIZ_MOTION``", "off (0)", "Trust the previous frame's HiZ pyramid even when the view-projection has drifted (matches the old GL backend's behaviour). Default ``0`` is strict: any VP delta invalidates the pyramid for this frame, so transparent windows and other view-dependent surfaces aren't culled against stale depth. Set to ``1`` when chasing perf to re-enable the loose path."
   "``WGPU_HIZ_TRACE``", "off", "Set to ``1`` to arm a one-shot per-frame log when HiZ is about to reject instances. Dumps the pyramid's bottom rows + per-rejection details. Useful for diagnosing the *missing-geometry* class of HiZ correctness bug — task #58."
   "``WGPU_MIN_PX``", "GUI value", "Override the ``viewport/min_pixel_radius`` setting from the shell. Stationary contribution-cull threshold in pixels: instances whose sphere projection falls below this are dropped from the visible list. Useful for sweeping in benchmarks without flipping the GUI value back and forth."
   "``WGPU_MIN_PX_MOTION``", "GUI value", "Same as above for ``viewport/motion_min_pixel_radius`` — the (typically larger) threshold applied while the camera is moving."
   "``WGPU_CULL_THREADS``", "on", "Set to ``0`` to disable the per-model ``std::async`` dispatch. Forces every model's cull pass to run sequentially on the main thread — used to measure the parallel-cull speedup and to bisect regressions suspected to live in the worker join."
   "``WGPU_PRESENT_MODE``", "(auto)", "Override the surface present mode. Accepts ``fifo``, ``fifo_relaxed``, ``mailbox``, or ``immediate``. Default picks the first of Mailbox → Immediate → FifoRelaxed → Fifo that the surface actually advertises. Useful for fly-mode input-latency triage — see :doc:`debug-output` for the full rationale."
   "``WGPU_FLY_DEBUG``", "off (0)", "Set to ``1`` to print a per-frame ``[fly] dt=X.XXms render_gap=Y.YYms`` line while fly mode is active. Diagnoses pacing irregularities — see the fly-mode latency notes in :doc:`debug-output`."
   "``WGPU_NAV_PRESET``", "``blender``", "Mouse-navigation preset. ``blender`` (MMB orbit, Shift+MMB pan, scroll dolly), ``rhino``, or ``revit``. Selection always stays on LMB. Mirrors the GL backend's preset model — see ``AppSettings::NavPreset``."
   "``WGPU_STREAM_DEBUG``", "off (0)", "Set to ``1`` to enable per-frame ``[stream-debug]`` logging. Reports residency state, pool occupancy, eviction decisions, and per-chunk priority scores. Used to triage streaming residency thrash on big federations."
   "``WGPU_STREAM_DEEP_DEBUG``", "off", "When set (any value), every 120th frame in interactive mode dumps the priority-projection AABBs of all currently *missing* visible chunks. Lets the loader's chunk-priority math be inspected without breaking out of normal navigation. Pairs with ``WGPU_STREAM_DEBUG``."
   "``WGPU_STREAM_EVICT_LOG``", "off", "When set (any value), each eviction prints the candidate chunk + the chunk it displaced plus their priority scores. Useful when ``driveStreamingLoads`` appears to thrash but the per-frame totals look stable."

LOD build tuning
----------------

These affect how the LOD1 representation is generated when a sidecar
is *baked*; loading an existing ``.ifcfed`` does not re-read them.
Override only when you're regenerating sidecars and want to inspect or
adjust the trade-off between LOD0 fidelity and LOD1 triangle savings.

.. csv-table::
   :header: "Variable", "Default", "Description"
   :widths: 26, 14, 60

   "``IFC_LOD_ERROR``", "0.05 (clamped to ≥ 0.2)", "``meshopt_simplify`` ``target_error`` parameter — maximum positional error allowed when collapsing edges, normalised to the mesh AABB diagonal. BIM meshes are typically non-manifold and a 0.2 floor still looks fine at sub-4 pixel sizes; smaller values often produce zero collapses on these inputs."
   "``IFC_LOD_RATIO``", "meshopt default", "``meshopt_simplify`` ``target_ratio`` parameter — desired fraction of the original index count to retain. Combined with ``target_error`` it forms the simplification budget."
   "``IFC_LOD_MIN_SAVINGS``", "0.25", "Minimum fraction of triangles that must be eliminated for the LOD1 result to be accepted. Below this, the LOD1 slot is left empty and LOD0 is always drawn for that mesh — avoids paying upload cost for trivial reductions."
   "``IFC_LOD_DEBUG``", "off", "Set to ``1`` to print per-mesh LOD build diagnostics for the first few meshes of each ``buildLodsForSidecar`` call: input/output triangle counts, target error, and the accept/reject decision. Caps printing automatically so it can be left on for full builds without flooding the log."
