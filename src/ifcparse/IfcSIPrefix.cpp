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

double IfcParse::IfcSIPrefixToValue(IfcSchema::IfcSIPrefix::IfcSIPrefix v) {
	if      ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_EXA   ) return 1.e18;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_PETA  ) return 1.e15;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_TERA  ) return 1.e12;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_GIGA  ) return 1.e9;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_MEGA  ) return 1.e6;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_KILO  ) return 1.e3;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_HECTO ) return 1.e2;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_DECA  ) return 1.;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_DECI  ) return 1.e-1;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_CENTI ) return 1.e-2;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_MILLI ) return 1.e-3;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_MICRO ) return 1.e-6;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_NANO  ) return 1.e-9;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_PICO  ) return 1.e-12;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_FEMTO ) return 1.e-15;
	else if ( v == IfcSchema::IfcSIPrefix::IfcSIPrefix_ATTO  ) return 1.e-18;
	else return 1.;
}