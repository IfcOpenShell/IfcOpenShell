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

#include "FederationSettingsDialog.h"
#include "Federation.h"

#include <QComboBox>
#include <QDialogButtonBox>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QLabel>
#include <QShowEvent>
#include <QStringList>
#include <QVBoxLayout>

namespace {

// Common length units users will pick.  itemData() carries
// (prefix, name) — empty prefix for non-prefixed or conversion-based units.
struct UnitChoice {
    const char* label;
    const char* prefix;
    const char* name;
};
const UnitChoice kUnitChoices[] = {
    { "Metres (m)",       "",      "METRE" },
    { "Millimetres (mm)", "MILLI", "METRE" },
    { "Centimetres (cm)", "CENTI", "METRE" },
    { "Kilometres (km)",  "KILO",  "METRE" },
    { "Feet (ft)",        "",      "foot"  },
    { "Inches (in)",      "",      "inch"  },
    { "Yards (yd)",       "",      "yard"  },
    { "Miles (mi)",       "",      "mile"  },
};

}  // namespace

FederationSettingsDialog::FederationSettingsDialog(Federation* federation,
                                                   QWidget* parent)
    : QDialog(parent), federation_(federation)
{
    setWindowTitle("Federation Settings");
    setupUi();
}

void FederationSettingsDialog::setupUi() {
    auto* root = new QVBoxLayout(this);

    // Unit
    {
        auto* group = new QGroupBox("Federation Unit", this);
        auto* form = new QFormLayout(group);
        unit_combo_ = new QComboBox(group);
        for (const auto& uc : kUnitChoices) {
            QStringList data;
            data << QString::fromUtf8(uc.prefix) << QString::fromUtf8(uc.name);
            unit_combo_->addItem(uc.label, data);
        }
        unit_combo_->setToolTip(
            "All Federated False Origin and Model Transformation numbers "
            "are interpreted in this unit.  Changing it after data has been "
            "entered re-interprets the numbers — same physical location "
            "expressed in the new unit.");
        form->addRow("Unit", unit_combo_);
        root->addWidget(group);
    }

    // Federated False Origin
    {
        auto* group = new QGroupBox("Federated False Origin", this);
        group->setToolTip(
            "Nominate a point in the federation that becomes the new (0,0,0).  "
            "Optional Z-rotation aligns north for the federation.");
        auto* form = new QFormLayout(group);

        auto build_xyz = [this](QDoubleSpinBox*& sb) {
            sb = new QDoubleSpinBox();
            sb->setRange(-1e12, 1e12);
            sb->setDecimals(6);
            sb->setSingleStep(1.0);
        };
        build_xyz(xyz_x_);
        build_xyz(xyz_y_);
        build_xyz(xyz_z_);
        form->addRow("X", xyz_x_);
        form->addRow("Y", xyz_y_);
        form->addRow("Z", xyz_z_);

        rz_deg_ = new QDoubleSpinBox();
        rz_deg_->setRange(-360.0, 360.0);
        rz_deg_->setDecimals(6);
        rz_deg_->setSingleStep(1.0);
        form->addRow("Z rotation (°)", rz_deg_);
        root->addWidget(group);
    }

    auto* button_box = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    root->addWidget(button_box);
    connect(button_box, &QDialogButtonBox::accepted, this,
            &FederationSettingsDialog::onAccepted);
    connect(button_box, &QDialogButtonBox::rejected, this, &QDialog::reject);
}

void FederationSettingsDialog::showEvent(QShowEvent* event) {
    syncFromFederation();
    QDialog::showEvent(event);
}

void FederationSettingsDialog::syncFromFederation() {
    if (!federation_) return;

    const auto& cfg = federation_->config();
    int idx = -1;
    for (int i = 0; i < unit_combo_->count(); ++i) {
        const QStringList data = unit_combo_->itemData(i).toStringList();
        if (data.size() == 2 &&
            data[0].toStdString() == cfg.unit_prefix &&
            data[1].toStdString() == cfg.unit_name) {
            idx = i;
            break;
        }
    }
    if (idx >= 0) {
        unit_combo_->setCurrentIndex(idx);
    } else {
        // Federation has a unit that isn't in the common list — fall back to
        // the first entry.  Saving keeps whatever the user picks; the
        // original federation unit is preserved unless they hit Ok.
        unit_combo_->setCurrentIndex(0);
    }

    const auto& origin = federation_->federatedFalseOrigin();
    xyz_x_->setValue(origin.xyz.x());
    xyz_y_->setValue(origin.xyz.y());
    xyz_z_->setValue(origin.xyz.z());
    rz_deg_->setValue(origin.rz_deg);
}

void FederationSettingsDialog::onAccepted() {
    if (!federation_) { accept(); return; }

    const QStringList data = unit_combo_->currentData().toStringList();
    FederationConfig cfg;
    if (data.size() == 2) {
        cfg.unit_prefix = data[0].toStdString();
        cfg.unit_name   = data[1].toStdString();
    }
    federation_->setConfig(cfg);

    FederatedFalseOrigin origin;
    origin.xyz    = Eigen::Vector3d(xyz_x_->value(), xyz_y_->value(), xyz_z_->value());
    origin.rz_deg = rz_deg_->value();
    federation_->setFederatedFalseOrigin(origin);

    accept();
}
