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

#include "../../ViewerSettings.h"
#include "../../components/Section.h"
#include "../../components/SvgIcon.h"

#include <QBrush>
#include <QColor>
#include <QDataStream>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QHeaderView>
#include <QInputDialog>
#include <QLineEdit>
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

QString promptGroupName(QWidget* parent, const QString& title, const QString& label, const QString& value) {
    bool ok = false;
    const QString name = QInputDialog::getText(parent, title, label, QLineEdit::Normal, value, &ok);
    return ok ? name.trimmed() : QString();
}

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

ModelsPanel::ModelsPanel(QWidget* parent)
    : components::Panel("Models", nullptr, parent, true)
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
        emit moveModelsRequested(ids, target_group_id);
    };
    tree->on_group_drop = [this](const QString& id, const QString& target_group_id) {
        emit moveGroupRequested(id, target_group_id);
    };
    section->addBodyWidget(tree_);
    addBodyWidget(section);

    connect(tree_, &QTreeWidget::itemClicked, this, [this](QTreeWidgetItem* item, int column) {
        if (!item || column != 1) return;
        emit visibilityToggleRequested(
            static_cast<ItemKind>(item->data(0, Qt::UserRole).toInt()),
            item->data(0, Qt::UserRole + 1).toString());
    });

    connect(tree_, &QTreeWidget::customContextMenuRequested, this, [this](const QPoint& pos) {
        auto* item = tree_->itemAt(pos);
        QMenu menu(tree_);
        if (!item) {
            QAction* add_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "Add Group");
            connect(add_group_action, &QAction::triggered, this, [this]() {
                const QString name = promptGroupName(this, "New Group", "Group name:", "Group");
                if (!name.isEmpty()) {
                    emit addGroupRequested(QString(), name);
                }
            });
            menu.exec(tree_->viewport()->mapToGlobal(pos));
            return;
        }

        const auto kind = itemKind(item);
        const QString id = itemId(item);

        QAction* toggle_visibility_action = menu.addAction(
            components::icons::makeSvgIcon(":/icons/eye.svg"), "Toggle Visibility");
        connect(toggle_visibility_action, &QAction::triggered, this, [this, kind, id]() {
            emit visibilityToggleRequested(kind, id);
        });

        if (kind == ItemKind::Group) {
            QAction* add_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "New Subgroup");
            connect(add_group_action, &QAction::triggered, this, [this, id]() {
                const QString name = promptGroupName(this, "New Group", "Group name:", "Group");
                if (!name.isEmpty()) {
                    emit addGroupRequested(id, name);
                }
            });
            QAction* rename_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder.svg"), "Rename Group");
            connect(rename_group_action, &QAction::triggered, this, [this, item, id]() {
                const QString name = promptGroupName(
                    this, "Rename Group", "Group name:", item->text(0));
                if (!name.isEmpty()) emit renameGroupRequested(id, name);
            });
            QMenu* move_menu = menu.addMenu("Move to Parent");
            QAction* move_root_action = move_menu->addAction("(Root)");
            connect(move_root_action, &QAction::triggered, this, [this, id]() {
                emit moveGroupRequested(id, QString());
            });
            move_menu->addSeparator();
            QList<QTreeWidgetItem*> stack;
            for (int i = 0; i < tree_->topLevelItemCount(); ++i) {
                stack.push_back(tree_->topLevelItem(i));
            }
            while (!stack.isEmpty()) {
                QTreeWidgetItem* candidate = stack.takeFirst();
                if (candidate != item && itemKind(candidate) == ItemKind::Group) {
                    bool would_cycle = false;
                    for (QTreeWidgetItem* cur = candidate; cur != nullptr; cur = cur->parent()) {
                        if (cur == item) {
                            would_cycle = true;
                            break;
                        }
                    }
                    auto* action = move_menu->addAction(candidate->text(0));
                    action->setEnabled(!would_cycle && candidate != item->parent());
                    connect(action, &QAction::triggered, this, [this, id, candidate]() {
                        emit moveGroupRequested(id, itemId(candidate));
                    });
                }
                for (int i = 0; i < candidate->childCount(); ++i) {
                    stack.push_back(candidate->child(i));
                }
            }
            QAction* remove_group_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/folder-minus.svg"), "Remove Group");
            connect(remove_group_action, &QAction::triggered, this, [this, id]() {
                emit removeGroupRequested(id);
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
                const QString name = promptGroupName(this, "New Group", "Group name:", "Group");
                if (!name.isEmpty()) {
                    emit addGroupRequested(parent_group_id, name);
                }
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
                emit moveModelsRequested(selected_model_ids, QString());
            });
            move_menu->addSeparator();
            QList<QTreeWidgetItem*> stack;
            for (int i = 0; i < tree_->topLevelItemCount(); ++i) {
                stack.push_back(tree_->topLevelItem(i));
            }
            while (!stack.isEmpty()) {
                QTreeWidgetItem* candidate = stack.takeFirst();
                if (itemKind(candidate) == ItemKind::Group) {
                    const QString group_id = itemId(candidate);
                    QAction* action = move_menu->addAction(candidate->text(0));
                    connect(action, &QAction::triggered, this, [this, selected_model_ids, group_id]() {
                        emit moveModelsRequested(selected_model_ids, group_id);
                    });
                }
                for (int i = 0; i < candidate->childCount(); ++i) {
                    stack.push_back(candidate->child(i));
                }
            }
            QAction* remove_model_action = menu.addAction(
                components::icons::makeSvgIcon(":/icons/minus-square.svg"), "Remove Model");
            connect(remove_model_action, &QAction::triggered, this, [this, id]() {
                emit removeModelRequested(id);
            });
        }
        menu.exec(tree_->viewport()->mapToGlobal(pos));
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
