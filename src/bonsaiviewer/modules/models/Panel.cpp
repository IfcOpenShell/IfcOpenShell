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

#include "Panel.h"

#include "Commands.h"
#include "FederationItemModel.h"
#include "View.h"

#include "../../SessionState.h"
#include "../../components/Section.h"
#include "../../components/SvgIcon.h"
#include "../../../ifcviewer/Federation.h"

#include <QDataStream>
#include <QDrag>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QDropEvent>
#include <QHeaderView>
#include <QMenu>
#include <QMimeData>
#include <QSizePolicy>
#include <QTreeView>

namespace bonsaiviewer::modules::models {

namespace {

constexpr auto kDragMimeType = "application/x-bonsaiviewer-model-items";

QString idOf(const QModelIndex& index) {
    return index.sibling(index.row(), 0).data(FederationItemModel::IdRole).toString();
}

ItemKind kindOf(const QModelIndex& index) {
    return static_cast<ItemKind>(
        index.sibling(index.row(), 0).data(FederationItemModel::KindRole).toInt());
}

QStringList selectedModelIdsAt(QTreeView* tree, const QModelIndex& clicked_index) {
    QStringList ids;
    const QModelIndexList selection = tree->selectionModel()->selectedRows(0);
    bool clicked_in_selection = false;
    for (const QModelIndex& index : selection) {
        if (index == clicked_index.sibling(clicked_index.row(), 0)) {
            clicked_in_selection = true;
            break;
        }
    }
    if (clicked_in_selection) {
        for (const QModelIndex& index : selection) {
            if (kindOf(index) == ItemKind::Model) {
                ids << idOf(index);
            }
        }
        ids.removeDuplicates();
    } else {
        ids << idOf(clicked_index);
    }
    return ids;
}

constexpr int kVisibilityColumnWidth = 28;

// QTreeView subclass that handles drag-and-drop. Drop logic dispatches
// through commands (not directly into the model) so notifications + status
// messages happen the same way as menu-driven moves.
class ModelsTreeView : public QTreeView {
public:
    explicit ModelsTreeView(bonsaiviewer::SessionState* session_state, QWidget* parent)
        : QTreeView(parent), session_state_(session_state) {}

protected:
    void startDrag(Qt::DropActions actions) override {
        const QModelIndexList selection = selectionModel()->selectedRows(0);
        if (selection.isEmpty()) return;

        const auto first_kind = kindOf(selection.first());
        if (first_kind == ItemKind::Group && selection.size() != 1) return;

        QByteArray payload;
        QDataStream stream(&payload, QIODevice::WriteOnly);
        stream << static_cast<int>(first_kind);
        if (first_kind == ItemKind::Group) {
            stream << idOf(selection.first());
        } else {
            QStringList ids;
            for (const QModelIndex& index : selection) {
                if (kindOf(index) != first_kind) return;
                ids.push_back(idOf(index));
            }
            ids.removeDuplicates();
            stream << ids;
        }

        auto* mime = new QMimeData();
        mime->setData(QString::fromUtf8(kDragMimeType), payload);
        auto* drag = new QDrag(this);
        drag->setMimeData(mime);
        drag->exec(actions);
    }

    void dragEnterEvent(QDragEnterEvent* event) override {
        if (event->mimeData()->hasFormat(QString::fromUtf8(kDragMimeType))) {
            event->acceptProposedAction();
            return;
        }
        QTreeView::dragEnterEvent(event);
    }

    void dragMoveEvent(QDragMoveEvent* event) override {
        if (!event->mimeData()->hasFormat(QString::fromUtf8(kDragMimeType))) {
            QTreeView::dragMoveEvent(event);
            return;
        }
        QString target_group_id;
        if (!decodeTargetGroup(event->position().toPoint(), target_group_id) ||
            !canAcceptDrop(event->mimeData(), indexAt(event->position().toPoint()), target_group_id)) {
            event->ignore();
            return;
        }
        event->acceptProposedAction();
    }

    void dropEvent(QDropEvent* event) override {
        if (!event->mimeData()->hasFormat(QString::fromUtf8(kDragMimeType))) {
            QTreeView::dropEvent(event);
            return;
        }

        QString target_group_id;
        if (!decodeTargetGroup(event->position().toPoint(), target_group_id) ||
            !canAcceptDrop(event->mimeData(), indexAt(event->position().toPoint()), target_group_id)) {
            event->ignore();
            return;
        }

        QByteArray payload = event->mimeData()->data(QString::fromUtf8(kDragMimeType));
        QDataStream stream(&payload, QIODevice::ReadOnly);
        int kind_int = 0;
        stream >> kind_int;
        const auto kind = static_cast<ItemKind>(kind_int);
        if (kind == ItemKind::Group) {
            QString group_id;
            stream >> group_id;
            commands::moveGroup(*session_state_, group_id, target_group_id);
        } else {
            QStringList ids;
            stream >> ids;
            ids.removeDuplicates();
            if (!ids.isEmpty()) commands::moveModels(*session_state_, ids, target_group_id);
        }
        event->acceptProposedAction();
    }

private:
    bool decodeTargetGroup(const QPoint& pos, QString& out) const {
        out.clear();
        const QModelIndex index = indexAt(pos);
        if (!index.isValid()) return true;
        if (kindOf(index) != ItemKind::Group) return false;
        out = idOf(index);
        return true;
    }

