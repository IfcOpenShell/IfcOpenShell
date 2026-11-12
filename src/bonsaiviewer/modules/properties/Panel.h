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

#ifndef IFCINTERFACE_MODULES_PROPERTIES_PANEL_H
#define IFCINTERFACE_MODULES_PROPERTIES_PANEL_H

#include "Types.h"

#include "../../components/Panel.h"

#include <QString>

class QLabel;
class QLineEdit;
class QToolButton;
class QWidget;

namespace bonsaiviewer::modules::properties {

class PropertiesPanel : public components::Panel {
    Q_OBJECT
public:
    explicit PropertiesPanel(QWidget* parent = nullptr);

    void render(const PropertiesPanelState& state);

private:
    // Rebuild the set widgets inside their container, applying the current
    // (case-insensitive) filter text: a set is shown only if its name or one of
    // its property names/values matches, and — when it's a property/value match
    // rather than a set-name match — only the matching rows are kept. Toggles a
    // "No properties" / "No matching properties" placeholder.
    void rebuildPropertyWidgets();
    void rebuildQuantityWidgets();

    bool attributes_expanded_ = true;
    bool relationships_expanded_ = true;
    bool properties_expanded_ = true;
    bool quantities_expanded_ = true;
    bool properties_filter_visible_ = false;
    bool quantities_filter_visible_ = false;
    QString properties_filter_text_;
    QString quantities_filter_text_;

    // Raw data + the container the set widgets live in, so a filter change can
    // rebuild just the sets without disturbing the filter field. Recreated on
    // each render(); the container is owned by its section.
    QList<PropertySet> property_sets_data_;
    QList<PropertySet> quantity_sets_data_;
    QWidget* properties_container_ = nullptr;
    QWidget* quantities_container_ = nullptr;
};

} // namespace bonsaiviewer::modules::properties

#endif
