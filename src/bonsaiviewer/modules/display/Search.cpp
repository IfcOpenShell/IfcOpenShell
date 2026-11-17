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

#include "Search.h"

#include "DisplayState.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "../../../ifcparse/argument_type.h"
#include "../../../ifcparse/express.h"
#include "../../../ifcparse/file.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/ViewportWindow.h"
#include "element.h"  // helpers: get_container, get_predefined_type, get_string_attribute
#include "pset.h"     // helpers: get_psets

#include <QList>
#include <QStringList>

#include <map>
#include <set>

namespace bonsaiviewer::modules::display::search {

namespace {

// ---- Query parsing ---------------------------------------------------------

// Splits `input` on spaces, keeping double-quoted segments as single tokens.
QStringList tokenize(const QString& input) {
    QStringList tokens;
    QString current;
    bool in_quotes = false;
    bool has_token = false;
    for (const QChar c : input) {
        if (c == QLatin1Char('"')) {
            in_quotes = !in_quotes;
            has_token = true;
        } else if (c.isSpace() && !in_quotes) {
            if (has_token) tokens.append(current);
            current.clear();
            has_token = false;
        } else {
            current.append(c);
            has_token = true;
        }
    }
    if (has_token) tokens.append(current);
    return tokens;
}

std::optional<QString> readQuotedOrPlainToken(const QStringList& tokens, int& index) {
    if (index >= tokens.size()) return std::nullopt;
    return tokens.at(index++);
}

// ---- IFC data access --------------------------------------------------------

// Every string reachable from `element`'s attributes, recursing into
// referenced instances up to `max_depth`. Used for material names (a
// layer-set usage stores its material several hops away) and for the -fs
// full-text scan.
void collectStrings(const express::base& element, int max_depth, QStringList& out) {
    if (!element || max_depth < 0) return;
    const ifcopenshell::entity* declaration = element.declaration().as_entity();
    if (declaration == nullptr) return;
    const auto& attributes = declaration->all_attributes();
    for (std::size_t index = 0; index < attributes.size(); ++index) {
        ifcopenshell::attribute_value value;
        try {
            value = element.get_attribute_value(index);
        } catch (...) {
            continue;
        }
        if (value.isNull()) continue;
        switch (value.type()) {
        case ifcopenshell::Argument_STRING:
            out.append(QString::fromStdString(static_cast<std::string>(value)));
            break;
        case ifcopenshell::Argument_ENUMERATION:
            break;  // enumeration labels (e.g. .CEILING.) are not searched
        case ifcopenshell::Argument_ENTITY_INSTANCE: {
            try {
                collectStrings(static_cast<express::base>(value), max_depth - 1, out);
            } catch (...) {
            }
            break;
        }
        case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
            try {
                for (const auto& referenced : static_cast<std::vector<express::base>>(value)) {
                    collectStrings(referenced, max_depth - 1, out);
                }
            } catch (...) {
            }
            break;
        }
        case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE:
            break;  // not present on any path we traverse
        default:
            break;  // ints/doubles/bools: the search is text-only
        }
    }
}

// The storey ("étage de rattachement") for an element, or an invalid entity.
express::base containerStorey(const express::base& element) {
    express::base container = get_container(element);
    while (container) {
        if (container.declaration().is("IfcBuildingStorey")) return container;
        container = get_container(container);
    }
    return {};
}

// ifc_id -> material strings for one model (from IfcRelAssociatesMaterial).
std::map<int, QStringList> materialNamesForModel(ifcopenshell::file& file) {
    std::map<int, QStringList> result;
    try {
        for (const auto& rel : file.instances_by_type("IfcRelAssociatesMaterial")) {
            const ifcopenshell::entity* declaration = rel.declaration().as_entity();
            if (declaration == nullptr) continue;
            const std::ptrdiff_t objects_index = declaration->attribute_index("RelatedObjects");
            const std::ptrdiff_t material_index = declaration->attribute_index("RelatedMaterial");
            if (objects_index < 0 || material_index < 0) continue;

            QStringList material_strings;
            try {
                ifcopenshell::attribute_value material_value =
                    rel.get_attribute_value(static_cast<std::size_t>(material_index));
                if (!material_value.isNull()
                    && material_value.type() == ifcopenshell::Argument_ENTITY_INSTANCE) {
                    // Depth 4 covers the longest chain we care about:
                    // usage → ForLayerSet → MaterialLayers → Material → Name.
                    collectStrings(static_cast<express::base>(material_value), 4, material_strings);
                }
            } catch (...) {
            }
            if (material_strings.isEmpty()) continue;

            try {
                ifcopenshell::attribute_value objects_value =
                    rel.get_attribute_value(static_cast<std::size_t>(objects_index));
                if (objects_value.type() != ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE) continue;
                for (const auto& object : static_cast<std::vector<express::base>>(objects_value)) {
                    if (!object) continue;
                    QStringList& entry = result[static_cast<int>(object.id())];
                    for (const QString& text : material_strings) {
                        if (!entry.contains(text)) entry.append(text);
                    }
                }
            } catch (...) {
            }
        }
    } catch (...) {
    }
    return result;
}

// The scalar text of a property_value (numbers formatted like the properties
// panel). Returns an empty string for non-scalar values.
QString formatPropertyValue(const property_value& value) {
    if (const auto* text = value.get_if<std::string>()) {
        return QString::fromStdString(*text);
    }
    if (const auto* flag = value.get_if<bool>()) {
        return *flag ? QStringLiteral("True") : QStringLiteral("False");
    }
    if (const auto* integer = value.get_if<std::int64_t>()) {
        return QString::number(static_cast<qlonglong>(*integer));
    }
    if (const auto* real = value.get_if<double>()) {
        return QString::number(*real);
    }
    return {};
}

// The value of one specific property ("Set.Name" or bare "Name"), searched
// across every property set of the element.
QStringList propertyValuesFor(const express::base& element, const QString& property_path) {
    QStringList out;
    QString set_name;
    QString property_name = property_path;
    const int dot = property_path.indexOf(QLatin1Char('.'));
    if (dot > 0) {
        set_name = property_path.left(dot);
        property_name = property_path.mid(dot + 1);
    }
    try {
        const element_properties sets = get_psets(element, /*psets_only=*/false, /*qtos_only=*/false);
        for (const auto& [set, properties] : sets) {
            if (!set_name.isEmpty() && QString::fromStdString(set) != set_name) continue;
            const auto it = properties.find(property_name.toStdString());
            if (it == properties.end()) continue;
            const QString formatted = formatPropertyValue(it->second);
            if (!formatted.isEmpty()) out.append(formatted);
        }
    } catch (...) {
    }
    return out;
}

bool containsText(const QStringList& fields, const QString& text, bool case_sensitive) {
    if (text.isEmpty()) return !fields.isEmpty();
    for (const QString& field : fields) {
        if (field.contains(text, case_sensitive ? Qt::CaseSensitive : Qt::CaseInsensitive)) {
            return true;
        }
    }
    return false;
}

} // namespace

