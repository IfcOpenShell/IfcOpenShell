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

#include "../../SessionState.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../components/Section.h"
#include "../../components/Style.h"
#include "../../components/SvgIcon.h"
#include "../../components/Tabs.h"

#include <QComboBox>
#include <QDialogButtonBox>
#include <QFormLayout>
#include <QHeaderView>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QRegularExpression>
#include <QSizePolicy>
#include <QShowEvent>
#include <QSignalBlocker>
#include <QScrollBar>
#include <QTableWidget>
#include <QTableWidgetItem>
#include <QVBoxLayout>

#include <cmath>

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

QLineEdit* makeNumericField(QWidget* parent, const QString& placeholder = {}) {
    auto* field = new QLineEdit(parent);
    field->setPlaceholderText(placeholder);
    field->setMaximumWidth(96);
    return field;
}

QWidget* makeEqualThirdsRow(QWidget* parent, QLineEdit* a, QLineEdit* b, QLineEdit* c) {
    auto* row = new QWidget(parent);
    auto* layout = new QHBoxLayout(row);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(components::style::metrics::padding);
    for (QLineEdit* field : {a, b, c}) {
        field->setMaximumWidth(QWIDGETSIZE_MAX);
        field->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
        layout->addWidget(field, 1);
    }
    return row;
}

QString formatNumber(double value) {
    return QString::number(value, 'f', 6);
}

double parseNumber(QLineEdit* field) {
    bool ok = false;
    const double value = field->text().toDouble(&ok);
    return ok ? value : 0.0;
}

QString formatVector3(const Eigen::Vector3d& value) {
    return QString("%1, %2, %3").arg(formatNumber(value.x()), formatNumber(value.y()), formatNumber(value.z()));
}

Eigen::Vector3d parseVector3(const QString& text) {
    const QStringList parts = text.split(QRegularExpression("[,\\s]+"), Qt::SkipEmptyParts);
    if (parts.size() != 3) return Eigen::Vector3d::Zero();

    bool ok_x = false;
    bool ok_y = false;
    bool ok_z = false;
    const double x = parts[0].toDouble(&ok_x);
    const double y = parts[1].toDouble(&ok_y);
    const double z = parts[2].toDouble(&ok_z);
    if (!ok_x || !ok_y || !ok_z) return Eigen::Vector3d::Zero();
    return Eigen::Vector3d(x, y, z);
}

QString formatAngleDms(double degrees) {
    const double absolute = std::fabs(degrees);
    const int d = static_cast<int>(absolute);
    const double minutes_total = (absolute - static_cast<double>(d)) * 60.0;
    const int m = static_cast<int>(minutes_total);
    const double s = (minutes_total - static_cast<double>(m)) * 60.0;
    const QString sign = degrees < 0.0 ? "-" : "";
    return QString("%1%2° %3' %4\"").arg(sign).arg(d).arg(m, 2, 10, QChar('0')).arg(formatNumber(s));
}

QLabel* makeReadOnlyValue(QWidget* parent) {
    auto* label = new QLabel(parent);
    label->setTextInteractionFlags(Qt::TextSelectableByMouse);
    label->setWordWrap(true);
    return label;
}

} // namespace

SettingsDialog::SettingsDialog(ifcinterface::SessionState* session_state, QWidget* parent)
    : components::TabbedDialog(parent)
    , session_state_(session_state)
    , federation_(session_state ? session_state->federation() : nullptr)
    , loader_(session_state ? session_state->loader() : nullptr)
{
    setObjectName("appDialog");
    setWindowTitle("Model Settings");
    setModal(true);
    resize(980, 560);
    setupUi();
}

void SettingsDialog::showEvent(QShowEvent* event) {
    federation_ = session_state_ ? session_state_->federation() : federation_;
    loader_ = session_state_ ? session_state_->loader() : loader_;
    syncFromFederation();
    populateModelTable();
    QDialog::showEvent(event);
}

