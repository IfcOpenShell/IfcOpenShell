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

#ifndef IFCINTERFACE_COMPONENTS_SECTION_H
#define IFCINTERFACE_COMPONENTS_SECTION_H

#include <QWidget>

class QHBoxLayout;
class QToolButton;
class QVBoxLayout;

namespace ifcinterface::components {

enum class SectionHeaderMode {
    Visible,
    Hidden,
};

class Section : public QWidget {
    Q_OBJECT
public:
    explicit Section(const QString& title,
                     SectionHeaderMode header_mode = SectionHeaderMode::Visible,
                     QWidget* parent = nullptr);

    void addBodyWidget(QWidget* widget);
    void clearBody();
    void addHeaderWidget(QWidget* widget);
    bool isExpanded() const;
    void setExpanded(bool expanded);

private:
    QWidget* body_ = nullptr;
    QVBoxLayout* body_layout_ = nullptr;
    QHBoxLayout* header_layout_ = nullptr;
    QToolButton* toggle_button_ = nullptr;
};

} // namespace ifcinterface::components

#endif
