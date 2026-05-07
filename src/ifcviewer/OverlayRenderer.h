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

    // Top-left HUD text drawn via QPainter on the GL surface as part of
    // render().  Empty hides the HUD.
    void setHudText(const QString& text);

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
    QOpenGLFunctions_4_5_Core* gl_ = nullptr;
    GLuint  program_       = 0;
    GLuint  vao_           = 0;
    GLuint  vbo_           = 0;
    size_t  vbo_capacity_  = 0;       // bytes
    GLsizei vertex_count_  = 0;
    float   color_[4]      = {0, 0, 0, 0};
    GLint   u_view_proj_   = -1;
    GLint   u_color_       = -1;
    QString hud_text_;
};

#endif // IFCVIEWER_OVERLAYRENDERER_H