void SettingsDialog::setupUi() {
    auto* federation_tab = new QWidget(this);
    auto* federation_layout = new QVBoxLayout(federation_tab);
    federation_layout->setContentsMargins(0, 0, 0, 0);
    federation_layout->setSpacing(components::style::metrics::padding);
    federation_layout->setAlignment(Qt::AlignTop);

    auto* federation_unit_section =
        new components::Section("Federation Unit", components::SectionHeaderMode::Visible, federation_tab);
    auto* unit_hint = new QLabel(
        "All measurements, federated false origins, and destination model transforms will be interpreted in this unit.",
        federation_unit_section);
    unit_hint->setProperty("textRole", "secondary");
    unit_hint->setWordWrap(true);
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
    federation_unit_section->addBodyWidget(unit_hint);
    federation_unit_section->addBodyWidget(federation_unit_body);

    auto* origin_section =
        new components::Section("Federated False Origin", components::SectionHeaderMode::Visible, federation_tab);
    auto* origin_hint = new QLabel(
        "Nominate a false origin and project north to use when viewing the federation of models.",
        origin_section);
    origin_hint->setProperty("textRole", "secondary");
    origin_hint->setWordWrap(true);
    auto* origin_body = new QWidget(origin_section);
    auto* origin_form = new QFormLayout(origin_body);
    origin_form->setContentsMargins(0, 0, 0, 0);
    origin_form->setHorizontalSpacing(16);
    origin_form->setVerticalSpacing(10);
    xyz_x_ = makeNumericField(origin_body, "X");
    xyz_y_ = makeNumericField(origin_body, "Y");
    xyz_z_ = makeNumericField(origin_body, "Z");
    rz_deg_ = makeNumericField(origin_body, "deg");
    origin_form->addRow("XYZ", makeEqualThirdsRow(origin_body, xyz_x_, xyz_y_, xyz_z_));
    origin_form->addRow("Z rotation (°)", rz_deg_);
    origin_section->addBodyWidget(origin_hint);
    origin_section->addBodyWidget(origin_body);

    federation_layout->addWidget(federation_unit_section);
    federation_layout->addWidget(origin_section);
    federation_layout->addStretch(1);

    auto* model_tab = new QWidget(this);
    auto* model_layout = new QVBoxLayout(model_tab);
    model_layout->setContentsMargins(0, 0, 0, 0);
    model_layout->setSpacing(components::style::metrics::padding);
    model_layout->setAlignment(Qt::AlignTop);

    auto* georef_section =
        new components::Section("Selected Model Georeferencing", components::SectionHeaderMode::Visible, model_tab);
    auto* georef_body = new QWidget(georef_section);
    auto* georef_layout = new QHBoxLayout(georef_body);
    georef_layout->setContentsMargins(0, 0, 0, 0);
    georef_layout->setSpacing(16);
    georef_layout->setAlignment(Qt::AlignTop);
    georef_present_value_ = makeReadOnlyValue(georef_body);
    georef_type_value_ = makeReadOnlyValue(georef_body);
    georef_easting_value_ = makeReadOnlyValue(georef_body);
    georef_northing_value_ = makeReadOnlyValue(georef_body);
    georef_height_value_ = makeReadOnlyValue(georef_body);
    georef_x_axis_abscissa_value_ = makeReadOnlyValue(georef_body);
    georef_x_axis_ordinate_value_ = makeReadOnlyValue(georef_body);
    georef_rotation_dd_value_ = makeReadOnlyValue(georef_body);
    georef_rotation_dms_value_ = makeReadOnlyValue(georef_body);
    georef_scale_value_ = makeReadOnlyValue(georef_body);
    georef_factor_x_value_ = makeReadOnlyValue(georef_body);
    georef_factor_y_value_ = makeReadOnlyValue(georef_body);
    georef_factor_z_value_ = makeReadOnlyValue(georef_body);

    auto* georef_col_1 = new QFormLayout();
    georef_col_1->setContentsMargins(0, 0, 0, 0);
    georef_col_1->setHorizontalSpacing(12);
    georef_col_1->setVerticalSpacing(8);
    georef_col_1->addRow("Georeferenced", georef_present_value_);
    georef_col_1->addRow("Coordinate Operation", georef_type_value_);
    georef_col_1->addRow("Easting", georef_easting_value_);
    georef_col_1->addRow("Northing", georef_northing_value_);
    georef_col_1->addRow("OrthogonalHeight", georef_height_value_);

    auto* georef_col_2 = new QFormLayout();
    georef_col_2->setContentsMargins(0, 0, 0, 0);
    georef_col_2->setHorizontalSpacing(12);
    georef_col_2->setVerticalSpacing(8);
    georef_col_2->addRow("XAxisAbscissa", georef_x_axis_abscissa_value_);
    georef_col_2->addRow("XAxisOrdinate", georef_x_axis_ordinate_value_);
    georef_col_2->addRow("Rotation (DD)", georef_rotation_dd_value_);
    georef_col_2->addRow("Rotation (DMS)", georef_rotation_dms_value_);

    auto* georef_col_3 = new QFormLayout();
    georef_col_3->setContentsMargins(0, 0, 0, 0);
    georef_col_3->setHorizontalSpacing(12);
    georef_col_3->setVerticalSpacing(8);
    georef_col_3->addRow("Scale", georef_scale_value_);
    georef_col_3->addRow("FactorX", georef_factor_x_value_);
    georef_col_3->addRow("FactorY", georef_factor_y_value_);
    georef_col_3->addRow("FactorZ", georef_factor_z_value_);

    auto* georef_col_1_widget = new QWidget(georef_body);
    georef_col_1_widget->setLayout(georef_col_1);
    auto* georef_col_2_widget = new QWidget(georef_body);
    georef_col_2_widget->setLayout(georef_col_2);
    auto* georef_col_3_widget = new QWidget(georef_body);
    georef_col_3_widget->setLayout(georef_col_3);

    georef_layout->addWidget(georef_col_1_widget, 1);
    georef_layout->addWidget(georef_col_2_widget, 1);
    georef_layout->addWidget(georef_col_3_widget, 1);
    georef_section->addBodyWidget(georef_body);

    auto* table_section =
        new components::Section("Model Transformations", components::SectionHeaderMode::Visible, model_tab);
    auto* table_body = new QWidget(table_section);
    auto* table_layout = new QVBoxLayout(table_body);
    table_layout->setContentsMargins(0, 0, 0, 0);
    table_layout->setSpacing(components::style::metrics::padding);

    model_table_ = new QTableWidget(table_body);
    model_table_->setObjectName("modelCoordinatesTable");
    model_table_->setColumnCount(6);
    model_table_->setHorizontalHeaderLabels(
        {"Model", "From", "From Point", "To Point", "Rotate", "Pivot Point"});
    model_table_->verticalHeader()->setVisible(false);
    model_table_->horizontalHeader()->setStretchLastSection(false);
    model_table_->horizontalHeader()->setSectionsMovable(false);
    model_table_->horizontalHeader()->setSectionsClickable(true);
    model_table_->horizontalHeader()->setSectionResizeMode(QHeaderView::Interactive);
    model_table_->horizontalHeader()->resizeSection(0, 180);
    model_table_->horizontalHeader()->resizeSection(1, 150);
    model_table_->horizontalHeader()->resizeSection(2, 180);
    model_table_->horizontalHeader()->resizeSection(3, 180);
    model_table_->horizontalHeader()->resizeSection(4, 180);
    model_table_->horizontalHeader()->resizeSection(5, 180);
    model_table_->setSelectionBehavior(QAbstractItemView::SelectRows);
    model_table_->setSelectionMode(QAbstractItemView::SingleSelection);
    model_table_->setShowGrid(true);
    model_table_->setWordWrap(false);
    model_table_->setEditTriggers(QAbstractItemView::DoubleClicked | QAbstractItemView::EditKeyPressed);
    model_table_->setAlternatingRowColors(false);
    model_table_->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);

    auto* table_hint = new QLabel(
        "This section lets you override model coordinates by specifying an optional translation from a point to "
        "another desired point, and an optional rotation.",
        table_section);
    table_hint->setProperty("textRole", "secondary");
    table_hint->setWordWrap(true);

    table_layout->addWidget(model_table_, 1);
    table_section->addBodyWidget(table_hint);
    table_section->addBodyWidget(table_body);
    model_layout->addWidget(georef_section);
    model_layout->addWidget(table_section);

    addTab("Federation", federation_tab);
    addTab("Model", model_tab);

    connect(model_table_, &QTableWidget::currentCellChanged, this,
            [this](int /*current_row*/, int /*current_column*/, int /*previous_row*/, int /*previous_column*/) {
        updateSelectedModelGeoref();
    });

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

    addFooterWidget(buttons);
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

