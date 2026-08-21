/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef WGPUMODELGPUDATA_H
#define WGPUMODELGPUDATA_H

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <cstddef>
#include <cstdint>
#include <limits>
#include <string>
#include <unordered_map>
#include <vector>

#include "InstancedGeometry.h"
#include "BufferPool.h"
#include "FederationMath.h"   // ModelUnits
#include "ChunkPlanner.h"  // WGPU_CHUNK_VERTEX_BYTES_LIMIT (shared with bake)
#include "SidecarCache.h"  // ElementTableRecord (element metadata)

// Per-model wgpu state. Mirrors the GL backend's ModelGpuData but with
// wgpu handles. Stage 2 only allocates and uploads the four core buffers;
// bind groups, pipelines, BVH and cull scratch land in later stages.
//
// All vertex/index/mesh/instance bytes are uploaded once at load time via
// wgpuQueueWriteBuffer. The vertex storage buffer is read by the vertex
// shader (vertex pulling), not used as a classic vertex buffer — there is
// no input-assembler vertex layout to match.
// Web (WebGPU) mandates `maxStorageBufferBindingSize` ≥ 128 MB; some browsers
// grant more, but we plan for the floor. Applied identically on desktop —
// the cost is a few extra draws per frame (1 per chunk; typical models =
// 1–3 chunks), which is invisible compared to per-frame GPU work.
//
// At INSTANCED_VERTEX_STRIDE_BYTES = 12 B/vertex this caps a chunk at
// ~1.4 M vertices. 16 MB is the sweet spot once background-thread I/O
// (StreamingThread) is in place: scatter-gather per-mesh seeks
// happen on the worker, not the render thread, so smaller chunks
// (and thus more per-frame loads as orbit shifts) no longer stall
// rendering. The win is much finer pool-allocation granularity —
// a 3 GB pool fits ~190 chunks vs ~21 at 128 MB — so visible
// geometry is far less likely to get "trapped" behind invisible
// chunkmates. Pre-async this size gave 7 fps (the sync loads blocked
// the render thread); now it's bounded by cull cost not stream cost.
//
// Sidecar v14 (on-disk spatial reorder) would let us go smaller still
// (~4 MB) with single-fread chunk loads, but the difference between
// 16 MB and 4 MB is much smaller than the difference between 128 MB
// and 16 MB.
//
// The limit itself lives in ChunkPlanner.h (pure, no wgpu) so the bake-time
// layout pass can share it; re-exported here for the existing call sites.

struct ModelGpuData {
    // std430 layout: 16 bytes per entry, naturally aligned. base_vertex is
    // CHUNK-LOCAL — the bound vertex_storage on that chunk's bind group
    // gives the right slice when the shader indexes vertices[].
    struct alignas(16) VisibleDrawGpu {
        uint32_t mesh_id;        // -> meshes[] for quantisation basis
        uint32_t instance_idx;   // -> instances[] for transform + ids
        uint32_t ebo_first_u32;  // start of this entry's slice in indices[] (global)
        uint32_t base_vertex;    // chunk-local start of this mesh's slice in vertex_storage
    };
    static_assert(sizeof(VisibleDrawGpu) == 16, "VisibleDrawGpu must be 16 bytes");

    // Per-chunk state. Each chunk references a vertex range and an
    // index range inside ViewportWindow::pool_, plus a small set of
    // per-frame buffers (visible_draws, prefix_sums, uniform) and a bind
    // group that binds the pool ranges alongside the model-shared
    // mesh/instance storage. Rendering issues one drawcall per non-empty
    // chunk.
    //
    // Streaming (task #16): a chunk may be marked is_resident=false; its
    // pool ranges (pool_*_size == 0) and bind_group are then unclaimed
    // until the streaming loader brings it in. Other per-chunk buffers
    // (visible_draws etc.) stay allocated regardless because cull still
    // needs them. Non-streaming path always sets is_resident=true and
    // populates pool ranges at applyCachedModel time.
    struct Chunk {
        // Pool-allocated vertex + index bytes. Both slices land in the
        // shared ViewportWindow::pool_; the slice tells us which
        // sub-buffer they live in (the pool may span multiple sub-buffers
        // when scenes exceed wgpu's single-buffer cap). When non-resident,
        // both .size are 0.
        BufferPool::Slice vertex_slice;
        BufferPool::Slice index_slice;

