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

#ifndef IFCINTERFACE_MODULES_MODELS_SETTINGSDIALOG_H
#define IFCINTERFACE_MODULES_MODELS_SETTINGSDIALOG_H

#include "../../components/Dialog.h"
#include "Types.h"

#include <QString>
#include <vector>

class Federation;
class SceneLoader;
class QComboBox;
class QLabel;
class QLineEdit;
class QShowEvent;
class QTableWidget;
class QTableWidgetItem;

namespace ifcviewerfull {
class SessionState;
}

namespace ifcviewerfull::modules::models {

class SettingsView;

class SettingsDialog : public components::TabbedDialog {
    Q_OBJECT
public:
    explicit SettingsDialog(ifcviewerfull::SessionState* session_state, QWidget* parent = nullptr);
    void renderSelectedModelGeoref(const SelectedModelGeorefState& state);

protected:
    void showEvent(QShowEvent* event) override;

private:
    struct ModelRowWidgets {
        QString fed_id;
        QComboBox* frame = nullptr;
        QTableWidgetItem* from_point = nullptr;
        QTableWidgetItem* to_point = nullptr;
        QTableWidgetItem* rotate = nullptr;
        QTableWidgetItem* pivot = nullptr;
    };

    void setupUi();
    void syncFromFederation();
    void populateModelTable();
    void updateSelectedModelGeoref();
    void onAccepted();

    ifcviewerfull::SessionState* session_state_ = nullptr;
    Federation* federation_ = nullptr;
    SceneLoader* loader_ = nullptr;

    QComboBox* unit_combo_ = nullptr;
    QLineEdit* xyz_x_ = nullptr;
    QLineEdit* xyz_y_ = nullptr;
    QLineEdit* xyz_z_ = nullptr;
    QLineEdit* rz_deg_ = nullptr;

    QLabel* georef_present_value_ = nullptr;
    QLabel* georef_type_value_ = nullptr;
    QLabel* georef_project_unit_value_ = nullptr;
    QLabel* georef_map_unit_value_ = nullptr;
    QLabel* georef_easting_value_ = nullptr;
    QLabel* georef_northing_value_ = nullptr;
    QLabel* georef_height_value_ = nullptr;
    QLabel* georef_x_axis_abscissa_value_ = nullptr;
    QLabel* georef_x_axis_ordinate_value_ = nullptr;
    QLabel* georef_rotation_dd_value_ = nullptr;
    QLabel* georef_rotation_dms_value_ = nullptr;
    QLabel* georef_scale_value_ = nullptr;
    QLabel* georef_factor_x_value_ = nullptr;
    QLabel* georef_factor_y_value_ = nullptr;
    QLabel* georef_factor_z_value_ = nullptr;

    QTableWidget* model_table_ = nullptr;
    std::vector<ModelRowWidgets> model_rows_;
    SettingsView* settings_view_ = nullptr;
};

} // namespace ifcviewerfull::modules::models

#endif
