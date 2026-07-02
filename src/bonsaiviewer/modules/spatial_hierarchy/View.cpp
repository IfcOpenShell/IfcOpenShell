// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "View.h"

#include "Panel.h"

#include "../../SessionState.h"

namespace bonsaiviewer::modules::spatial_hierarchy {

namespace {

TreeNode* findNodeRecursive(QList<TreeNode>& nodes, const NodePath& path, int depth) {
    for (auto& node : nodes) {
        if (node.name != path.at(depth)) continue;
        if (depth == path.size() - 1) return &node;
        return findNodeRecursive(node.children, path, depth + 1);
    }
    return nullptr;
}

} // namespace

SpatialHierarchyPanelView::SpatialHierarchyPanelView(SpatialHierarchyPanel* widget,
                                                     bonsaiviewer::SessionState* session_state,
                                                     QObject* parent)
    : QObject(parent), widget_(widget), session_state_(session_state)
{
    nodes_ = {
        {"Site A", ItemKind::Site, true,
         {{"Building 01", ItemKind::Building, true,
           {{"Level 02", ItemKind::Storey, true,
             {{"Lobby", ItemKind::Space, true, {}},
              {"Core", ItemKind::Space, true, {}}}}}}}},
    };

    connect(widget_, &SpatialHierarchyPanel::visibilityToggleRequested, this, [this](const NodePath& path) {
        if (auto* node = findNode(path)) {
            node->visible = !node->visible;
            reload();
            session_state_->setStatusMessage("Spatial", node->visible ? "Item shown" : "Item hidden");
        }
    });

    reload();
}

void SpatialHierarchyPanelView::reload() {
    widget_->setNodes(nodes_);
}

TreeNode* SpatialHierarchyPanelView::findNode(const NodePath& path) {
    if (path.isEmpty()) return nullptr;
    return findNodeRecursive(nodes_, path, 0);
}

} // namespace bonsaiviewer::modules::spatial_hierarchy