        WGPUBuffer    visible_draws_buffer    = nullptr;
        WGPUBuffer    prefix_sums_buffer      = nullptr;
        WGPUBuffer    per_chunk_uniform       = nullptr;
        WGPUBindGroup bind_group              = nullptr;

        uint32_t      vertex_count            = 0;   // chunk capacity (vertices)
        size_t        visible_draws_capacity  = 0;
        size_t        prefix_sums_capacity    = 0;

        // Per-frame, populated by cullModelCpuCompute and consumed by render().
        // total_visible_* are post-frustum + contribution + HiZ — used to size
        // the actual draw call. frustum_visible_count is bumped immediately
        // after the frustum check (before contribution / HiZ), and is what
        // driveStreamingLoads keys on for residency decisions. Streaming
        // must NOT use the HiZ-post counters: HiZ visibility flips
        // frame-to-frame as occluders shift, which would otherwise thrash
        // the loader (evict-then-reload every frame even with the camera
        // stationary, killing FPS and producing visible flicker).
        uint32_t      total_visible_vertices  = 0;
        uint32_t      total_visible_draws     = 0;
        uint32_t      frustum_visible_count   = 0;
        // Instances that passed frustum AND the contribution cull (projected
        // radius ≥ min_radius_px), but BEFORE HiZ. Streaming gates on this so
        // it only fetches chunks big enough on screen to actually draw —
        // without coupling to HiZ occlusion (which flips frame-to-frame and
        // would thrash the loader). Stable while the camera is still; changes
        // only on navigation, which is exactly when the working set should.
        uint32_t      contribution_visible_count = 0;

        // Opaque-first partition counts.  The cull loop fills
        // visible_draws_scratch with all opaque visible instances first,
        // then all transparent ones; cumulative prefix_sums_scratch spans
        // both. The opaque-pass draw call uses firstVertex=0 and
        // vertexCount=opaque_visible_vertices; the transparent-pass draw
        // call uses firstVertex=opaque_visible_vertices and
        // vertexCount=(total_visible_vertices - opaque_visible_vertices).
        // 0 means no opaque (transparent-only chunk) or no transparent
        // (opaque-only chunk) — the render loop skips empty halves.
        uint32_t      opaque_visible_vertices = 0;
        uint32_t      opaque_visible_draws    = 0;

        std::vector<VisibleDrawGpu> visible_draws_scratch;
        std::vector<uint32_t>       prefix_sums_scratch;

        // What was last handed to the GPU, so an unchanged frame writes
        // nothing. On Dawn-web every wgpuQueueWriteBuffer is an IPC message to
        // the GPU process, and the cull re-uploaded all three buffers for every
        // chunk on every frame — measured at 370-546 writes and up to 1 MB per
        // frame across this federation, which is ~22,000 messages a second at
        // 60fps. Comparing here costs a memcmp of the same bytes; sending them
        // costs a serialised round trip through the wire.
        std::vector<VisibleDrawGpu> visible_draws_uploaded;
        std::vector<uint32_t>       prefix_sums_uploaded;
        uint32_t                    uniform_uploaded[4] = { 0xffffffffu, 0, 0, 0 };

        // Transient transparent-half scratch. Populated alongside
        // visible_draws_scratch during cull (the cull loop routes each
        // visible instance to opaque or transparent based on the
        // mesh_has_alpha + color_override_rgba8 classification). After
        // the chunk's instances are walked, the post-process step appends
        // these entries onto visible_draws_scratch and continues the
        // prefix-sum sequence, yielding a single buffer/upload with
        // [opaque-draws][transparent-draws] partitioning. Cleared at the
        // start of each cull alongside visible_draws_scratch.
        std::vector<VisibleDrawGpu> visible_draws_scratch_transparent;
        std::vector<uint32_t>       transparent_per_draw_vertex_counts;

