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

#ifndef IFCVIEWER_OVERLAYRENDERER_H
#define IFCVIEWER_OVERLAYRENDERER_H

#include <QRect>
#include <QString>
#include <QtOpenGL/QOpenGLFunctions_4_5_Core>

#include <vector>

// Neutral overlay-primitive renderer attached to ViewportWindow.  Today it
// draws a single tinted, translucent triangle list in world space — used by
// the area-measurement tool to shade selected coplanar patches.  More
// primitives (lines, points, world-anchored labels) will land here as
// future tools require them.
//
// Lifetime: owned by ViewportWindow, initialised in the same context.  All
// public methods assume the caller has already made the GL context current.
class OverlayRenderer {
public:
    void initialize(QOpenGLFunctions_4_5_Core* gl);
    void release();

    // Replace the highlight-triangle list.  `world_xyz` is 3 floats per
    // vertex, 3 verts per triangle, in world space (post-composed-transform).
    // Empty disables the overlay.  Color is RGBA in [0, 1].
    void setHighlightTriangles(const std::vector<float>& world_xyz,
                               float r, float g, float b, float a);

    // One stylistic group of line segments rendered through the
    // outlined / optionally-dashed line shader.  Multiple groups in a
    // single setOverlayLines call let the caller mix solid + dashed +
    // axis-coloured legs in one frame (e.g. the length tool's white
    // total line + RGB XYZ stair-step + dashed perpendicular).
    struct LineGroup {
        std::vector<float> world_xyz;         // 6 floats per segment (a, b)
        float color[4]        = {1, 1, 1, 1}; // inner color
        float stroke_color[4] = {0, 0, 0, 1}; // outline (0 alpha = no outline)
        float line_width      = 1.5f;         // pixels (inner)
        float stroke_extra    = 0.5f;         // pixels per side outside inner
        float dash_period_px  = 0.0f;         // 0 = solid; else screen-space dash period
        float dash_on_ratio   = 0.6f;         // [0..1], used only when period > 0
    };
    void setOverlayLines(const std::vector<LineGroup>& groups);

    // Replace the overlay-point list (3 floats per point, world space).
    // `pixel_size` is the inner-dot diameter in physical pixels.
    //
    // When stroke_a > 0, every point is rendered twice: a wider
    // (pixel_size + 2*stroke_extra) outer dot in stroke_color, then the
    // pixel_size inner dot in the main color — giving a crisp halo that
    // reads on any background.
    void setOverlayPoints(const std::vector<float>& world_xyz,
                          float r, float g, float b, float a,
                          float pixel_size,
                          float stroke_r, float stroke_g, float stroke_b, float stroke_a,
                          float stroke_extra);

    // World-anchored text labels: each one is projected to screen space
    // and drawn via QPainter at that pixel.  Used today for per-segment
    // length readouts in the length tool.
    struct Label {
        float   world_pos[3];
        QString text;
    };
    void setOverlayLabels(const std::vector<Label>& labels);

    // Top-left HUD text drawn via QPainter on the GL surface as part of
    // render().  Empty hides the HUD.
    void setHudText(const QString& text);

    // Box-select rectangle (in logical pixel coords, top-left origin).
    // Drawn as a translucent fill + 1-px outline using the same
    // screen-space rect program that draws label/HUD backgrounds.
    // Empty rect hides it.
    void setSelectionRect(const QRect& rect_logical);

    // Render every overlay primitive in order: GL highlight triangles
    // (using `view_proj`, column-major float[16]), then HUD text via
    // QPainter on a QOpenGLPaintDevice sized to (pixel_w × pixel_h)
    // with the supplied device pixel ratio.  Caller is responsible for
    // ensuring glViewport covers the full surface — the QPainter pass
    // after this call leaves GL state in an undefined shape, so treat
    // this as the last GL operation per frame before swapBuffers (or
    // sandwich it before any pass that re-binds its own programs).
    void render(const float view_proj[16],
                int pixel_w, int pixel_h, qreal device_pixel_ratio);

private:
    // Triangle bundle: position-only VBO, single-color shader.
    struct TriBundle {
        GLuint  vao          = 0;
        GLuint  vbo          = 0;
        size_t  vbo_capacity = 0;
        GLsizei vertex_count = 0;
        float   color[4]     = {0, 0, 0, 0};
    };

    // Point bundle: position-only VBO, sprite shader uses gl_PointCoord
    // to draw an antialiased disc with an outlined halo.
    struct PointBundle {
        GLuint  vao          = 0;
        GLuint  vbo          = 0;
        size_t  vbo_capacity = 0;
        GLsizei vertex_count = 0;
        float   inner_color[4]  = {0, 0, 0, 0};
        float   stroke_color[4] = {0, 0, 0, 0};
        float   pixel_size      = 8.0f;
        float   stroke_extra    = 0.0f;
    };

    // Per-group draw-call record.  setOverlayLines populates one of these
    // per LineGroup, with `first` indexing into a shared expanded-vertex
    // VBO.  At render time we iterate them, set per-group uniforms, and
    // issue one glDrawArrays each.
    struct LineDrawCall {
        float color[4]        = {1, 1, 1, 1};
        float stroke_color[4] = {0, 0, 0, 0};
        float line_width      = 1.5f;
        float stroke_extra    = 0.5f;
        float dash_period_px  = 0.0f;
        float dash_on_ratio   = 0.6f;
        GLint   first         = 0;
        GLsizei count         = 0;
    };

    QOpenGLFunctions_4_5_Core* gl_ = nullptr;

    // Triangle program (highlight tris).
    GLuint program_tri_      = 0;
    GLint  u_tri_view_proj_  = -1;
    GLint  u_tri_color_      = -1;

    // Point program (sprite).
    GLuint program_pt_           = 0;
    GLint  u_pt_view_proj_       = -1;
    GLint  u_pt_point_size_      = -1;
    GLint  u_pt_inner_color_     = -1;
    GLint  u_pt_stroke_color_    = -1;
    GLint  u_pt_inner_radius_    = -1;

    // Line program (screen-space expanded quads).
    GLuint program_ln_           = 0;
    GLint  u_ln_view_proj_       = -1;
    GLint  u_ln_screen_size_     = -1;
    GLint  u_ln_half_width_      = -1;
    GLint  u_ln_stroke_extra_    = -1;
    GLint  u_ln_inner_color_     = -1;
    GLint  u_ln_stroke_color_    = -1;
    GLint  u_ln_dash_period_     = -1;
    GLint  u_ln_dash_on_ratio_   = -1;

    // Screen-space rect program (label + HUD backgrounds).  Vertex
    // attribute is vec2 NDC; fragment outputs a uniform color.  Drawn
    // with depth test off so rects stack on top of the entire scene.
    GLuint program_rect_         = 0;
    GLint  u_rect_color_         = -1;
    GLuint vao_rect_             = 0;
    GLuint vbo_rect_             = 0;
    size_t vbo_rect_capacity_    = 0;

    TriBundle   triangles_;
    PointBundle points_;

    // Lines: one shared VAO/VBO holding the concatenated expanded
    // vertices of every group; line_draws_ records each group's slice.
    GLuint vao_lines_           = 0;
    GLuint vbo_lines_           = 0;
    size_t vbo_lines_capacity_  = 0;
    std::vector<LineDrawCall> line_draws_;

    std::vector<Label> labels_;
    QString            hud_text_;

    // Box-select rectangle in logical pixels.  Null/empty = hidden.
    QRect              selection_rect_;
};

#endif // IFCVIEWER_OVERLAYRENDERER_H
