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

#include "ModelTransformationDialog.h"
#include "Federation.h"

#include <QButtonGroup>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QRadioButton>
#include <QShowEvent>
#include <QVBoxLayout>

namespace {

QString unitDisplay(const FederationConfig& cfg) {
    QString s;
    if (!cfg.unit_prefix.empty()) s += QString::fromStdString(cfg.unit_prefix) + " ";
    s += QString::fromStdString(cfg.unit_name);
    return s;
}

}  // namespace

ModelTransformationDialog::ModelTransformationDialog(Federation* federation,
                                                     QWidget* parent)
    : QDialog(parent), federation_(federation)
{
    setWindowTitle("Model Transformation");
    setupUi();
}

void ModelTransformationDialog::setupUi() {
    auto* root = new QVBoxLayout(this);

    // Model picker.
    {
        auto* row = new QHBoxLayout();
        row->addWidget(new QLabel("Model:", this));
        model_combo_ = new QComboBox(this);
        row->addWidget(model_combo_, 1);
        root->addLayout(row);
        connect(model_combo_, QOverload<int>::of(&QComboBox::currentIndexChanged),
                this, &ModelTransformationDialog::onModelChanged);
    }

    auto build_xyz = [](QDoubleSpinBox*& sb) {
        sb = new QDoubleSpinBox();
        sb->setRange(-1e12, 1e12);
        sb->setDecimals(6);
        sb->setSingleStep(1.0);
    };

    // A-frame + A.
    {
        auto* group = new QGroupBox("Point A", this);
        group->setToolTip(
            "The model-side anchor point.  ModelLocal expresses A in the "
            "model's project length unit, before its CoordinateOperation.  "
            "ModelGlobal expresses A in the model's map unit, after its "
            "CoordinateOperation.");
        auto* form = new QFormLayout(group);

        radio_local_  = new QRadioButton("ModelLocal", group);
        radio_global_ = new QRadioButton("ModelGlobal", group);
        radio_global_->setChecked(true);
        auto* af_group = new QButtonGroup(this);
        af_group->addButton(radio_local_);
        af_group->addButton(radio_global_);
        connect(radio_local_,  &QRadioButton::toggled,
                this, &ModelTransformationDialog::onAFrameToggled);
        connect(radio_global_, &QRadioButton::toggled,
                this, &ModelTransformationDialog::onAFrameToggled);

        auto* af_row = new QHBoxLayout();
        af_row->addWidget(radio_local_);
        af_row->addWidget(radio_global_);
        af_row->addStretch();
        form->addRow("Frame", af_row);

        build_xyz(a_x_); build_xyz(a_y_); build_xyz(a_z_);
        form->addRow("X", a_x_);
        form->addRow("Y", a_y_);
        form->addRow("Z", a_z_);
        a_unit_label_ = new QLabel("(model unit)", group);
        form->addRow("Unit", a_unit_label_);

        root->addWidget(group);
    }

    // B.
    {
        auto* group = new QGroupBox("Point B (federation target)", this);
        group->setToolTip(
            "Where in the federation point A should land.  In federation units.");
        auto* form = new QFormLayout(group);
        build_xyz(b_x_); build_xyz(b_y_); build_xyz(b_z_);
        form->addRow("X", b_x_);
        form->addRow("Y", b_y_);
        form->addRow("Z", b_z_);
        b_unit_label_ = new QLabel("(federation unit)", group);
        form->addRow("Unit", b_unit_label_);
        root->addWidget(group);
    }

    // Rotation (intrinsic XYZ).
    {
        auto* group = new QGroupBox("Rotation (intrinsic XYZ, degrees)", this);
        group->setToolTip(
            "Composed as R = R_z(rz) · R_y(ry) · R_x(rx).  Y-up models "
            "rotated to Z-up: rx = 90, ry = 0, rz = 0.");
        auto* form = new QFormLayout(group);
        rx_ = new QDoubleSpinBox(); rx_->setRange(-360, 360); rx_->setDecimals(6);
        ry_ = new QDoubleSpinBox(); ry_->setRange(-360, 360); ry_->setDecimals(6);
        rz_ = new QDoubleSpinBox(); rz_->setRange(-360, 360); rz_->setDecimals(6);
        form->addRow("rx (°)", rx_);
        form->addRow("ry (°)", ry_);
        form->addRow("rz (°)", rz_);
        root->addWidget(group);
    }

    // Pivot.
    {
        auto* group = new QGroupBox("Rotation Pivot", this);
        group->setToolTip(
            "The point the rotation rotates around, in federation units.  "
            "Set pivot = B to keep A landing on B regardless of rotation.");
        auto* form = new QFormLayout(group);
        build_xyz(pivot_x_); build_xyz(pivot_y_); build_xyz(pivot_z_);
        form->addRow("X", pivot_x_);
        form->addRow("Y", pivot_y_);
        form->addRow("Z", pivot_z_);
        pivot_unit_label_ = new QLabel("(federation unit)", group);
        form->addRow("Unit", pivot_unit_label_);
        root->addWidget(group);
    }

    auto* button_box = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    root->addWidget(button_box);
    connect(button_box, &QDialogButtonBox::accepted, this,
            &ModelTransformationDialog::onAccepted);
    connect(button_box, &QDialogButtonBox::rejected, this, &QDialog::reject);
}

