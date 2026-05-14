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

#ifndef IFCINTERFACE_INTERFACESETTINGS_H
#define IFCINTERFACE_INTERFACESETTINGS_H

#include <QObject>
#include <QString>
#include <vector>

namespace ifcinterface {

class InterfaceSettings : public QObject {
    Q_OBJECT
public:
    enum class ThemeMode {
        Dark = 0,
        Light = 1,
        Custom = 2,
    };
    Q_ENUM(ThemeMode)

    struct ThemeColorSpec {
        const char* key;
        const char* label;
        const char* dark_default;
        const char* light_default;
    };

    static InterfaceSettings& instance();
    static const std::vector<ThemeColorSpec>& themeColorSpecs();

    ThemeMode themeMode() const;
    void setThemeMode(ThemeMode mode);

    QString color(const QString& key) const;
    QString customColor(const QString& key) const;
    void setCustomColor(const QString& key, const QString& value);

signals:
    void themeModeChanged(ThemeMode mode);
    void themeChanged();

private:
    InterfaceSettings();
    void load();
    void persist() const;

    ThemeMode theme_mode_ = ThemeMode::Dark;
    std::vector<QString> custom_colors_;
};

} // namespace ifcinterface

#endif
