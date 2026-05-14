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

#include "AddModelDialog.h"

#include "../../components/Dialog.h"
#include "../../components/Buttons.h"
#include "../../components/Section.h"
#include "../../components/Style.h"

#include <QEvent>
#include <QHBoxLayout>
#include <QLabel>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcviewerfull::modules::models {

namespace {

class HoverDescriptionFilter : public QObject {
public:
    HoverDescriptionFilter(QLabel* label, QString hover_text, QString default_text)
        : label_(label), hover_text_(std::move(hover_text)), default_text_(std::move(default_text)) {}

protected:
    bool eventFilter(QObject* watched, QEvent* event) override {
        Q_UNUSED(watched);
        if (event->type() == QEvent::Enter) {
            label_->setText(hover_text_);
        } else if (event->type() == QEvent::Leave) {
            label_->setText(default_text_);
        }
        return false;
    }

private:
    QLabel* label_ = nullptr;
    QString hover_text_;
    QString default_text_;
};

} // namespace

AddModelDialog::AddModelDialog(QWidget* parent)
    : components::Dialog(parent)
{
    setObjectName("appDialog");
    setWindowTitle("Add Model");
    setModal(true);
    setupUi();
}

void AddModelDialog::setupUi() {
    if (auto* root = qobject_cast<QVBoxLayout*>(layout())) {
        root->setSizeConstraint(QLayout::SetFixedSize);
    }

    const QString default_description = "Choose what to add to the project";
    auto* description_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    auto* description = new QLabel(default_description, description_section);
    description->setProperty("textRole", "secondary");
    description->setWordWrap(true);
    description->setAlignment(Qt::AlignCenter);
    description->setMinimumWidth((90 * 4) + (components::style::metrics::padding * 3));
    description->setMinimumHeight(description->fontMetrics().lineSpacing() * 2 + 4);
    description_section->addBodyWidget(description);

    auto* choices_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    auto* choices = new QWidget(choices_section);
    auto* row = new QHBoxLayout(choices);
    row->setContentsMargins(0, 0, 0, 0);
    row->setSpacing(components::style::metrics::padding);

    auto* add_ifc = components::buttons::makeButton("Add IFC File", ":/icons/cube.svg", choices);
    connect(add_ifc, &QToolButton::clicked, this, [this]() {
        selected_mode_ = SourceMode::IfcFile;
        accept();
    });
    add_ifc->installEventFilter(new HoverDescriptionFilter(
        description,
        "Add IFC files and load both geometry and data.",
        default_description));

    auto* add_database = components::buttons::makeButton("Add IFC\nDatabase", ":/icons/database.svg", choices);
    connect(add_database, &QToolButton::clicked, this, [this]() {
        selected_mode_ = SourceMode::IfcDatabase;
        accept();
    });
    add_database->installEventFilter(new HoverDescriptionFilter(
        description,
        "Add IFC RDB databases for optimised performance",
        default_description));

    auto* add_geometry = components::buttons::makeButton("Add Geometry", ":/icons/cube-bandage.svg", choices);
    connect(add_geometry, &QToolButton::clicked, this, [this]() {
        selected_mode_ = SourceMode::GeometryOnly;
        accept();
    });
    add_geometry->installEventFilter(new HoverDescriptionFilter(
        description,
        "Add pure geometry for fast visualisation",
        default_description));

    auto* convert_database = components::buttons::makeButton("Convert IFC File\nto Database", ":/icons/database-restore.svg", choices);
    connect(convert_database, &QToolButton::clicked, this, [this]() {
        selected_mode_ = SourceMode::ConvertToDatabase;
        accept();
    });
    convert_database->installEventFilter(new HoverDescriptionFilter(
        description,
        "Convert IFC files to databases for smaller filesizes, reduced memory, and faster access. No data is lost.",
        default_description));

    row->addWidget(components::buttons::makeButtonGroup("ADD", {add_ifc, add_database, add_geometry}, choices, true, 8));
    row->addWidget(components::buttons::makeButtonGroup("TOOLS", {convert_database}, choices, false, 8));
    choices_section->addBodyWidget(choices);

    addBodyWidget(description_section);
    addBodyWidget(choices_section);
}

} // namespace ifcviewerfull::modules::models