void SettingsDialog::populateModelTable() {
    model_rows_.clear();
    const QSignalBlocker blocker(model_table_);
    model_table_->clearContents();
    model_table_->setRowCount(0);
    if (!federation_) return;

    int row = 0;
    for (const auto& model : federation_->models()) {
        const auto& xf = model.model_transformation;
        model_table_->insertRow(row);

        auto* model_item = new QTableWidgetItem(model.display_name.isEmpty() ? model.id : model.display_name);
        model_item->setData(Qt::UserRole, model.id);
        model_table_->setItem(row, 0, model_item);

        ModelRowWidgets widgets;
        widgets.fed_id = model.id;

        widgets.frame = new QComboBox(model_table_);
        widgets.frame->addItem("Local", static_cast<int>(AFrame::ModelLocal));
        widgets.frame->addItem("Global", static_cast<int>(AFrame::ModelGlobal));
        widgets.frame->setCurrentIndex(xf.a_frame == AFrame::ModelGlobal ? 1 : 0);
        model_table_->setCellWidget(row, 1, widgets.frame);

        widgets.from_point = new QTableWidgetItem(formatVector3(xf.a));
        widgets.to_point = new QTableWidgetItem(formatVector3(xf.b));
        widgets.rotate = new QTableWidgetItem(formatVector3(xf.rxyz_deg));
        widgets.pivot = new QTableWidgetItem(formatVector3(xf.pivot));
        model_table_->setItem(row, 2, widgets.from_point);
        model_table_->setItem(row, 3, widgets.to_point);
        model_table_->setItem(row, 4, widgets.rotate);
        model_table_->setItem(row, 5, widgets.pivot);

        model_rows_.push_back(widgets);
        model_table_->setRowHeight(row, 42);
        ++row;
    }

    int table_height = model_table_->frameWidth() * 2 + model_table_->horizontalHeader()->height();
    for (int i = 0; i < model_table_->rowCount(); ++i) {
        table_height += model_table_->rowHeight(i);
    }
    if (model_table_->horizontalScrollBar()->isVisible()) {
        table_height += model_table_->horizontalScrollBar()->sizeHint().height();
    }
    model_table_->setMinimumHeight(table_height);
    model_table_->setMaximumHeight(table_height);

    if (model_table_->rowCount() > 0) {
        model_table_->setCurrentCell(0, 0);
    }
    updateSelectedModelGeoref();
}

