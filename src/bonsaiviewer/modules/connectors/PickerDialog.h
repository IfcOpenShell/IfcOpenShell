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

#ifndef IFCINTERFACE_MODULES_CONNECTORS_PICKERDIALOG_H
#define IFCINTERFACE_MODULES_CONNECTORS_PICKERDIALOG_H

#include "Discovery.h"

#include "../../components/Dialog.h"

#include <QString>
#include <vector>

namespace bonsaiviewer::modules::connectors {

// Connector chooser, modelled on AddModelDialog: one button per available
// connector. Always shown (even when only one connector is installed), per
// project UX direction.
class ConnectorPickerDialog : public components::Dialog {
    Q_OBJECT
public:
    // `title` and `description` adapt the dialog to the calling workflow
    // (e.g. "Open from Cloud", "Save Model to Cloud").
    ConnectorPickerDialog(const std::vector<ConnectorManifest>& manifests,
                          const QString& title,
                          const QString& description,
                          QWidget* parent = nullptr);

    QString selectedId() const { return selected_id_; }

private:
    QString selected_id_;
};

} // namespace bonsaiviewer::modules::connectors

#endif
