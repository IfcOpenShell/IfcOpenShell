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

#include "PanelChrome.h"

#include "SvgIcon.h"

#include <QDockWidget>
#include <QFrame>
#include <QHBoxLayout>
#include <QLabel>
#include <QMenu>
#include <QToolButton>
#include <QVBoxLayout>

namespace ifcinterface::components::panel {

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
        text->setObjectName("dockTitleText");

        layout->addWidget(text);
        layout->addStretch(1);
        if (has_settings) {
            auto* settings = new QToolButton(this);
            settings->setIcon(icons::makePanelSvgIcon(":/icons/settings.svg"));
            settings->setAutoRaise(true);
            settings->setCursor(Qt::ArrowCursor);
            settings->setFixedSize(18, 18);
            settings->setObjectName("dockTitleButton");
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

QDockWidget* makeDock(const QString& title, QWidget* content, QWidget* parent, bool has_settings) {
    auto* dock = new QDockWidget(title, parent);
    dock->setObjectName(title);
    dock->setFeatures(QDockWidget::DockWidgetMovable |
                      QDockWidget::DockWidgetFloatable |
                      QDockWidget::DockWidgetClosable);
    dock->setTitleBarWidget(new DockTitleBar(title, has_settings, dock));
    dock->setWidget(content);
    return dock;
}

QFrame* wrapPanel(QWidget* inner) {
    auto* outer = new QFrame();
    auto* outer_layout = new QVBoxLayout(outer);
    outer_layout->setContentsMargins(6, 6, 6, 6);
    outer_layout->setSpacing(0);

    auto* frame = new QFrame(outer);
    frame->setObjectName("panelFrame");
    auto* layout = new QVBoxLayout(frame);
    layout->setContentsMargins(0, 8, 0, 8);
    layout->setSpacing(0);
    layout->addWidget(inner);

    outer_layout->addWidget(frame);
    return outer;
}

} // namespace ifcinterface::components::panel
