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

#ifndef IFCINTERFACE_COMPONENTS_DIALOG_H
#define IFCINTERFACE_COMPONENTS_DIALOG_H

#include <QDialog>

class QVBoxLayout;
class QWidget;
class QTabWidget;

namespace ifcviewerfull::components {

class Dialog : public QDialog {
    Q_OBJECT

public:
    explicit Dialog(QWidget* parent = nullptr,
                    bool scrollable = false);

    void addBodyWidget(QWidget* widget);
    void addFooterWidget(QWidget* widget);

private:
    QVBoxLayout* body_layout_ = nullptr;
    QVBoxLayout* footer_layout_ = nullptr;
};

class TabbedDialog : public QDialog {
    Q_OBJECT

public:
    explicit TabbedDialog(QWidget* parent = nullptr);

    void addTab(const QString& title, QWidget* widget);
    void addFooterWidget(QWidget* widget);

private:
    QTabWidget* tabs_ = nullptr;
    QVBoxLayout* footer_layout_ = nullptr;
};

} // namespace ifcviewerfull::components

#endif
