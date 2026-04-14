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

#ifndef VIEWPORTWINDOW_H
#define VIEWPORTWINDOW_H

#include <QWindow>
#include <QOpenGLContext>
#include <QtOpenGL/QOpenGLFunctions_4_5_Core>
#include <QTimer>
#include <QElapsedTimer>
#include <QMatrix4x4>
#include <QVector3D>

#include <vector>
#include <unordered_map>
#include <cstdint>
#include <mutex>
#include <memory>

#include "BvhAccel.h"
#include "InstancedGeometry.h"
#include "SidecarCache.h"

// Matches GL_DRAW_INDIRECT_BUFFER layout for glMultiDrawElementsIndirect.
struct DrawElementsIndirectCommand {
    uint32_t count;
    uint32_t instanceCount;
    uint32_t firstIndex;
    uint32_t baseVertex;
    uint32_t baseInstance;
};

// Per-model GPU state for the instanced render path.
//
//   VBO: local-coord interleaved verts (pos3 + normal3 + color1_packed) — 28 B.
//   EBO: mesh-local indices (uint32).
//   meshes[]: per-unique-representation metadata; indexed by local_mesh_id.
//   instances[]: CPU-side per-instance records; sorted by mesh_id at finalize.
//   ssbo: InstanceGpu[]; populated at finalize.
//
// A model is drawable once `finalized == true`.
struct ModelGpuData {
    GLuint vao = 0;
    GLuint vbo = 0;
    GLuint ebo = 0;
    GLuint ssbo = 0;

    size_t vbo_capacity = 0;
    size_t ebo_capacity = 0;
    size_t ssbo_capacity = 0;       // bytes
    size_t vbo_used = 0;
    size_t ebo_used = 0;
    uint32_t vertex_count = 0;      // total (across all meshes)
    uint32_t total_triangles = 0;

    std::vector<MeshInfo>    meshes;
    std::vector<InstanceCpu> instances;    // unsorted
    // 1:1 with instances[] — true when the instance transform has
    // det < 0 (a reflection).  Reflected instances need their
    // triangle winding treated as reversed so GL_CULL_FACE culls
    // the correct side.
    std::vector<uint8_t>     instance_reflected;
    uint32_t                 ssbo_instance_count = 0;

    // Per-instance world AABB + BVH (built at finalize).  The BVH is the
    // same ordering as `instances`; bvh_items[i] corresponds to instances[i].
    std::vector<BvhItem> bvh_items;
    ModelBvh             bvh;

    // Dynamic visible-instance index buffer (std430, binding = 1).
    // Re-uploaded each frame from visible_flat_.
    GLuint  visible_ssbo = 0;
    size_t  visible_ssbo_capacity = 0;  // bytes

    // GL_DRAW_INDIRECT_BUFFER of DrawElementsIndirectCommand[], one per
    // non-empty mesh.  Re-uploaded each frame.
    GLuint  indirect_buffer = 0;
    size_t  indirect_capacity = 0;        // bytes
    uint32_t indirect_command_count = 0;  // total valid commands this frame
    uint32_t indirect_forward_count = 0;  // first N are CCW-winding draws

    bool finalized = false;
    bool hidden    = false;
};

class ViewportWindow : public QWindow {
    Q_OBJECT
public:
    explicit ViewportWindow(QWindow* parent = nullptr);
    ~ViewportWindow();

    // Streaming ingress.
    void uploadMeshChunk(const MeshChunk& chunk);
    void uploadInstanceChunk(const InstanceChunk& chunk);

    // Called once all chunks for a model have arrived: sorts instances by
    // mesh_id, assigns each mesh its contiguous range, and uploads the
    // instance SSBO. The model becomes drawable.
    void finalizeModel(uint32_t model_id);

    void resetScene();

    // Snapshot the finalised model into a SidecarData struct for caching.
    // Vertices + indices are read back from the GPU; meshes/instances come
    // from the CPU-side vectors.  Leaves `elements` and `string_table` empty
    // for the caller to fill in.
    bool snapshotModel(uint32_t model_id, SidecarData& out) const;

    // Restore a finalised model from a cached SidecarData struct.  Replaces
    // any existing state for model_id and marks it drawable.
    void applyCachedModel(uint32_t model_id, SidecarData data);