// ---- API ---------------------------------------------------------------------

std::optional<SearchOptions> parse(const QString& input, QString* error_out) {
    const QStringList tokens = tokenize(input);
    SearchOptions options;
    int index = 0;
    while (index < tokens.size()) {
        const QString token = tokens.at(index);
        if (token == QLatin1String("-fs")) {
            options.full_search = true;
        } else if (token == QLatin1String("-v")) {
            options.visible_only = true;
        } else if (token == QLatin1String("-p")) {
            options.current_box_only = true;
        } else if (token == QLatin1String("-c")) {
            options.case_sensitive = true;
        } else if (token == QLatin1String("-prop")) {
            ++index;
            const auto name = readQuotedOrPlainToken(tokens, index);
            if (!name.has_value() || name->isEmpty()) {
                if (error_out) *error_out = QStringLiteral("The -prop prefix must be followed by a property name.");
                return std::nullopt;
            }
            options.property_name = *name;
        } else if (token.startsWith(QLatin1Char('-')) && token.size() > 1) {
            if (error_out) *error_out = QStringLiteral("Unknown prefix: %1").arg(token);
            return std::nullopt;
        } else {
            break;  // first non-prefix token: the search text starts here
        }
        ++index;
    }
    options.text = tokens.mid(index).join(QLatin1Char(' '));
    if (options.text.isEmpty()) {
        if (error_out) *error_out = QStringLiteral("Enter a text to search.");
        return std::nullopt;
    }
    return options;
}

