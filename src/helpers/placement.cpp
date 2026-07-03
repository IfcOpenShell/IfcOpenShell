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

#include "../ifcparse/exception.h"
#include "schema_dispatch.i"

#include <type_traits>
#include <vector>

namespace {

Eigen::Vector3d safe_normalize(const Eigen::Vector3d& v,
                               const Eigen::Vector3d& fallback) {
    const double n = v.norm();
    return (n > 0.0) ? Eigen::Vector3d(v / n) : fallback;
}

template <typename Schema, typename = void>
struct has_axis2_placement_linear : std::false_type {};

template <typename Schema>
struct has_axis2_placement_linear<Schema, std::void_t<typename Schema::IfcAxis2PlacementLinear>> : std::true_type {};

[[noreturn]] void unsupported_schema(const std::string& name) {
    throw ifcopenshell::exception("No helper implementation was built for schema " + name);
}

template <typename Schema>
Eigen::Vector3d direction_or(const typename Schema::IfcDirection& direction,
                             const Eigen::Vector3d& fallback) {
    if (!direction) {
        return fallback;
    }
    const auto ratios = direction.DirectionRatios();
    if (ratios.size() < 2) {
        return fallback;
    }
    return Eigen::Vector3d(ratios[0], ratios[1], ratios.size() > 2 ? ratios[2] : 0.0);
}

template <typename Schema>
std::optional<Eigen::Vector3d> cartesian_point(const typename Schema::IfcPoint& point) {
    const auto cartesian = point.template as<typename Schema::IfcCartesianPoint>();
    if (!cartesian) {
        return std::nullopt;
    }
    const auto coordinates = cartesian.Coordinates();
    if (coordinates.size() < 2) {
        return std::nullopt;
    }
    return Eigen::Vector3d(coordinates[0], coordinates[1], coordinates.size() > 2 ? coordinates[2] : 0.0);
}

template <typename Schema, typename Placement>
Eigen::Matrix4d axis2_placement_3d_s(const Placement& placement) {
    const auto origin = cartesian_point<Schema>(placement.Location());
    if (!origin) {
        return Eigen::Matrix4d::Identity();
    }
    const auto z = direction_or<Schema>(placement.Axis(), Eigen::Vector3d::UnitZ());
    const auto x = direction_or<Schema>(placement.RefDirection(), Eigen::Vector3d::UnitX());
    return axes_to_placement(*origin, z, x);
}

template <typename Schema>
Eigen::Matrix4d get_axis2_placement_s(const express::Base& placement) {
    if (auto axis3 = placement.template as<typename Schema::IfcAxis2Placement3D>()) {
        return axis2_placement_3d_s<Schema>(axis3);
    }
    if constexpr (has_axis2_placement_linear<Schema>::value) {
        if (auto linear = placement.template as<typename Schema::IfcAxis2PlacementLinear>()) {
            return axis2_placement_3d_s<Schema>(linear);
        }
    }
    if (auto axis2 = placement.template as<typename Schema::IfcAxis2Placement2D>()) {
        const auto origin = cartesian_point<Schema>(axis2.Location());
        if (!origin) {
            return Eigen::Matrix4d::Identity();
        }
        const auto x = direction_or<Schema>(axis2.RefDirection(), Eigen::Vector3d::UnitX());
        return axes_to_placement(*origin, Eigen::Vector3d::UnitZ(), x);
    }
    if (auto axis1 = placement.template as<typename Schema::IfcAxis1Placement>()) {
        const auto origin = cartesian_point<Schema>(axis1.Location());
        if (!origin) {
            return Eigen::Matrix4d::Identity();
        }
        const auto z = direction_or<Schema>(axis1.Axis(), Eigen::Vector3d::UnitZ());
        return axes_to_placement(*origin, z, Eigen::Vector3d::UnitX());
    }
    return Eigen::Matrix4d::Identity();
}

template <typename Schema>
Eigen::Matrix4d get_local_placement_s(const express::Base& placement) {
    if (auto local = placement.template as<typename Schema::IfcLocalPlacement>()) {
        Eigen::Matrix4d parent = Eigen::Matrix4d::Identity();
        if (const auto relative_to = local.PlacementRelTo()) {
            parent = get_local_placement_s<Schema>(relative_to);
        }
        const auto relative = local.RelativePlacement();
        if (!relative) {
            return parent;
        }
        return parent * get_axis2_placement_s<Schema>(relative.concrete());
    }
    return get_axis2_placement_s<Schema>(placement);
}

} // namespace

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
    if (!placement) {
        return Eigen::Matrix4d::Identity();
    }
    const auto name = placement.declaration().schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_axis2_placement_s<Schema>(placement);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

Eigen::Matrix4d get_local_placement(const express::Base& placement) {
    if (!placement) {
        return Eigen::Matrix4d::Identity();
    }
    const auto name = placement.declaration().schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_local_placement_s<Schema>(placement);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}
