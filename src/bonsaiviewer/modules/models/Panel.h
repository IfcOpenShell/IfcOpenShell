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

#ifndef IFCINTERFACE_MODULES_MODELS_PANEL_H
#define IFCINTERFACE_MODULES_MODELS_PANEL_H

#include "Types.h"

#include "../../components/Panel.h"

class QTreeView;
class ViewportWindow;
namespace bonsaiviewer { class SessionState; }

namespace bonsaiviewer::modules::models {

class FederationItemModel;

// The widget for the Models dock. Owns no domain state; click handlers call
// commands directly. The QTreeView reads from a FederationItemModel which
// subscribes to Federation's granular signals — view state (expansion,
// selection, scroll) is preserved across mutations automatically.
class ModelsPanel : public components::Panel {
    Q_OBJECT
public:
    explicit ModelsPanel(bonsaiviewer::SessionState* session_state,
                         ViewportWindow* viewport,
                         QWidget* parent = nullptr);

    // Owned externally (the View constructs and owns the model). The panel
    // assigns it to the tree view; same model can outlive setModel calls.
    void setModel(FederationItemModel* model);

private:
    bonsaiviewer::SessionState* session_state_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
    QTreeView* tree_ = nullptr;
    FederationItemModel* model_ = nullptr;
};

} // namespace bonsaiviewer::modules::models

#endif
