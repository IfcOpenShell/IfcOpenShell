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

#include "Commands.h"

#include "DisplayState.h"

#include "../../SessionState.h"
#include "../../../ifcviewer/ViewportWindow.h"

#include <QColorDialog>
#include <QDialog>
#include <QDialogButtonBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QList>
#include <QMessageBox>
#include <QObject>
#include <QPainter>
#include <QPainterPath>
#include <QPushButton>
#include <QRadioButton>
#include <QVBoxLayout>

#include <functional>

namespace bonsaiviewer::modules::display::commands {

namespace {

std::vector<uint32_t> selectionIds(ViewportWindow& viewport) {
    return {viewport.selection().selectionIds().begin(),
            viewport.selection().selectionIds().end()};
}

} // namespace

// ---- Section -------------------------------------------------------------------

void activateCutPlaneTool(SessionState& session, ViewportWindow& viewport) {
    // One plane per activation (SPEC: after a cut is created the cursor
    // returns to its initial selection shape and function).
    viewport.setSectionToolSingleShot(true);
    if (!viewport.sectionToolActive()) viewport.toggleSectionTool();
    session.setStatusMessage("Section", "Click a surface to place the section plane");
}

void removeAllCutPlanes(SessionState& session, ViewportWindow& viewport) {
    viewport.clearSectionPlanes();
    session.setStatusMessage("Section", "Section planes removed");
}

void setCutPlanesVisible(SessionState& session, ViewportWindow& viewport, bool visible) {
    viewport.setSectionGizmosVisible(visible);
    session.setStatusMessage("Section", visible ? "Section planes shown"
                                                : "Section planes hidden");
}

void setCutSuspension(SessionState& session, ViewportWindow& viewport, bool suspended) {
    viewport.setSectionCutsEnabled(!suspended);
    session.setStatusMessage("Section", suspended ? "Sections suspended"
                                                  : "Sections reactivated");
}

// ---- Colour ----------------------------------------------------------------------

void paintSelectionWithDialog(SessionState& session, ViewportWindow& viewport,
                              DisplayState& display_state, QWidget* parent) {
    const std::vector<uint32_t> ids = selectionIds(viewport);
    if (ids.empty()) {
        session.setStatusMessage("Color", "No element selected");
        return;
    }
    const QColor color = QColorDialog::getColor(Qt::white, parent, "Choose a color");
    if (!color.isValid()) return;
    display_state.applyColor(ids, color, viewport);
    session.setStatusMessage("Color",
        QString("%1 element(s) painted").arg(ids.size()));
}

void applyTransparencyWithDialog(SessionState& session, ViewportWindow& viewport,
                                 DisplayState& display_state, QWidget* parent) {
    const std::vector<uint32_t> ids = selectionIds(viewport);
    if (ids.empty()) {
        session.setStatusMessage("Color", "No element selected");
        return;
    }

    QDialog dialog(parent);
    dialog.setWindowTitle("Transparency of selected elements");
    auto* layout = new QVBoxLayout(&dialog);

    auto* presets_label = new QLabel("Opacity:", &dialog);
    layout->addWidget(presets_label);

    auto* presets_row = new QHBoxLayout();
    QList<QRadioButton*> buttons;
    const QList<int> percents = {100, 75, 50, 25};
    for (int percent : percents) {
        auto* button = new QRadioButton(QString("%1 %").arg(percent), &dialog);
        if (percent == 50) button->setChecked(true);
        presets_row->addWidget(button);
        buttons.append(button);
    }
    layout->addLayout(presets_row);

    auto* box = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, &dialog);
    QObject::connect(box, &QDialogButtonBox::accepted, &dialog, &QDialog::accept);
    QObject::connect(box, &QDialogButtonBox::rejected, &dialog, &QDialog::reject);
    layout->addWidget(box);

    if (dialog.exec() != QDialog::Accepted) return;

    int opacity = 100;
    for (int i = 0; i < buttons.size(); ++i) {
        if (buttons[i]->isChecked()) {
            opacity = percents[i];
            break;
        }
    }
    display_state.applyOpacity(ids, opacity, viewport);
    session.setStatusMessage("Color",
        QString("%1 element(s) at %2% opacity").arg(ids.size()).arg(opacity));
}

void resetSelectionColor(SessionState& session, ViewportWindow& viewport,
                         DisplayState& display_state) {
    const std::vector<uint32_t> ids = selectionIds(viewport);
    if (ids.empty()) {
        session.setStatusMessage("Color", "No element selected");
        return;
    }
    display_state.resetColor(ids, viewport);
    session.setStatusMessage("Color",
        QString("%1 element(s) restored to original color").arg(ids.size()));
}

// ---- Box -----------------------------------------------------------------------

void boxFromSelection(SessionState& session, ViewportWindow& viewport,
                      DisplayState& display_state) {
    display_state.replaceBoxWithSelection(viewport);
    session.setStatusMessage("Box",
        QString("%1 object(s) in the current box")
            .arg(display_state.currentBox().size()));
}

void boxAddSelection(SessionState& session, ViewportWindow& viewport,
                     DisplayState& display_state) {
    display_state.addSelectionToBox(viewport);
    session.setStatusMessage("Box",
        QString("%1 object(s) in the current box")
            .arg(display_state.currentBox().size()));
}

void boxRemoveSelection(SessionState& session, ViewportWindow& viewport,
                        DisplayState& display_state) {
    display_state.removeSelectionFromBox(viewport);
    session.setStatusMessage("Box",
        QString("%1 object(s) in the current box")
            .arg(display_state.currentBox().size()));
}

