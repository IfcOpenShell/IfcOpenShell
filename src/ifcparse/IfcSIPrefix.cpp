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
double IfcParse::get_SI_equivalent(typename Schema::IfcNamedUnit* named_unit) {
    double scale = 1.;
    typename Schema::IfcSIUnit* si_unit = 0;

    if (named_unit->declaration().is(Schema::IfcConversionBasedUnit::Class())) {
        typename Schema::IfcConversionBasedUnit* conv_unit = named_unit->template as<typename Schema::IfcConversionBasedUnit>();
        typename Schema::IfcMeasureWithUnit* factor = conv_unit->ConversionFactor();
        typename Schema::IfcUnit* component = factor->UnitComponent();
        if (component->declaration().is(Schema::IfcSIUnit::Class())) {
            si_unit = component->template as<typename Schema::IfcSIUnit>();
            typename Schema::IfcValue* value = factor->ValueComponent();
            scale = value->data().get_attribute_value(0);
        }
    } else if (named_unit->declaration().is(Schema::IfcSIUnit::Class())) {
        si_unit = named_unit->template as<typename Schema::IfcSIUnit>();
    }
    if (si_unit) {
        if (si_unit->Prefix()) {
            scale *= IfcSIPrefixToValue(Schema::IfcSIPrefix::ToString(*si_unit->Prefix()));
        }
    } else {
        scale = 0.;
    }

    return scale;
}

#if defined(_MSC_VER) && _MSC_VER < 1900

#ifdef HAS_SCHEMA_2x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc2x3>(Ifc2x3::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4>(Ifc4::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x1>(Ifc4x1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x2>(Ifc4x2::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc1>(Ifc4x3_rc1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc2>(Ifc4x3_rc2::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc3>(Ifc4x3_rc3::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc4>(Ifc4x3_rc4::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3>(Ifc4x3::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add1>(Ifc4x3_add1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add2>(Ifc4x3_add2::IfcNamedUnit* named_unit);
#endif

#else

#ifdef HAS_SCHEMA_2x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc2x3>(typename Ifc2x3::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4>(typename Ifc4::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x1>(typename Ifc4x1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x2>(typename Ifc4x2::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc1>(typename Ifc4x3_rc1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc2>(typename Ifc4x3_rc2::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc3>(typename Ifc4x3_rc3::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_rc4
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_rc4>(typename Ifc4x3_rc4::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3>(typename Ifc4x3::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_tc1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_tc1>(typename Ifc4x3_tc1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add1
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add1>(typename Ifc4x3_add1::IfcNamedUnit* named_unit);
#endif
#ifdef HAS_SCHEMA_4x3_add2
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3_add2>(typename Ifc4x3_add2::IfcNamedUnit* named_unit);
#endif

#endif
