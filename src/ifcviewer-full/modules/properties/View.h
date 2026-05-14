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

#ifndef IFCINTERFACE_PANELS_PROPERTIESPANELVIEW_H
#define IFCINTERFACE_PANELS_PROPERTIESPANELVIEW_H

#include "Types.h"

#include <QObject>

namespace ifcviewerfull { class SessionState; }
namespace ifcviewerfull::modules::properties {

class PropertiesPanel;

class PropertiesPanelView : public QObject {
    Q_OBJECT
public:
    explicit PropertiesPanelView(PropertiesPanel* widget,
                                 ifcviewerfull::SessionState* session_state,
                                 QObject* parent = nullptr);

private:
    void refresh(uint32_t object_id);

    PropertiesPanel* widget_ = nullptr;
    ifcviewerfull::SessionState* session_state_ = nullptr;
};

} // namespace ifcviewerfull::modules::properties

#endif
