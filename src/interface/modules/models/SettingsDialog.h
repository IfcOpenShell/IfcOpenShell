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

#include <QString>

class Federation;
class QComboBox;
class QLabel;
class QLineEdit;
class QRadioButton;
class QShowEvent;

namespace ifcinterface::modules::models {

class SettingsDialog : public components::Dialog {
    Q_OBJECT
public:
    explicit SettingsDialog(Federation* federation, QWidget* parent = nullptr);

protected:
    void showEvent(QShowEvent* event) override;

private:
    void setupUi();
    void syncFromFederation();
    void populateModelCombo();
    void syncFromModel(const QString& fed_id);
    void refreshUnitLabels();
    void onAFrameToggled();
    void onAccepted();

    Federation* federation_ = nullptr;

    QComboBox* unit_combo_ = nullptr;
    QLineEdit* xyz_x_ = nullptr;
    QLineEdit* xyz_y_ = nullptr;
    QLineEdit* xyz_z_ = nullptr;
    QLineEdit* rz_deg_ = nullptr;

    QComboBox* model_combo_ = nullptr;
    QRadioButton* radio_local_ = nullptr;
    QRadioButton* radio_global_ = nullptr;
    QLineEdit* a_x_ = nullptr;
    QLineEdit* a_y_ = nullptr;
    QLineEdit* a_z_ = nullptr;
    QLabel* a_unit_label_ = nullptr;
    QLineEdit* b_x_ = nullptr;
    QLineEdit* b_y_ = nullptr;
    QLineEdit* b_z_ = nullptr;
    QLabel* b_unit_label_ = nullptr;
    QLineEdit* rx_ = nullptr;
    QLineEdit* ry_ = nullptr;
    QLineEdit* rz_ = nullptr;
    QLineEdit* pivot_x_ = nullptr;
    QLineEdit* pivot_y_ = nullptr;
    QLineEdit* pivot_z_ = nullptr;
    QLabel* pivot_unit_label_ = nullptr;
};

} // namespace ifcinterface::modules::models

#endif