void isolateCurrentBox(SessionState& session, ViewportWindow& viewport,
                       DisplayState& display_state) {
    const std::vector<uint32_t> ids(display_state.currentBox().begin(),
                                    display_state.currentBox().end());
    if (ids.empty()) {
        session.setStatusMessage("Box", "The current box is empty");
        return;
    }
    isolateObjects(viewport, display_state, ids);
    session.setStatusMessage("Box",
        QString("View isolated on %1 object(s)").arg(ids.size()));
}

void hideCurrentBox(SessionState& session, ViewportWindow& viewport,
                   DisplayState& display_state) {
    const std::vector<uint32_t> ids(display_state.currentBox().begin(),
                                    display_state.currentBox().end());
    if (ids.empty()) {
        session.setStatusMessage("Box", "The current box is empty");
        return;
    }
    viewport.setObjectsVisible(ids, false);
    session.setStatusMessage("Box",
        QString("%1 object(s) hidden").arg(ids.size()));
}

void isolateBoxSlot(SessionState& session, ViewportWindow& viewport,
                    DisplayState& display_state, int slot) {
    const std::vector<uint32_t> ids = display_state.boxSlotIds(slot);
    if (ids.empty()) {
        session.setStatusMessage("Box", QString("Box %1 is empty").arg(slot));
        return;
    }
    isolateObjects(viewport, display_state, ids);
    session.setStatusMessage("Box",
        QString("View isolated on Box %1 (%2 object(s))").arg(slot).arg(ids.size()));
}

// ---- Display -----------------------------------------------------------------------

void showSelection(ViewportWindow& viewport, DisplayState& display_state) {
    const std::vector<uint32_t> ids = selectionIds(viewport);
    viewport.setObjectsVisible(display_state.shownableIds(ids), true);
}

void hideSelection(ViewportWindow& viewport) {
    viewport.setObjectsVisible(selectionIds(viewport), false);
}

void showEverything(SessionState& session, ViewportWindow& viewport,
                    DisplayState& display_state) {
    viewport.showAllElements();
    // Category filters are durable for the session (disabled spaces /
    // openings must not come back), so re-apply them after the reset.
    display_state.applyAllCategoryFilters(viewport);
    session.setStatusMessage("Display", "All objects shown");
}

void isolateObjects(ViewportWindow& viewport, DisplayState& display_state,
                    const std::vector<uint32_t>& ids) {
    viewport.hideAllElements();
    // A disabled category can never be shown, even via an isolation.
    viewport.setObjectsVisible(display_state.shownableIds(ids), true);
}

// ---- Zoom -----------------------------------------------------------------------------

void fitActiveView(SessionState& session, ViewportWindow& viewport, QWidget* parent) {
    if (!viewport.hasVisibleElements()) {
        QMessageBox::information(parent, "Fit Active View", "The active view is empty.");
        session.setStatusMessage("Zoom", "The active view is empty");
        return;
    }
    viewport.viewVisibleElements();
    if (!viewport.anyDrawableElementWithinCameraPlane(200.0f)) {
        QMessageBox::information(parent, "Fit Active View", "The objects are far away.");
        session.setStatusMessage("Zoom", "View fitted — objects are far away");
        return;
    }
    session.setStatusMessage("Zoom", "View fitted");
}

void activatePerpendicularView(SessionState& session, ViewportWindow& viewport) {
    viewport.activatePerpendicularViewTool();
    session.setStatusMessage("Zoom", "Click a surface for the perpendicular view");
}

// ---- Tool cursors ----------------------------------------------------------------------

namespace {

// Draws a tool cursor pixmap: black shapes with a white outline so it reads
// on both light and dark viewports.
QCursor makeToolCursor(int hotspot_x, int hotspot_y, const std::function<void(QPainter&)>& draw) {
    QPixmap pixmap(32, 32);
    pixmap.fill(Qt::transparent);
    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing);
    // Outline pass (white, thick) then fill pass (black).
    QPen white(Qt::white);
    white.setWidthF(3.5);
    painter.setPen(white);
    painter.setBrush(Qt::NoBrush);
    draw(painter);
    QPen black(Qt::black);
    black.setWidthF(1.5);
    painter.setPen(black);
    painter.setBrush(Qt::black);
    draw(painter);
    return QCursor(pixmap, hotspot_x, hotspot_y);
}

} // namespace

QCursor knifeCursor() {
    return makeToolCursor(2, 2, [](QPainter& painter) {
        // A small diagonal knife: straight spine + curved cutting edge on the
        // blade (pointing at the top-left hotspot), thick rounded handle
        // (bottom-right).
        QPainterPath blade;
        blade.moveTo(3, 3);
        blade.lineTo(17, 11.5);              // spine
        blade.quadTo(19.5, 13, 16, 16);      // bolster end
        blade.quadTo(9, 10.5, 3, 3);         // curved cutting edge to the tip
        blade.closeSubpath();
        painter.drawPath(blade);

        QPen handle = painter.pen();
        handle.setWidthF(4.5);
        handle.setCapStyle(Qt::RoundCap);
        painter.setPen(handle);
        painter.drawLine(QPointF(15.5, 13.5), QPointF(26.5, 25.5));
    });
}

QCursor setSquareCursor() {
    return makeToolCursor(4, 4, [](QPainter& painter) {
        // Set square: right triangle with the right angle at the top-left
        // corner, plus the inner cut-out stroke.
        QPainterPath triangle;
        triangle.moveTo(4, 4);
        triangle.lineTo(4, 24);
        triangle.lineTo(24, 4);
        triangle.closeSubpath();
        painter.drawPath(triangle);
        QPainterPath inner;
        inner.moveTo(9, 9);
        inner.lineTo(9, 13);
        inner.lineTo(13, 9);
        painter.drawPath(inner);
    });
}

} // namespace bonsaiviewer::modules::display::commands
