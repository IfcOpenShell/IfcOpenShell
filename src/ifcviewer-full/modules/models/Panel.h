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

#ifndef IFCINTERFACE_MODULES_MODELS_PANEL_H
#define IFCINTERFACE_MODULES_MODELS_PANEL_H

#include "Types.h"

#include "../../components/Panel.h"

class QTreeWidget;
class QTreeWidgetItem;

namespace ifcviewerfull::modules::models {

class ModelsPanel : public components::Panel {
    Q_OBJECT
public:
    explicit ModelsPanel(QWidget* parent = nullptr);

    void setNodes(const QList<TreeNode>& nodes);

signals:
    void visibilityToggleRequested(ItemKind kind, const QString& id);
    void addGroupRequested(const QString& parent_group_id, const QString& name);
    void renameGroupRequested(const QString& id, const QString& name);
    void moveGroupRequested(const QString& id, const QString& parent_group_id);
    void moveModelsRequested(const QStringList& ids, const QString& parent_group_id);
    void removeGroupRequested(const QString& id);
    void removeModelRequested(const QString& id);

private:
    void addNode(QTreeWidgetItem* parent, const TreeNode& node);

    QTreeWidget* tree_ = nullptr;
};

} // namespace ifcviewerfull::modules::models

#endif
