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
#include <QFormLayout>
#include <QLineEdit>
#include <QShowEvent>
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
}

void SettingsWindow::onAccepted() {
    AppSettings::instance().setGeometryLibrary(geometry_library_edit_->text());
    AppSettings::instance().setShowStats(show_stats_check_->isChecked());
    accept();
}
