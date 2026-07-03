// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
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

namespace bonsaiviewer::modules::models {

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
    description_section->addBodyWidget(description);

    auto* choices_section = new components::Section("", components::SectionHeaderMode::Hidden, this);
    auto* choices = new QWidget(choices_section);
    auto* row = new QHBoxLayout(choices);
    row->setContentsMargins(0, 0, 0, 0);
    row->setSpacing(components::style::metrics::padding);

    struct Choice {
        SourceMode mode;
        QString text;
        QString icon;
        QString hover;
    };
    const QList<Choice> local_choices = {
        {SourceMode::IfcFile, "Add IFC File", ":/icons/cube.svg",
         "Add IFC files and load both geometry and data."},
        {SourceMode::IfcDatabase, "Add IFC\nDatabase", ":/icons/database.svg",
         "Add IFC RDB databases for optimised performance"},
        {SourceMode::GeometryOnly, "Add Geometry", ":/icons/cube-bandage.svg",
         "Add pure geometry for fast visualisation"},
    };
    const QList<Choice> cloud_choices = {
        {SourceMode::CloudModel, "Add From\nCloud", ":/icons/cloud-square.svg",
         "Browse a cloud connector and add one or more models from there."},
    };
    const QList<Choice> tool_choices = {
        {SourceMode::ConvertToDatabase, "Convert IFC File\nto Database", ":/icons/database-restore.svg",
         "Convert IFC files to databases for smaller filesizes, reduced memory, "
         "and faster access. No data is lost."},
        {SourceMode::ExportGeometryDatabase, "Export Geometry\nDatabase", ":/icons/database-restore.svg",
         "Convert IFC files to a read-only geometry database for smaller filesizes, "
         "reduced memory, and faster access. Ideal for cloud read-only coordination "
         "workflows. Only parametric geometry editing capabilities are lost."},
    };

    QStringList descriptions = {default_description};
    auto build_group = [&](const QString& title, const QList<Choice>& group_choices) {
        QList<QToolButton*> buttons;
        for (const Choice& choice : group_choices) {
            auto* button = components::buttons::makeButton(choice.text, choice.icon, choices);
            const SourceMode mode = choice.mode;
            connect(button, &QToolButton::clicked, this, [this, mode]() {
                selected_mode_ = mode;
                accept();
            });
            button->installEventFilter(
                new HoverDescriptionFilter(description, choice.hover, default_description));
            descriptions << choice.hover;
            buttons << button;
        }
        return components::buttons::makeButtonGroup(title, buttons, choices, 8);
    };

    components::buttons::addButtonGroups(row, {
        build_group("LOCAL", local_choices),
        build_group("CLOUD", cloud_choices),
        build_group("TOOLS", tool_choices),
    });
    choices_section->addBodyWidget(choices);

    // Hovering a button swaps in a longer description; with a free-growing
    // label that reflow shoves the buttons below it downward. Lock the label
    // to the tallest string it will ever show. The label is laid out at the
    // choices' width (both sit in Section bodies with identical margins), so
    // measure every string at that width and keep the largest result.
    const int label_width = choices->sizeHint().width();
    int reserved_height = 0;
    for (const QString& text : descriptions) {
        description->setText(text);
        reserved_height = qMax(reserved_height, description->heightForWidth(label_width));
    }
    description->setText(default_description);
    description->setFixedHeight(reserved_height);

    addBodyWidget(description_section);
    addBodyWidget(choices_section);
}

} // namespace bonsaiviewer::modules::models
