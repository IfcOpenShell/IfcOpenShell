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

#include <deque>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <cstdint>
#include <mutex>
#include <thread>
#include <memory>
#include <atomic>

#include "BvhAccel.h"
#include "SidecarCache.h"

struct MaterialInfo {
    float r = 0.75f, g = 0.75f, b = 0.78f, a = 1.0f;
};

struct UploadChunk {
    // Interleaved per-vertex layout (8 floats / 32 bytes per vertex):
    //   pos(3 float) + normal(3 float) + object_id(1 float bitcast from uint)
    //   + color(1 float holding RGBA8 packed bytes, read on the GPU as
    //   GL_UNSIGNED_BYTE * 4 normalized).
    std::vector<float> vertices;
    std::vector<uint32_t> indices; // local to this chunk's vertices
    uint32_t object_id = 0;
    uint32_t model_id = 0;
};

// Per-model GPU state: own VAO, VBO, EBO, draw info, BVH.
struct ModelGpuData {
    GLuint vao = 0;
    GLuint vbo = 0;
    GLuint ebo = 0;
    size_t vbo_capacity = 0;
    size_t ebo_capacity = 0;
    size_t vbo_used = 0;   // bytes
    size_t ebo_used = 0;   // bytes
    uint32_t vertex_count = 0;
    uint32_t total_triangles = 0;
    std::vector<ObjectDrawInfo> draw_info;
    uint32_t active_draw_count = 0; // how many objects are drawable (progressive upload)
    bool hidden = false;
};

// Pending progressive upload — VBO first, then EBO.
struct PendingUpload {
    uint32_t model_id = 0;
    std::vector<float> vertices;
    std::vector<uint32_t> indices;
    std::shared_ptr<BvhSet> bvh_set;
    size_t vbo_uploaded = 0;  // bytes
    size_t ebo_uploaded = 0;  // bytes
};

class ViewportWindow : public QWindow {
    Q_OBJECT
public:
    explicit ViewportWindow(QWindow* parent = nullptr);
    ~ViewportWindow();

    void uploadChunk(const UploadChunk& chunk);
    void resetScene();

    // Bulk upload pre-built geometry from a sidecar cache.
    // Creates a perfectly-sized per-model buffer set. No copy.
    void uploadBulk(uint32_t model_id,
                    std::vector<float> vertices,
                    std::vector<uint32_t> indices,
                    const std::vector<ObjectDrawInfo>& draw_info,
                    std::shared_ptr<BvhSet> bvh_set);

    void hideModel(uint32_t model_id);
    void showModel(uint32_t model_id);
    void removeModel(uint32_t model_id);

    // Build BVH and optionally write a sidecar cache.
    void buildBvhAsync(uint32_t model_id,
                       const std::string& ifc_path = "",
                       uint64_t ifc_file_size = 0,
                       std::vector<PackedElementInfo> sidecar_elements = {},
                       std::string sidecar_string_table = {});

    // Read snapshots of a model's GPU buffers into CPU vectors.
    std::vector<uint32_t> readbackEbo(uint32_t model_id) const;
    std::vector<float> readbackVbo(uint32_t model_id) const;

    void setSelectedObjectId(uint32_t id);
    uint32_t pickObjectAt(int x, int y);

    struct FrameStats {
        float fps;
        float frame_time_ms;
        uint32_t total_objects;
        uint32_t visible_objects;
        uint32_t total_triangles;
        uint32_t visible_triangles;
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
    bool growModelVbo(ModelGpuData& m, size_t needed_total);
    bool growModelEbo(ModelGpuData& m, size_t needed_total);
    void buildVisibleList(const QMatrix4x4& vp);
    void traverseBvh(const ModelBvh& mbvh, const ModelGpuData& mgpu,
                     const float planes[6][4]);
    static bool aabbInFrustum(const float aabb_min[3], const float aabb_max[3],
                              const float planes[6][4]);
    void applyBvhResult();
    void processPendingUploads();

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

    // Axis gizmo (separate VAO/VBO since vertex layout differs from scene)
    GLuint axis_vao_ = 0;
    GLuint axis_vbo_ = 0;

    // Per-model GPU data
    std::unordered_map<uint32_t, ModelGpuData> models_gpu_;
    std::mutex models_mutex_;

    // Pick framebuffer
    GLuint pick_fbo_ = 0;
    GLuint pick_color_tex_ = 0;
    GLuint pick_depth_rbo_ = 0;
    int pick_width_ = 0;
    int pick_height_ = 0;

    // Per-model BVH
    std::unordered_map<uint32_t, std::shared_ptr<const BvhSet>> model_bvhs_;

    // Progressive upload queue
    std::deque<PendingUpload> pending_uploads_;

    // Scratch buffers reused each frame to avoid allocation.
    struct ModelDrawCmd {
        GLuint vao;
        std::vector<GLsizei> counts;
        std::vector<const void*> offsets;
    };
    std::vector<ModelDrawCmd> frame_draw_cmds_;
    uint32_t visible_triangles_ = 0;

    // Camera
    QVector3D camera_target_{0, 0, 0};
    float camera_distance_ = 50.0f;
    float camera_yaw_ = 45.0f;
    float camera_pitch_ = 30.0f;
    QMatrix4x4 view_matrix_;
    QMatrix4x4 proj_matrix_;

    // Mouse state
    Qt::MouseButton active_button_ = Qt::NoButton;
    QPoint last_mouse_pos_;

    // Selection
    uint32_t selected_object_id_ = 0;
    bool pick_requested_ = false;
    int pick_x_ = 0, pick_y_ = 0;

    // BVH build (phase 2)
    struct PendingBvh {
        uint32_t model_id;
        std::shared_ptr<BvhSet> bvh_set;
        EboReorderResult ebo_reorder;
    };
    std::unique_ptr<PendingBvh> pending_bvh_;
    std::mutex bvh_result_mutex_;
    std::thread bvh_build_thread_;

    // Stats
    int frame_count_ = 0;
    float accumulated_time_ = 0.0f;
    float last_fps_ = 0.0f;
};

#endif // VIEWPORTWINDOW_H
