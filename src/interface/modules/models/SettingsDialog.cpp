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

#include "SettingsDialog.h"

#include "../../../ifcviewer/Federation.h"
#include "../../components/Section.h"
#include "../../components/Style.h"
#include "../../components/SvgIcon.h"
#include "../../components/Tabs.h"

#include <QButtonGroup>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QRadioButton>
#include <QShowEvent>
#include <QVBoxLayout>

namespace ifcinterface::modules::models {

namespace {

struct UnitChoice {
    const char* label;
    const char* prefix;
    const char* name;
};

const UnitChoice kUnitChoices[] = {
    {"Metres (m)", "", "METRE"},
    {"Millimetres (mm)", "MILLI", "METRE"},
    {"Centimetres (cm)", "CENTI", "METRE"},
    {"Kilometres (km)", "KILO", "METRE"},
    {"Feet (ft)", "", "foot"},
    {"Inches (in)", "", "inch"},
    {"Yards (yd)", "", "yard"},
    {"Miles (mi)", "", "mile"},
};

QString unitDisplay(const FederationConfig& cfg) {
    QString s;
    if (!cfg.unit_prefix.empty()) s += QString::fromStdString(cfg.unit_prefix) + " ";
    s += QString::fromStdString(cfg.unit_name);
    return s;
}

QLineEdit* makeNumericField(QWidget* parent, const QString& placeholder = {}) {
    auto* field = new QLineEdit(parent);
    field->setPlaceholderText(placeholder);
    field->setMaximumWidth(96);
    return field;
}

QString formatNumber(double value) {
    return QString::number(value, 'f', 6);
}

double parseNumber(QLineEdit* field) {
    bool ok = false;
    const double value = field->text().toDouble(&ok);
    return ok ? value : 0.0;
}

QWidget* makeVector3Row(QLineEdit* x,
                        QLineEdit* y,
                        QLineEdit* z,
                        QWidget* parent) {
    auto* row = new QWidget(parent);
    auto* layout = new QHBoxLayout(row);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(components::style::metrics::padding);
    layout->addWidget(x);
    layout->addWidget(y);
    layout->addWidget(z);
    layout->addStretch(1);
    return row;
}

QWidget* makeRotationRow(QLineEdit* rx,
                         QLineEdit* ry,
                         QLineEdit* rz,
                         QWidget* parent) {
    auto* row = new QWidget(parent);
    auto* layout = new QHBoxLayout(row);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(components::style::metrics::padding);
    layout->addWidget(rx);
    layout->addWidget(ry);
    layout->addWidget(rz);
    layout->addStretch(1);
    return row;
}

} // namespace

SettingsDialog::SettingsDialog(Federation* federation, QWidget* parent)
    : components::Dialog(parent)
    , federation_(federation)
{
    setObjectName("appDialog");
    setWindowTitle("Model Settings");
    setModal(true);
    resize(560, 560);
    setStyleSheet(components::style::buildAppStyleSheet());
    setupUi();
}

void SettingsDialog::showEvent(QShowEvent* event) {
    syncFromFederation();
    populateModelCombo();
    refreshUnitLabels();
    if (model_combo_->count() > 0) {
        syncFromModel(model_combo_->currentData().toString());
    }
    QDialog::showEvent(event);
}

void SettingsDialog::setupUi() {
    auto* tabs = new components::TabWidget(this);

    auto* federation_tab = new QWidget(tabs);
    auto* federation_layout = new QVBoxLayout(federation_tab);
    federation_layout->setContentsMargins(0, 0, 0, 0);
    federation_layout->setSpacing(components::style::metrics::padding);

    auto* federation_unit_section = new components::Section("Federation Unit", components::SectionHeaderMode::Visible, federation_tab);
    auto* federation_unit_body = new QWidget(federation_unit_section);
    auto* federation_unit_form = new QFormLayout(federation_unit_body);
    federation_unit_form->setContentsMargins(0, 0, 0, 0);
    federation_unit_form->setHorizontalSpacing(16);
    federation_unit_form->setVerticalSpacing(10);
    unit_combo_ = new QComboBox(federation_unit_body);
    for (const auto& uc : kUnitChoices) {
        QStringList data;
        data << QString::fromUtf8(uc.prefix) << QString::fromUtf8(uc.name);
        unit_combo_->addItem(uc.label, data);
    }
    federation_unit_form->addRow("Unit", unit_combo_);
    auto* unit_hint = new QLabel(
        "All federated false origin and model transformation values are interpreted in this unit.",
        federation_unit_body);
    unit_hint->setProperty("textRole", "secondary");
    unit_hint->setWordWrap(true);
    federation_unit_form->addRow(QString(), unit_hint);
    federation_unit_section->addBodyWidget(federation_unit_body);

    auto* origin_section = new components::Section("Federated False Origin", components::SectionHeaderMode::Visible, federation_tab);
    auto* origin_body = new QWidget(origin_section);
    auto* origin_form = new QFormLayout(origin_body);
    origin_form->setContentsMargins(0, 0, 0, 0);
    origin_form->setHorizontalSpacing(16);
    origin_form->setVerticalSpacing(10);
    xyz_x_ = makeNumericField(origin_body, "X");
    xyz_y_ = makeNumericField(origin_body, "Y");
    xyz_z_ = makeNumericField(origin_body, "Z");
    rz_deg_ = makeNumericField(origin_body, "deg");
    origin_form->addRow("XYZ", makeVector3Row(xyz_x_, xyz_y_, xyz_z_, origin_body));
    origin_form->addRow("Z rotation (°)", rz_deg_);
    auto* origin_hint = new QLabel(
        "Nominate a federation point that becomes the new origin, with optional north rotation.",
        origin_body);
    origin_hint->setProperty("textRole", "secondary");
    origin_hint->setWordWrap(true);
    origin_form->addRow(QString(), origin_hint);
    origin_section->addBodyWidget(origin_body);

    federation_layout->addWidget(federation_unit_section);
    federation_layout->addWidget(origin_section);
    federation_layout->addStretch(1);

    auto* model_tab = new QWidget(tabs);
    auto* model_layout = new QVBoxLayout(model_tab);
    model_layout->setContentsMargins(0, 0, 0, 0);
    model_layout->setSpacing(components::style::metrics::padding);

    auto* picker_section = new components::Section("", components::SectionHeaderMode::Hidden, model_tab);
    auto* picker_body = new QWidget(picker_section);
    auto* picker_form = new QFormLayout(picker_body);
    picker_form->setContentsMargins(0, 0, 0, 0);
    picker_form->setHorizontalSpacing(16);
    picker_form->setVerticalSpacing(10);
    model_combo_ = new QComboBox(picker_body);
    picker_form->addRow("Current Model", model_combo_);
    picker_section->addBodyWidget(picker_body);

    auto* a_section = new components::Section("Point A", components::SectionHeaderMode::Visible, model_tab);
    auto* a_body = new QWidget(a_section);
    auto* a_form = new QFormLayout(a_body);
    a_form->setContentsMargins(0, 0, 0, 0);
    a_form->setHorizontalSpacing(16);
    a_form->setVerticalSpacing(10);
    radio_local_ = new QRadioButton("ModelLocal", a_body);
    radio_global_ = new QRadioButton("ModelGlobal", a_body);
    radio_global_->setChecked(true);
    auto* a_frame_group = new QButtonGroup(this);
    a_frame_group->addButton(radio_local_);
    a_frame_group->addButton(radio_global_);
    auto* a_frame_row = new QHBoxLayout();
    a_frame_row->setContentsMargins(0, 0, 0, 0);
    a_frame_row->setSpacing(components::style::metrics::padding);
    a_frame_row->addWidget(radio_local_);
    a_frame_row->addWidget(radio_global_);
    a_frame_row->addStretch(1);
    a_form->addRow("Frame", a_frame_row);
    a_x_ = makeNumericField(a_body, "X");
    a_y_ = makeNumericField(a_body, "Y");
    a_z_ = makeNumericField(a_body, "Z");
    a_form->addRow("XYZ", makeVector3Row(a_x_, a_y_, a_z_, a_body));
    a_unit_label_ = new QLabel(a_body);
    a_unit_label_->setProperty("textRole", "secondary");
    a_form->addRow("Unit", a_unit_label_);
    a_section->addBodyWidget(a_body);

    auto* b_section = new components::Section("Point B", components::SectionHeaderMode::Visible, model_tab);
    auto* b_body = new QWidget(b_section);
    auto* b_form = new QFormLayout(b_body);
    b_form->setContentsMargins(0, 0, 0, 0);
    b_form->setHorizontalSpacing(16);
    b_form->setVerticalSpacing(10);
    b_x_ = makeNumericField(b_body, "X");
    b_y_ = makeNumericField(b_body, "Y");
    b_z_ = makeNumericField(b_body, "Z");
    b_form->addRow("XYZ", makeVector3Row(b_x_, b_y_, b_z_, b_body));
    b_unit_label_ = new QLabel(b_body);
    b_unit_label_->setProperty("textRole", "secondary");
    b_form->addRow("Unit", b_unit_label_);
    b_section->addBodyWidget(b_body);

    auto* rotation_section = new components::Section("Rotation", components::SectionHeaderMode::Visible, model_tab);
    auto* rotation_body = new QWidget(rotation_section);
    auto* rotation_form = new QFormLayout(rotation_body);
    rotation_form->setContentsMargins(0, 0, 0, 0);
    rotation_form->setHorizontalSpacing(16);
    rotation_form->setVerticalSpacing(10);
    rx_ = makeNumericField(rotation_body, "rx");
    ry_ = makeNumericField(rotation_body, "ry");
    rz_ = makeNumericField(rotation_body, "rz");
    rotation_form->addRow("RXYZ", makeRotationRow(rx_, ry_, rz_, rotation_body));
    rotation_section->addBodyWidget(rotation_body);

    auto* pivot_section = new components::Section("Rotation Pivot", components::SectionHeaderMode::Visible, model_tab);
    auto* pivot_body = new QWidget(pivot_section);
    auto* pivot_form = new QFormLayout(pivot_body);
    pivot_form->setContentsMargins(0, 0, 0, 0);
    pivot_form->setHorizontalSpacing(16);
    pivot_form->setVerticalSpacing(10);
    pivot_x_ = makeNumericField(pivot_body, "X");
    pivot_y_ = makeNumericField(pivot_body, "Y");
    pivot_z_ = makeNumericField(pivot_body, "Z");
    pivot_form->addRow("XYZ", makeVector3Row(pivot_x_, pivot_y_, pivot_z_, pivot_body));
    pivot_unit_label_ = new QLabel(pivot_body);
    pivot_unit_label_->setProperty("textRole", "secondary");
    pivot_form->addRow("Unit", pivot_unit_label_);
    pivot_section->addBodyWidget(pivot_body);

    model_layout->addWidget(picker_section);
    model_layout->addWidget(a_section);
    model_layout->addWidget(b_section);
    model_layout->addWidget(rotation_section);
    model_layout->addWidget(pivot_section);
    model_layout->addStretch(1);

    tabs->addTab(federation_tab, "Federation");
    tabs->addTab(model_tab, "Model");

    connect(model_combo_, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [this](int) {
        if (model_combo_->count() > 0) {
            syncFromModel(model_combo_->currentData().toString());
        }
    });
    connect(radio_local_, &QRadioButton::toggled, this, [this]() { onAFrameToggled(); });
    connect(radio_global_, &QRadioButton::toggled, this, [this]() { onAFrameToggled(); });

    auto* buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    if (auto* ok = buttons->button(QDialogButtonBox::Ok)) {
        ok->setText("OK");
        ok->setIcon(components::icons::makeSvgIcon(":/icons/check.svg"));
    }
    if (auto* cancel = buttons->button(QDialogButtonBox::Cancel)) {
        cancel->setText("Cancel");
        cancel->setIcon(components::icons::makeSvgIcon(":/icons/xmark-circle.svg"));
    }
    connect(buttons, &QDialogButtonBox::accepted, this, [this]() { onAccepted(); });
    connect(buttons, &QDialogButtonBox::rejected, this, &QDialog::reject);

    auto* actions_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    actions_section->addBodyWidget(buttons);

    addBodyWidget(tabs);
    addBodyWidget(actions_section);
}

void SettingsDialog::syncFromFederation() {
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
    unit_combo_->setCurrentIndex(idx >= 0 ? idx : 0);

    const auto& origin = federation_->federatedFalseOrigin();
    xyz_x_->setText(formatNumber(origin.xyz.x()));
    xyz_y_->setText(formatNumber(origin.xyz.y()));
    xyz_z_->setText(formatNumber(origin.xyz.z()));
    rz_deg_->setText(formatNumber(origin.rz_deg));
}

void SettingsDialog::populateModelCombo() {
    model_combo_->blockSignals(true);
    QString previous = model_combo_->currentData().toString();
    model_combo_->clear();
    if (federation_) {
        for (const auto& model : federation_->models()) {
            model_combo_->addItem(model.display_name.isEmpty() ? model.id : model.display_name, model.id);
        }
    }
    int restore = -1;
    for (int i = 0; i < model_combo_->count(); ++i) {
        if (model_combo_->itemData(i).toString() == previous) {
            restore = i;
            break;
        }
    }
    if (restore >= 0) model_combo_->setCurrentIndex(restore);
    model_combo_->blockSignals(false);
}

void SettingsDialog::syncFromModel(const QString& fed_id) {
    if (!federation_) return;
    const Federation::Model* model = federation_->findById(fed_id);
    if (!model) return;

    const auto& xf = model->model_transformation;
    radio_local_->setChecked(xf.a_frame == AFrame::ModelLocal);
    radio_global_->setChecked(xf.a_frame == AFrame::ModelGlobal);
    a_x_->setText(formatNumber(xf.a.x()));
    a_y_->setText(formatNumber(xf.a.y()));
    a_z_->setText(formatNumber(xf.a.z()));
    b_x_->setText(formatNumber(xf.b.x()));
    b_y_->setText(formatNumber(xf.b.y()));
    b_z_->setText(formatNumber(xf.b.z()));
    rx_->setText(formatNumber(xf.rxyz_deg.x()));
    ry_->setText(formatNumber(xf.rxyz_deg.y()));
    rz_->setText(formatNumber(xf.rxyz_deg.z()));
    pivot_x_->setText(formatNumber(xf.pivot.x()));
    pivot_y_->setText(formatNumber(xf.pivot.y()));
    pivot_z_->setText(formatNumber(xf.pivot.z()));
}

void SettingsDialog::refreshUnitLabels() {
    if (!federation_) return;
    const QString fed_unit = unitDisplay(federation_->config());
    b_unit_label_->setText("(federation: " + fed_unit + ")");
    pivot_unit_label_->setText("(federation: " + fed_unit + ")");
    onAFrameToggled();
}

void SettingsDialog::onAFrameToggled() {
    if (!a_unit_label_) return;
    if (radio_local_->isChecked()) {
        a_unit_label_->setText("(model project length unit)");
    } else {
        a_unit_label_->setText("(model map unit)");
    }
}

void SettingsDialog::onAccepted() {
    if (federation_) {
        const QStringList data = unit_combo_->currentData().toStringList();
        FederationConfig cfg;
        if (data.size() == 2) {
            cfg.unit_prefix = data[0].toStdString();
            cfg.unit_name = data[1].toStdString();
        }
        federation_->setConfig(cfg);

        FederatedFalseOrigin origin;
        origin.xyz = Eigen::Vector3d(parseNumber(xyz_x_), parseNumber(xyz_y_), parseNumber(xyz_z_));
        origin.rz_deg = parseNumber(rz_deg_);
        federation_->setFederatedFalseOrigin(origin);

        if (model_combo_->count() > 0) {
            ModelTransformation xf;
            xf.a_frame = radio_local_->isChecked() ? AFrame::ModelLocal : AFrame::ModelGlobal;
            xf.a = Eigen::Vector3d(parseNumber(a_x_), parseNumber(a_y_), parseNumber(a_z_));
            xf.b = Eigen::Vector3d(parseNumber(b_x_), parseNumber(b_y_), parseNumber(b_z_));
            xf.rxyz_deg = Eigen::Vector3d(parseNumber(rx_), parseNumber(ry_), parseNumber(rz_));
            xf.pivot = Eigen::Vector3d(parseNumber(pivot_x_), parseNumber(pivot_y_), parseNumber(pivot_z_));
            federation_->setModelTransformation(model_combo_->currentData().toString(), xf);
        }
    }
    accept();
}

} // namespace ifcinterface::modules::models
