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

#include "../../components/Section.h"
#include "../../components/SvgIcon.h"

#include <QHeaderView>
#include <QMenu>
#include <QShowEvent>
#include <QSizePolicy>
#include <QTreeWidget>
#include <QTreeWidgetItem>

namespace bonsaiviewer::modules::spatial_hierarchy {

namespace {

void setSubtreeExpanded(QTreeWidgetItem* item, bool expanded) {
    item->setExpanded(expanded);
    for (int i = 0; i < item->childCount(); ++i) {
        setSubtreeExpanded(item->child(i), expanded);
    }
}

} // namespace

SpatialHierarchyPanel::SpatialHierarchyPanel(QWidget* parent)
    : components::Panel("Spatial Hierarchy", nullptr, parent)
{
    auto* section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    section->setBodyExpanding(true);  // let the tree fill the panel's height

    tree_ = new QTreeWidget(section);
    tree_->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    tree_->setColumnCount(3);
    tree_->setHeaderLabels({"Name", "Long Name", ""});
    tree_->setIconSize(QSize(16, 16));
    tree_->setSelectionMode(QAbstractItemView::ExtendedSelection);
    tree_->setUniformRowHeights(true);
    // Name is drag-resizable, Long Name fills the rest, the eye is pinned to
    // the right at a fixed width. Header stays visible so the Name/Long-Name
    // divider can be dragged. Initial 20/80 split applied in showEvent once the
    // real width is known.
    tree_->header()->setStretchLastSection(false);
    tree_->header()->setSectionsMovable(false);
    tree_->header()->setSectionResizeMode(0, QHeaderView::Interactive);  // name
    tree_->header()->setSectionResizeMode(1, QHeaderView::Stretch);      // LongName / elevation
    tree_->header()->setSectionResizeMode(2, QHeaderView::Fixed);        // visibility
    tree_->header()->resizeSection(2, 28);
    section->addBodyWidget(tree_);
    addBodyWidget(section);

    connect(tree_, &QTreeWidget::itemClicked, this, [this](QTreeWidgetItem* item, int column) {
        if (!item || column != 2) return;
        emit visibilityToggleRequested(itemPath(item));
    });

    // Right-click: recursive expand/collapse of a subtree or the whole tree.
    tree_->setContextMenuPolicy(Qt::CustomContextMenu);
    connect(tree_, &QTreeWidget::customContextMenuRequested, this, [this](const QPoint& pos) {
        QMenu menu(tree_);
        if (QTreeWidgetItem* item = tree_->itemAt(pos); item && item->childCount() > 0) {
            menu.addAction("Expand Subtree", tree_, [item]() { setSubtreeExpanded(item, true); });
            menu.addAction("Collapse Subtree", tree_, [item]() { setSubtreeExpanded(item, false); });
            menu.addSeparator();
        }
        menu.addAction("Expand All", tree_, [this]() { tree_->expandAll(); });
        menu.addAction("Collapse All", tree_, [this]() { tree_->collapseAll(); });
        menu.exec(tree_->viewport()->mapToGlobal(pos));
    });
}

void SpatialHierarchyPanel::showEvent(QShowEvent* event) {
    components::Panel::showEvent(event);
    // Default the Name column to 20% of the width once the panel has a real
    // layout size; Long Name (stretch) takes the rest. Left interactive after,
    // so the user's own drag persists.
    if (!column_widths_initialized_) {
        const int available = tree_->viewport()->width();
        if (available > 100) {
            tree_->header()->resizeSection(0, available / 5);
            column_widths_initialized_ = true;
        }
    }
}

void SpatialHierarchyPanel::setNodes(const QList<TreeNode>& nodes) {
    tree_->clear();
    for (const auto& node : nodes) {
        addNode(tree_->invisibleRootItem(), node);
    }
    tree_->expandAll();
}

void SpatialHierarchyPanel::addNode(QTreeWidgetItem* parent, const TreeNode& node) {
    auto* item = new QTreeWidgetItem(parent, {node.name, node.detail, ""});
    item->setData(2, Qt::UserRole, node.visible);
    item->setSizeHint(0, QSize(0, 24));
    item->setIcon(0, components::icons::makeSvgIcon(iconPath(node.kind)));
    // Storey elevations read as right-aligned numbers; LongNames stay left.
    if (node.kind == ItemKind::Storey) {
        item->setTextAlignment(1, Qt::AlignRight | Qt::AlignVCenter);
    }
    item->setIcon(2, components::icons::makeSvgIcon(node.visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg"));
    for (const auto& child : node.children) {
        addNode(item, child);
    }
}

NodePath SpatialHierarchyPanel::itemPath(QTreeWidgetItem* item) const {
    NodePath path;
    while (item) {
        path.prepend(item->text(0));
        item = item->parent();
    }
    return path;
}

QString SpatialHierarchyPanel::iconPath(ItemKind kind) const {
    switch (kind) {
    case ItemKind::Site: return ":/icons/frame-alt.svg";
    case ItemKind::Building: return ":/icons/city.svg";
    case ItemKind::Storey: return ":/icons/planimetry.svg";
    case ItemKind::Space: return ":/icons/square3d-from-center.svg";
    }
    return ":/icons/frame-alt.svg";
}

} // namespace bonsaiviewer::modules::spatial_hierarchy
