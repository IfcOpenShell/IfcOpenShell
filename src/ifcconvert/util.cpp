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

#include <set>
#include <iostream>

#include "../ifcconvert/util.h"

using namespace util;

SHARED_PTR<string_buffer::string_item> string_buffer::add(const std::string& s) {
	SHARED_PTR<string_item> i = SHARED_PTR<string_item>(new string_item(s));
	items.push_back(i);
	return i;
}
SHARED_PTR<string_buffer::float_item> string_buffer::add(const double& d) {
	SHARED_PTR<float_item> i = SHARED_PTR<float_item>(new float_item(d));
	items.push_back(i);
	return i;
}
std::string string_buffer::str() const {
	std::stringstream ss;
	for (std::vector< SHARED_PTR<item> >::const_iterator it = items.begin(); it != items.end(); ++it) {
		ss << (**it).str();
	}
	return ss.str();
}
