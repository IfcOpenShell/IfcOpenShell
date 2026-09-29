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

#include "si_prefix.h"

double ifcopenshell::si_prefix_to_value(const std::string& prefix) {
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
