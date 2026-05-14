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

#ifndef IFCINTERFACE_MODULES_PROPERTIES_PANEL_H
#define IFCINTERFACE_MODULES_PROPERTIES_PANEL_H

#include "Types.h"

#include "../../components/Panel.h"

#include <QString>

class QLabel;
class QLineEdit;
class QToolButton;

namespace ifcinterface::modules::properties {

class PropertiesPanel : public components::Panel {
    Q_OBJECT
public:
    explicit PropertiesPanel(QWidget* parent = nullptr);

    void render(const PropertiesPanelState& state);

private:
    bool attributes_expanded_ = true;
    bool relationships_expanded_ = true;
    bool properties_expanded_ = true;
    bool quantities_expanded_ = true;
    bool properties_filter_visible_ = false;
    bool quantities_filter_visible_ = false;
    QString properties_filter_text_;
    QString quantities_filter_text_;
};

} // namespace ifcinterface::modules::properties

#endif
