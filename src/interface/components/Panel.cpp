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

#include "Panel.h"

#include "Style.h"
#include "SvgIcon.h"

#include <QDockWidget>
#include <QFrame>
#include <QHBoxLayout>
#include <QLabel>
#include <QMenu>
#include <QScrollArea>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcinterface::components {

namespace {

class DockTitleBar : public QWidget {
public:
    explicit DockTitleBar(const QString& title, bool has_settings = false, QWidget* parent = nullptr)
        : QWidget(parent)
    {
        auto* layout = new QHBoxLayout(this);
        layout->setContentsMargins(10, 6, 6, 6);
        layout->setSpacing(6);

        auto* text = new QLabel(title.toUpper(), this);
        text->setObjectName("panelTitleText");

        layout->addWidget(text);
        layout->addStretch(1);
        if (has_settings) {
            auto* settings = new QToolButton(this);
            settings->setIcon(icons::makeSvgIcon(":/icons/settings.svg"));
            settings->setAutoRaise(true);
            settings->setCursor(Qt::ArrowCursor);
            settings->setFixedSize(18, 18);
            settings->setObjectName("panelTitleButton");
            settings->setToolTip(QString("%1 settings").arg(title));
            connect(settings, &QToolButton::clicked, this, [this, title]() {
                auto* anchor = parentWidget();
                QMenu menu(anchor);
                menu.addAction(QString("%1 settings coming soon").arg(title));
                menu.exec(QCursor::pos());
            });
            layout->addWidget(settings);
        }
    }
};

} // namespace

Panel::Panel(const QString& title, QWidget* content, QWidget* parent, bool has_settings, bool scrollable)
    : QDockWidget(title, parent)
{
    auto* outer = new QFrame();
    auto* outer_layout = new QVBoxLayout(outer);
    outer_layout->setContentsMargins(style::metrics::padding,
                                     style::metrics::padding,
                                     style::metrics::padding,
                                     style::metrics::padding);
    outer_layout->setSpacing(0);

    auto* frame = new QFrame(outer);
    frame->setObjectName("panel");
    auto* frame_layout = new QVBoxLayout(frame);
    frame_layout->setContentsMargins(0, style::metrics::section_body_padding, 0, style::metrics::section_body_padding);
    frame_layout->setSpacing(0);

    if (scrollable) {
        auto* scroll = new QScrollArea(frame);
        scroll->setWidgetResizable(true);
        scroll->setFrameShape(QFrame::NoFrame);

        auto* scroll_body = new QWidget(scroll);
        scroll_body->setObjectName("panelScrollBody");
        auto* scroll_body_layout = new QVBoxLayout(scroll_body);
        scroll_body_layout->setContentsMargins(0, 0, 0, 0);
        scroll_body_layout->setSpacing(0);
        scroll_body_layout->addWidget(content);

        scroll->setWidget(scroll_body);
        frame_layout->addWidget(scroll);
    } else {
        frame_layout->addWidget(content);
    }
    outer_layout->addWidget(frame);

    setObjectName(title);
    setFeatures(QDockWidget::DockWidgetMovable |
                QDockWidget::DockWidgetFloatable |
                QDockWidget::DockWidgetClosable);
    setTitleBarWidget(new DockTitleBar(title, has_settings, this));
    setWidget(outer);
}

} // namespace ifcinterface::components
