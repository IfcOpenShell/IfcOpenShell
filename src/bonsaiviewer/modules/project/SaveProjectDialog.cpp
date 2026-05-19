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

#include "SaveProjectDialog.h"

#include "../../components/Buttons.h"
#include "../../components/Section.h"
#include "../../components/Style.h"

#include <QEvent>
#include <QHBoxLayout>
#include <QLabel>
#include <QToolButton>
#include <QVBoxLayout>

namespace bonsaiviewer::modules::project {

namespace {

class HoverDescriptionFilter : public QObject {
public:
    HoverDescriptionFilter(QLabel* label, QString hover_text, QString default_text)
        : label_(label), hover_text_(std::move(hover_text)), default_text_(std::move(default_text)) {}

protected:
    bool eventFilter(QObject*, QEvent* event) override {
        if (event->type() == QEvent::Enter) label_->setText(hover_text_);
        else if (event->type() == QEvent::Leave) label_->setText(default_text_);
        return false;
    }

private:
    QLabel* label_ = nullptr;
    QString hover_text_;
    QString default_text_;
};

} // namespace

SaveProjectDialog::SaveProjectDialog(bool has_manifest, QWidget* parent)
    : components::Dialog(parent)
{
    setObjectName("appDialog");
    setWindowTitle("Save Project");
    setModal(true);
    setupUi(has_manifest);
}

void SaveProjectDialog::setupUi(bool has_manifest) {
    if (auto* root = qobject_cast<QVBoxLayout*>(layout())) {
        root->setSizeConstraint(QLayout::SetFixedSize);
    }

    const QString default_description = "Choose where to save this project";
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

    auto* save_local = components::buttons::makeButton(
        "Save Local", ":/icons/floppy-disk.svg", choices);
    connect(save_local, &QToolButton::clicked, this, [this]() {
        selected_target_ = SaveTarget::Local;
        accept();
    });
    save_local->installEventFilter(new HoverDescriptionFilter(
        description,
        "Save to the project's current file on disk (prompts for a path if none).",
        default_description));

    auto* save_as_local = components::buttons::makeButton(
        "Save As\nLocal", ":/icons/floppy-disk-arrow-in.svg", choices);
    connect(save_as_local, &QToolButton::clicked, this, [this]() {
        selected_target_ = SaveTarget::LocalAs;
        accept();
    });
    save_as_local->installEventFilter(new HoverDescriptionFilter(
        description,
        "Save the project to a new file on disk.",
        default_description));

    auto* save_cloud = components::buttons::makeButton(
        "Save To\nCloud", ":/icons/cloud-square.svg", choices);
    save_cloud->setEnabled(has_manifest);
    if (!has_manifest) {
        save_cloud->setToolTip(
            "This project has no cloud target yet. Use \"Save As To Cloud\" first.");
    }
    connect(save_cloud, &QToolButton::clicked, this, [this]() {
        selected_target_ = SaveTarget::Cloud;
        accept();
    });
    save_cloud->installEventFilter(new HoverDescriptionFilter(
        description,
        has_manifest
            ? "Push back to the cloud location this project came from."
            : "Disabled until this project has a cloud target (use Save As To Cloud).",
        default_description));

    auto* save_as_cloud = components::buttons::makeButton(
        "Save As\nTo Cloud", ":/icons/cloud-square.svg", choices);
    connect(save_as_cloud, &QToolButton::clicked, this, [this]() {
        selected_target_ = SaveTarget::CloudAs;
        accept();
    });
    save_as_cloud->installEventFilter(new HoverDescriptionFilter(
        description,
        "Pick a connector and push this project to a fresh cloud location.",
        default_description));

    row->addWidget(components::buttons::makeButtonGroup(
        "LOCAL", {save_local, save_as_local}, choices, true, 8));
    row->addWidget(components::buttons::makeButtonGroup(
        "CLOUD", {save_cloud, save_as_cloud}, choices, false, 8));
    choices_section->addBodyWidget(choices);

    addBodyWidget(description_section);
    addBodyWidget(choices_section);
}

} // namespace bonsaiviewer::modules::project
