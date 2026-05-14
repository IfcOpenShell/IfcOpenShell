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

#include "../../../ifcviewer/ViewportWindow.h"

#include <QFrame>
#include <QVBoxLayout>
#include <QWidget>

namespace ifcviewerfull::modules::viewport {

ViewportPanel::ViewportPanel(QWidget* parent)
    : QWidget(parent)
{
    auto* root = new QVBoxLayout(this);
    root->setContentsMargins(0, 0, 0, 0);
    root->setSpacing(0);

    auto* shell = new QFrame(this);
    shell->setObjectName("viewportShell");
    auto* shell_layout = new QVBoxLayout(shell);
    shell_layout->setContentsMargins(10, 10, 10, 10);
    shell_layout->setSpacing(0);

    auto* frame = new QFrame(shell);
    frame->setObjectName("viewportFrame");
    auto* frame_layout = new QVBoxLayout(frame);
    frame_layout->setContentsMargins(0, 0, 0, 0);
    frame_layout->setSpacing(0);

    viewport_ = new ViewportWindow();
    viewport_container_ = QWidget::createWindowContainer(viewport_, frame);
    viewport_container_->setMinimumSize(400, 300);
    viewport_container_->setFocusPolicy(Qt::StrongFocus);

    frame_layout->addWidget(viewport_container_);
    shell_layout->addWidget(frame);
    root->addWidget(shell);
}

} // namespace ifcviewerfull::modules::viewport
