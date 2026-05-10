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

#include "Dialog.h"

#include "../../../ifcviewer/AppSettings.h"
#include "../../components/Dialog.h"
#include "../../components/Section.h"
#include "../../components/Style.h"
#include "../../components/SvgIcon.h"
#include "../../components/Tabs.h"

#include <QCheckBox>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QDoubleSpinBox>
#include <QFrame>
#include <QFormLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QShowEvent>
#include <QSpinBox>
#include <QVBoxLayout>

namespace ifcinterface::modules::settings {

SettingsDialog::SettingsDialog(QWidget* parent)
    : components::Dialog(parent)
{
    setObjectName("appDialog");
    setWindowTitle("Settings");
    setModal(true);
    resize(520, 420);
    setStyleSheet(components::style::buildAppStyleSheet());
    setupUi();
}

void SettingsDialog::showEvent(QShowEvent* event) {
    syncFromSettings();
    QDialog::showEvent(event);
}

void SettingsDialog::setupUi() {
    auto* tabs = new components::TabWidget(this);

    auto* graphics_tab = new QWidget(tabs);
    auto* graphics_layout = new QVBoxLayout(graphics_tab);
    graphics_layout->setContentsMargins(0, 0, 0, 0);
    graphics_layout->setSpacing(components::style::metrics::padding);

    auto* general_section = new components::Section("General", components::SectionHeaderMode::Visible, graphics_tab);
    auto* general_body = new QWidget(general_section);
    auto* general_form = new QFormLayout(general_body);
    general_form->setContentsMargins(0, 0, 0, 0);
    general_form->setHorizontalSpacing(16);
    general_form->setVerticalSpacing(10);

    geometry_library_edit_ = new QLineEdit(general_body);
    geometry_library_edit_->setMinimumWidth(300);
    general_form->addRow("Geometry Library", geometry_library_edit_);

    show_stats_check_ = new QCheckBox(general_body);
    general_form->addRow("Show Performance Stats", show_stats_check_);

    backface_culling_check_ = new QCheckBox(general_body);
    backface_culling_check_->setToolTip(
        "Skip triangles facing away from the camera. Big FPS win on closed solids; "
        "disable if you see holes in open geometry.");
    general_form->addRow("Backface Culling", backface_culling_check_);

    general_section->addBodyWidget(general_body);

    auto* loading_section = new components::Section("Loading", components::SectionHeaderMode::Visible, graphics_tab);
    auto* loading_body = new QWidget(loading_section);
    auto* loading_form = new QFormLayout(loading_body);
    loading_form->setContentsMargins(0, 0, 0, 0);
    loading_form->setHorizontalSpacing(16);
    loading_form->setVerticalSpacing(10);

    void_limit_spin_ = new QSpinBox(loading_body);
    void_limit_spin_->setRange(0, 100000);
    loading_form->addRow("Void Limit", void_limit_spin_);

    deflection_tolerance_spin_ = new QDoubleSpinBox(loading_body);
    deflection_tolerance_spin_->setRange(0.000001, 1000.0);
    deflection_tolerance_spin_->setDecimals(6);
    deflection_tolerance_spin_->setSingleStep(0.001);
    loading_form->addRow("Deflection Tolerance", deflection_tolerance_spin_);

    angular_tolerance_spin_ = new QDoubleSpinBox(loading_body);
    angular_tolerance_spin_->setRange(0.000001, 3.141592);
    angular_tolerance_spin_->setDecimals(6);
    angular_tolerance_spin_->setSingleStep(0.05);
    loading_form->addRow("Angular Tolerance", angular_tolerance_spin_);

    min_pixel_radius_spin_ = new QDoubleSpinBox(loading_body);
    min_pixel_radius_spin_->setRange(0.0, 100.0);
    min_pixel_radius_spin_->setDecimals(2);
    min_pixel_radius_spin_->setSingleStep(0.5);
    min_pixel_radius_spin_->setToolTip(
        "Minimum projected sphere radius (in pixels) for an instance to "
        "be drawn. Bigger = faster but more pop-in on small detail.");
    loading_form->addRow("Min Pixel Radius", min_pixel_radius_spin_);

    motion_min_pixel_radius_spin_ = new QDoubleSpinBox(loading_body);
    motion_min_pixel_radius_spin_->setRange(0.0, 100.0);
    motion_min_pixel_radius_spin_->setDecimals(2);
    motion_min_pixel_radius_spin_->setSingleStep(1.0);
    motion_min_pixel_radius_spin_->setToolTip(
        "Aggressive cull threshold while the camera is moving. 0 = no "
        "motion boost (motion uses the same threshold as still frames).");
    loading_form->addRow("Motion Min Pixel Radius", motion_min_pixel_radius_spin_);

    lod1_pixel_threshold_spin_ = new QDoubleSpinBox(loading_body);
    lod1_pixel_threshold_spin_->setRange(0.0, 1000.0);
    lod1_pixel_threshold_spin_->setDecimals(1);
    lod1_pixel_threshold_spin_->setSingleStep(1.0);
    lod1_pixel_threshold_spin_->setToolTip(
        "Pixel radius below which an instance switches to its LOD1 "
        "representation. 0 disables LOD1 entirely.");
    loading_form->addRow("LOD1 Pixel Threshold", lod1_pixel_threshold_spin_);

    hiz_enabled_check_ = new QCheckBox(loading_body);
    hiz_enabled_check_->setToolTip(
        "Enable HiZ (hierarchical Z) occlusion culling. Hides geometry "
        "behind opaque blockers based on a downsampled depth pyramid.");
    loading_form->addRow("HiZ Occlusion", hiz_enabled_check_);

    hiz_resolution_spin_ = new QSpinBox(loading_body);
    hiz_resolution_spin_->setRange(64, 4096);
    hiz_resolution_spin_->setSingleStep(64);
    hiz_resolution_spin_->setToolTip(
        "Base HiZ pyramid width in texels (height tracks aspect). "
        "Changes take effect on next viewport reinitialization.");
    loading_form->addRow("HiZ Resolution", hiz_resolution_spin_);

    loading_section->addBodyWidget(loading_body);
    graphics_layout->addWidget(general_section);
    graphics_layout->addWidget(loading_section);
    graphics_layout->addStretch(1);

    // Navigation tab: orbit / pan presets.  Selection always stays on
    // LMB so click + box-select keep working regardless of preset.
    auto* navigation_tab = new QWidget(tabs);
    {
        auto* layout = new QVBoxLayout(navigation_tab);
        layout->setContentsMargins(0, 0, 0, 0);
        layout->setSpacing(components::style::metrics::padding);

        auto* section = new components::Section(
            "Navigation", components::SectionHeaderMode::Visible, navigation_tab);
        auto* body = new QWidget(section);
        auto* form = new QFormLayout(body);
        form->setContentsMargins(0, 0, 0, 0);
        form->setHorizontalSpacing(16);
        form->setVerticalSpacing(10);

        nav_preset_combo_ = new QComboBox(body);
        // Order must match AppSettings::NavPreset enum ordering — index
        // is what we read back via currentIndex / setCurrentIndex.
        nav_preset_combo_->addItem("Blender (Orbit MMB, Pan Shift+MMB)");
        nav_preset_combo_->addItem("Rhino (Orbit RMB, Pan Shift+RMB)");
        nav_preset_combo_->addItem("Revit (Orbit Shift+MMB, Pan MMB)");
        nav_preset_combo_->setToolTip(
            "Mouse-button mapping for orbit and pan.  Selection stays on "
            "left mouse button for every preset, so click + box-select "
            "always work.");
        form->addRow("Preset", nav_preset_combo_);

        section->addBodyWidget(body);
        layout->addWidget(section);
        layout->addStretch(1);
    }

    auto make_placeholder_tab = [tabs](const QString& title, const QString& detail) {
        auto* tab = new QWidget(tabs);
        auto* layout = new QVBoxLayout(tab);
        layout->setContentsMargins(0, 0, 0, 0);
        layout->setSpacing(components::style::metrics::padding);

        auto* section = new components::Section(title, components::SectionHeaderMode::Visible, tab);
        auto* body = new QWidget(section);
        auto* body_layout = new QVBoxLayout(body);
        body_layout->setContentsMargins(0, 0, 0, 0);
        body_layout->setSpacing(8);

        auto* heading = new QLabel(title, body);
        auto* content = new QLabel(detail, body);
        content->setProperty("textRole", "secondary");
        content->setWordWrap(true);

        body_layout->addWidget(heading);
        body_layout->addWidget(content);
        section->addBodyWidget(body);
        layout->addWidget(section);
        layout->addStretch(1);
        return tab;
    };

    tabs->addTab(navigation_tab, "Navigation");
    tabs->addTab(make_placeholder_tab("Keybindings", "Shortcut presets and command bindings will live here."),
                 "Keybindings");
    tabs->addTab(graphics_tab, "Graphics");
    tabs->addTab(make_placeholder_tab("Theme", "Theme, density, and UI appearance settings will live here."),
                 "Theme");
    tabs->addTab(make_placeholder_tab("About", "Version, credits, and environment information will live here."),
                 "About");

    auto* buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    if (auto* ok = buttons->button(QDialogButtonBox::Ok)) {
        ok->setText("OK");
        ok->setIcon(components::icons::makeSvgIcon(":/icons/check.svg"));
    }
    if (auto* cancel = buttons->button(QDialogButtonBox::Cancel)) {
        cancel->setText("Cancel");
        cancel->setIcon(components::icons::makeSvgIcon(":/icons/xmark-circle.svg"));
    }
    connect(buttons, &QDialogButtonBox::accepted, this, &SettingsDialog::onAccepted);
    connect(buttons, &QDialogButtonBox::rejected, this, &QDialog::reject);

    addBodyWidget(tabs);
    addFooterWidget(buttons);
}

void SettingsDialog::syncFromSettings() {
    geometry_library_edit_->setText(AppSettings::instance().geometryLibrary());
    show_stats_check_->setChecked(AppSettings::instance().showStats());
    backface_culling_check_->setChecked(AppSettings::instance().backfaceCulling());
    void_limit_spin_->setValue(AppSettings::instance().voidLimit());
    deflection_tolerance_spin_->setValue(AppSettings::instance().deflectionTolerance());
    angular_tolerance_spin_->setValue(AppSettings::instance().angularTolerance());
    min_pixel_radius_spin_->setValue(AppSettings::instance().minPixelRadius());
    motion_min_pixel_radius_spin_->setValue(AppSettings::instance().motionMinPixelRadius());
    lod1_pixel_threshold_spin_->setValue(AppSettings::instance().lod1PixelThreshold());
    hiz_enabled_check_->setChecked(AppSettings::instance().hizEnabled());
    hiz_resolution_spin_->setValue(AppSettings::instance().hizResolution());
    nav_preset_combo_->setCurrentIndex(static_cast<int>(AppSettings::instance().navPreset()));
}

void SettingsDialog::onAccepted() {
    AppSettings::instance().setGeometryLibrary(geometry_library_edit_->text());
    AppSettings::instance().setShowStats(show_stats_check_->isChecked());
    AppSettings::instance().setBackfaceCulling(backface_culling_check_->isChecked());
    AppSettings::instance().setVoidLimit(void_limit_spin_->value());
    AppSettings::instance().setDeflectionTolerance(deflection_tolerance_spin_->value());
    AppSettings::instance().setAngularTolerance(angular_tolerance_spin_->value());
    AppSettings::instance().setMinPixelRadius(min_pixel_radius_spin_->value());
    AppSettings::instance().setMotionMinPixelRadius(motion_min_pixel_radius_spin_->value());
    AppSettings::instance().setLod1PixelThreshold(lod1_pixel_threshold_spin_->value());
    AppSettings::instance().setHizEnabled(hiz_enabled_check_->isChecked());
    AppSettings::instance().setHizResolution(hiz_resolution_spin_->value());
    AppSettings::instance().setNavPreset(
        static_cast<AppSettings::NavPreset>(nav_preset_combo_->currentIndex()));
    accept();
}

} // namespace ifcinterface::modules::settings
