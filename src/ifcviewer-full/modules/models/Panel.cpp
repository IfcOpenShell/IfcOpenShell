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

#include "Panel.h"

#include "Commands.h"

#include "../../ViewerSettings.h"
#include "../../components/Section.h"
#include "../../components/SvgIcon.h"

#include <QBrush>
#include <QColor>
#include <QDataStream>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QHeaderView>
#include <QMenu>
#include <QMimeData>
#include <QDropEvent>
#include <QSizePolicy>
#include <QTreeWidget>
#include <QTreeWidgetItem>

#include <functional>

namespace ifcviewerfull::modules::models {

namespace {

constexpr auto kDragMimeType = "application/x-ifcviewerfull-model-items";

class ModelsTreeWidget : public QTreeWidget {
public:
    explicit ModelsTreeWidget(QWidget* parent = nullptr) : QTreeWidget(parent) {}

    std::function<void(const QStringList&, const QString&)> on_model_drop;
    std::function<void(const QString&, const QString&)> on_group_drop;

protected:
    QStringList mimeTypes() const override {
        return {QString::fromUtf8(kDragMimeType)};
    }

    QMimeData* mimeData(const QList<QTreeWidgetItem*>& items) const override {
        Q_UNUSED(items);
        const QList<QTreeWidgetItem*> selected = selectedItems();
        if (selected.isEmpty()) return nullptr;

        const int first_kind = selected.first()->data(0, Qt::UserRole).toInt();
        if (first_kind == static_cast<int>(ItemKind::Group) && selected.size() != 1) {
            return nullptr;
        }

        QByteArray payload;
        QDataStream stream(&payload, QIODevice::WriteOnly);
        stream << first_kind;
        if (first_kind == static_cast<int>(ItemKind::Group)) {
            stream << selected.first()->data(0, Qt::UserRole + 1).toString();
        } else {
            QStringList ids;
            for (QTreeWidgetItem* item : selected) {
                if (item->data(0, Qt::UserRole).toInt() != first_kind) return nullptr;
                ids.push_back(item->data(0, Qt::UserRole + 1).toString());
            }
            ids.removeDuplicates();
            stream << ids;
        }

        auto* mime = new QMimeData();
        mime->setData(QString::fromUtf8(kDragMimeType), payload);
        return mime;
    }

    Qt::DropActions supportedDropActions() const override {
        return Qt::MoveAction;
    }

    void dragEnterEvent(QDragEnterEvent* event) override {
        if (event->mimeData()->hasFormat(QString::fromUtf8(kDragMimeType))) {
            event->acceptProposedAction();
            return;
        }
        QTreeWidget::dragEnterEvent(event);
    }

    void dragMoveEvent(QDragMoveEvent* event) override {
        if (!event->mimeData()->hasFormat(QString::fromUtf8(kDragMimeType))) {
            QTreeWidget::dragMoveEvent(event);
            return;
        }

        QString group_id;
        if (!decodeDropTarget(event->position().toPoint(), group_id)) {
            event->ignore();
            return;
        }

        if (canAcceptDrop(event->mimeData(), itemAt(event->position().toPoint()), group_id)) {
            event->acceptProposedAction();
        } else {
            event->ignore();
        }
    }

    void dropEvent(QDropEvent* event) override {
        if (!event->mimeData()->hasFormat(QString::fromUtf8(kDragMimeType))) {
            QTreeWidget::dropEvent(event);
            return;
        }

        QString target_group_id;
        if (!decodeDropTarget(event->position().toPoint(), target_group_id)) {
            event->ignore();
            return;
        }

        QTreeWidgetItem* target_item = itemAt(event->position().toPoint());
        if (!canAcceptDrop(event->mimeData(), target_item, target_group_id)) {
            event->ignore();
            return;
        }

        QByteArray payload = event->mimeData()->data(QString::fromUtf8(kDragMimeType));
        QDataStream stream(&payload, QIODevice::ReadOnly);
        int kind = 0;
        stream >> kind;
        if (kind == static_cast<int>(ItemKind::Group)) {
            QString group_id;
            stream >> group_id;
            if (on_group_drop) on_group_drop(group_id, target_group_id);
        } else if (kind == static_cast<int>(ItemKind::Model)) {
            QStringList ids;
            stream >> ids;
            ids.removeDuplicates();
            if (!ids.isEmpty() && on_model_drop) on_model_drop(ids, target_group_id);
        } else {
            event->ignore();
            return;
        }

        event->acceptProposedAction();
    }

private:
    bool decodeDropTarget(const QPoint& pos, QString& target_group_id) const {
        target_group_id.clear();
        QTreeWidgetItem* target_item = itemAt(pos);
        if (!target_item) return true;

        const int kind = target_item->data(0, Qt::UserRole).toInt();
        if (kind != static_cast<int>(ItemKind::Group)) return false;

        target_group_id = target_item->data(0, Qt::UserRole + 1).toString();
        return true;
    }

