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

#include "SpatialHierarchyPanelWidget.h"

#include <QFile>
#include <QHeaderView>
#include <QPainter>
#include <QPixmap>
#include <QRegularExpression>
#include <QSvgRenderer>
#include <QTreeWidget>
#include <QTreeWidgetItem>
#include <QVBoxLayout>

namespace {

QPixmap renderPanelSvgPixmap(const QString& icon_path, const QString& color, const QSize& size) {
    QFile file(icon_path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return QIcon(icon_path).pixmap(size);
    }

    QString svg = QString::fromUtf8(file.readAll());
    svg.replace("currentColor", color, Qt::CaseSensitive);
    svg.replace(QRegularExpression(R"(stroke="[^"]*")"), QString("stroke=\"%1\"").arg(color));
    svg.replace(QRegularExpression(R"(fill="none")"), "fill=\"none\"");

    QSvgRenderer renderer(svg.toUtf8());
    QPixmap pixmap(size);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    renderer.render(&painter);
    return pixmap;
}

QIcon makePanelSvgIcon(const QString& icon_path) {
    QIcon icon;
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#e7ebf2", QSize(20, 20)), QIcon::Normal, QIcon::Off);
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#ffffff", QSize(20, 20)), QIcon::Active, QIcon::Off);
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#ffffff", QSize(20, 20)), QIcon::Selected, QIcon::Off);
    icon.addPixmap(renderPanelSvgPixmap(icon_path, "#6f7988", QSize(20, 20)), QIcon::Disabled, QIcon::Off);
    return icon;
}

} // namespace

namespace ifcinterface::panels::spatial_hierarchy {

SpatialHierarchyPanelWidget::SpatialHierarchyPanelWidget(QWidget* parent)
    : QWidget(parent)
{
    auto* layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);

    tree_ = new QTreeWidget(this);
    tree_->setColumnCount(2);
    tree_->setHeaderLabels({"Spatial Item", ""});
    tree_->setIconSize(QSize(16, 16));
    tree_->setSelectionMode(QAbstractItemView::ExtendedSelection);
    tree_->setUniformRowHeights(true);
    tree_->header()->setStretchLastSection(false);
    tree_->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    tree_->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    tree_->header()->resizeSection(1, 28);
    tree_->header()->hide();
    layout->addWidget(tree_);

    connect(tree_, &QTreeWidget::itemClicked, this, [this](QTreeWidgetItem* item, int column) {
        if (!item || column != 1) return;
        emit visibilityToggleRequested(itemPath(item));
    });
}

void SpatialHierarchyPanelWidget::setNodes(const QList<TreeNode>& nodes) {
    tree_->clear();
    for (const auto& node : nodes) {
        addNode(tree_->invisibleRootItem(), node);
    }
    tree_->expandAll();
}

void SpatialHierarchyPanelWidget::addNode(QTreeWidgetItem* parent, const TreeNode& node) {
    auto* item = new QTreeWidgetItem(parent, {node.name, ""});
    item->setData(1, Qt::UserRole, node.visible);
    item->setSizeHint(0, QSize(0, 24));
    item->setIcon(0, makePanelSvgIcon(iconPath(node.kind)));
    item->setIcon(1, makePanelSvgIcon(node.visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg"));
    for (const auto& child : node.children) {
        addNode(item, child);
    }
}

NodePath SpatialHierarchyPanelWidget::itemPath(QTreeWidgetItem* item) const {
    NodePath path;
    while (item) {
        path.prepend(item->text(0));
        item = item->parent();
    }
    return path;
}

QString SpatialHierarchyPanelWidget::iconPath(ItemKind kind) const {
    switch (kind) {
    case ItemKind::Site: return ":/icons/frame-alt.svg";
    case ItemKind::Building: return ":/icons/city.svg";
    case ItemKind::Storey: return ":/icons/planimetry.svg";
    case ItemKind::Space: return ":/icons/square3d-from-center.svg";
    }
    return ":/icons/frame-alt.svg";
}

} // namespace ifcinterface::panels::spatial_hierarchy
