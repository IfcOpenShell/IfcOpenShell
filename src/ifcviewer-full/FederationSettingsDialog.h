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

#ifndef FEDERATIONSETTINGSDIALOG_H
#define FEDERATIONSETTINGSDIALOG_H

#include <QDialog>

QT_BEGIN_NAMESPACE
class QComboBox;
class QDoubleSpinBox;
QT_END_NAMESPACE

class Federation;

// Edits federation-wide state: the display unit (used to interpret all
// FederatedFalseOrigin / ModelTransformation numeric inputs) and the
// FederatedFalseOrigin (XYZ + Z-axis rotation in that unit).  On Ok,
// calls Federation::setConfig + setFederatedFalseOrigin, which fire the
// granular Federation signals and trigger the viewport to recompose.
class FederationSettingsDialog : public QDialog {
    Q_OBJECT
public:
    explicit FederationSettingsDialog(Federation* federation, QWidget* parent = nullptr);

protected:
    void showEvent(QShowEvent* event) override;

private:
    void setupUi();
    void syncFromFederation();
    void onAccepted();

    Federation* federation_ = nullptr;

    // The combobox encodes (prefix, name) pairs in user data; common length
    // units are listed.  itemData(idx) returns a QStringList { prefix, name }.
    QComboBox*       unit_combo_ = nullptr;
    QDoubleSpinBox*  xyz_x_      = nullptr;
    QDoubleSpinBox*  xyz_y_      = nullptr;
    QDoubleSpinBox*  xyz_z_      = nullptr;
    QDoubleSpinBox*  rz_deg_     = nullptr;
};

#endif
