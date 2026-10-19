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

#ifndef IFCINTERFACE_MODULES_DISPLAY_COMMANDS_H
#define IFCINTERFACE_MODULES_DISPLAY_COMMANDS_H

#include <QCursor>

#include <cstdint>
#include <vector>

class SessionState;
class ViewportWindow;
class QWidget;

namespace bonsaiviewer::modules::display {
class DisplayState;
}

namespace bonsaiviewer::modules::display::commands {

// ---- Coupe ---------------------------------------------------------------

// Arm the one-shot cut-plane tool: the next plain left-click on a surface
// drops a plane perpendicular to the surface normal, then the tool
// deactivates. The knife cursor follows via ViewportWindow::sectionToolChanged.
void activateCutPlaneTool(SessionState& session, ViewportWindow& viewport);
// Deletes every cut plane (visible, hidden or suspended).
void removeAllCutPlanes(SessionState& session, ViewportWindow& viewport);
// "Masquer le plan de coupe": gizmos off, cutting stays on.
void setCutPlanesVisible(SessionState& session, ViewportWindow& viewport, bool visible);
// "Suspendre la coupe": cutting off (and gizmos hidden). Resuming re-shows
// the gizmos and reactivates the cuts.
void setCutSuspension(SessionState& session, ViewportWindow& viewport, bool suspended);

// ---- Coloration ------------------------------------------------------------

// QColorDialog for the selection; no-op when the selection is empty.
void paintSelectionWithDialog(SessionState& session, ViewportWindow& viewport,
                              DisplayState& display_state, QWidget* parent);
// Custom preset dialog (100/75/50/25 % opacity) for the selection.
void applyTransparencyWithDialog(SessionState& session, ViewportWindow& viewport,
                                 DisplayState& display_state, QWidget* parent);
// Elements return to the colour baked at load; opacity stays untouched.
void resetSelectionColor(SessionState& session, ViewportWindow& viewport,
                         DisplayState& display_state);

// ---- Boîte -----------------------------------------------------------------

void boxFromSelection(SessionState& session, ViewportWindow& viewport,
                      DisplayState& display_state);
void boxAddSelection(SessionState& session, ViewportWindow& viewport,
                     DisplayState& display_state);
void boxRemoveSelection(SessionState& session, ViewportWindow& viewport,
                        DisplayState& display_state);
// "Afficher uniquement la boîte courante": isolate the view on the box.
void isolateCurrentBox(SessionState& session, ViewportWindow& viewport,
                       DisplayState& display_state);
// "Masquer la boîte courante de la vue active".
void hideCurrentBox(SessionState& session, ViewportWindow& viewport,
                   DisplayState& display_state);
// "Afficher la Boîte N": isolate on slot N (1..3) without touching the
// current box.
void isolateBoxSlot(SessionState& session, ViewportWindow& viewport,
                    DisplayState& display_state, int slot);

// ---- Affichage --------------------------------------------------------------

// Disabled categories can never come back: the show/isolate verbs below
// filter their ids through DisplayState::shownableIds.
void showSelection(ViewportWindow& viewport, DisplayState& display_state);
void hideSelection(ViewportWindow& viewport);
// "Afficher tout": clears every per-element hide, then re-applies the
// category filters so disabled spaces/reservations stay hidden.
void showEverything(SessionState& session, ViewportWindow& viewport,
                    DisplayState& display_state);
// Shared isolation verb (box, search results): hide all, then show `ids`
// (minus disabled-category members).
void isolateObjects(ViewportWindow& viewport, DisplayState& display_state,
                    const std::vector<uint32_t>& ids);

// ---- Zoom -------------------------------------------------------------------

// "Ajuster sur la vue active": viewAll + the two informational pop-ups
// ("La vue active est vide." / "Les objets sont lointains.").
void fitActiveView(SessionState& session, ViewportWindow& viewport, QWidget* parent);
// "Vue perpendiculaire": arm the one-shot tool; the set-square cursor follows
// via ViewportWindow::perpendicularViewToolChanged.
void activatePerpendicularView(SessionState& session, ViewportWindow& viewport);

// ---- Tool cursors -------------------------------------------------------------

// Knife cursor for the cut-plane tool.
QCursor knifeCursor();
// Set-square (équerre) cursor for the perpendicular-view tool.
QCursor setSquareCursor();

} // namespace bonsaiviewer::modules::display::commands

#endif
