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
#include "../ifcparse/Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
#include "../ifcparse/Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
#include "../ifcparse/Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
#include "../ifcparse/Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
#include "../ifcparse/Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
#include "../ifcparse/Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
#include "../ifcparse/Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
#include "../ifcparse/Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
#include "../ifcparse/Ifc4x3.h"
#endif

double IfcParse::IfcSIPrefixToValue(const std::string& v) {
	if      ( v == "EXA"   ) return 1.e18;
	else if ( v == "PETA"  ) return 1.e15;
	else if ( v == "TERA"  ) return 1.e12;
	else if ( v == "GIGA"  ) return 1.e9;
	else if ( v == "MEGA"  ) return 1.e6;
	else if ( v == "KILO"  ) return 1.e3;
	else if ( v == "HECTO" ) return 1.e2;
	else if ( v == "DECA"  ) return 1.e1;
	else if ( v == "DECI"  ) return 1.e-1;
	else if ( v == "CENTI" ) return 1.e-2;
	else if ( v == "MILLI" ) return 1.e-3;
	else if ( v == "MICRO" ) return 1.e-6;
	else if ( v == "NANO"  ) return 1.e-9;
	else if ( v == "PICO"  ) return 1.e-12;
	else if ( v == "FEMTO" ) return 1.e-15;
	else if ( v == "ATTO"  ) return 1.e-18;
	else return 1.;
}

template <typename Schema>
double IfcParse::get_SI_equivalent(typename Schema::IfcNamedUnit* named_unit) {
	double scale =  1.;
	typename Schema::IfcSIUnit* si_unit = 0;

	if (named_unit->declaration().is(Schema::IfcConversionBasedUnit::Class())) {
		typename Schema::IfcConversionBasedUnit* conv_unit = named_unit->template as<typename Schema::IfcConversionBasedUnit>();
		typename Schema::IfcMeasureWithUnit* factor = conv_unit->ConversionFactor();
		typename Schema::IfcUnit* component = factor->UnitComponent();
		if (component->declaration().is(Schema::IfcSIUnit::Class())) {
			si_unit = component->template as<typename Schema::IfcSIUnit>();
			typename Schema::IfcValue* v = factor->ValueComponent();
			scale = *v->data().getArgument(0);
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
template double IFC_PARSE_API IfcParse::get_SI_equivalent<Ifc4x3>(Ifc4x3_rc4::IfcNamedUnit* named_unit);
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

#endif
