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

} // namespace

ModelsPanelView::ModelsPanelView(ModelsPanel* widget,
                                 ifcviewerfull::SessionState* session_state,
                                 QObject* parent)
    : QObject(parent), widget_(widget), session_state_(session_state)
{
    connect(session_state_, &ifcviewerfull::SessionState::modelsChanged,
            this, [this]() { reload(); });
    connect(session_state_, &ifcviewerfull::SessionState::federationStructureChanged,
            this, [this]() { reload(); });
    connect(session_state_, &ifcviewerfull::SessionState::visibilityChanged,
            this, [this]() { reload(); });
    connect(session_state_, &ifcviewerfull::SessionState::projectReset,
            this, [this]() { reload(); });
    connect(session_state_, &ifcviewerfull::SessionState::projectOpened,
            this, [this](const QString&) { reload(); });
    connect(&ifcviewerfull::ViewerSettings::instance(),
            &ifcviewerfull::ViewerSettings::themeChanged,
            this, [this]() { reload(); });

    reload();
}

void ModelsPanelView::reload() {
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

} // namespace ifcviewerfull::modules::models