        // Residency. Streaming sets is_resident=false at applyCachedModel
        // and flips true once the chunk's vertex bytes are uploaded.
        // Render and pick skip chunks where !is_resident.
        bool     is_resident                  = true;
        // Set true while a worker-thread read is in flight for this
        // chunk. Prevents driveStreamingLoads from re-enqueueing it
        // every frame until its result is drained. Cleared when the
        // result is applied (or dropped on failure / stale model).
        // Eviction is not gated on this (eviction only acts on resident
        // chunks; a loading chunk has no slice to free yet).
        bool     is_loading                   = false;

        // Aggregate vertex / index sizes across all meshes in this chunk
        // (sum of mesh.vertex_count * stride / mesh.index_count for each
        // mesh in mesh_ids). Used to size the pool allocation and to
        // compute the cull's per-chunk free-room check. Per-mesh layout
        // is recovered by walking mesh_ids and the model's MeshInfo[].
        uint64_t vertex_byte_size             = 0;
        uint64_t index_count                  = 0;
        // v16: where this chunk's two zstd frames live in the file's geometry
        // section (offsets relative to model.geometry_section_offset) and their
        // compressed sizes. The raw sizes are vertex_byte_size / index_count*4.
        // A per-chunk load fetches [off, +comp) and decompresses.
        uint64_t v_comp_off                   = 0;
        uint64_t v_comp_size                  = 0;
        uint64_t i_comp_off                   = 0;
        uint64_t i_comp_size                  = 0;
        // Of `index_count`, how many are LOD1 indices. LOD0 indices occupy
        // chunk-local u32 offsets [0, index_count - lod1_index_count); LOD1
        // indices occupy [index_count - lod1_index_count, index_count). 0
        // when no mesh in this chunk had a baked LOD1 slice.
        uint32_t lod1_index_count             = 0;

        // World-space AABB covering every instance whose mesh lives in
        // this chunk. With spatial chunk planning this AABB is tight
        // (chunks group meshes by world centroid, not mesh-id), so the
        // distance-based evictor can meaningfully tell chunks apart.
        // Used by cull to reject whole chunks against the frustum before
        // iterating instances — and by the streaming loader to
        // prioritise which non-resident chunks to fetch first.
        float    aabb_min[3]                  = {  std::numeric_limits<float>::infinity(),
                                                    std::numeric_limits<float>::infinity(),
                                                    std::numeric_limits<float>::infinity() };
        float    aabb_max[3]                  = { -std::numeric_limits<float>::infinity(),
                                                   -std::numeric_limits<float>::infinity(),
                                                   -std::numeric_limits<float>::infinity() };

        // Mesh IDs assigned to this chunk, in chunk-local layout order.
        // Spatial chunk planning sorts meshes by world centroid first,
        // so this list is not in mesh-id order in general — each mesh's
        // bytes live at scattered offsets in the sidecar file. The
        // loader walks this list to scatter-gather the chunk's vertex
        // + index bytes; mesh_chunk_local_base_vertex /
        // mesh_chunk_local_ebo_first_u32 are computed in this same
        // order at planning time so the cull's VisibleDrawGpu entries
        // point at the correct chunk-local offsets.
        std::vector<uint32_t> mesh_ids;

        // Instance indices belonging to this chunk (i.e. whose mesh lives
        // in this chunk). Built at chunk-planning time. Lets cull iterate
        // chunks as the outer loop, frustum-test the chunk AABB once,
        // and skip every instance inside in one shot when the chunk is
        // off-screen — far cheaper than the per-instance frustum check
        // on flat-scan culls of 1M+ instance scenes.
        std::vector<uint32_t> instance_ids;