    bool canAcceptDrop(const QMimeData* mime,
                       const QModelIndex& target_index,
                       const QString& target_group_id) const {
        QByteArray payload = mime->data(QString::fromUtf8(kDragMimeType));
        QDataStream stream(&payload, QIODevice::ReadOnly);
        int kind_int = 0;
        stream >> kind_int;
        const auto kind = static_cast<ItemKind>(kind_int);

        if (kind == ItemKind::Group) {
            QString group_id;
            stream >> group_id;
            if (group_id.isEmpty()) return false;
            if (!target_index.isValid()) return true;
            if (kindOf(target_index) != ItemKind::Group) return false;
            if (group_id == target_group_id) return false;
            for (QModelIndex ancestor_index = target_index; ancestor_index.isValid();
                 ancestor_index = ancestor_index.parent()) {
                if (idOf(ancestor_index) == group_id) return false;
            }
            return true;
        }

        if (kind == ItemKind::Model) {
            QStringList ids;
            stream >> ids;
            ids.removeDuplicates();
            if (ids.isEmpty()) return false;
            return !target_index.isValid() || !target_group_id.isNull();
        }

        return false;
    }

    bonsaiviewer::SessionState* session_state_;
};

} // namespace

ModelsPanel::ModelsPanel(bonsaiviewer::SessionState* session_state,
                         ViewportWindow* viewport,
                         QWidget* parent)
    : components::Panel("Models", nullptr, parent, true)
    , session_state_(session_state)
    , viewport_(viewport)
{
    auto* section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    section->setBodyExpanding(true);

    tree_ = new ModelsTreeView(session_state_, section);
    tree_->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    tree_->setIconSize(QSize(16, 16));
    tree_->setSelectionMode(QAbstractItemView::ExtendedSelection);
    tree_->setContextMenuPolicy(Qt::CustomContextMenu);
    tree_->setDragEnabled(true);
    tree_->viewport()->setAcceptDrops(true);
    tree_->setDropIndicatorShown(true);
    tree_->setDragDropMode(QAbstractItemView::DragDrop);
    tree_->setDefaultDropAction(Qt::MoveAction);
    tree_->setUniformRowHeights(true);
    tree_->setExpandsOnDoubleClick(false);
    tree_->setEditTriggers(QAbstractItemView::NoEditTriggers);
    tree_->header()->hide();

    section->addBodyWidget(tree_);
    addBodyWidget(section);

    connect(tree_, &QTreeView::clicked, this, [this](const QModelIndex& index) {
        if (!index.isValid()) return;
        if (index.column() == 1) {
            commands::toggleVisibility(*session_state_, kindOf(index), idOf(index));
            return;
        }
        // Clicking a model (its cube icon / row) makes it the active model.
        if (kindOf(index) == ItemKind::Model) {
            session_state_->setActiveModelId(idOf(index));
        }
    });

    connect(tree_, &QTreeView::customContextMenuRequested, this, [this](const QPoint& pos) {
        const QModelIndex index = tree_->indexAt(pos);
        QMenu menu(tree_);

        if (!index.isValid()) {
            QAction* add_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "Add Group");
            connect(add_group_action, &QAction::triggered, this, [this]() {
                commands::addGroup(*session_state_, *this, QString());
            });
            menu.exec(tree_->viewport()->mapToGlobal(pos));
            return;
        }

        const auto kind = kindOf(index);
        const QString id = idOf(index);

        QAction* toggle_action = menu.addAction(
            components::icons::makeSvgIcon(":/icons/eye.svg"), "Toggle Visibility");
        connect(toggle_action, &QAction::triggered, this, [this, kind, id]() {
            commands::toggleVisibility(*session_state_, kind, id);
        });

        if (kind == ItemKind::Group) {
            QAction* add_subgroup = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "New Subgroup");
            connect(add_subgroup, &QAction::triggered, this, [this, id]() {
                commands::addGroup(*session_state_, *this, id);
            });
            QAction* rename = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder.svg"), "Rename Group");
            connect(rename, &QAction::triggered, this, [this, id]() {
                commands::renameGroup(*session_state_, *this, id);
            });

            QMenu* move_menu = menu.addMenu("Move to Parent");
            QAction* move_root = move_menu->addAction("(Root)");
            connect(move_root, &QAction::triggered, this, [this, id]() {
                commands::moveGroup(*session_state_, id, QString());
            });
            move_menu->addSeparator();
            for (const auto& target : validMoveTargets(*session_state_->federation(), id)) {
                QAction* action = move_menu->addAction(target.display_name);
                const QString target_id = target.id;
                connect(action, &QAction::triggered, this, [this, id, target_id]() {
                    commands::moveGroup(*session_state_, id, target_id);
                });
            }

            QAction* remove = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-minus.svg"), "Remove Group");
            connect(remove, &QAction::triggered, this, [this, id]() {
                commands::removeGroup(*session_state_, *this, id);
            });
        } else {
            QString parent_group_id;
            const QModelIndex parent_index = index.parent();
            if (parent_index.isValid() && kindOf(parent_index) == ItemKind::Group) {
                parent_group_id = idOf(parent_index);
            }

            const QStringList selected_model_ids = selectedModelIdsAt(tree_, index);

            // Frame the camera on just these models — View All, scoped. Right
            // above Rename so the two "do something with this model" actions
            // that need no dialog sit together at the top.
            QAction* view_models = menu.addAction(
                components::icons::makeSvgIcon(":/icons/cube-scan.svg"),
                selected_model_ids.size() > 1 ? "View Selected Models"
                                             : "View Selected Model");
            connect(view_models, &QAction::triggered, this, [this, selected_model_ids]() {
                commands::viewModels(*session_state_, *viewport_, selected_model_ids);
            });

            QAction* rename = menu.addAction(
                components::icons::makeSvgIcon(":/icons/cube.svg"), "Rename");
            connect(rename, &QAction::triggered, this, [this, id]() {
                commands::renameModel(*session_state_, *this, id);
            });

            QAction* add_group = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "New Group");
            connect(add_group, &QAction::triggered, this, [this, parent_group_id]() {
                commands::addGroup(*session_state_, *this, parent_group_id);
            });

            QMenu* move_menu = menu.addMenu("Move to Group");
            QAction* move_root = move_menu->addAction("(Root)");
            connect(move_root, &QAction::triggered, this, [this, selected_model_ids]() {
                commands::moveModels(*session_state_, selected_model_ids, QString());
            });
            move_menu->addSeparator();
            for (const auto& target : validMoveTargets(*session_state_->federation(), QString())) {
                QAction* action = move_menu->addAction(target.display_name);
                const QString target_id = target.id;
                connect(action, &QAction::triggered, this, [this, selected_model_ids, target_id]() {
                    commands::moveModels(*session_state_, selected_model_ids, target_id);
                });
            }

            const Federation::Model* selected = session_state_->federation()->findById(id);
            const bool has_cloud_source = selected && selected->source_connector != "local";

            menu.addSeparator();
            QAction* save_to_cloud = menu.addAction(
                components::icons::makeSvgIcon(":/icons/cloud-square.svg"), "Save To Cloud");
            save_to_cloud->setEnabled(has_cloud_source);
            if (!has_cloud_source) {
                save_to_cloud->setToolTip(
                    "This model has no cloud target yet. Use \"Save As To Cloud\" first.");
            }
            connect(save_to_cloud, &QAction::triggered, this, [this, id]() {
                commands::saveModelToCloud(*session_state_, *this, id);
            });
            QAction* save_as_to_cloud = menu.addAction(
                components::icons::makeSvgIcon(":/icons/cloud-square.svg"), "Save As To Cloud");
            connect(save_as_to_cloud, &QAction::triggered, this, [this, id]() {
                commands::saveModelAsToCloud(*session_state_, *this, id);
            });

            menu.addSeparator();
            QAction* remove = menu.addAction(
                components::icons::makeSvgIcon(":/icons/minus-square.svg"), "Remove Model");
            connect(remove, &QAction::triggered, this, [this, id]() {
                commands::removeModel(*session_state_, *viewport_, *this, id);
            });
        }
        menu.exec(tree_->viewport()->mapToGlobal(pos));
    });

    connect(this, &components::Panel::settingsRequested, this, [this]() {
        commands::openSettings(*session_state_, *this);
    });
}

void ModelsPanel::setModel(FederationItemModel* model) {
    model_ = model;
    tree_->setModel(model);
    // QHeaderView resets per-section resize modes to Interactive whenever the
    // column set is rebuilt — which FederationItemModel::rebuildAll() does on
    // project open / theme change (clear() + setColumnCount()). Re-apply the
    // layout every time the columns reappear.
    connect(tree_->header(), &QHeaderView::sectionCountChanged,
            this, [this]() { applyColumnLayout(); });
    applyColumnLayout();
    tree_->expandAll();
}

void ModelsPanel::applyColumnLayout() {
    // Column 0 (name) stretches to fill; column 1 (visibility icon) is fixed.
    QHeaderView* header = tree_->header();
    if (header->count() < 2) return;
    header->setStretchLastSection(false);
    header->setMinimumSectionSize(kVisibilityColumnWidth);
    header->setSectionResizeMode(0, QHeaderView::Stretch);
    header->setSectionResizeMode(1, QHeaderView::Fixed);
    header->resizeSection(1, kVisibilityColumnWidth);
}

} // namespace bonsaiviewer::modules::models
