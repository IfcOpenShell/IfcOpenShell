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

#include "FederationItemModel.h"
#include "Panel.h"

#include "../../ViewerSettings.h"
#include "../../SessionState.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QTimer>

namespace bonsaiviewer::modules::models {

namespace {

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

QList<GroupOption> validMoveTargets(const Federation& federation,
                                    const QString& exclude_subtree_root) {
    QList<GroupOption> out;
    for (const auto& root : federation.rootGroups()) {
        collectGroupsRecursive(root.get(), exclude_subtree_root, out);
    }
    return out;
}

ModelsPanelView::ModelsPanelView(ModelsPanel* widget,
                                 bonsaiviewer::SessionState* session_state,
                                 ViewportWindow* viewport,
                                 QObject* parent)
    : QObject(parent)
    , widget_(widget)
    , session_state_(session_state)
    , viewport_(viewport)
    , model_(new FederationItemModel(session_state->federation(), this))
{
    widget_->setModel(model_);

    // Coarse signals: full rebuild + re-style. The granular Federation
    // signals are handled inside FederationItemModel and don't reach here.
    auto rebuild = [this]() { model_->rebuildAll(); refreshResidency(); };
    connect(session_state_, &SessionState::projectReset,  this, rebuild);
    connect(session_state_, &SessionState::projectOpened, this, rebuild);
    connect(&bonsaiviewer::ViewerSettings::instance(),
            &bonsaiviewer::ViewerSettings::themeChanged,
            this, rebuild);
    connect(session_state_, &SessionState::activeModelChanged, this, [this](const QString& model_id) {
        model_->setActiveModelId(model_id);
    });

    // Residency: immediately on the events that change it, and on a slow
    // tick for the memory figures, which move as chunks stream.
    auto refresh = [this]() { refreshResidency(); };
    connect(session_state_, &SessionState::modelLoadStateChanged, this, refresh);
    connect(session_state_, &SessionState::modelGeometryReady,   this, refresh);
    connect(session_state_, &SessionState::modelsChanged,        this, refresh);
    auto* tick = new QTimer(this);
    tick->setInterval(1000);
    connect(tick, &QTimer::timeout, this, refresh);
    tick->start();
}

void ModelsPanelView::refreshResidency() {
    for (const auto& model : session_state_->federation()->models()) {
        const uint32_t session_model_id = session_state_->sessionModelIdForModelId(model.id);
        if (session_model_id == 0) {
            model_->setModelResidency(model.id, false, 0);
            continue;
        }
        model_->setModelResidency(model.id,
                                  viewport_->isModelUnloaded(session_model_id),
                                  viewport_->modelVramBytes(session_model_id));
    }
}

} // namespace bonsaiviewer::modules::models
