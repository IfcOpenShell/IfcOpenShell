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

#ifndef SETTINGSWINDOW_H
#define SETTINGSWINDOW_H

#include <QDialog>

class QCheckBox;
class QDoubleSpinBox;
class QLineEdit;
class QShowEvent;
class QSpinBox;

class SettingsWindow : public QDialog {
    Q_OBJECT
public:
    explicit SettingsWindow(QWidget *parent = nullptr);

protected:
    void showEvent(QShowEvent* event) override;

private slots:
    void onAccepted();

private:
    void setupUi();
    void syncFromSettings();

    QLineEdit* geometry_library_edit_ = nullptr;
    QCheckBox* show_stats_check_ = nullptr;
    QCheckBox* backface_culling_check_ = nullptr;
    QSpinBox* void_limit_spin_ = nullptr;
    QDoubleSpinBox* deflection_tolerance_spin_ = nullptr;
    QDoubleSpinBox* angular_tolerance_spin_ = nullptr;
    QDoubleSpinBox* min_pixel_radius_spin_ = nullptr;
    QDoubleSpinBox* motion_min_pixel_radius_spin_ = nullptr;
    QDoubleSpinBox* lod1_pixel_threshold_spin_ = nullptr;
    QSpinBox* hiz_resolution_spin_ = nullptr;
    QCheckBox* hiz_enabled_check_ = nullptr;
};

#endif
