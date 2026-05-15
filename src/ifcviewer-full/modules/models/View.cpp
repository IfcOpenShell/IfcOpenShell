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

#include "View.h"

#include "Panel.h"

#include "../../ViewerSettings.h"
#include "../../SessionState.h"
#include "../../../ifcviewer/Federation.h"

namespace ifcviewerfull::modules::models {

namespace {

TreeNode makeGroupNode(const Federation* federation, const Federation::Group* group) {
    TreeNode node;
    node.id = group->id;
    node.name = group->display_name;
    node.kind = ItemKind::Group;
    node.visible = group->visible;

    for (const auto& child_group : group->children) {
        node.children.append(makeGroupNode(federation, child_group.get()));
    }

    for (const auto& model : federation->models()) {
        if (model.group_id != group->id) continue;
        node.children.append({
            model.id,
            model.display_name,
            ItemKind::Model,
            federation->isModelEffectivelyVisible(model.id),
            {}
        });
    }
    return node;
}

// Walks the federation's group tree, appending every group except those under
// exclude_subtree_root (used to prevent a group from being moved into itself).
void collectGroupsRecursive(const Federation::Group* group,
                            const QString& exclude_subtree_root,
                            QList<GroupOption>& out) {
    if (group->id == exclude_subtree_root) return;
    out.append({group->id, group->display_name});
    for (const auto& child : group->children) {
        collectGroupsRecursive(child.get(), exclude_subtree_root, out);
    }
}

} // namespace

ModelsPanelView::ModelsPanelView(ModelsPanel* widget,
                                 ifcviewerfull::SessionState* session_state,
                                 QObject* parent)
    : QObject(parent)
    , widget_(widget)
    , session_state_(session_state)
{
    connect(session_state_, &SessionState::modelsChanged,     this, &ModelsPanelView::refresh);
    connect(session_state_, &SessionState::federationChanged, this, &ModelsPanelView::refresh);
    connect(session_state_, &SessionState::visibilityChanged, this, &ModelsPanelView::refresh);
    connect(session_state_, &SessionState::projectReset,      this, &ModelsPanelView::refresh);
    connect(session_state_, &SessionState::projectOpened,     this, [this](const QString&) { refresh(); });
    connect(&ifcviewerfull::ViewerSettings::instance(),
            &ifcviewerfull::ViewerSettings::themeChanged,
            this, &ModelsPanelView::refresh);

    widget_->setGroupListProvider([this](const QString& exclude_subtree_root) {
        return groupListForMove(exclude_subtree_root);
    });

    refresh();
}

void ModelsPanelView::refresh() {
    Federation* federation = session_state_->federation();
    QList<TreeNode> nodes;
    for (const auto& root_group : federation->rootGroups()) {
        nodes.append(makeGroupNode(federation, root_group.get()));
    }
    for (const auto& model : federation->models()) {
        if (!model.group_id.isEmpty()) continue;
        nodes.append({
            model.id,
            model.display_name,
            ItemKind::Model,
            federation->isModelEffectivelyVisible(model.id),
            {}
        });
    }
    widget_->setNodes(nodes);
}

QList<GroupOption> ModelsPanelView::groupListForMove(const QString& exclude_subtree_root) const {
    QList<GroupOption> out;
    for (const auto& root : session_state_->federation()->rootGroups()) {
        collectGroupsRecursive(root.get(), exclude_subtree_root, out);
    }
    return out;
}

} // namespace ifcviewerfull::modules::models
