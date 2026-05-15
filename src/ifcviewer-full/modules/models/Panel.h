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

#include <functional>

class QTreeWidget;
class QTreeWidgetItem;
class ViewportWindow;
namespace ifcviewerfull { class SessionState; }

namespace ifcviewerfull::modules::models {

// The widget for the Models dock. Owns no domain state; its click handlers
// call commands directly. The View tells it what to render (setNodes) and
// supplies derived data for the right-click menu (setGroupListProvider).
class ModelsPanel : public components::Panel {
    Q_OBJECT
public:
    // Returns the groups a move operation may target. If exclude_subtree_root
    // is non-empty, that group + its descendants are excluded so a group can't
    // be moved into its own subtree. For model moves the panel passes an empty
    // string and gets every group back.
    using GroupListProvider =
        std::function<QList<GroupOption>(const QString& exclude_subtree_root)>;

    explicit ModelsPanel(ifcviewerfull::SessionState* session_state,
                         ViewportWindow* viewport,
                         QWidget* parent = nullptr);

    void setNodes(const QList<TreeNode>& nodes);
    void setGroupListProvider(GroupListProvider provider);

private:
    void addNode(QTreeWidgetItem* parent, const TreeNode& node);

    ifcviewerfull::SessionState* session_state_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
    QTreeWidget* tree_ = nullptr;
    GroupListProvider group_list_provider_;
};

} // namespace ifcviewerfull::modules::models

#endif
