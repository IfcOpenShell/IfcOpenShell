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

#include "Geolocation.h"

#include "../ifcparse/express.h"
#include "../ifcparse/file.h"
#include "../ifcparse/instance_data.h"
#include "../ifcparse/schema.h"

#include <cmath>
#include <string>
#include <vector>

namespace {

// IfcAxis2Placement3D / IfcAxis2PlacementLinear -> column-major 4x4 matrix.
// Mirrors ifcopenshell.util.placement.a2p + get_axis2placement, but only the
// branches needed for IfcGeometricRepresentationContext.WorldCoordinateSystem.
std::optional<Eigen::Matrix4d> getAxis2Placement(express::Base placement) {
    if (!placement) return std::nullopt;
    const auto& decl = placement.declaration();
    if (!(decl.is("IfcAxis2Placement3D") || decl.is("IfcAxis2PlacementLinear"))) {
        return std::nullopt;
    }

    auto entity = placement.as<express::Entity>();

    Eigen::Vector3d z(0.0, 0.0, 1.0);
    Eigen::Vector3d x(1.0, 0.0, 0.0);

    auto axis_attr = entity.get("Axis");
    if (!axis_attr.isNull()) {
        express::Base axis = axis_attr;
        std::vector<double> dr =
            axis.as<express::Entity>().get("DirectionRatios");
        if (dr.size() >= 3) z = Eigen::Vector3d(dr[0], dr[1], dr[2]);
    }

    auto refdir_attr = entity.get("RefDirection");
    if (!refdir_attr.isNull()) {
        express::Base refdir = refdir_attr;
        std::vector<double> dr =
            refdir.as<express::Entity>().get("DirectionRatios");
        if (dr.size() >= 3) x = Eigen::Vector3d(dr[0], dr[1], dr[2]);
    }

    auto loc_attr = entity.get("Location");
    if (loc_attr.isNull()) return std::nullopt;
    express::Base location = loc_attr;
    auto coords_attr = location.as<express::Entity>().get("Coordinates");
    if (coords_attr.isNull()) return std::nullopt;
    std::vector<double> coords = coords_attr;
    if (coords.size() < 3) return std::nullopt;

    Eigen::Vector3d xn = x.normalized();
    Eigen::Vector3d zn = z.normalized();
    Eigen::Vector3d yn = zn.cross(xn).normalized();

    Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
    m.block<3, 1>(0, 0) = xn;
    m.block<3, 1>(0, 1) = yn;
    m.block<3, 1>(0, 2) = zn;
    m(0, 3) = coords[0];
    m(1, 3) = coords[1];
    m(2, 3) = coords[2];
    return m;
}

// Read a numeric NominalValue out of an IfcPropertySingleValue.  IFC2X3
// ePSet_MapConversion stores eastings/northings/scale as IfcLengthMeasure or
// IfcReal wrapped inside IfcValue (a SELECT) — get_attribute_value(0) peels
// the wrapper.  Returns nullopt if the value is missing or non-numeric.
std::optional<double> readPropertyValueDouble(const express::Base& property) {
    if (!property.declaration().is("IfcPropertySingleValue")) return std::nullopt;
    auto pe = property.as<express::Entity>();
    auto nv = pe.get("NominalValue");
    if (nv.isNull()) return std::nullopt;
    express::Base wrapper = nv;
    auto inner = wrapper.get_attribute_value(0);
    if (inner.isNull()) return std::nullopt;
    switch (inner.type()) {
        case ifcopenshell::Argument_DOUBLE: return (double) inner;
        case ifcopenshell::Argument_INT:    return (double)(int) inner;
        default: return std::nullopt;
    }
}

}  // namespace