void ModelTransformationDialog::showEvent(QShowEvent* event) {
    populateModelCombo();
    refreshUnitLabels();
    if (model_combo_->count() > 0) {
        syncFromModel(model_combo_->currentData().toString());
    }
    QDialog::showEvent(event);
}

void ModelTransformationDialog::populateModelCombo() {
    model_combo_->blockSignals(true);
    QString prev_id = model_combo_->currentData().toString();
    model_combo_->clear();
    if (federation_) {
        for (const auto& m : federation_->models()) {
            QString label = m.display_name.isEmpty() ? m.id : m.display_name;
            model_combo_->addItem(label, m.id);
        }
    }
    int restore = -1;
    for (int i = 0; i < model_combo_->count(); ++i) {
        if (model_combo_->itemData(i).toString() == prev_id) { restore = i; break; }
    }
    if (restore >= 0) model_combo_->setCurrentIndex(restore);
    model_combo_->blockSignals(false);
}

void ModelTransformationDialog::syncFromModel(const QString& fed_id) {
    if (!federation_) return;
    const Federation::Model* m = federation_->findById(fed_id);
    if (!m) return;
    const ModelTransformation& xf = m->model_transformation;

    radio_local_->setChecked(xf.a_frame == AFrame::ModelLocal);
    radio_global_->setChecked(xf.a_frame == AFrame::ModelGlobal);

    a_x_->setValue(xf.a.x()); a_y_->setValue(xf.a.y()); a_z_->setValue(xf.a.z());
    b_x_->setValue(xf.b.x()); b_y_->setValue(xf.b.y()); b_z_->setValue(xf.b.z());
    rx_->setValue(xf.rxyz_deg.x());
    ry_->setValue(xf.rxyz_deg.y());
    rz_->setValue(xf.rxyz_deg.z());
    pivot_x_->setValue(xf.pivot.x());
    pivot_y_->setValue(xf.pivot.y());
    pivot_z_->setValue(xf.pivot.z());
}

void ModelTransformationDialog::refreshUnitLabels() {
    if (!federation_) return;
    const QString fed_unit = unitDisplay(federation_->config());
    b_unit_label_->setText("(federation: " + fed_unit + ")");
    pivot_unit_label_->setText("(federation: " + fed_unit + ")");
    onAFrameToggled();
}

void ModelTransformationDialog::onModelChanged(int /*idx*/) {
    if (model_combo_->count() == 0) return;
    syncFromModel(model_combo_->currentData().toString());
}

void ModelTransformationDialog::onAFrameToggled() {
    if (!a_unit_label_) return;
    if (radio_local_->isChecked()) {
        a_unit_label_->setText("(model project length unit, e.g. millimetre)");
    } else {
        a_unit_label_->setText("(model map unit, e.g. metre)");
    }
}

void ModelTransformationDialog::onAccepted() {
    if (!federation_ || model_combo_->count() == 0) { accept(); return; }
    const QString fed_id = model_combo_->currentData().toString();

    ModelTransformation xf;
    xf.a_frame  = radio_local_->isChecked() ? AFrame::ModelLocal : AFrame::ModelGlobal;
    xf.a        = Eigen::Vector3d(a_x_->value(),     a_y_->value(),     a_z_->value());
    xf.b        = Eigen::Vector3d(b_x_->value(),     b_y_->value(),     b_z_->value());
    xf.rxyz_deg = Eigen::Vector3d(rx_->value(),      ry_->value(),      rz_->value());
    xf.pivot    = Eigen::Vector3d(pivot_x_->value(), pivot_y_->value(), pivot_z_->value());

    federation_->setModelTransformation(fed_id, xf);
    accept();
}