        // LRU marker for streaming eviction. Updated to the window's
        // streaming_frame_idx_ every frame the chunk is rendered (i.e.
        // total_visible_draws > 0). The evictor picks the smallest value
        // among non-visible resident chunks when it needs to free VRAM.
        uint64_t last_visible_frame_idx       = 0;
        // EMA-smoothed visibility score, in [0, 1]. Bumped each frame
        // toward 1 when total_visible_draws > 0 (the chunk's instances
        // passed frustum + contribution + HiZ), toward 0 otherwise.
        // Time constant ~30 frames. Used by the streaming evictor to
        // de-prioritise chunks that are technically in the frustum but
        // consistently HiZ-occluded — e.g. interior pipes behind a
        // building's exterior walls. The smoothing prevents thrash from
        // momentary HiZ flicker (a wall briefly visible behind a panning
        // window doesn't displace the window from the pool).
        float    visibility_history           = 0.0f;
        // streaming_frame_idx_ when this chunk was last loaded. The
        // evictor grants newly-loaded chunks ~30 frames of grace at
        // full priority (max history factor = 1.0) so they have time
        // for visibility_history to develop. Without this, a just-
        // loaded chunk's effective priority drops to contribution ×
        // 0.05 next frame, and the chunk it displaced — back as a
        // candidate at full priority — re-displaces it: infinite
        // cycle between equal-priority chunks. The cycle prevents any
        // lower-priority candidate (e.g. a structural-brace chunk
        // ranked position 20 in the missing list) from ever getting
        // attempted.
        uint64_t loaded_frame_idx             = 0;
        // How many times this chunk has been (re-)loaded over the
        // session. Bumped each successful applyStreamedChunk. A chunk
        // with load_count >> 1 has been cycling — used by the stream
        // debug log (WGPU_STREAM_DEBUG=1) to surface thrash.
        uint32_t load_count                   = 0;
        // Eviction attribution — who pushed this chunk out the last
        // time? Filled by evict_lowest_priority_than when the chunk is
        // unloaded. Read by the cycle-detection logger when this chunk
        // re-enters as a candidate so we can spot A→B→A 2-cycles. Zero
        // for chunks that were never evicted or were LRU-evicted (the
        // latter doesn't have an obvious "evictor" — just a slot
        // pressure event).
        uint32_t last_evicted_by_session_model_id     = 0;
        uint32_t last_evicted_by_chunk_idx    = UINT32_MAX;
        float    last_evicted_by_priority     = 0.0f;
        // Frame at which this chunk was most recently evicted, so the
        // cycle log only fires when re-entry is "soon" (cache thrash)
        // rather than "minutes later" (legitimate camera move).
        uint64_t last_evicted_frame_idx       = 0;
        // Cooldown frame: if streaming_frame_idx_ < this, skip the
        // chunk in the candidate gather. Set when a candidate is
        // blocked OOM (eviction exhausted, still doesn't fit) OR when
        // applyStreamedChunk fails on the drained worker result. Caps
        // web bandwidth waste at one fetch per cooldown for chunks
        // that genuinely can't fit in the current pool state; the
        // cooldown expires naturally so the chunk re-enters when
        // pool layout has had a chance to change.
        uint64_t blocked_cooldown_until_frame_idx = 0;
        // Per-frame instance-aware priority. Sum of px² projected
        // contributions of every instance owned by this chunk —
        // captures the chunk's actual on-screen footprint, not the
        // (often loose) AABB union projection. Computed once per
        // frame at the top of driveStreamingLoads from the camera
        // state; the candidate/resident priority lambdas just read
        // this. See task #57 for the rationale.
        float    current_priority             = 0.0f;
    };
    std::vector<Chunk> chunks;

    // Streaming source. Non-empty path means this model was loaded via the
    // streaming path: chunks may be non-resident and need byte-range reads
    // from this file. Empty path = legacy non-streaming load.
    std::string streaming_file_path;
    // v16: file offset of the compressed geometry section. A chunk's blobs are
    // at geometry_section_offset + chunk.{v_comp_off,i_comp_off}.
    uint64_t    geometry_section_offset = 0;
    // Web only: chunk byte ranges come from the JS-side source — a picked File
    // (Blob.slice) or a remote URL (HTTP Range) — read asynchronously, not via
    // a synchronous fopen on streaming_file_path. Set by loadSidecarMetadataWeb
    // so driveStreamingLoads routes this model through the async web path
    // instead of the MEMFS sync read.
    bool        streaming_from_web = false;
    // Web analog of streaming_file_path: which registered JS byte-source
    // (Module.__ifcvSources[id] = a picked File or a remote URL) this model's
    // chunk + element metadata reads pull from. Lets several federated models stream
    // from different files at once, mirroring the desktop per-model path.
    // -1 when the model came from somewhere else (a path read on desktop, the
    // embedded sample) — source id 0 is a real source, so it can't mean "none".
    int         web_source_id = -1;

