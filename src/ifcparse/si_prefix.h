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

#ifndef IFCSIPREFIX
#define IFCSIPREFIX

#include "ifc_parse_api.h"

#include <string>

namespace ifcopenshell {
IFC_PARSE_API double si_prefix_to_value(const std::string& prefix);

template <typename Schema>
double get_SI_equivalent(const typename Schema::IfcNamedUnit& named_unit) {
    double scale = 1.;
    typename Schema::IfcSIUnit si_unit;

    if (auto conv_unit = named_unit.template as<typename Schema::IfcConversionBasedUnit>()) {
        auto factor = conv_unit.ConversionFactor();
        auto component = factor.UnitComponent();
        if (si_unit = component.concrete().template as<typename Schema::IfcSIUnit>()) {
            auto value = factor.ValueComponent();
            scale = value.get_attribute_value(0);
        }
    } else {
        si_unit = named_unit.template as<typename Schema::IfcSIUnit>();
    }
    if (si_unit) {
        if (si_unit.Prefix()) {
            scale *= si_prefix_to_value(Schema::IfcSIPrefix::ToString(*si_unit.Prefix()));
        }
    } else {
        scale = 0.;
    }

    return scale;
}
} // namespace ifcopenshell

#endif
