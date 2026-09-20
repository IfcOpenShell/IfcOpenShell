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

#ifndef IFCINTERFACE_PANELS_SETTINGSDIALOG_H
#define IFCINTERFACE_PANELS_SETTINGSDIALOG_H

#include "../../components/Dialog.h"

#include <QString>
#include <vector>

class QCheckBox;
class QComboBox;
class QDoubleSpinBox;
class QLineEdit;
class QShowEvent;
class QSpinBox;
class QWidget;

namespace bonsaiviewer { class SessionState; }

namespace bonsaiviewer::modules::settings {

class SettingsDialog : public components::TabbedDialog {
    Q_OBJECT
public:
    explicit SettingsDialog(bonsaiviewer::SessionState* session_state,
                            QWidget* parent = nullptr);

protected:
    void showEvent(QShowEvent* event) override;

private:
    void setupUi();
    QWidget* buildConnectorsTab();
    void syncFromSettings();
    void syncThemeSettings();
    void updateThemeEditorEnabled();
    void pickThemeColor(QLineEdit* edit);
    void onAccepted();

    bonsaiviewer::SessionState* session_state_ = nullptr;

    struct ThemeColorEditor {
        QString key;
        QLineEdit* edit = nullptr;
    };

    QLineEdit* geometry_library_edit_ = nullptr;
    QCheckBox* show_stats_check_ = nullptr;
    QCheckBox* backface_culling_check_ = nullptr;
    QSpinBox* void_limit_spin_ = nullptr;
    QDoubleSpinBox* deflection_tolerance_spin_ = nullptr;
    QDoubleSpinBox* angular_tolerance_spin_ = nullptr;
    QDoubleSpinBox* min_pixel_radius_spin_ = nullptr;
    QDoubleSpinBox* motion_min_pixel_radius_spin_ = nullptr;
    QDoubleSpinBox* lod1_pixel_threshold_spin_ = nullptr;
    QCheckBox* hiz_enabled_check_ = nullptr;
    QSpinBox* hiz_resolution_spin_ = nullptr;
    QComboBox* nav_preset_combo_ = nullptr;
    QComboBox* theme_mode_combo_ = nullptr;
    QWidget* theme_custom_body_ = nullptr;
    std::vector<ThemeColorEditor> theme_color_editors_;
};

} // namespace bonsaiviewer::modules::settings

#endif
