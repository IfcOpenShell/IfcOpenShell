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

#include "SettingsWindow.h"
#include "AppSettings.h"

#include <QCheckBox>
#include <QDialogButtonBox>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QLineEdit>
#include <QShowEvent>
#include <QSpinBox>
#include <QVBoxLayout>

SettingsWindow::SettingsWindow(QWidget *parent)
    : QDialog(parent)
{
    setWindowTitle("Settings");
    setupUi();
}

void SettingsWindow::setupUi() {
    auto* form = new QFormLayout();

    geometry_library_edit_ = new QLineEdit(this);
    geometry_library_edit_->setMinimumWidth(280);
    form->addRow("Geometry Library", geometry_library_edit_);

    show_stats_check_ = new QCheckBox(this);
    form->addRow("Show Performance Stats", show_stats_check_);

    backface_culling_check_ = new QCheckBox(this);
    backface_culling_check_->setToolTip(
        "Skip triangles facing away from the camera.  Big FPS win on "
        "closed solids; disable if you see holes in open geometry.");
    form->addRow("Backface Culling", backface_culling_check_);

    void_limit_spin_ = new QSpinBox(this);
    void_limit_spin_->setRange(0, 100000);
    void_limit_spin_->setToolTip(
        "Skip elements with more openings (HasOpenings) than this.  "
        "A handful of pathological elements can dominate boolean-subtraction "
        "time; dropping them keeps load times sane.");
    form->addRow("Void Limit", void_limit_spin_);

    deflection_tolerance_spin_ = new QDoubleSpinBox(this);
    deflection_tolerance_spin_->setRange(0.000001, 1000.0);
    deflection_tolerance_spin_->setDecimals(6);
    deflection_tolerance_spin_->setSingleStep(0.001);
    deflection_tolerance_spin_->setToolTip(
        "Linear chord error between curved geometry and its triangulation, "
        "in model length units.  Smaller = smoother curves but more "
        "triangles and slower load.");
    form->addRow("Deflection Tolerance", deflection_tolerance_spin_);

    angular_tolerance_spin_ = new QDoubleSpinBox(this);
    angular_tolerance_spin_->setRange(0.000001, 3.141592);
    angular_tolerance_spin_->setDecimals(6);
    angular_tolerance_spin_->setSingleStep(0.05);
    angular_tolerance_spin_->setToolTip(
        "Maximum angle (radians) between adjacent facet normals on a "
        "curved surface.  Smaller = smoother shading but more triangles.");
    form->addRow("Angular Tolerance", angular_tolerance_spin_);

    min_pixel_radius_spin_ = new QDoubleSpinBox(this);
    min_pixel_radius_spin_->setRange(0.0, 100.0);
    min_pixel_radius_spin_->setDecimals(2);
    min_pixel_radius_spin_->setSingleStep(0.5);
    min_pixel_radius_spin_->setToolTip(
        "Minimum projected sphere radius (in pixels) for an instance to "
        "be drawn.  Bigger = faster but more pop-in on small detail.");
    form->addRow("Min Pixel Radius", min_pixel_radius_spin_);

    motion_min_pixel_radius_spin_ = new QDoubleSpinBox(this);
    motion_min_pixel_radius_spin_->setRange(0.0, 100.0);
    motion_min_pixel_radius_spin_->setDecimals(2);
    motion_min_pixel_radius_spin_->setSingleStep(1.0);
    motion_min_pixel_radius_spin_->setToolTip(
        "Aggressive cull threshold while the camera is moving.  0 = no "
        "motion boost (motion uses the same threshold as still frames).  "
        "Big perceived FPS win on heavy scenes.");
    form->addRow("Motion Min Pixel Radius", motion_min_pixel_radius_spin_);

    lod1_pixel_threshold_spin_ = new QDoubleSpinBox(this);
    lod1_pixel_threshold_spin_->setRange(0.0, 1000.0);
    lod1_pixel_threshold_spin_->setDecimals(1);
    lod1_pixel_threshold_spin_->setSingleStep(1.0);
    lod1_pixel_threshold_spin_->setToolTip(
        "Pixel radius below which an instance switches to its LOD1 "
        "representation.  0 disables LOD1 entirely (always draw LOD0).");
    form->addRow("LOD1 Pixel Threshold", lod1_pixel_threshold_spin_);

    hiz_enabled_check_ = new QCheckBox(this);
    hiz_enabled_check_->setToolTip(
        "Enable HiZ (hierarchical Z) occlusion culling.  Hides geometry "
        "behind opaque blockers based on a downsampled depth pyramid "
        "from the previous frame.  Big perf win on dense interiors.");
    form->addRow("HiZ Occlusion", hiz_enabled_check_);

    hiz_resolution_spin_ = new QSpinBox(this);
    hiz_resolution_spin_->setRange(64, 4096);
    hiz_resolution_spin_->setSingleStep(64);
    hiz_resolution_spin_->setToolTip(
        "Base HiZ pyramid width in texels (height tracks aspect).  "
        "Bigger = tighter occlusion but more readback bandwidth.  "
        "Changes take effect on next viewport reinitialization.");
    form->addRow("HiZ Resolution", hiz_resolution_spin_);

    auto* button_box = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);

    auto* root = new QVBoxLayout(this);
    root->addLayout(form);
    root->addWidget(button_box);

    connect(button_box, &QDialogButtonBox::accepted, this, &SettingsWindow::onAccepted);
    connect(button_box, &QDialogButtonBox::rejected, this, &SettingsWindow::reject);
}

void SettingsWindow::showEvent(QShowEvent* event) {
    // Re-sync widgets from the persisted settings every time the dialog is
    // shown, so a previous Cancel doesn't leave stale text in the field.
    syncFromSettings();
    QDialog::showEvent(event);
}

void SettingsWindow::syncFromSettings() {
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
}

void SettingsWindow::onAccepted() {
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
    accept();
}