    bool canAcceptDrop(const QMimeData* mime,
                       QTreeWidgetItem* target_item,
                       const QString& target_group_id) const {
        QByteArray payload = mime->data(QString::fromUtf8(kDragMimeType));
        QDataStream stream(&payload, QIODevice::ReadOnly);
        int kind = 0;
        stream >> kind;

        if (kind == static_cast<int>(ItemKind::Group)) {
            QString group_id;
            stream >> group_id;
            if (group_id.isEmpty()) return false;
            if (!target_item) return true;
            if (target_item->data(0, Qt::UserRole).toInt() != static_cast<int>(ItemKind::Group)) return false;
            if (group_id == target_group_id) return false;
            for (QTreeWidgetItem* cur = target_item; cur != nullptr; cur = cur->parent()) {
                if (cur->data(0, Qt::UserRole + 1).toString() == group_id) return false;
            }
            return true;
        }

        if (kind == static_cast<int>(ItemKind::Model)) {
            QStringList ids;
            stream >> ids;
            ids.removeDuplicates();
            if (ids.isEmpty()) return false;
            return target_item == nullptr || !target_group_id.isNull();
        }

        return false;
    }
};

QString itemId(QTreeWidgetItem* item) {
    return item ? item->data(0, Qt::UserRole + 1).toString() : QString();
}

ItemKind itemKind(QTreeWidgetItem* item) {
    return static_cast<ItemKind>(item->data(0, Qt::UserRole).toInt());
}

QList<QTreeWidgetItem*> selectedItemsOfKind(QTreeWidget* tree, ItemKind kind) {
    QList<QTreeWidgetItem*> matches;
    for (QTreeWidgetItem* item : tree->selectedItems()) {
        if (itemKind(item) == kind) matches.push_back(item);
    }
    return matches;
}

} // namespace

ModelsPanel::ModelsPanel(ifcviewerfull::SessionState* session_state,
                         ViewportWindow* viewport,
                         QWidget* parent)
    : components::Panel("Models", nullptr, parent, true)
    , session_state_(session_state)
    , viewport_(viewport)
{
    auto* section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    section->setBodyExpanding(true);
    auto* tree = new ModelsTreeWidget(section);
    tree_ = tree;
    tree_->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    tree_->setColumnCount(2);
    tree_->setHeaderLabels({"Model", ""});
    tree_->setIconSize(QSize(16, 16));
    tree_->setSelectionMode(QAbstractItemView::ExtendedSelection);
    tree_->setContextMenuPolicy(Qt::CustomContextMenu);
    tree_->setDragEnabled(true);
    tree_->viewport()->setAcceptDrops(true);
    tree_->setDropIndicatorShown(true);
    tree_->setDragDropMode(QAbstractItemView::DragDrop);
    tree_->setDefaultDropAction(Qt::MoveAction);
    tree_->setUniformRowHeights(true);
    tree_->header()->setStretchLastSection(false);
    tree_->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    tree_->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    tree_->header()->resizeSection(1, 28);
    tree_->header()->hide();
    tree->on_model_drop = [this](const QStringList& ids, const QString& target_group_id) {
        commands::moveModels(*session_state_, ids, target_group_id);
    };
    tree->on_group_drop = [this](const QString& id, const QString& target_group_id) {
        commands::moveGroup(*session_state_, id, target_group_id);
    };
    section->addBodyWidget(tree_);
    addBodyWidget(section);

    connect(tree_, &QTreeWidget::itemClicked, this, [this](QTreeWidgetItem* item, int column) {
        if (!item || column != 1) return;
        commands::toggleVisibility(*session_state_, itemKind(item), itemId(item));
    });

    connect(tree_, &QTreeWidget::customContextMenuRequested, this, [this](const QPoint& pos) {
        auto* item = tree_->itemAt(pos);
        QMenu menu(tree_);
        if (!item) {
            QAction* add_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "Add Group");
            connect(add_group_action, &QAction::triggered, this, [this]() {
                commands::addGroup(*session_state_, *this, QString());
            });
            menu.exec(tree_->viewport()->mapToGlobal(pos));
            return;
        }

        const auto kind = itemKind(item);
        const QString id = itemId(item);

        QAction* toggle_visibility_action = menu.addAction(
            components::icons::makeSvgIcon(":/icons/eye.svg"), "Toggle Visibility");
        connect(toggle_visibility_action, &QAction::triggered, this, [this, kind, id]() {
            commands::toggleVisibility(*session_state_, kind, id);
        });

        if (kind == ItemKind::Group) {
            QAction* add_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "New Subgroup");
            connect(add_group_action, &QAction::triggered, this, [this, id]() {
                commands::addGroup(*session_state_, *this, id);
            });
            QAction* rename_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder.svg"), "Rename Group");
            connect(rename_group_action, &QAction::triggered, this, [this, id]() {
                commands::renameGroup(*session_state_, *this, id);
            });

            QMenu* move_menu = menu.addMenu("Move to Parent");
            QAction* move_root_action = move_menu->addAction("(Root)");
            connect(move_root_action, &QAction::triggered, this, [this, id]() {
                commands::moveGroup(*session_state_, id, QString());
            });
            move_menu->addSeparator();
            const QList<GroupOption> targets =
                group_list_provider_ ? group_list_provider_(id) : QList<GroupOption>{};
            for (const auto& target : targets) {
                QAction* action = move_menu->addAction(target.display_name);
                const QString target_id = target.id;
                connect(action, &QAction::triggered, this, [this, id, target_id]() {
                    commands::moveGroup(*session_state_, id, target_id);
                });
            }

            QAction* remove_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-minus.svg"), "Remove Group");
            connect(remove_group_action, &QAction::triggered, this, [this, id]() {
                commands::removeGroup(*session_state_, *this, id);
            });
        } else {
            QString parent_group_id;
            if (auto* parent_item = item->parent()) {
                if (itemKind(parent_item) == ItemKind::Group) {
                    parent_group_id = itemId(parent_item);
                }
            }

            QAction* add_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "New Group");
            connect(add_group_action, &QAction::triggered, this, [this, parent_group_id]() {
                commands::addGroup(*session_state_, *this, parent_group_id);
            });

            QStringList selected_model_ids;
            const QList<QTreeWidgetItem*> selected_models = selectedItemsOfKind(tree_, ItemKind::Model);
            if (selected_models.contains(item)) {
                for (QTreeWidgetItem* selected : selected_models) {
                    selected_model_ids.push_back(itemId(selected));
                }
                selected_model_ids.removeDuplicates();
            } else {
                selected_model_ids = {id};
            }

            QMenu* move_menu = menu.addMenu("Move to Group");
            QAction* move_root_action = move_menu->addAction("(Root)");
            connect(move_root_action, &QAction::triggered, this, [this, selected_model_ids]() {
                commands::moveModels(*session_state_, selected_model_ids, QString());
            });
            move_menu->addSeparator();
            const QList<GroupOption> targets =
                group_list_provider_ ? group_list_provider_(QString()) : QList<GroupOption>{};
            for (const auto& target : targets) {
                QAction* action = move_menu->addAction(target.display_name);
                const QString target_id = target.id;
                connect(action, &QAction::triggered, this, [this, selected_model_ids, target_id]() {
                    commands::moveModels(*session_state_, selected_model_ids, target_id);
                });
            }

            QAction* remove_model_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/minus-square.svg"), "Remove Model");
            connect(remove_model_action, &QAction::triggered, this, [this, id]() {
                commands::removeModel(*session_state_, *viewport_, *this, id);
            });
        }
        menu.exec(tree_->viewport()->mapToGlobal(pos));
    });

    connect(this, &components::Panel::settingsRequested, this, [this]() {
        commands::openSettings(*session_state_, *this);
    });
}

