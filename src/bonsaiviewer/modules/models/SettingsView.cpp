// This file was generated with the assistance of an AI coding tool.
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

#include "SettingsView.h"
#include "SettingsDialog.h"

#include "../../SessionState.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/Geolocation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/Unit.h"

#include <cmath>

namespace bonsaiviewer::modules::models {

namespace {

QString formatNumber(double value) {
    return QString::number(value, 'f', 6);
}

QString formatAngleDms(double degrees) {
    const double absolute = std::fabs(degrees);
    const int d = static_cast<int>(absolute);
    const double minutes_total = (absolute - static_cast<double>(d)) * 60.0;
    const int m = static_cast<int>(minutes_total);
    const double s = (minutes_total - static_cast<double>(m)) * 60.0;
    const QString sign = degrees < 0.0 ? "-" : "";
    return QString("%1%2° %3' %4\"").arg(sign).arg(d).arg(m, 2, 10, QChar('0')).arg(formatNumber(s));
}

SelectedModelGeorefState unknownState(const QString& georef, const QString& type) {
    return {
        georef,
        type,
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
        "—",
    };
}

QString formatCachedUnitScale(double meters_per_unit) {
    return QString("Cached scale: 1 unit = %1 m").arg(formatNumber(meters_per_unit));
}

std::string enumString(const attribute_value& av) {
    if (av.isNull()) return {};
    if (av.type() != ifcopenshell::Argument_ENUMERATION) return {};
    enumeration_reference er = av;
    return std::string(er.value() ? er.value() : "");
}

QString formatNamedUnit(const express::Base& unit) {
    if (!unit) return "—";
    auto entity = unit.as<express::Entity>();
    if (unit.declaration().is("IfcSIUnit")) {
        const std::string prefix = enumString(entity.get("Prefix"));
        const std::string name = enumString(entity.get("Name"));
        QString text;
        if (!prefix.empty()) {
            text += QString::fromStdString(prefix) + " ";
        }
        text += QString::fromStdString(name);
        auto symbol_it = kUnitSymbols.find(name);
        if (symbol_it != kUnitSymbols.end()) {
            text += " (" + QString::fromStdString(symbol_it->second) + ")";
        }
        return text;
    }

    auto name_attr = entity.get("Name");
    if (name_attr.isNull()) return "—";
    const std::string name = static_cast<std::string>(name_attr);
    QString text = QString::fromStdString(name);
    auto symbol_it = kUnitSymbols.find(name);
    if (symbol_it != kUnitSymbols.end()) {
        text += " (" + QString::fromStdString(symbol_it->second) + ")";
    }
    return text;
}

std::optional<QString> coordinateOperationType(ifcopenshell::file* ifc_file) {
    if (!ifc_file) return std::nullopt;
    try {
        const auto coordops = ifc_file->instances_by_type("IfcCoordinateOperation");
        if (!coordops.empty()) {
            return QString::fromStdString(coordops[0].declaration().name());
        }
    } catch (...) {
        return std::nullopt;
    }

    if (ifc_file->schema()->name() == "IFC2X3") {
        if (getHelmertTransformationParameters(ifc_file)) {
            return QStringLiteral("ePSet_MapConversion");
        }
    }
    return QStringLiteral("None");
}

SelectedModelGeorefState stateFromLiveFile(ifcopenshell::file* ifc_file) {
    if (!ifc_file) return unknownState("Not available yet", "No data source");

    const auto params = getHelmertTransformationParameters(ifc_file);
    const auto coordop_type = coordinateOperationType(ifc_file);
    const auto project_unit_value = getProjectUnit(ifc_file, "LENGTHUNIT");
    const auto map_unit_value = getMapUnit(ifc_file);
    const QString project_unit = project_unit_value ? formatNamedUnit(*project_unit_value) : QString("—");
    const QString map_unit = map_unit_value ? formatNamedUnit(*map_unit_value) : project_unit;

    if (!params) {
        auto state = unknownState("No", coordop_type.value_or("Unknown"));
        state.project_unit = project_unit;
        state.map_unit = map_unit;
        return state;
    }

    const double rotation_dd = xaxis2angleDeg(params->xaa, params->xao);
    return {
        "Yes",
        coordop_type.value_or("Unknown"),
        project_unit,
        map_unit,
        formatNumber(params->e),
        formatNumber(params->n),
        formatNumber(params->h),
        formatNumber(params->xaa),
        formatNumber(params->xao),
        formatNumber(rotation_dd),
        formatAngleDms(rotation_dd),
        formatNumber(params->scale),
        formatNumber(params->factor_x),
        formatNumber(params->factor_y),
        formatNumber(params->factor_z),
    };
}

SelectedModelGeorefState stateFromCachedGeoref(const ModelGeoref& georef) {
    if (!georef.has_coordinate_operation) {
        return unknownState("No", "None");
    }

    const Eigen::Matrix4d& m = georef.coordinate_operation_meters;
    const Eigen::Vector3d translation = m.block<3, 1>(0, 3);
    const Eigen::Vector3d x_axis = m.block<3, 1>(0, 0);
    const Eigen::Vector3d y_axis = m.block<3, 1>(0, 1);
    const double factor_x = x_axis.norm();
    const double factor_y = y_axis.norm();
    const double factor_z = m.block<3, 1>(0, 2).norm();
    const double scale = (factor_x + factor_y) * 0.5;
    const double x_axis_abscissa = factor_x > 0.0 ? x_axis.x() / factor_x : 1.0;
    const double x_axis_ordinate = factor_x > 0.0 ? x_axis.y() / factor_x : 0.0;
    constexpr double kRadiansToDegrees = 57.29577951308232;
    const double rotation_dd = std::atan2(x_axis_ordinate, x_axis_abscissa) * kRadiansToDegrees;

    return {
        "Yes",
        "Cached coordinate operation",
        formatCachedUnitScale(georef.units.project_length_to_meters),
        formatCachedUnitScale(georef.units.map_unit_to_meters),
        formatNumber(translation.x()),
        formatNumber(translation.y()),
        formatNumber(translation.z()),
        formatNumber(x_axis_abscissa),
        formatNumber(x_axis_ordinate),
        formatNumber(rotation_dd),
        formatAngleDms(rotation_dd),
        formatNumber(scale),
        formatNumber(factor_x),
        formatNumber(factor_y),
        formatNumber(factor_z),
    };
}

} // namespace

SettingsView::SettingsView(SettingsDialog* widget,
                           bonsaiviewer::SessionState* session_state)
    : widget_(widget), session_state_(session_state)
{
}

void SettingsView::refresh(const QString& fed_id) const {
    if (!widget_) {
        return;
    }

    if (!session_state_) {
        widget_->renderSelectedModelGeoref(unknownState("Unavailable", "No session state"));
        return;
    }

    SceneLoader* loader = session_state_->loader();
    if (!loader) {
        widget_->renderSelectedModelGeoref(unknownState("Unavailable", "No loader"));
        return;
    }

    const uint32_t mid = session_state_->modelIdForFedId(fed_id);
    if (mid == 0) {
        widget_->renderSelectedModelGeoref(unknownState("Not loaded", "No live model"));
        return;
    }

    if (auto* ifc_file = loader->ifcFile(mid)) {
        widget_->renderSelectedModelGeoref(stateFromLiveFile(ifc_file));
        return;
    }

    const ModelGeoref* georef = loader->modelGeoref(mid);
    if (!georef) {
        widget_->renderSelectedModelGeoref(unknownState("Not available yet", "No data source"));
        return;
    }
    widget_->renderSelectedModelGeoref(stateFromCachedGeoref(*georef));
}

} // namespace bonsaiviewer::modules::models
