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
#include <cstdint>
#include <mutex>

struct MaterialInfo {
    float r = 0.75f, g = 0.75f, b = 0.78f, a = 1.0f;
};

struct ObjectDrawInfo {
    uint32_t index_offset;  // byte offset into EBO
    uint32_t index_count;   // number of indices
    float aabb_min[3];      // world-space AABB
    float aabb_max[3];
};

struct UploadChunk {
    // Interleaved per-vertex layout (8 floats / 32 bytes per vertex):
    //   pos(3 float) + normal(3 float) + object_id(1 float bitcast from uint)
    //   + color(1 float holding RGBA8 packed bytes, read on the GPU as
    //   GL_UNSIGNED_BYTE * 4 normalized).
    std::vector<float> vertices;
    std::vector<uint32_t> indices; // local to this chunk's vertices
    uint32_t object_id = 0;
};

class ViewportWindow : public QWindow {
    Q_OBJECT
public:
    explicit ViewportWindow(QWindow* parent = nullptr);
    ~ViewportWindow();

    void uploadChunk(const UploadChunk& chunk);
    void resetScene();

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
    bool growVbo(size_t needed_total);
    bool growEbo(size_t needed_total);
    void buildVisibleList(const QMatrix4x4& vp);

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

    // Geometry buffers - one big buffer pair
    GLuint vao_ = 0;
    GLuint vbo_ = 0;
    GLuint ebo_ = 0;
    size_t vbo_capacity_ = 0;
    size_t ebo_capacity_ = 0;
    size_t vbo_used_ = 0;  // in bytes
    size_t ebo_used_ = 0;  // in bytes
    uint32_t vertex_count_ = 0;

    // Pick framebuffer
    GLuint pick_fbo_ = 0;
    GLuint pick_color_tex_ = 0;
    GLuint pick_depth_rbo_ = 0;
    int pick_width_ = 0;
    int pick_height_ = 0;

    // Per-object draw metadata for frustum culling.
    std::vector<ObjectDrawInfo> object_draw_info_;
    uint32_t total_index_count_ = 0;
    std::mutex upload_mutex_;

    // Scratch buffers reused each frame to avoid allocation.
    std::vector<GLsizei> visible_counts_;
    std::vector<const void*> visible_offsets_;

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

    // Stats
    uint32_t total_triangles_ = 0;
    uint32_t visible_triangles_ = 0;
    int frame_count_ = 0;
    float accumulated_time_ = 0.0f;
    float last_fps_ = 0.0f;
};

#endif // VIEWPORTWINDOW_H