std::vector<uint32_t> run(const SearchOptions& options,
                          SessionState& session_state,
                          ViewportWindow& viewport,
                          const DisplayState& display_state) {
    ElementRegistry* registry = session_state.elementRegistry();
    SceneLoader* loader = session_state.loader();
    if (registry == nullptr || loader == nullptr) return {};

    std::vector<uint32_t> matches;
    const auto& box = display_state.currentBox();

    for (uint32_t session_model_id : session_state.sessionModelIds()) {
        const QString model_name = loader->displayName(session_model_id);
        ifcopenshell::file* file = loader->ifcFile(session_model_id);

        const std::map<int, QStringList> materials =
            (file != nullptr) ? materialNamesForModel(*file) : std::map<int, QStringList>();

        for (const auto& info : registry->basicElementInfoForModel(session_model_id)) {
            if (options.visible_only && viewport.isElementHidden(info.object_id)) continue;
            if (options.current_box_only && box.count(info.object_id) == 0) continue;

            express::base entity;
            if (file != nullptr) {
                try {
                    entity = file->instance_by_id(info.ifc_id);
                } catch (...) {
                }
            }

            // A disabled category can never be shown — keep it out of the
            // results so the reported count matches what gets isolated.
            if (entity) {
                if (!display_state.categoryEnabled(DisplayState::Category::Spaces)
                    && entity.declaration().is("IfcSpace")) {
                    continue;
                }
                if (!display_state.categoryEnabled(DisplayState::Category::Reservations)
                    && entity.declaration().is("IfcOpeningElement")) {
                    continue;
                }
            }

            QStringList fields;
            fields.append(info.name);
            // Identity fields searched by default: GUID, class name (from the
            // element table, else the live entity declaration) and the
            // predefined type.
            fields.append(info.guid);
            if (!info.type.isEmpty()) fields.append(info.type);
            fields.append(model_name);
            if (entity) {
                fields.append(QString::fromStdString(entity.declaration().name()));
                if (auto predefined = get_predefined_type(entity)) {
                    fields.append(QString::fromStdString(*predefined));
                }
                if (auto long_name = get_string_attribute(entity, "LongName")) {
                    fields.append(QString::fromStdString(*long_name));
                }
                if (const express::base storey = containerStorey(entity)) {
                    if (auto storey_name = get_string_attribute(storey, "Name")) {
                        fields.append(QString::fromStdString(*storey_name));
                    }
                    if (auto storey_long_name = get_string_attribute(storey, "LongName")) {
                        fields.append(QString::fromStdString(*storey_long_name));
                    }
                }
            }
            if (!options.property_name.isEmpty()) {
                // -prop: the search text applies to that property's value only.
                if (entity) {
                    fields = propertyValuesFor(entity, options.property_name);
                } else {
                    fields.clear();
                }
            } else {
                const auto materials_it = materials.find(info.ifc_id);
                if (materials_it != materials.end()) fields.append(materials_it->second);
                if (options.full_search && entity) {
                    try {
                        for (const auto& [set, properties] : get_psets(entity, false, false)) {
                            for (const auto& [property, value] : properties) {
                                fields.append(QString::fromStdString(set));
                                fields.append(QString::fromStdString(property));
                                const QString formatted = formatPropertyValue(value);
                                if (!formatted.isEmpty()) fields.append(formatted);
                            }
                        }
                    } catch (...) {
                    }
                }
            }

            if (containsText(fields, options.text, options.case_sensitive)) {
                matches.push_back(info.object_id);
            }
        }
    }
    return matches;
}

} // namespace bonsaiviewer::modules::display::search
