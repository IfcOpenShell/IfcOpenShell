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

#ifndef IFCINTERFACE_COMPONENTS_ICONS_SVGICON_H
#define IFCINTERFACE_COMPONENTS_ICONS_SVGICON_H

#include <QIcon>
#include <QPixmap>
#include <QString>
#include <QSize>

namespace ifcinterface::components::icons {

QPixmap renderTintedSvgPixmap(const QString& icon_path, const QString& color, const QSize& size);
QIcon makeTintedSvgIcon(const QString& icon_path,
                        const QString& normal = "#39b54a",
                        const QString& active = "#53c763",
                        const QString& disabled = "#6f7988");
QIcon makeSvgIcon(const QString& icon_path);
QPixmap makeSvgPixmap(const QString& icon_path, const QSize& size);

} // namespace ifcinterface::components::icons

#endif