    // v15 element metadata (web, on-demand). The IFC element metadata
    // (elements + string_table — names/GUIDs, for UI/picking, never
    // rendering) lives in a separate file block fetched only when a consumer
    // asks, so first paint doesn't wait on it. Empty until
    // loadElementMetadataWeb fetches [element_metadata_comp_offset, +bytes) and parses
    // it; element_metadata_loaded latches so it fetches at most once.
    std::vector<ElementTableRecord> elements;
    std::string                    string_table;
    // v16: the element metadata block is a single zstd frame at
    // element_metadata_comp_offset of element_metadata_comp_size bytes,
    // expanding to element_metadata_raw_size.
    uint64_t    element_metadata_comp_offset = 0;
    uint64_t    element_metadata_comp_size   = 0;
    uint64_t    element_metadata_raw_size    = 0;
    bool        element_metadata_loaded      = false;
    // applyCachedModel rebases instance object_ids by this base to keep them
    // globally unique across models; element metadata records carry the sidecar's
    // original (local) ids, so they're rebased by the same amount on load.
    uint32_t    object_id_base = 0;

    // For each mesh in meshes[], the chunk it lives in plus the chunk-local
    // offsets into that chunk's vertex_storage and index_buffer. Populated
    // at applyCachedModel time; consumed by cullModelCpuCompute when it
    // populates VisibleDrawGpu entries.
    std::vector<uint32_t> mesh_chunk_idx;
    std::vector<uint32_t> mesh_chunk_local_base_vertex;
    std::vector<uint32_t> mesh_chunk_local_ebo_first_u32;
    // Where in the chunk's index slice this mesh's LOD1 indices start
    // (in u32 units). Only meaningful when m.meshes[mi].lod1_index_count > 0;
    // entries for meshes without LOD1 are 0 and unused.
    std::vector<uint32_t> mesh_chunk_local_lod1_first_u32;

    // Per-INSTANCE chunk lookup tables. Mirror the per-mesh arrays above,
    // but resolved at planning time so cull can read them directly without
    // routing through mesh_id. The split exists because the spatial-
    // bucketing planner (#55) can place the same mesh in multiple chunks
    // (mesh data duplicated when its instances live in different buckets)
    // — under that scheme `mesh_chunk_idx[mesh_id]` is ambiguous, but
    // `instance_chunk_idx[instance_id]` is always exactly one chunk.
    // The mesh-keyed planner populates these by translation
    // (instance_chunk_idx[i] = mesh_chunk_idx[instances[i].mesh_id]);
    // the spatial-bucket planner populates them directly.
    std::vector<uint32_t> instance_chunk_idx;
    std::vector<uint32_t> instance_base_vertex;
    std::vector<uint32_t> instance_ebo_first_u32;
    std::vector<uint32_t> instance_lod1_first_u32;

    // Model-shared buffers. Mesh + instance storage are small (<10 MB on
    // any real scene we've seen); the chunked index buffer lives in Chunk
    // alongside vertex_storage so streaming can defer both together.
    WGPUBuffer mesh_storage     = nullptr;   // MeshGpu[]: aabb_min/max
    WGPUBuffer instance_storage = nullptr;   // InstanceGpu[]: transform + ids

    // Cumulative VRAM accounting (bytes), populated at applyCachedModel
    // time. Sum of vertex_storage across chunks + index_buffer + mesh_storage
    // + instance_storage + per-chunk visible_draws + prefix_sums + uniforms.
    // Used by the per-frame stats log to attribute total VRAM.
    uint64_t vram_bytes_vbo = 0;   // vertex storage total
    uint64_t vram_bytes_ebo = 0;   // index buffer
    uint64_t vram_bytes_ssbo = 0;  // mesh + instance + per-chunk small buffers

    // Size mirrors for stats / range checks. vertex_bytes is the sum across
    // all chunks; index_count / mesh_count / instance_count are unchanged.
    size_t   vertex_bytes   = 0;
    uint32_t index_count    = 0;
    uint32_t mesh_count     = 0;
    uint32_t instance_count = 0;

    // CPU side, kept for cull / picking / federation recompose.
    std::vector<MeshInfo>    meshes;
    std::vector<InstanceInfo> instances;

