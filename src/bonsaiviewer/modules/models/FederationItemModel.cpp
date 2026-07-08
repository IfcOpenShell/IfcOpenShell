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

#include "FederationItemModel.h"

#include "../../ViewerSettings.h"
#include "../../components/SvgIcon.h"
#include "../../../ifcviewer/Federation.h"

#include <QBrush>
#include <QColor>

namespace bonsaiviewer::modules::models {

namespace {

QStandardItem* siblingVisibilityItem(QStandardItem* name_item) {
    QStandardItem* parent = name_item->parent();
    if (!parent) parent = name_item->model()->invisibleRootItem();
    return parent->child(name_item->row(), 1);
}

template <typename F>
void walkSubtree(QStandardItem* root, F visit) {
    visit(root);
    for (int i = 0; i < root->rowCount(); ++i) {
        walkSubtree(root->child(i, 0), visit);
    }
}

} // namespace

FederationItemModel::FederationItemModel(Federation* federation, QObject* parent)
    : QStandardItemModel(parent)
    , federation_(federation)
{
    setColumnCount(2);
    rebuildAll();

    connect(federation_, &Federation::groupAdded,              this, &FederationItemModel::onGroupAdded);
    connect(federation_, &Federation::groupRemoved,            this, &FederationItemModel::onGroupRemoved);
    connect(federation_, &Federation::groupChanged,            this, &FederationItemModel::onGroupChanged);
    connect(federation_, &Federation::groupVisibilityChanged,  this, &FederationItemModel::onGroupVisibilityChanged);
    connect(federation_, &Federation::modelAdded,              this, &FederationItemModel::onModelAdded);
    connect(federation_, &Federation::modelRemoved,            this, &FederationItemModel::onModelRemoved);
    connect(federation_, &Federation::modelVisibilityChanged,  this, &FederationItemModel::onModelVisibilityChanged);
    connect(federation_, &Federation::modelGroupChanged,       this, &FederationItemModel::onModelGroupChanged);
    connect(federation_, &Federation::modelChanged,            this, &FederationItemModel::onModelChanged);
}

void FederationItemModel::rebuildAll() {
    clear();
    setColumnCount(2);
    id_to_name_item_.clear();

    for (const auto& root_group : federation_->rootGroups()) {
        appendGroupSubtreeTo(invisibleRootItem(), root_group->id);
    }
    for (const auto& model : federation_->models()) {
        if (!model.group_id.isEmpty()) continue;
        appendModelTo(invisibleRootItem(), model.id);
    }
}

QStandardItem* FederationItemModel::makeGroupNameItem(const QString& group_id, const QString& display_name) const {
    auto* item = new QStandardItem(components::icons::makeSvgIcon(":/icons/folder.svg"), display_name);
    item->setData(group_id, IdRole);
    item->setData(int(ItemKind::Group), KindRole);
    item->setEditable(false);
    return item;
}

QStandardItem* FederationItemModel::makeModelNameItem(const QString& model_id, const QString& display_name) const {
    auto* item = new QStandardItem(components::icons::makeSvgIcon(":/icons/cube.svg"), display_name);
    item->setData(model_id, IdRole);
    item->setData(int(ItemKind::Model), KindRole);
    item->setEditable(false);
    return item;
}

QStandardItem* FederationItemModel::makeVisibilityItem(ItemKind kind, bool visible) const {
    QString icon_path;
    if (kind == ItemKind::Group) {
        icon_path = visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg";
    } else {
        icon_path = visible ? ":/icons/eye-solid.svg" : ":/icons/eye-closed.svg";
    }
    auto* item = new QStandardItem(components::icons::makeSvgIcon(icon_path), QString());
    item->setEditable(false);
    return item;
}

void FederationItemModel::styleRowVisibility(QStandardItem* name_item, bool visible) const {
    QStandardItem* vis_item = siblingVisibilityItem(name_item);
    if (visible) {
        name_item->setData(QVariant(), Qt::ForegroundRole);
        if (vis_item) vis_item->setData(QVariant(), Qt::ForegroundRole);
    } else {
        const QBrush disabled(QColor(bonsaiviewer::ViewerSettings::instance().color("disabled_text")));
        name_item->setForeground(disabled);
        if (vis_item) vis_item->setForeground(disabled);
    }
}

QStandardItem* FederationItemModel::findItem(const QString& id) const {
    return id_to_name_item_.value(id, nullptr);
}

QStandardItem* FederationItemModel::parentItemForGroup(const QString& parent_group_id) const {
    if (parent_group_id.isEmpty()) return invisibleRootItem();
    QStandardItem* found = findItem(parent_group_id);
    return found ? found : invisibleRootItem();
}

void FederationItemModel::appendModelTo(QStandardItem* parent_item, const QString& model_id) {
    const Federation::Model* model = federation_->findById(model_id);
    if (!model) return;
    auto* name_item = makeModelNameItem(model_id, model->display_name);
    auto* vis_item = makeVisibilityItem(ItemKind::Model, federation_->isModelEffectivelyVisible(model_id));
    parent_item->appendRow({name_item, vis_item});
    id_to_name_item_.insert(model_id, name_item);
    styleRowVisibility(name_item, federation_->isModelEffectivelyVisible(model_id));
}

void FederationItemModel::appendGroupSubtreeTo(QStandardItem* parent_item, const QString& group_id) {
    const Federation::Group* group = federation_->findGroupById(group_id);
    if (!group) return;
    auto* name_item = makeGroupNameItem(group_id, group->display_name);
    auto* vis_item = makeVisibilityItem(ItemKind::Group, group->visible);
    parent_item->appendRow({name_item, vis_item});
    id_to_name_item_.insert(group_id, name_item);
    styleRowVisibility(name_item, group->visible);

    for (const auto& child : group->children) {
        appendGroupSubtreeTo(name_item, child->id);
    }
    for (const auto& model : federation_->models()) {
        if (model.group_id != group_id) continue;
        appendModelTo(name_item, model.id);
    }
}

void FederationItemModel::refreshSubtreeVisibility(QStandardItem* root) {
    walkSubtree(root, [this](QStandardItem* item) {
        const QString id = item->data(IdRole).toString();
        if (id.isEmpty()) return;
        const auto kind = static_cast<ItemKind>(item->data(KindRole).toInt());
        bool visible = true;
        if (kind == ItemKind::Group) {
            const Federation::Group* group = federation_->findGroupById(id);
            visible = group && group->visible;
        } else {
            visible = federation_->isModelEffectivelyVisible(id);
        }
        QStandardItem* vis_item = siblingVisibilityItem(item);
        if (vis_item) {
            const QString icon_path = (kind == ItemKind::Group)
                ? (visible ? ":/icons/eye.svg" : ":/icons/eye-closed.svg")
                : (visible ? ":/icons/eye-solid.svg" : ":/icons/eye-closed.svg");
            vis_item->setIcon(components::icons::makeSvgIcon(icon_path));
        }
        styleRowVisibility(item, visible);
    });
}

void FederationItemModel::onGroupAdded(const QString& group_id) {
    const Federation::Group* group = federation_->findGroupById(group_id);
    if (!group) return;
    QStandardItem* parent_item = parentItemForGroup(group->parent ? group->parent->id : QString());
    appendGroupSubtreeTo(parent_item, group_id);
}

void FederationItemModel::onGroupRemoved(const QString& group_id) {
    QStandardItem* item = findItem(group_id);
    if (!item) return;
    walkSubtree(item, [this](QStandardItem* descendant) {
        const QString id = descendant->data(IdRole).toString();
        if (!id.isEmpty()) id_to_name_item_.remove(id);
    });
    QStandardItem* parent_item = item->parent();
    if (!parent_item) parent_item = invisibleRootItem();
    parent_item->removeRow(item->row());
}

void FederationItemModel::onGroupChanged(const QString& group_id) {
    QStandardItem* item = findItem(group_id);
    if (!item) return;
    const Federation::Group* group = federation_->findGroupById(group_id);
    if (!group) return;

    QStandardItem* current_parent = item->parent();
    if (!current_parent) current_parent = invisibleRootItem();
    QStandardItem* target_parent = parentItemForGroup(group->parent ? group->parent->id : QString());

    if (current_parent == target_parent) {
        item->setText(group->display_name);
        return;
    }

    // Reparent: take row from current parent, append at target. Pointers
    // survive — id_to_name_item_ entries remain valid.
    QList<QStandardItem*> taken = current_parent->takeRow(item->row());
    taken.first()->setText(group->display_name);
    target_parent->appendRow(taken);
    refreshSubtreeVisibility(taken.first());
}

void FederationItemModel::onGroupVisibilityChanged(const QString& group_id, bool /*visible*/) {
    QStandardItem* item = findItem(group_id);
    if (!item) return;
    refreshSubtreeVisibility(item);
}

void FederationItemModel::onModelAdded(const QString& model_id) {
    const Federation::Model* model = federation_->findById(model_id);
    if (!model) return;
    QStandardItem* parent_item = parentItemForGroup(model->group_id);
    appendModelTo(parent_item, model_id);
}

void FederationItemModel::onModelRemoved(const QString& model_id) {
    QStandardItem* item = findItem(model_id);
    if (!item) return;
    id_to_name_item_.remove(model_id);
    QStandardItem* parent_item = item->parent();
    if (!parent_item) parent_item = invisibleRootItem();
    parent_item->removeRow(item->row());
}

void FederationItemModel::onModelVisibilityChanged(const QString& model_id, bool /*visible*/) {
    QStandardItem* item = findItem(model_id);
    if (!item) return;
    refreshSubtreeVisibility(item);
}

void FederationItemModel::onModelChanged(const QString& model_id) {
    QStandardItem* item = findItem(model_id);
    if (!item) return;
    const Federation::Model* model = federation_->findById(model_id);
    if (!model) return;
    item->setText(model->display_name);
}

void FederationItemModel::onModelGroupChanged(const QString& model_id, const QString& new_group_id) {
    QStandardItem* item = findItem(model_id);
    if (!item) return;
    QStandardItem* current_parent = item->parent();
    if (!current_parent) current_parent = invisibleRootItem();
    QStandardItem* target_parent = parentItemForGroup(new_group_id);
    if (current_parent == target_parent) return;

    QList<QStandardItem*> taken = current_parent->takeRow(item->row());
    target_parent->appendRow(taken);
    refreshSubtreeVisibility(taken.first());
}

} // namespace bonsaiviewer::modules::models
