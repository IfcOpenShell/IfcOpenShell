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

#include "../../components/Section.h"
#include "../../components/SvgIcon.h"

#include <QHeaderView>
#include <QInputDialog>
#include <QLineEdit>
#include <QMenu>
#include <QTreeWidget>
#include <QTreeWidgetItem>

namespace ifcinterface::modules::models {

ModelsPanel::ModelsPanel(QWidget* parent)
    : components::Panel("Models", nullptr, parent, true)
{
    auto* section = new components::Section("", components::SectionHeaderMode::Hidden, this);

    tree_ = new QTreeWidget(section);
    tree_->setColumnCount(2);
    tree_->setHeaderLabels({"Model", ""});
    tree_->setIconSize(QSize(16, 16));
    tree_->setSelectionMode(QAbstractItemView::ExtendedSelection);
    tree_->setContextMenuPolicy(Qt::CustomContextMenu);
    tree_->setUniformRowHeights(true);
    tree_->header()->setStretchLastSection(false);
    tree_->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    tree_->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    tree_->header()->resizeSection(1, 28);
    tree_->header()->hide();
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
            menu.addAction(components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "Add Group", [this]() {
                bool ok = false;
                const QString name = QInputDialog::getText(
                    this, "New Group", "Group name:", QLineEdit::Normal, "Group", &ok);
                if (ok && !name.isEmpty()) {
                    emit addGroupRequested(QString(), name);
                }
            });
            menu.exec(tree_->viewport()->mapToGlobal(pos));
            return;
        }

        const auto kind = static_cast<ItemKind>(item->data(0, Qt::UserRole).toInt());
        const QString id = item->data(0, Qt::UserRole + 1).toString();

        menu.addAction(components::icons::makeSvgIcon(":/icons/eye.svg"), "Toggle Visibility", [this, kind, id]() {
            emit visibilityToggleRequested(kind, id);
        });

        if (kind == ItemKind::Group) {
            menu.addAction(components::icons::makeSvgIcon(":/icons/folder-plus.svg"), "Add Group", [this, id]() {
                bool ok = false;
                const QString name = QInputDialog::getText(
                    this, "New Group", "Group name:", QLineEdit::Normal, "Group", &ok);
                if (ok && !name.isEmpty()) {
                    emit addGroupRequested(id, name);
                }
            });
            menu.addAction(components::icons::makeSvgIcon(":/icons/folder-minus.svg"), "Remove Group", [this, id]() {
                emit removeGroupRequested(id);
            });
        } else {
            menu.addAction(components::icons::makeSvgIcon(":/icons/minus-square.svg"), "Remove Model", [this, id]() {
                emit removeModelRequested(id);
            });
        }
        menu.exec(tree_->viewport()->mapToGlobal(pos));
    });
}

void ModelsPanel::setNodes(const QList<TreeNode>& nodes) {
    tree_->clear();
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

    for (const auto& child : node.children) {
        addNode(item, child);
    }
}

} // namespace ifcinterface::modules::models
