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

#ifndef IFCINTERFACE_MODULES_PROJECT_SAVEPROJECTDIALOG_H
#define IFCINTERFACE_MODULES_PROJECT_SAVEPROJECTDIALOG_H

#include "../../components/Dialog.h"

namespace bonsaiviewer::modules::project {

enum class SaveTarget {
    None,
    Local,    // saveProject:      write to current file_path_ (or fall through to LocalAs)
    LocalAs,  // saveProjectAs:    pick file with QFileDialog
    Cloud,    // saveCloudProject: push_ifcfed using existing manifest
    CloudAs,  // saveAsCloudProject: connector picker + push_ifcfed_interactive
};

// "Save Project" dispatch dialog, modelled on AddModelDialog. Always shows
// all four buttons; "Save to Cloud" is disabled when the project has no
// .ifcfed.manifest (there is no cloud target to push to).
class SaveProjectDialog : public components::Dialog {
    Q_OBJECT
public:
    explicit SaveProjectDialog(bool has_manifest, QWidget* parent = nullptr);

    SaveTarget selectedTarget() const { return selected_target_; }

private:
    void setupUi(bool has_manifest);

    SaveTarget selected_target_ = SaveTarget::None;
};

} // namespace bonsaiviewer::modules::project

#endif
