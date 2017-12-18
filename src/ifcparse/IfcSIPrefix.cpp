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

double IfcParse::IfcSIPrefixToValue(const std::string& v) {
	if      ( v == "EXA"   ) return 1.e18;
	else if ( v == "PETA"  ) return 1.e15;
	else if ( v == "TERA"  ) return 1.e12;
	else if ( v == "GIGA"  ) return 1.e9;
	else if ( v == "MEGA"  ) return 1.e6;
	else if ( v == "KILO"  ) return 1.e3;
	else if ( v == "HECTO" ) return 1.e2;
	else if ( v == "DECA"  ) return 1.;
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
	IfcSchema::IfcSIUnit* si_unit = 0;

	if (named_unit->declaration().is(IfcSchema::Type::IfcConversionBasedUnit)) {
		IfcSchema::IfcConversionBasedUnit* conv_unit = named_unit->as<IfcSchema::IfcConversionBasedUnit>();
		IfcSchema::IfcMeasureWithUnit* factor = conv_unit->ConversionFactor();
		IfcSchema::IfcUnit* component = factor->UnitComponent();
		if (component->declaration().is(IfcSchema::Type::IfcSIUnit)) {
			si_unit = component->as<IfcSchema::IfcSIUnit>();
			IfcSchema::IfcValue* v = factor->ValueComponent();
			scale = *v->data().getArgument(0);
		}		
	} else if (named_unit->declaration().is(IfcSchema::Type::IfcSIUnit)) {
		si_unit = named_unit->as<IfcSchema::IfcSIUnit>();
	}
	if (si_unit) {
		if (si_unit->hasPrefix()) {
			scale *= IfcSIPrefixToValue(si_unit->Prefix());
		}
	} else {
		scale = 0.;
	}

	return scale;
}
