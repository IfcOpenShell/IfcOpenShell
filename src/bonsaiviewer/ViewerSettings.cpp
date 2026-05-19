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

#include "ViewerSettings.h"

#include "components/Style.h"

#include <QColor>
#include <QSettings>

namespace {

constexpr const char* kThemeModeKey = "interface/theme/mode";
constexpr const char* kThemeColorPrefix = "interface/theme/colors/";

using Spec = bonsaiviewer::ViewerSettings::ThemeColorSpec;

const std::vector<Spec> kThemeColorSpecs = {
    {"app_background", "App Background", bonsaiviewer::components::style::palette::app_background, "#eef1f5"},
    {"border", "Border", bonsaiviewer::components::style::palette::border, "#c9d1dc"},
    {"selection_background", "Selection Background", bonsaiviewer::components::style::palette::selection_background,
     "#2f9e44"},
    {"tab_bar_background", "Tab Bar Background", bonsaiviewer::components::style::palette::tab_bar_background,
     "#eef1f5"},
    {"tab_background", "Tab Background", bonsaiviewer::components::style::palette::tab_background, "#e3e8ef"},
    {"ribbon_background", "Ribbon Background", bonsaiviewer::components::style::palette::ribbon_background,
     "#e3e8ef"},
    {"ribbon_button_hover", "Ribbon Button Hover", bonsaiviewer::components::style::palette::ribbon_button_hover,
     "#d6dde7"},
    {"ribbon_button_pressed", "Ribbon Button Pressed", bonsaiviewer::components::style::palette::ribbon_button_pressed,
     "#cad3df"},
    {"viewport_shell_background", "Viewport Shell Background",
     bonsaiviewer::components::style::palette::viewport_shell_background, "#dbe1e8"},
    {"viewport_background", "Viewport Background", bonsaiviewer::components::style::palette::viewport_background,
     "#eef2f6"},
    {"panel_background", "Panel Background", bonsaiviewer::components::style::palette::panel_background, "#ffffff"},
    {"control_background", "Control Background", bonsaiviewer::components::style::palette::control_background,
     "#f5f7fa"},
    {"control_border_focus", "Control Border Focus", bonsaiviewer::components::style::palette::control_border_focus,
     "#7c8ca3"},
    {"box_background", "Box Background", bonsaiviewer::components::style::palette::box_background, "#f5f7fa"},
    {"scroll_handle", "Scroll Handle", bonsaiviewer::components::style::palette::scroll_handle, "#b1bac8"},
    {"scroll_handle_hover", "Scroll Handle Hover", bonsaiviewer::components::style::palette::scroll_handle_hover,
     "#929daf"},
    {"status_background", "Status Background", bonsaiviewer::components::style::palette::status_background,
     "#edf1f5"},
    {"section_header_background", "Section Header Background",
     bonsaiviewer::components::style::palette::section_header_background, "#eef2f6"},
    {"primary_text", "Primary Text", bonsaiviewer::components::style::palette::primary_text, "#1f2937"},
    {"secondary_text", "Secondary Text", bonsaiviewer::components::style::palette::secondary_text, "#5b6676"},
    {"disabled_text", "Disabled Text", bonsaiviewer::components::style::palette::disabled_text, "#8b95a3"},
    {"warning_text", "Warning Text", bonsaiviewer::components::style::palette::warning_text, "#b26b00"},
    {"selection_text", "Selection Text", bonsaiviewer::components::style::palette::selection_text, "#ffffff"},
    {"hover_text", "Hover Text", bonsaiviewer::components::style::palette::hover_text, "#0f172a"},
    {"icon_color", "Icon Color", "#e7ebf2", "#445066"},
    {"icon_active_color", "Icon Active Color", "#ffffff", "#101828"},
    {"icon_disabled_color", "Icon Disabled Color", "#6f7988", "#98a2b3"},
    {"icon_accent_color", "Accent Icon Color", "#39b54a", "#2f9e44"},
    {"icon_accent_active_color", "Accent Icon Active Color", "#53c763", "#267e37"},
};

int colorIndexForKey(const QString& key) {
    for (size_t i = 0; i < kThemeColorSpecs.size(); ++i) {
        if (QString::fromUtf8(kThemeColorSpecs[i].key) == key) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

QString normalizedColor(const QString& value, const QString& fallback) {
    const QString trimmed = value.trimmed();
    if (!QColor::isValidColorName(trimmed)) return fallback;
    return QColor(trimmed).name(QColor::HexRgb);
}

} // namespace

namespace bonsaiviewer {

ViewerSettings& ViewerSettings::instance() {
    static ViewerSettings inst;
    return inst;
}

const std::vector<ViewerSettings::ThemeColorSpec>& ViewerSettings::themeColorSpecs() {
    return kThemeColorSpecs;
}

ViewerSettings::ViewerSettings() {
    custom_colors_.resize(kThemeColorSpecs.size());
    load();
}

ViewerSettings::ThemeMode ViewerSettings::themeMode() const {
    return theme_mode_;
}

void ViewerSettings::setThemeMode(ThemeMode mode) {
    if (theme_mode_ == mode) return;
    theme_mode_ = mode;
    persist();
    emit themeModeChanged(mode);
    emit themeChanged();
}

QString ViewerSettings::color(const QString& key) const {
    const int index = colorIndexForKey(key);
    if (index < 0) return {};

    const auto& spec = kThemeColorSpecs[static_cast<size_t>(index)];
    switch (theme_mode_) {
    case ThemeMode::Dark:
        return QString::fromUtf8(spec.dark_default);
    case ThemeMode::Light:
        return QString::fromUtf8(spec.light_default);
    case ThemeMode::Custom:
        return customColor(key);
    }
    return QString::fromUtf8(spec.dark_default);
}

QString ViewerSettings::customColor(const QString& key) const {
    const int index = colorIndexForKey(key);
    if (index < 0) return {};
    const auto& spec = kThemeColorSpecs[static_cast<size_t>(index)];
    const QString& stored = custom_colors_[static_cast<size_t>(index)];
    return stored.isEmpty() ? QString::fromUtf8(spec.dark_default) : stored;
}

void ViewerSettings::setCustomColor(const QString& key, const QString& value) {
    const int index = colorIndexForKey(key);
    if (index < 0) return;

    const auto& spec = kThemeColorSpecs[static_cast<size_t>(index)];
    const QString normalized = normalizedColor(value, QString::fromUtf8(spec.dark_default));
    QString& stored = custom_colors_[static_cast<size_t>(index)];
    if (stored == normalized) return;
    stored = normalized;
    persist();
    if (theme_mode_ == ThemeMode::Custom) {
        emit themeChanged();
    }
}

void ViewerSettings::load() {
    QSettings settings;
    int raw_mode = settings.value(kThemeModeKey, static_cast<int>(ThemeMode::Dark)).toInt();
    if (raw_mode < static_cast<int>(ThemeMode::Dark) || raw_mode > static_cast<int>(ThemeMode::Custom)) {
        raw_mode = static_cast<int>(ThemeMode::Dark);
    }
    theme_mode_ = static_cast<ThemeMode>(raw_mode);

    for (size_t i = 0; i < kThemeColorSpecs.size(); ++i) {
        const auto& spec = kThemeColorSpecs[i];
        const QString stored = settings.value(QString::fromUtf8(kThemeColorPrefix) + QString::fromUtf8(spec.key),
                                              QString::fromUtf8(spec.dark_default))
                                   .toString();
        custom_colors_[i] = normalizedColor(stored, QString::fromUtf8(spec.dark_default));
    }
}

void ViewerSettings::persist() const {
    QSettings settings;
    settings.setValue(kThemeModeKey, static_cast<int>(theme_mode_));
    for (size_t i = 0; i < kThemeColorSpecs.size(); ++i) {
        settings.setValue(QString::fromUtf8(kThemeColorPrefix) + QString::fromUtf8(kThemeColorSpecs[i].key),
                          custom_colors_[i]);
    }
}

} // namespace bonsaiviewer
