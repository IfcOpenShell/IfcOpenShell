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

    load_data_source_check_ = new QCheckBox(this);
    load_data_source_check_->setToolTip(
        "Keep the .ifc/.rdb open after loading so element properties can "
        "be queried.  Disable for geometry-only viewing — saves memory "
        "and, on sidecar hits, avoids a second file read.");
    form->addRow("Load Property Data Source", load_data_source_check_);

    apply_coordinate_operation_check_ = new QCheckBox(this);
    apply_coordinate_operation_check_->setToolTip(
        "Apply each model's IfcCoordinateOperation (e.g. IfcMapConversion) "
        "after load so it lands in georeferenced map coordinates.  "
        "Disable to keep models in their local engineering frame.");
    form->addRow("Apply Coordinate Operation",
                 apply_coordinate_operation_check_);

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
    load_data_source_check_->setChecked(AppSettings::instance().loadDataSource());
    apply_coordinate_operation_check_->setChecked(
        AppSettings::instance().applyCoordinateOperation());
    void_limit_spin_->setValue(AppSettings::instance().voidLimit());
    deflection_tolerance_spin_->setValue(AppSettings::instance().deflectionTolerance());
    angular_tolerance_spin_->setValue(AppSettings::instance().angularTolerance());
}

void SettingsWindow::onAccepted() {
    AppSettings::instance().setGeometryLibrary(geometry_library_edit_->text());
    AppSettings::instance().setShowStats(show_stats_check_->isChecked());
    AppSettings::instance().setBackfaceCulling(backface_culling_check_->isChecked());
    AppSettings::instance().setLoadDataSource(load_data_source_check_->isChecked());
    AppSettings::instance().setApplyCoordinateOperation(
        apply_coordinate_operation_check_->isChecked());
    AppSettings::instance().setVoidLimit(void_limit_spin_->value());
    AppSettings::instance().setDeflectionTolerance(deflection_tolerance_spin_->value());
    AppSettings::instance().setAngularTolerance(angular_tolerance_spin_->value());
    accept();
}
