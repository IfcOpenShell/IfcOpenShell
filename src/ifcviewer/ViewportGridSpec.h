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

#ifndef VIEWPORTGRIDSPEC_H
#define VIEWPORTGRIDSPEC_H

#include <Eigen/Dense>

#include <string>

// Axis-aligned line grids for the viewport overlay.
// Each grid is a set of lines on a plane (XY, XZ, or YZ). Lines on every
// 10th step are the primary grid (light grey). The steps between them are
// the secondary grid and are drawn lighter.
struct ViewportGridSpec {
    enum class Plane { XY = 0, XZ = 1, YZ = 2 };

    // Close to the background, like Blender's floor grid. Distance fog fades
    // these lines out; a bright grey reads as a wireframe, not a ground plane.
    static Eigen::Vector3f defaultGridColor() {
        return Eigen::Vector3f(0.42f, 0.42f, 0.42f);
    }

    std::string     id;
    // World coordinates, metres: the frame the axes and the models are in,
    // not the viewer frame shifted by the false origin.
    Eigen::Vector3d origin   = Eigen::Vector3d::Zero();
    Plane           plane    = Plane::XY;
    float           spacing  = 1.0f;
    int             divisions = 50;
    Eigen::Vector3f color_u  = defaultGridColor();
    Eigen::Vector3f color_v  = defaultGridColor();
    float           opacity  = 0.7f;
    bool            visible  = true;

    static ViewportGridSpec defaultBaseGrid() {
        ViewportGridSpec spec;
        spec.id         = "base";
        spec.plane      = Plane::XY;
        spec.spacing    = 1.0f;
        spec.divisions  = 200;
        spec.color_u    = defaultGridColor();
        spec.color_v    = defaultGridColor();
        spec.opacity    = 0.85f;
        spec.visible    = true;
        return spec;
    }

    static Eigen::Vector3f defaultAxisColor(char) {
        return defaultGridColor();
    }

    void applyDefaultAxisColors() {
        switch (plane) {
            case Plane::XY:
                color_u = defaultAxisColor('x');
                color_v = defaultAxisColor('y');
                break;
            case Plane::XZ:
                color_u = defaultAxisColor('x');
                color_v = defaultAxisColor('z');
                break;
            case Plane::YZ:
                color_u = defaultAxisColor('y');
                color_v = defaultAxisColor('z');
                break;
        }
    }
};

#endif  // VIEWPORTGRIDSPEC_H
