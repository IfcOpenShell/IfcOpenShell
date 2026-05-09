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

    load_data_source_checkbox_ = new QCheckBox(loading_body);
    load_data_source_checkbox_->setToolTip(
        "Keep the .ifc/.rdb open after loading so element properties can be queried. "
        "Disable for geometry-only viewing.");
    loading_form->addRow("Load Property Data Source", load_data_source_checkbox_);

    apply_coordinate_operation_check_ = new QCheckBox(loading_body);
    apply_coordinate_operation_check_->setToolTip(
        "Apply each model's IfcCoordinateOperation after load so it lands in "
        "georeferenced map coordinates.");
    loading_form->addRow("Apply Coordinate Operation", apply_coordinate_operation_check_);

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

    auto* description = new QLabel(
        "These settings are shared with the viewer backend and persist via QSettings.",
        loading_body);
    description->setProperty("textRole", "secondary");
    description->setWordWrap(true);
    loading_form->addRow(QString(), description);

    loading_section->addBodyWidget(loading_body);
    graphics_layout->addWidget(general_section);
    graphics_layout->addWidget(loading_section);
    graphics_layout->addStretch(1);

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

    tabs->addTab(make_placeholder_tab("Navigation", "Navigation preferences and interaction modes will live here."),
                 "Navigation");
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

    auto* actions_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    actions_section->addBodyWidget(buttons);

    addBodyWidget(tabs);
    addBodyWidget(actions_section);
}

void SettingsDialog::syncFromSettings() {
    geometry_library_edit_->setText(AppSettings::instance().geometryLibrary());
    show_stats_check_->setChecked(AppSettings::instance().showStats());
    backface_culling_check_->setChecked(AppSettings::instance().backfaceCulling());
    load_data_source_checkbox_->setChecked(AppSettings::instance().loadDataSource());
    apply_coordinate_operation_check_->setChecked(AppSettings::instance().applyCoordinateOperation());
    void_limit_spin_->setValue(AppSettings::instance().voidLimit());
    deflection_tolerance_spin_->setValue(AppSettings::instance().deflectionTolerance());
    angular_tolerance_spin_->setValue(AppSettings::instance().angularTolerance());
}

void SettingsDialog::onAccepted() {
    AppSettings::instance().setGeometryLibrary(geometry_library_edit_->text());
    AppSettings::instance().setShowStats(show_stats_check_->isChecked());
    AppSettings::instance().setBackfaceCulling(backface_culling_check_->isChecked());
    AppSettings::instance().setLoadDataSource(load_data_source_checkbox_->isChecked());
    AppSettings::instance().setApplyCoordinateOperation(apply_coordinate_operation_check_->isChecked());
    AppSettings::instance().setVoidLimit(void_limit_spin_->value());
    AppSettings::instance().setDeflectionTolerance(deflection_tolerance_spin_->value());
    AppSettings::instance().setAngularTolerance(angular_tolerance_spin_->value());
    accept();
}

} // namespace ifcinterface::modules::settings