    // After buildLods() has extended sd.indices + populated lod1_* fields,
    // push just the appended index slice + the refreshed mesh metadata onto
    // the live GPU state for model_id.  VBO / SSBO / instance array are left
    // alone; only the EBO grows and m.meshes is replaced.  No-op if the
    // model isn't finalised on the viewport.
    void applyLodExtension(uint32_t model_id, const SidecarData& sd);

    void hideModel(uint32_t model_id);
    void showModel(uint32_t model_id);
    void removeModel(uint32_t model_id);

    void setSelectedObjectId(uint32_t id);
    uint32_t pickObjectAt(int x, int y);

    struct FrameStats {
        float fps;
        float frame_time_ms;
        uint32_t total_objects;
        uint32_t visible_objects;
        uint32_t total_triangles;
        uint32_t visible_triangles;
        uint32_t unique_meshes;
        uint32_t gl_draw_calls;        // actual glMultiDrawElementsIndirect issues per frame
        uint32_t indirect_sub_draws;   // total commands packed into those indirect buffers
    };

signals:
    void objectPicked(uint32_t object_id);
    void initialized();
    void frameStatsUpdated(const ViewportWindow::FrameStats& stats);

protected:
    void exposeEvent(QExposeEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;
    bool event(QEvent* event) override;

private:
    void initGL();
    void render();
    void renderPickPass();
    void renderAxisGizmo();
    void updateCamera();
    void buildShaders();
    void buildAxisGizmo();
    void setupVaoLayout(GLuint vao, GLuint vbo, GLuint ebo);

    // Resolve the default framebuffer's MSAA depth into a single-sample
    // texture, read it back, and max-reduce a mip pyramid on the CPU.  The
    // resulting pyramid is stored in hiz_pyramid_ along with the VP matrix
    // used to draw it; next frame's cullAndUploadVisible can test AABBs
    // against it.  Synchronous readback — at 256×128 the cost is sub-ms
    // and not a measured bottleneck; Phase 3D's compute-shader cull will
    // eliminate the readback entirely.
    void buildHizPyramid();

    // True if the AABB is fully occluded by the previous frame's depth.
    // Returns false when the HiZ is invalid, the AABB crosses the near
    // plane, or the projection falls outside NDC.
    bool aabbOccludedByHiz(const float mn[3], const float mx[3]) const;
    bool growModelVbo(ModelGpuData& m, size_t needed_total);
    bool growModelEbo(ModelGpuData& m, size_t needed_total);
    bool growModelSsbo(ModelGpuData& m, size_t needed_total);
    ModelGpuData& getOrCreateModel(uint32_t model_id);

    // Frustum-cull m's instances (BVH if available, else linear scan),
    // build the per-mesh DrawElementsIndirectCommand array + flat visible
    // list, and upload both to m.indirect_buffer / m.visible_ssbo.
    //
    // `min_pixel_radius` controls contribution culling: instances (and BVH
    // subtrees) whose projected bounding-sphere radius would be below this
    // many pixels are dropped.  0 = disabled (all frustum-visible kept),
    // which is what the pick pass uses so clickable targets aren't filtered.
    void cullAndUploadVisible(ModelGpuData& m, const float planes[6][4],
                              float focal_px, float min_pixel_radius);

    // Mouse interaction
    void handleMousePress(QMouseEvent* event);
    void handleMouseRelease(QMouseEvent* event);
    void handleMouseMove(QMouseEvent* event);
    void handleWheel(QWheelEvent* event);

    QOpenGLContext* context_ = nullptr;
    QOpenGLFunctions_4_5_Core* gl_ = nullptr;
    QTimer render_timer_;
    QElapsedTimer frame_clock_;
    bool gl_initialized_ = false;

    // Shaders
    GLuint main_program_ = 0;
    GLuint pick_program_ = 0;
    GLuint axis_program_ = 0;

    // Axis gizmo
    GLuint axis_vao_ = 0;
    GLuint axis_vbo_ = 0;

    // Per-model GPU data
    std::unordered_map<uint32_t, ModelGpuData> models_gpu_;

    // Pick framebuffer
    GLuint pick_fbo_ = 0;
    GLuint pick_color_tex_ = 0;
    GLuint pick_depth_rbo_ = 0;
    int pick_width_ = 0;
    int pick_height_ = 0;

    // HiZ occlusion culling (Phase 3C).
    //
    // Each frame after the main draw we blit the MSAA depth buffer down
    // into a single-sample depth texture (hiz_fbo_ / hiz_depth_tex_), then
    // glReadPixels it into hiz_depth_readback_.  We max-reduce that into a
    // mip pyramid (hiz_pyramid_) and remember the VP matrix used
    // (hiz_vp_ + hiz_vp_valid_) so next frame's cull can test AABBs
    // against a slightly-stale depth.  Skipped for the pick pass and when
    // IFC_NO_HIZ=1.
    GLuint hiz_fbo_ = 0;
    GLuint hiz_depth_tex_ = 0;
    GLuint hiz_resolve_fbo_ = 0;         // full-size single-sample resolve
    GLuint hiz_resolve_depth_tex_ = 0;
    int    hiz_resolve_w_ = 0;
    int    hiz_resolve_h_ = 0;
    int    hiz_base_w_ = 0;
    int    hiz_base_h_ = 0;
    std::vector<float>    hiz_depth_readback_;   // hiz_base_w_ * hiz_base_h_ floats
    std::vector<float>    hiz_pyramid_;          // concatenated mip levels
    std::vector<uint32_t> hiz_mip_offset_;       // into hiz_pyramid_
    std::vector<uint32_t> hiz_mip_w_;
    std::vector<uint32_t> hiz_mip_h_;
    QMatrix4x4            hiz_vp_;
    bool                  hiz_vp_valid_ = false;
    uint32_t              hiz_reject_count_ = 0;  // per-frame stat

    // Cull-phase timers.  Accumulated across all frames in the current
    // 1-second stats window; divided by frame_count_ at print time to
    // give per-frame average ms.  Reset each window.  Lets us see where
    // CPU time actually goes: bucket clears vs BVH traversal vs emit vs
    // GPU upload.
    uint64_t cull_clear_ns_    = 0;
    uint64_t cull_traverse_ns_ = 0;
    uint64_t cull_emit_ns_     = 0;
    uint64_t cull_upload_ns_   = 0;

    // Per-frame stats
    uint32_t visible_triangles_ = 0;
    uint32_t visible_objects_ = 0;
    uint32_t gl_draw_calls_ = 0;
    uint32_t indirect_sub_draws_ = 0;

    // Reused scratch: visible-instance index lists per mesh, flattened into
    // `visible_flat_` for upload.  Both live in the parent object to avoid
    // per-frame allocation.  indirect_scratch_ is the matching array of
    // DrawElementsIndirectCommand records — forward-declared as bytes so
    // the header doesn't need the struct definition.
    // Four buckets = {fwd, rev} × {LOD0, LOD1}.  LOD1 buckets are only
    // populated when the mesh has lod1_index_count > 0 and the projected
    // pixel radius is below the LOD switch threshold.
    std::vector<std::vector<uint32_t>>     visible_by_mesh_fwd_lod0_;
    std::vector<std::vector<uint32_t>>     visible_by_mesh_fwd_lod1_;
    std::vector<std::vector<uint32_t>>     visible_by_mesh_rev_lod0_;
    std::vector<std::vector<uint32_t>>     visible_by_mesh_rev_lod1_;
    std::vector<uint32_t>                  visible_flat_;
    std::vector<DrawElementsIndirectCommand> indirect_scratch_;

    // Camera
    QVector3D camera_target_{0, 0, 0};
    QVector3D camera_eye_{0, 0, 0};      // world-space eye, set in updateCamera
    float camera_distance_ = 50.0f;
    float camera_yaw_ = 45.0f;
    float camera_pitch_ = 30.0f;
    float camera_fov_y_deg_ = 45.0f;
    QMatrix4x4 view_matrix_;
    QMatrix4x4 proj_matrix_;

    // Mouse
    Qt::MouseButton active_button_ = Qt::NoButton;
    QPoint last_mouse_pos_;

    // Selection
    uint32_t selected_object_id_ = 0;

    // FPS smoothing
    int frame_count_ = 0;
    float accumulated_time_ = 0.0f;
    float last_fps_ = 0.0f;
};

#endif // VIEWPORTWINDOW_H
