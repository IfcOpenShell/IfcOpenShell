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

#include "geolocation.h"

#include "../ifcparse/exception.h"
#include "../ifcparse/file.h"
#include "../ifcparse/instance_data.h"
#include "placement.h"
#include "pset.h"
#include "schema_dispatch.i"

#include <cmath>
#include <string>
#include <type_traits>
#include <vector>

namespace {

template <typename T>
struct is_optional : std::false_type {};

template <typename T>
struct is_optional<std::optional<T>> : std::true_type {};

template <typename Schema, typename = void>
struct is_ifc4_or_higher : std::false_type {};

template <typename Schema>
struct is_ifc4_or_higher<Schema, std::void_t<typename Schema::IfcCoordinateOperation>> : std::true_type {};

template <typename Schema, typename = void>
struct has_map_conversion_scaled : std::false_type {};

template <typename Schema>
struct has_map_conversion_scaled<Schema, std::void_t<typename Schema::IfcMapConversionScaled>> : std::true_type {};

template <typename T, typename = void>
struct has_factor_x : std::false_type {};

template <typename T>
struct has_factor_x<T, std::void_t<decltype(std::declval<T>().FactorX())>> : std::true_type {};

template <typename Schema, typename = void>
struct has_rigid_operation : std::false_type {};

template <typename Schema>
struct has_rigid_operation<Schema, std::void_t<typename Schema::IfcRigidOperation>> : std::true_type {};

[[noreturn]] void unsupported_schema(const std::string& name) {
    throw ifcopenshell::exception("No helper implementation was built for schema " + name);
}

double numeric_property(const property_map& properties,
                        const std::string& name,
                        double fallback) {
    const auto found = properties.find(name);
    if (found == properties.end()) {
        return fallback;
    }
    if (const auto value = found->second.get_if<double>()) {
        return *value;
    }
    if (const auto value = found->second.get_if<std::int64_t>()) {
        return static_cast<double>(*value);
    }
    return fallback;
}

double selected_number(const express::Base& selected, double fallback) {
    if (!selected) {
        return fallback;
    }
    const auto value = selected.get_attribute_value(0);
    if (value.isNull()) {
        return fallback;
    }
    if (value.type() == ifcopenshell::Argument_DOUBLE) {
        return static_cast<double>(value);
    }
    if (value.type() == ifcopenshell::Argument_INT) {
        return static_cast<double>(static_cast<int64_t>(value));
    }
    return fallback;
}

template <typename T>
double optional_number(const T& value, double fallback) {
    if constexpr (is_optional<T>::value) {
        return value.value_or(fallback);
    } else {
        return value;
    }
}

template <typename Schema>
std::optional<HelmertTransformation> get_helmert_transformation_parameters_s(ifcopenshell::file* ifc_file) {
    HelmertTransformation result;
    if constexpr (!is_ifc4_or_higher<Schema>::value) {
        const auto projects = ifc_file->template instances_by_type<typename Schema::IfcProject>();
        if (projects.empty()) {
            return std::nullopt;
        }
        const auto conversion = get_pset(projects.front(), "ePSet_MapConversion");
        if (!conversion) {
            return std::nullopt;
        }
        const auto* properties = conversion->template get_if<property_map>();
        if (!properties) {
            return std::nullopt;
        }
        result.e = numeric_property(*properties, "Eastings", 0.0);
        result.n = numeric_property(*properties, "Northings", 0.0);
        result.h = numeric_property(*properties, "OrthogonalHeight", 0.0);
        result.xaa = numeric_property(*properties, "XAxisAbscissa", 0.0);
        result.xao = numeric_property(*properties, "XAxisOrdinate", 0.0);
        result.scale = numeric_property(*properties, "Scale", 1.0);
    } else {
        const auto conversions =
            ifc_file->template instances_by_type<typename Schema::IfcCoordinateOperation>();
        if (conversions.empty()) {
            return std::nullopt;
        }
        const auto& conversion = conversions.front();
        if (auto map_conversion = conversion.template as<typename Schema::IfcMapConversion>()) {
            result.e = map_conversion.Eastings();
            result.n = map_conversion.Northings();
            result.h = map_conversion.OrthogonalHeight();
            result.xaa = map_conversion.XAxisAbscissa().value_or(0.0);
            result.xao = map_conversion.XAxisOrdinate().value_or(0.0);
            result.scale = map_conversion.Scale().value_or(1.0);
            if constexpr (has_map_conversion_scaled<Schema>::value) {
                if (auto scaled = conversion.template as<typename Schema::IfcMapConversionScaled>()) {
                    if constexpr (has_factor_x<decltype(scaled)>::value) {
                        result.factor_x = scaled.FactorX();
                        result.factor_y = scaled.FactorY();
                        result.factor_z = scaled.FactorZ();
                    } else {
                        result.factor_x = scaled.ScaleX();
                        result.factor_y = scaled.ScaleY();
                        result.factor_z = scaled.ScaleZ();
                    }
                }
            }
        } else if constexpr (has_rigid_operation<Schema>::value) {
            if (auto rigid = conversion.template as<typename Schema::IfcRigidOperation>()) {
                result.e = selected_number(rigid.FirstCoordinate().concrete(), 0.0);
                result.n = selected_number(rigid.SecondCoordinate().concrete(), 0.0);
                result.h = optional_number(rigid.Height(), 0.0);
            } else {
                return std::nullopt;
            }
        } else {
            return std::nullopt;
        }
    }

    if (result.scale == 0.0) {
        result.scale = 1.0;
    }
    if (result.xaa == 0.0 && result.xao == 0.0) {
        result.xaa = 1.0;
    }
    return result;
}

template <typename Schema>
std::optional<Eigen::Matrix4d> get_wcs_s(ifcopenshell::file* ifc_file) {
    const auto contexts =
        ifc_file->template instances_by_type_excl_subtypes<typename Schema::IfcGeometricRepresentationContext>();
    express::Base wcs;
    for (const auto& context : contexts) {
        const auto placement = context.WorldCoordinateSystem();
        if (!placement) {
            continue;
        }
        wcs = placement.concrete();
        if (context.ContextType() == std::optional<std::string>("Model")) {
            break;
        }
    }
    if (!wcs) {
        return std::nullopt;
    }
    return get_axis2_placement(wcs);
}

template <typename Schema>
std::optional<express::Base> get_map_unit_s(ifcopenshell::file* ifc_file) {
    if constexpr (!is_ifc4_or_higher<Schema>::value) {
        return std::nullopt;
    } else {
        const auto operations =
            ifc_file->template instances_by_type<typename Schema::IfcCoordinateOperation>();
        if (operations.empty()) {
            return std::nullopt;
        }
        const auto target = operations.front().TargetCRS();
        const auto projected = target.template as<typename Schema::IfcProjectedCRS>();
        if (!projected) {
            return std::nullopt;
        }
        const auto unit = projected.MapUnit();
        if (!unit) {
            return std::nullopt;
        }
        return unit;
    }
}

} // namespace

