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

#ifndef MODELTRANSFORMATIONDIALOG_H
#define MODELTRANSFORMATIONDIALOG_H

#include <QDialog>
#include <QString>

QT_BEGIN_NAMESPACE
class QComboBox;
class QDoubleSpinBox;
class QLabel;
class QRadioButton;
QT_END_NAMESPACE

class Federation;

// Edits one model's ModelTransformation (the per-model placement within
// the federation: a_frame, a, b, rxyz Euler degrees, pivot).  A combobox
// at the top picks which model to edit.  Switching models discards any
// unsaved form edits — Ok saves the currently-visible model.  On Ok,
// calls Federation::setModelTransformation, which fires
// modelTransformationChanged → MainWindow recomposes the viewport for
// that model.
class ModelTransformationDialog : public QDialog {
    Q_OBJECT
public:
    explicit ModelTransformationDialog(Federation* federation, QWidget* parent = nullptr);

protected:
    void showEvent(QShowEvent* event) override;

private slots:
    void onModelChanged(int idx);
    void onAFrameToggled();
    void onAccepted();

private:
    void setupUi();
    void populateModelCombo();
    void syncFromModel(const QString& fed_id);
    void refreshUnitLabels();

    Federation* federation_ = nullptr;

    QComboBox*    model_combo_ = nullptr;

    QRadioButton* radio_local_  = nullptr;
    QRadioButton* radio_global_ = nullptr;

    QDoubleSpinBox* a_x_ = nullptr;
    QDoubleSpinBox* a_y_ = nullptr;
    QDoubleSpinBox* a_z_ = nullptr;
    QLabel*         a_unit_label_ = nullptr;

    QDoubleSpinBox* b_x_ = nullptr;
    QDoubleSpinBox* b_y_ = nullptr;
    QDoubleSpinBox* b_z_ = nullptr;
    QLabel*         b_unit_label_ = nullptr;

    QDoubleSpinBox* rx_ = nullptr;
    QDoubleSpinBox* ry_ = nullptr;
    QDoubleSpinBox* rz_ = nullptr;

    QDoubleSpinBox* pivot_x_ = nullptr;
    QDoubleSpinBox* pivot_y_ = nullptr;
    QDoubleSpinBox* pivot_z_ = nullptr;
    QLabel*         pivot_unit_label_ = nullptr;
};

#endif
