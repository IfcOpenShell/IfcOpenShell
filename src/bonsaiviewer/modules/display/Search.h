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

#ifndef IFCINTERFACE_MODULES_DISPLAY_SEARCH_H
#define IFCINTERFACE_MODULES_DISPLAY_SEARCH_H

#include <QString>

#include <cstdint>
#include <optional>
#include <vector>

class SessionState;
class ViewportWindow;

namespace bonsaiviewer::modules::display {
class DisplayState;

// Search bar for the ribbon band (SPEC_Viewer.md, "SEARCH BAR").
// Reads the IFC data of every loaded model directly through the live data
// source (SceneLoader::ifcFile) — nothing goes through the Python engine.
namespace search {

struct SearchOptions {
    bool full_search       = false;  // -fs: all property names and values
    bool visible_only      = false;  // -v: visible objects in the active view
    bool current_box_only  = false;  // -p: current box members only
    bool case_sensitive    = false;  // -c
    QString property_name;          // -prop "Set.Name" ("" = not set)
    QString text;                   // the search text (may be empty)
};

// Parses the raw input. Prefixes come first, separated by spaces; the
// remainder is the search text. A -prop name may be quoted when it contains
// spaces. Returns nullopt + an error message on malformed input.
std::optional<SearchOptions> parse(const QString& input, QString* error_out);

// Returns the object_ids whose fields contain the search text (substring,
// case-insensitive unless -c). The caller isolates the view on the result.
std::vector<uint32_t> run(const SearchOptions& options,
                          SessionState& session_state,
                          ViewportWindow& viewport,
                          const DisplayState& display_state);

} // namespace search

} // namespace bonsaiviewer::modules::display

#endif