std::optional<HelmertTransformation>
getHelmertTransformationParameters(ifcopenshell::file* ifc_file) {
    HelmertTransformation p;
    const std::string schema_name = ifc_file->schema()->name();

    if (schema_name == "IFC2X3") {
        auto projects = ifc_file->instances_by_type("IfcProject");
        if (projects.empty()) return std::nullopt;
        const auto& project = projects[0];

        bool found = false;
        auto rels = project.as<express::Entity>().get_inverse("IsDefinedBy");
        for (const auto& rel : rels) {
            if (!rel.declaration().is("IfcRelDefinesByProperties")) continue;
            express::Base pset_base = rel.get("RelatingPropertyDefinition");
            if (!pset_base.declaration().is("IfcPropertySet")) continue;
            auto pset = pset_base.as<express::Entity>();
            auto name_attr = pset.get("Name");
            if (name_attr.isNull()) continue;
            std::string pset_name = name_attr;
            if (pset_name != "ePSet_MapConversion") continue;

            std::vector<express::Base> props = pset.get("HasProperties");
            for (const auto& prop : props) {
                if (!prop.declaration().is("IfcPropertySingleValue")) continue;
                auto pe = prop.as<express::Entity>();
                auto pname_attr = pe.get("Name");
                if (pname_attr.isNull()) continue;
                std::string pname = pname_attr;
                auto value = readPropertyValueDouble(prop);
                if (!value) continue;
                if      (pname == "Eastings")         p.e = *value;
                else if (pname == "Northings")        p.n = *value;
                else if (pname == "OrthogonalHeight") p.h = *value;
                else if (pname == "XAxisAbscissa")    p.xaa = *value;
                else if (pname == "XAxisOrdinate")    p.xao = *value;
                else if (pname == "Scale")            p.scale = *value;
            }
            found = true;
            break;
        }
        if (!found) return std::nullopt;

        // Python: `conversion.get("Scale", None) or 1` — 0 falls back to 1.
        if (p.scale == 0.0) p.scale = 1.0;
        p.factor_x = p.factor_y = p.factor_z = 1.0;
    } else {
        std::vector<express::Base> conversions;
        try {
            conversions = ifc_file->instances_by_type("IfcCoordinateOperation");
        } catch (...) {
            // Schema doesn't know IfcCoordinateOperation.
            return std::nullopt;
        }
        if (conversions.empty()) return std::nullopt;
        const auto& conversion = conversions[0];
        auto entity = conversion.as<express::Entity>();
        const std::string type_name = conversion.declaration().name();

        auto get_or = [&](const std::string& name, double fallback) {
            auto a = entity.get(name);
            return a.isNull() ? fallback : (double) a;
        };

        if (conversion.declaration().is("IfcMapConversion")) {
            p.e   = get_or("Eastings", 0.0);
            p.n   = get_or("Northings", 0.0);
            p.h   = get_or("OrthogonalHeight", 0.0);
            p.xaa = get_or("XAxisAbscissa", 0.0);
            p.xao = get_or("XAxisOrdinate", 0.0);
            p.scale = get_or("Scale", 1.0);
            if (p.scale == 0.0) p.scale = 1.0;

            if (type_name == "IfcMapConversionScaled") {
                p.factor_x = entity.get("FactorX");
                p.factor_y = entity.get("FactorY");
                p.factor_z = entity.get("FactorZ");
            } else {
                p.factor_x = p.factor_y = p.factor_z = 1.0;
            }
        } else if (type_name == "IfcRigidOperation") {
            // FirstCoordinate / SecondCoordinate are IfcLengthMeasure-typed
            // values; the C++ binding auto-unwraps defined types of REAL.
            p.e = get_or("FirstCoordinate", 0.0);
            p.n = get_or("SecondCoordinate", 0.0);
            p.h = get_or("Height", 0.0);
            p.xaa = 1.0;
            p.xao = 0.0;
            p.scale = p.factor_x = p.factor_y = p.factor_z = 1.0;
        } else {
            return std::nullopt;
        }
    }

    if (p.xaa == 0.0 && p.xao == 0.0) {
        p.xaa = 1.0;
        p.xao = 0.0;
    }
    return p;
}

std::optional<Eigen::Matrix4d> getWcs(ifcopenshell::file* ifc_file) {
    auto contexts = ifc_file->instances_by_type_excl_subtypes(
        "IfcGeometricRepresentationContext");
    express::Base wcs;
    bool found = false;
    for (const auto& ctx : contexts) {
        auto entity = ctx.as<express::Entity>();
        auto wcs_attr = entity.get("WorldCoordinateSystem");
        if (wcs_attr.isNull()) continue;
        wcs = (express::Base) wcs_attr;
        found = true;
        auto ctype_attr = entity.get("ContextType");
        if (!ctype_attr.isNull()) {
            std::string ctype = ctype_attr;
            if (ctype == "Model") break;
        }
    }
    if (!found) return std::nullopt;
    return getAxis2Placement(wcs);
}

Eigen::Matrix4d local2global(const Eigen::Matrix4d& matrix,
                             const HelmertTransformation& p) {
    const double theta = std::atan2(p.xao, p.xaa);
    const double c = std::cos(theta);
    const double s = std::sin(theta);

    Eigen::Matrix4d S = Eigen::Matrix4d::Identity();
    S(0, 0) = p.scale * p.factor_x;
    S(1, 1) = p.scale * p.factor_y;
    S(2, 2) = p.scale * p.factor_z;

    Eigen::Matrix4d R = Eigen::Matrix4d::Identity();
    R(0, 0) =  c; R(0, 1) = -s;
    R(1, 0) =  s; R(1, 1) =  c;

    Eigen::Matrix4d result = R * S * matrix;
    // The scale was baked into the rotation+scale matrix so each axis column
    // ended up scaled.  Renormalise so the rotation part is pure orientation
    // and the translation alone carries the scaled offsets.
    for (int col = 0; col < 3; ++col) {
        Eigen::Vector3d v = result.block<3, 1>(0, col);
        const double n = v.norm();
        if (n > 0.0) result.block<3, 1>(0, col) = v / n;
    }
    result(0, 3) += p.e;
    result(1, 3) += p.n;
    result(2, 3) += p.h;
    return result;
}

Eigen::Matrix4d autoLocal2Global(ifcopenshell::file* ifc_file,
                                 const Eigen::Matrix4d& matrix,
                                 bool should_return_in_map_units) {
    auto params = getHelmertTransformationParameters(ifc_file);
    if (!params) return matrix;

    Eigen::Matrix4d m = matrix;
    if (auto wcs = getWcs(ifc_file)) {
        m = wcs->inverse() * m;
    }
    Eigen::Matrix4d result = local2global(m, *params);
    if (!should_return_in_map_units) {
        result(0, 3) /= params->scale;
        result(1, 3) /= params->scale;
        result(2, 3) /= params->scale;
    }
    return result;
}