    // Per-mesh "any vertex has alpha < 255?" flag, indexed by mesh_id.
    // Populated at uploadStreamedMesh / applyStreamedChunk as vertex bytes
    // become CPU-resident. Used at cull time to classify each instance
    // into the opaque or transparent draw partition: an instance with
    // color_override_rgba8==0 (the "use baked vertex color" sentinel)
    // routes to the transparent pass iff its mesh has alpha; an instance
    // with a non-zero override uses the override's alpha byte instead.
    // 0 means false (opaque mesh), non-zero means true (any-vertex-alpha
    // < 255). Initial size matches meshes.size(); entries default to 0
    // until a vertex chunk arrives for that mesh, so a transparent mesh
    // is briefly mis-classified as opaque between instance compose and
    // chunk arrival — corrected on the next cull tick once the chunk
    // lands.
    std::vector<uint8_t> mesh_has_alpha;

    // Local-frame volume (m³) of every mesh, indexed by mesh_id. Computed
    // once at applyCachedModel via signed-tetrahedra-from-origin on the
    // raw vertex+index data; reused by the Volume measurement tool to
    // avoid re-reading the GPU buffers per click. Empty in streaming mode
    // until the chunk holding the mesh has been delivered.
    std::vector<double> mesh_local_volumes;

    // CPU shadow of each mesh's mesh-local positions + LOD0 indices.
    // Populated at applyCachedModel (or per-chunk in streaming) from
    // the same raw vertex bytes the volume calc dequantises. The Area
    // measurement tool reads this directly — no GPU readback, matching
    // the Volume tool's policy.
    //
    // Doubles per-vertex memory (12 B/vert GPU + 12 B/vert CPU). The
    // alternative is a wgpu mapAsync readback per first-touched mesh,
    // which adds async plumbing and a per-click stall; pay the memory
    // upfront instead. Trim by sizing each entry down at population
    // (reserve exact). For huge federations this can be a real
    // working-set cost — revisit if it shows up in profiles.
    struct MeshTriangles {
        std::vector<float>    positions;  // 3 * vertex_count, mesh-local
        std::vector<uint32_t> indices;    // 3 * triangle_count, LOD0
    };
    std::vector<MeshTriangles> mesh_triangles_cache;

    // object_id (globally rebased) → instance index in `instances`.
    // Populated alongside the instance vector so the Volume tool can do
    // O(1) instance lookup instead of linear-scanning every model.
    std::unordered_map<uint32_t, uint32_t> object_id_to_instance;

    // Spatial chunk-cull replaced the per-model BVH walk — chunks are
    // already a one-level spatial partition of the instances, so a
    // single frustum test per chunk gives the same wholesale-reject
    // win without the BVH's per-node traversal overhead. The BVH field
    // is gone; cull iterates m.chunks instead.

    bool hidden = false;

    // Per-model federation matrices in metres. Default identity → no
    // per-model contribution to the composed transform. See bonsai's
    // Federation.h for the full pipeline composition order. Stored
    // here so setModelCoordinateOperation / setModelTransformation
    // have somewhere to land; the recompose-and-reupload pass that
    // would actually apply them is deferred.
    Eigen::Matrix4d coordinate_operation_meters = Eigen::Matrix4d::Identity();
    Eigen::Matrix4d model_transformation_meters = Eigen::Matrix4d::Identity();

    // Whether coordinate_operation_meters came from a real IfcCoordinateOperation
    // (sidecar v11+ has_coordinate_operation) rather than being the identity
    // placeholder. The false-origin guess needs to tell those apart: identity
    // because the model is genuinely un-georeferenced is not the same as
    // identity because nothing has been applied yet.
    bool has_coordinate_operation = false;

    // Per-model unit scales, carried alongside the matrices because
    // composeModelTransformation needs them to lift ModelTransformation::a into
    // metres. Sourced from the sidecar so this works for sidecar-only loads
    // where there is no ifcopenshell::file to re-read.
    ModelUnits units;
};

// Release every wgpu handle in `m` (including per-chunk and per-model pool
// ranges via `pool.free()`) and clear its size mirrors. Safe to call
// repeatedly; idempotent on already-released entries.
void releaseWgpuModelGpuData(ModelGpuData& m, BufferPool& pool);

#endif // WGPUMODELGPUDATA_H
