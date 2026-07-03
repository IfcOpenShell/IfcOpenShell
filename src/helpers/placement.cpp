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

#include "placement.h"

#include "../ifcparse/instance_data.h"
#include "../ifcparse/schema.h"

#include <vector>

namespace {

Eigen::Vector3d safe_normalize(const Eigen::Vector3d& v,
                               const Eigen::Vector3d& fallback) {
    const double n = v.norm();
    return (n > 0.0) ? Eigen::Vector3d(v / n) : fallback;
}

std::vector<double> read_direction_ratios(const express::Base& dir) {
    if (!dir) return {};
    auto attr = dir.as<express::Entity>().get("DirectionRatios");
    if (attr.isNull()) return {};
    return attr;
}

}  // namespace

Eigen::Matrix4d axes_to_placement(const Eigen::Vector3d& origin,
                                  const Eigen::Vector3d& z,
                                  const Eigen::Vector3d& x) {
    const Eigen::Vector3d xn = safe_normalize(x, Eigen::Vector3d::UnitX());
    const Eigen::Vector3d zn = safe_normalize(z, Eigen::Vector3d::UnitZ());
    const Eigen::Vector3d yn = safe_normalize(zn.cross(xn), Eigen::Vector3d::UnitY());

    Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
    m.block<3, 1>(0, 0) = xn;
    m.block<3, 1>(0, 1) = yn;
    m.block<3, 1>(0, 2) = zn;
    m.block<3, 1>(0, 3) = origin;
    return m;
}

Eigen::Matrix4d get_axis2_placement(const express::Base& placement) {
    if (!placement) return Eigen::Matrix4d::Identity();
    const auto& decl = placement.declaration();
    auto entity = placement.as<express::Entity>();

    Eigen::Vector3d z(0.0, 0.0, 1.0);
    Eigen::Vector3d x(1.0, 0.0, 0.0);
    Eigen::Vector3d o(0.0, 0.0, 0.0);

    if (decl.is("IfcAxis2Placement3D") || decl.is("IfcAxis2PlacementLinear")) {
        auto axis_attr = entity.get("Axis");
        if (!axis_attr.isNull()) {
            auto dr = read_direction_ratios((express::Base) axis_attr);
            if (dr.size() >= 3) z = Eigen::Vector3d(dr[0], dr[1], dr[2]);
        }
        auto refdir_attr = entity.get("RefDirection");
        if (!refdir_attr.isNull()) {
            auto dr = read_direction_ratios((express::Base) refdir_attr);
            if (dr.size() >= 3) x = Eigen::Vector3d(dr[0], dr[1], dr[2]);
        }
        auto loc_attr = entity.get("Location");
        if (loc_attr.isNull()) return Eigen::Matrix4d::Identity();
        express::Base location = loc_attr;
        auto coords_attr = location.as<express::Entity>().get("Coordinates");
        if (coords_attr.isNull()) return Eigen::Matrix4d::Identity();
        std::vector<double> coords = coords_attr;
        if (coords.size() >= 3) o = Eigen::Vector3d(coords[0], coords[1], coords[2]);
    } else if (decl.is("IfcAxis2Placement2D")) {
        auto refdir_attr = entity.get("RefDirection");
        if (!refdir_attr.isNull()) {
            auto dr = read_direction_ratios((express::Base) refdir_attr);
            if (dr.size() >= 1) {
                x = Eigen::Vector3d(dr.size() > 0 ? dr[0] : 1.0,
                                    dr.size() > 1 ? dr[1] : 0.0,
                                    0.0);
            }
        }
        auto loc_attr = entity.get("Location");
        if (loc_attr.isNull()) return Eigen::Matrix4d::Identity();
        express::Base location = loc_attr;
        auto coords_attr = location.as<express::Entity>().get("Coordinates");
        if (coords_attr.isNull()) return Eigen::Matrix4d::Identity();
        std::vector<double> coords = coords_attr;
        if (coords.size() >= 2) {
            o = Eigen::Vector3d(coords[0], coords[1],
                                coords.size() >= 3 ? coords[2] : 0.0);
        }
    } else if (decl.is("IfcAxis1Placement")) {
        auto axis_attr = entity.get("Axis");
        if (!axis_attr.isNull()) {
            auto dr = read_direction_ratios((express::Base) axis_attr);
            if (dr.size() >= 3) z = Eigen::Vector3d(dr[0], dr[1], dr[2]);
        }
        auto loc_attr = entity.get("Location");
        if (loc_attr.isNull()) return Eigen::Matrix4d::Identity();
        express::Base location = loc_attr;
        auto coords_attr = location.as<express::Entity>().get("Coordinates");
        if (coords_attr.isNull()) return Eigen::Matrix4d::Identity();
        std::vector<double> coords = coords_attr;
        if (coords.size() >= 3) o = Eigen::Vector3d(coords[0], coords[1], coords[2]);
    } else {
        return Eigen::Matrix4d::Identity();
    }

    return axes_to_placement(o, z, x);
}

Eigen::Matrix4d get_local_placement(const express::Base& placement) {
    if (!placement) return Eigen::Matrix4d::Identity();
    const auto& decl = placement.declaration();

    if (decl.is("IfcLocalPlacement")) {
        auto entity = placement.as<express::Entity>();
        Eigen::Matrix4d parent = Eigen::Matrix4d::Identity();
        auto rel_attr = entity.get("PlacementRelTo");
        if (!rel_attr.isNull()) {
            parent = get_local_placement((express::Base) rel_attr);
        }
        auto rp_attr = entity.get("RelativePlacement");
        if (rp_attr.isNull()) return parent;
        return parent * get_axis2_placement((express::Base) rp_attr);
    }

    // IfcAxis2Placement* / IfcAxis1Placement passed in directly.
    return get_axis2_placement(placement);
}
