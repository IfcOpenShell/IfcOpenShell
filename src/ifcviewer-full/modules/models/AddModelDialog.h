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

#ifndef IFCINTERFACE_PANELS_ADDMODELDIALOG_H
#define IFCINTERFACE_PANELS_ADDMODELDIALOG_H

#include "../../components/Dialog.h"

namespace ifcviewerfull::modules::models {

enum class SourceMode {
    None,
    IfcFile,
    IfcDatabase,
    GeometryOnly,
};

class AddModelDialog : public components::Dialog {
    Q_OBJECT
public:
    explicit AddModelDialog(QWidget* parent = nullptr);

    SourceMode selectedMode() const { return selected_mode_; }

private:
    void setupUi();

    SourceMode selected_mode_ = SourceMode::None;
};

} // namespace ifcviewerfull::modules::models

#endif