void ModelsPanel::setNodes(const QList<TreeNode>& nodes) {
    tree_->clear();
    const bool has_hierarchy = std::any_of(nodes.begin(), nodes.end(), [](const TreeNode& node) {
        return !node.children.isEmpty() || node.kind == ItemKind::Group;
    });
    tree_->setRootIsDecorated(has_hierarchy);
    for (const auto& node : nodes) {
        addNode(tree_->invisibleRootItem(), node);
    }
    tree_->expandAll();
}

void ModelsPanel::setGroupListProvider(GroupListProvider provider) {
    group_list_provider_ = std::move(provider);
}

void ModelsPanel::addNode(QTreeWidgetItem* parent, const TreeNode& node) {
    auto* item = new QTreeWidgetItem(parent, {node.name, ""});
    item->setData(0, Qt::UserRole, static_cast<int>(node.kind));
    item->setData(0, Qt::UserRole + 1, node.id);
    item->setSizeHint(0, QSize(0, 24));

    if (node.kind == ItemKind::Group) {
        item->setIcon(0, components::icons::makeSvgIcon(":/icons/folder.svg"));
        item->setIcon(1, components::icons::makeSvgIcon(node.visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg"));
    } else {
        item->setIcon(0, components::icons::makeSvgIcon(":/icons/cube.svg"));
        item->setIcon(1, components::icons::makeSvgIcon(node.visible ? ":/icons/eye-solid.svg" : ":/icons/eye-closed.svg"));
    }

    if (!node.visible) {
        const QBrush disabled_brush(
            QColor(ifcviewerfull::ViewerSettings::instance().color("disabled_text")));
        item->setForeground(0, disabled_brush);
        item->setForeground(1, disabled_brush);
    }

    for (const auto& child : node.children) {
        addNode(item, child);
    }
}

} // namespace ifcviewerfull::modules::models
