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

#ifndef IFCINTERFACE_MODULES_MODELS_FEDERATIONITEMMODEL_H
#define IFCINTERFACE_MODULES_MODELS_FEDERATIONITEMMODEL_H

#include "Types.h"

#include <QHash>
#include <QStandardItemModel>

class Federation;

namespace bonsaiviewer::modules::models {

// QStandardItemModel that mirrors the Federation tree (groups + models in
// two columns: name + visibility icon). Subscribes directly to Federation's
// granular signals so each mutation only touches the affected rows — view
// state (expansion, selection, scroll) is preserved automatically.
//
// Coarse session events (project open/reset, theme change) are not the
// model's concern: the owning View calls rebuildAll() in those cases.
class FederationItemModel : public QStandardItemModel {
    Q_OBJECT
public:
    enum Role {
        IdRole   = Qt::UserRole + 1,
        KindRole = Qt::UserRole + 2,
    };

    explicit FederationItemModel(Federation* federation, QObject* parent = nullptr);

    // Discard everything and rebuild from current Federation state. Loses
    // expansion/selection — caller is the only one that knows whether that's
    // acceptable (e.g. project reset, where there's no prior state worth
    // preserving anyway).
    void rebuildAll();

private slots:
    void onGroupAdded(const QString& group_id);
    void onGroupRemoved(const QString& group_id);
    void onGroupChanged(const QString& group_id);
    void onGroupVisibilityChanged(const QString& group_id, bool visible);
    void onModelAdded(const QString& model_id);
    void onModelRemoved(const QString& model_id);
    void onModelVisibilityChanged(const QString& model_id, bool visible);
    void onModelGroupChanged(const QString& model_id, const QString& new_group_id);
    void onModelChanged(const QString& model_id);

private:
    QStandardItem* makeGroupNameItem(const QString& group_id, const QString& display_name) const;
    QStandardItem* makeModelNameItem(const QString& model_id, const QString& display_name) const;
    QStandardItem* makeVisibilityItem(ItemKind kind, bool visible) const;
    void styleRowVisibility(QStandardItem* name_item, bool visible) const;

    QStandardItem* findItem(const QString& id) const;
    QStandardItem* parentItemForGroup(const QString& parent_group_id) const;

    void appendModelTo(QStandardItem* parent_item, const QString& model_id);
    void appendGroupSubtreeTo(QStandardItem* parent_item, const QString& group_id);
    void refreshSubtreeVisibility(QStandardItem* root);

    Federation* federation_ = nullptr;
    QHash<QString, QStandardItem*> id_to_name_item_;  // both group_ids and model_ids
};

} // namespace bonsaiviewer::modules::models

#endif
