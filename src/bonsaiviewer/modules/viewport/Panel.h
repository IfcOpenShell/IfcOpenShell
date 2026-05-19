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

#ifndef IFCINTERFACE_MODULES_VIEWPORT_PANEL_H
#define IFCINTERFACE_MODULES_VIEWPORT_PANEL_H

#include <QWidget>

class ViewportWindow;

namespace bonsaiviewer::modules::viewport {

class ViewportPanel : public QWidget {
    Q_OBJECT

public:
    explicit ViewportPanel(QWidget* parent = nullptr);

    ViewportWindow* viewport() const { return viewport_; }

private:
    ViewportWindow* viewport_ = nullptr;
    QWidget* viewport_container_ = nullptr;
};

} // namespace bonsaiviewer::modules::viewport

#endif
