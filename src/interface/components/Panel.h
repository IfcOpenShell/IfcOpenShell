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

#ifndef IFCINTERFACE_COMPONENTS_PANEL_PANELCHROME_H
#define IFCINTERFACE_COMPONENTS_PANEL_PANELCHROME_H

#include <QDockWidget>

class QWidget;

namespace ifcinterface::components {

class Panel : public QDockWidget {
    Q_OBJECT

public:
    explicit Panel(const QString& title,
                   QWidget* content,
                   QWidget* parent = nullptr,
                   bool has_settings = false,
                   bool scrollable = false);
};

} // namespace ifcinterface::components

#endif
