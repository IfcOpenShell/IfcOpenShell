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

#ifndef IFCINTERFACE_PANELS_MODELSPANELVIEW_H
#define IFCINTERFACE_PANELS_MODELSPANELVIEW_H

#include "Types.h"

#include <QObject>

class Federation;
namespace bonsaiviewer { class SessionState; }

namespace bonsaiviewer::modules::models {

class FederationItemModel;
class ModelsPanel;

// Pure derivation used by ModelsPanel when building its "move to..." menus.
// Walks the federation's group tree and returns every group except those in
// the subtree rooted at exclude_subtree_root (skip a group's own subtree to
// prevent a cyclic move). Pass an empty exclude_subtree_root to get every
// group back.
QList<GroupOption> validMoveTargets(const Federation& federation,
                                    const QString& exclude_subtree_root);

// Owns the FederationItemModel, hands it to the panel, and listens to the
// coarse session signals (project open/reset, theme change) — those are the
// "rebuild from scratch" cases the model itself doesn't subscribe to.
// Granular Federation events are handled inside the model.
class ModelsPanelView : public QObject {
    Q_OBJECT
public:
    explicit ModelsPanelView(ModelsPanel* widget,
                             bonsaiviewer::SessionState* session_state,
                             QObject* parent = nullptr);

private:
    ModelsPanel* widget_ = nullptr;
    bonsaiviewer::SessionState* session_state_ = nullptr;
    FederationItemModel* model_ = nullptr;
};

} // namespace bonsaiviewer::modules::models

#endif