void SettingsDialog::updateSelectedModelGeoref() {
    auto set_unknown = [this](const QString& georef, const QString& type) {
        georef_present_value_->setText(georef);
        georef_type_value_->setText(type);
        georef_easting_value_->setText("—");
        georef_northing_value_->setText("—");
        georef_height_value_->setText("—");
        georef_x_axis_abscissa_value_->setText("—");
        georef_x_axis_ordinate_value_->setText("—");
        georef_rotation_dd_value_->setText("—");
        georef_rotation_dms_value_->setText("—");
        georef_scale_value_->setText("—");
        georef_factor_x_value_->setText("—");
        georef_factor_y_value_->setText("—");
        georef_factor_z_value_->setText("—");
    };

    const int row = model_table_->currentRow();
    if (row < 0 || row >= static_cast<int>(model_rows_.size())) {
        set_unknown("No model selected", "—");
        return;
    }

    const QString& fed_id = model_rows_[row].fed_id;
    if (!session_state_) {
        set_unknown("Unavailable", "No session state");
        return;
    }

    const uint32_t mid = session_state_->modelIdForFedId(fed_id);
    if (mid == 0 || !loader_) {
        set_unknown("Not loaded", "No live model");
        return;
    }

    const ModelGeoref* georef = loader_->modelGeoref(mid);
    if (!georef) {
        set_unknown("Not available yet", "No data source");
        return;
    }

    if (!georef->has_coordinate_operation) {
        set_unknown("No", "None");
        return;
    }

    const Eigen::Matrix4d& m = georef->coordinate_operation_meters;
    const Eigen::Vector3d translation = m.block<3, 1>(0, 3);
    const Eigen::Vector3d x_axis = m.block<3, 1>(0, 0);
    const Eigen::Vector3d y_axis = m.block<3, 1>(0, 1);
    const double factor_x = x_axis.norm();
    const double factor_y = y_axis.norm();
    const double factor_z = m.block<3, 1>(0, 2).norm();
    const double scale = (factor_x + factor_y) * 0.5;
    const double x_axis_abscissa = factor_x > 0.0 ? x_axis.x() / factor_x : 1.0;
    const double x_axis_ordinate = factor_x > 0.0 ? x_axis.y() / factor_x : 0.0;
    constexpr double kRadiansToDegrees = 57.29577951308232;
    const double rotation_dd = std::atan2(x_axis_ordinate, x_axis_abscissa) * kRadiansToDegrees;

    georef_present_value_->setText("Yes");
    georef_type_value_->setText("IfcMapConversion");
    georef_easting_value_->setText(formatNumber(translation.x()));
    georef_northing_value_->setText(formatNumber(translation.y()));
    georef_height_value_->setText(formatNumber(translation.z()));
    georef_x_axis_abscissa_value_->setText(formatNumber(x_axis_abscissa));
    georef_x_axis_ordinate_value_->setText(formatNumber(x_axis_ordinate));
    georef_rotation_dd_value_->setText(formatNumber(rotation_dd));
    georef_rotation_dms_value_->setText(formatAngleDms(rotation_dd));
    georef_scale_value_->setText(formatNumber(scale));
    georef_factor_x_value_->setText(formatNumber(factor_x));
    georef_factor_y_value_->setText(formatNumber(factor_y));
    georef_factor_z_value_->setText(formatNumber(factor_z));
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

        for (const auto& row : model_rows_) {
            ModelTransformation xf;
            xf.a_frame = static_cast<AFrame>(row.frame->currentData().toInt());
            xf.a = parseVector3(row.from_point->text());
            xf.b = parseVector3(row.to_point->text());
            xf.rxyz_deg = parseVector3(row.rotate->text());
            xf.pivot = parseVector3(row.pivot->text());
            federation_->setModelTransformation(row.fed_id, xf);
        }
    }
    accept();
}

} // namespace ifcinterface::modules::models
