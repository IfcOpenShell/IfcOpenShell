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

#include "SvgIcon.h"

#include "../ViewerSettings.h"

#include <QFile>
#include <QPainter>
#include <QRegularExpression>
#include <QSvgRenderer>

namespace ifcviewerfull::components::icons {

QPixmap renderTintedSvgPixmap(const QString& icon_path, const QString& color, const QSize& size) {
    QFile file(icon_path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QIcon(icon_path).pixmap(size);
    }

    QString svg = QString::fromUtf8(file.readAll());
    svg.replace("currentColor", color, Qt::CaseSensitive);
    svg.replace(QRegularExpression(R"(stroke="[^"]*")"), QString("stroke=\"%1\"").arg(color));
    svg.replace(QRegularExpression(R"(fill="none")"), "fill=\"none\"");

    QSvgRenderer renderer(svg.toUtf8());
    QPixmap pixmap(size);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    renderer.render(&painter);
    return pixmap;
}

QIcon makeTintedSvgIcon(const QString& icon_path, const QString& normal,
                        const QString& active, const QString& disabled) {
    QFile file(icon_path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QIcon(icon_path);
    }

    QIcon icon;
    icon.addPixmap(renderTintedSvgPixmap(icon_path, normal, QSize(20, 20)), QIcon::Normal, QIcon::Off);
    icon.addPixmap(renderTintedSvgPixmap(icon_path, active, QSize(20, 20)), QIcon::Active, QIcon::Off);
    icon.addPixmap(renderTintedSvgPixmap(icon_path, active, QSize(20, 20)), QIcon::Selected, QIcon::Off);
    icon.addPixmap(renderTintedSvgPixmap(icon_path, disabled, QSize(20, 20)), QIcon::Disabled, QIcon::Off);
    return icon;
}

QIcon makeAccentSvgIcon(const QString& icon_path) {
    const auto& theme = ifcviewerfull::ViewerSettings::instance();
    return makeTintedSvgIcon(icon_path,
                             theme.color("icon_accent_color"),
                             theme.color("icon_accent_active_color"),
                             theme.color("icon_disabled_color"));
}

QIcon makeSvgIcon(const QString& icon_path) {
    const auto& theme = ifcviewerfull::ViewerSettings::instance();
    return makeTintedSvgIcon(icon_path,
                             theme.color("icon_color"),
                             theme.color("icon_active_color"),
                             theme.color("icon_disabled_color"));
}

QPixmap makeSvgPixmap(const QString& icon_path, const QSize& size) {
    return renderTintedSvgPixmap(icon_path, ifcviewerfull::ViewerSettings::instance().color("icon_color"), size);
}

} // namespace ifcviewerfull::components::icons