std::optional<HelmertTransformation>
get_helmert_transformation_parameters(ifcopenshell::file* ifc_file) {
    const auto name = ifc_file->schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_helmert_transformation_parameters_s<Schema>(ifc_file);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

std::optional<Eigen::Matrix4d> get_wcs(ifcopenshell::file* ifc_file) {
    const auto name = ifc_file->schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_wcs_s<Schema>(ifc_file);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

Eigen::Matrix4d local_to_global(const Eigen::Matrix4d& matrix,
                                const HelmertTransformation& p) {
    const double theta = std::atan2(p.xao, p.xaa);
    const double c = std::cos(theta);
    const double s = std::sin(theta);

    Eigen::Matrix4d S = Eigen::Matrix4d::Identity();
    S(0, 0) = p.scale * p.factor_x;
    S(1, 1) = p.scale * p.factor_y;
    S(2, 2) = p.scale * p.factor_z;

    Eigen::Matrix4d R = Eigen::Matrix4d::Identity();
    R(0, 0) = c;
    R(0, 1) = -s;
    R(1, 0) = s;
    R(1, 1) = c;

    Eigen::Matrix4d result = R * S * matrix;
    // The scale was baked into the rotation+scale matrix so each axis column
    // ended up scaled.  Renormalise so the rotation part is pure orientation
    // and the translation alone carries the scaled offsets.
    for (int col = 0; col < 3; ++col) {
        Eigen::Vector3d v = result.block<3, 1>(0, col);
        const double n = v.norm();
        if (n > 0.0) {
            result.block<3, 1>(0, col) = v / n;
        }
    }
    result(0, 3) += p.e;
    result(1, 3) += p.n;
    result(2, 3) += p.h;
    return result;
}

Eigen::Matrix4d auto_local_to_global(ifcopenshell::file* ifc_file,
                                     const Eigen::Matrix4d& matrix,
                                     bool should_return_in_map_units) {
    auto params = get_helmert_transformation_parameters(ifc_file);
    if (!params) {
        return matrix;
    }

    Eigen::Matrix4d m = matrix;
    if (auto wcs = get_wcs(ifc_file)) {
        m = wcs->inverse() * m;
    }
    Eigen::Matrix4d result = local_to_global(m, *params);
    if (!should_return_in_map_units) {
        result(0, 3) /= params->scale;
        result(1, 3) /= params->scale;
        result(2, 3) /= params->scale;
    }
    return result;
}

Eigen::Matrix4d helmert_meters_from_parameters(const HelmertTransformation& p,
                                               double map_unit_to_meters) {
    const double theta = std::atan2(p.xao, p.xaa);
    const double c = std::cos(theta);
    const double s = std::sin(theta);

    Eigen::Matrix4d M = Eigen::Matrix4d::Identity();
    // R_z(theta) · diag(fx, fy, fz).  Factors stay in the rotation block so
    // they apply to placement translations on compose; this is the behaviour
    // IfcMapConversionScaled actually wants ("grid distance ≠ ground
    // distance" — buildings on the grid should appear scaled by f).
    M(0, 0) = c * p.factor_x;
    M(0, 1) = -s * p.factor_y;
    M(0, 2) = 0.0;
    M(1, 0) = s * p.factor_x;
    M(1, 1) = c * p.factor_y;
    M(1, 2) = 0.0;
    M(2, 0) = 0.0;
    M(2, 1) = 0.0;
    M(2, 2) = p.factor_z;
    M(0, 3) = p.e * map_unit_to_meters;
    M(1, 3) = p.n * map_unit_to_meters;
    M(2, 3) = p.h * map_unit_to_meters;
    return M;
}

std::optional<express::Base> get_map_unit(ifcopenshell::file* ifc_file) {
    const auto name = ifc_file->schema()->name();
#define IFCOPENSHELL_DISPATCH(Schema, Identifier) \
    if (name == Identifier)                       \
        return get_map_unit_s<Schema>(ifc_file);
    IFCOPENSHELL_HELPER_FOR_EACH_SCHEMA(IFCOPENSHELL_DISPATCH)
#undef IFCOPENSHELL_DISPATCH
    unsupported_schema(name);
}

double x_axis_to_angle_deg(double xaa, double xao) {
    constexpr double PI = 3.14159265358979323846;
    return -std::atan2(xao, xaa) * (180.0 / PI);
}
