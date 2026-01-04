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

#include "IfcSIPrefix.h"
#include "InstanceData.h"

#ifdef HAS_SCHEMA_2x3
#include "Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
#include "Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
#include "Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
#include "Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
#include "Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
#include "Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
#include "Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
#include "Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
#include "Ifc4x3.h"
#endif
#ifdef HAS_SCHEMA_4x3_tc1
#include "Ifc4x3_tc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add1
#include "Ifc4x3_add1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add2
#include "Ifc4x3_add2.h"
#endif

double IfcParse::IfcSIPrefixToValue(const std::string& prefix) {
    if (prefix == "EXA") {
        return 1.e18;
    }
    if (prefix == "PETA") {
        return 1.e15;
    }
    if (prefix == "TERA") {
        return 1.e12;
    }
    if (prefix == "GIGA") {
        return 1.e9;
    }
    if (prefix == "MEGA") {
        return 1.e6;
    }
    if (prefix == "KILO") {
        return 1.e3;
    }
    if (prefix == "HECTO") {
        return 1.e2;
    }
    if (prefix == "DECA") {
        return 1.e1;
    }
    if (prefix == "DECI") {
        return 1.e-1;
    }
    if (prefix == "CENTI") {
        return 1.e-2;
    }
    if (prefix == "MILLI") {
        return 1.e-3;
    }
    if (prefix == "MICRO") {
        return 1.e-6;
    }
    if (prefix == "NANO") {
        return 1.e-9;
    }
    if (prefix == "PICO") {
        return 1.e-12;
    }
    if (prefix == "FEMTO") {
        return 1.e-15;
    }
    if (prefix == "ATTO") {
        return 1.e-18;
    }
    return 1.;
}

template <typename Schema>
double IfcParse::get_SI_equivalent(const typename Schema::IfcNamedUnit& named_unit) {
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
            scale *= IfcSIPrefixToValue(Schema::IfcSIPrefix::ToString(*si_unit.Prefix()));
        }
    } else {
        scale = 0.;
    }

    return scale;
}

#if defined(_MSC_VER) && _MSC_VER < 1900

#ifdef HAS_SCHEMA_2x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc2x3>(const Ifc2x3::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4>(const Ifc4::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x1>(const Ifc4x1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x2>(const Ifc4x2::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc1>(const Ifc4x3_rc1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc2>(const Ifc4x3_rc2::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc3>(const Ifc4x3_rc3::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc4>(const Ifc4x3_rc4::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3>(const Ifc4x3::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_tc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_tc1>(const Ifc4x3_tc1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add1>(const Ifc4x3_add1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add2>(const Ifc4x3_add2::IfcNamedUnit& named_unit);
#endif

#else

#ifdef HAS_SCHEMA_2x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc2x3>(const typename Ifc2x3::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4>(const typename Ifc4::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x1>(const typename Ifc4x1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x2>(const typename Ifc4x2::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc1>(const typename Ifc4x3_rc1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc2>(const typename Ifc4x3_rc2::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc3>(const typename Ifc4x3_rc3::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc4>(const typename Ifc4x3_rc4::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3>(const typename Ifc4x3::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_tc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_tc1>(const typename Ifc4x3_tc1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add1>(const typename Ifc4x3_add1::IfcNamedUnit& named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add2>(const typename Ifc4x3_add2::IfcNamedUnit& named_unit);
#endif

#endif
